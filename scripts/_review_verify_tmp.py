#!/usr/bin/env python3
"""
Verification gate for the site. Serves the built `dist/` and drives it with
Playwright. This is the objective floor a ticket must clear; it does not judge
whether the design is good.

Universal checks, per route x viewport x theme:
  1. No horizontal scroll  (scrollWidth <= clientWidth). Measured, never eyeballed.
  2. No console errors, no failed requests.
  3. WCAG AA contrast on every rendered text leaf, at the threshold for its size
     and weight.
  4. Renders with prefers-reduced-motion forced: content present, not blank.
  5. Renders with JavaScript disabled: text present, nothing stuck at opacity 0.
  6. No em-dash anywhere the page publishes: body text, alt text, captions,
     the tab title, the meta description. One fails the build.
  7. Reachability: a link a route declares as reachable must be hit-testable at
     some point during the scroll-through, at every viewport. A link can be in
     the DOM, resolve, and still be clipped out of reach; that is a real bug the
     link crawl cannot see.
  8. Keyboard: tabbing through the page, every stop shows a visible focus ring,
     is at least half on screen, is not inside an aria-hidden subtree, and comes
     after the previous stop in the document. The skip link is the first stop and
     moves focus to its target. Focus wraps out of the page rather than trapping.
  9. What the page hands assistive technology: no sibling content announced
     twice, no aria-hidden thrown over a heading or a landmark, and exactly one
     banner, main and contentinfo.
Plus a link crawl from the entry pages.

Per-route checks come from EXPECTATIONS below: each route declares what must be
true of its own rendered output. Adding a page means adding its row.

Screenshots land in .verify/ (gitignored) for a human to look at.

Run:  npm run verify              (type check, build, then every route in the table)
      npm run verify -- /about/   (same, swept against one path for a fast loop)
"""
from __future__ import annotations

import functools
import http.server
import socketserver
import sys
import threading
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
OUT = ROOT / ".verify"
PORT = 4387

VIEWPORTS = {"375": (375, 812), "768": (768, 1024), "1440": (1440, 900)}
THEMES = ("dark",)   # dark-only site by decision; see CLAUDE.md


def serve(directory: Path, port: int) -> socketserver.TCPServer:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(directory))
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


CONTRAST_SWEEP = r"""
() => {
  // Tailwind's opacity modifiers emit color-mix()/oklab(), which a naive rgb regex
  // mangles. Canvas fillStyle normalizes any CSS color to #rrggbb / rgba() for us.
  // Tailwind's opacity modifiers emit color-mix(), which Chrome computes to
  // oklab(). Canvas fillStyle accepts that string but hands it straight back
  // unnormalized, so a naive rgb regex reads 0.97/0.0009/0.004 as near-black.
  // Convert the CSS Color 4 forms properly instead of guessing.
  const cv = document.createElement('canvas').getContext('2d');
  const g2 = (u) => {
    const v = u <= 0.0031308 ? 12.92 * u : 1.055 * Math.pow(u, 1 / 2.4) - 0.055;
    return Math.max(0, Math.min(255, Math.round(v * 255)));
  };
  const oklabToRgb = (L, A, B) => {
    const l = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3;
    const m = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3;
    const s2 = (L - 0.0894841775 * A - 1.2914855480 * B) ** 3;
    return [
      g2(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s2),
      g2(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s2),
      g2(-0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s2),
    ];
  };
  const nums = (v) => (v.match(/-?[\d.]+(?:e-?\d+)?/g) || []).map(Number);
  const parse = (c) => {
    if (!c || c === 'transparent' || c === 'none') return null;
    let v = c.trim();
    if (!/^(oklab|oklch|color)\(/.test(v)) {
      try { cv.fillStyle = '#000'; cv.fillStyle = v; v = cv.fillStyle; } catch (e) { return null; }
    }
    if (v[0] === '#') {
      return [parseInt(v.slice(1, 3), 16), parseInt(v.slice(3, 5), 16), parseInt(v.slice(5, 7), 16), 1];
    }
    if (v.startsWith('oklab(')) {
      const n = nums(v);
      return [...oklabToRgb(n[0], n[1], n[2]), n.length > 3 ? n[3] : 1];
    }
    if (v.startsWith('oklch(')) {
      const n = nums(v);
      const h = (n[2] || 0) * Math.PI / 180;
      return [...oklabToRgb(n[0], n[1] * Math.cos(h), n[1] * Math.sin(h)), n.length > 3 ? n[3] : 1];
    }
    if (v.startsWith('color(')) {
      // The colour-space keyword has to go before the digits are read, or the
      // 3 in `display-p3` is picked up as the red channel and every subsequent
      // channel shifts by one, which fabricates a ratio rather than failing.
      const n = nums(v.replace(/^color\(\s*[a-z][a-z0-9-]*/i, 'color('));
      if (n.length < 3) return null;
      return [
        Math.round(n[0] * 255), Math.round(n[1] * 255), Math.round(n[2] * 255),
        n.length > 3 ? n[3] : 1,
      ];
    }
    const n = nums(v);
    if (n.length < 3) return null;
    return [n[0], n[1], n[2], n.length > 3 ? n[3] : 1];
  };
  const over = (fg, bg) => [0, 1, 2].map((i) => fg[i] * fg[3] + bg[i] * (1 - fg[3]));
  const lum = (rgb) => {
    const a = rgb.map((v) => {
      const s = v / 255;
      return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2];
  };
  // Composite every semi-transparent background layer down to something opaque.
  const bgOf = (el) => {
    const layers = [];
    let n = el;
    while (n) {
      const c = parse(getComputedStyle(n).backgroundColor);
      if (c && c[3] > 0) { layers.push(c); if (c[3] >= 1) break; }
      n = n.parentElement;
    }
    if (!layers.length || layers[layers.length - 1][3] < 1) layers.push([255, 255, 255, 1]);
    let out = layers[layers.length - 1].slice(0, 3);
    for (let i = layers.length - 2; i >= 0; i--) out = over(layers[i], out);
    return out;
  };

  // How much bigger or smaller than its own user units an SVG element is drawn.
  // 1 for anything that is not inside an SVG.
  const svgScale = (el) => {
    const svg = el.ownerSVGElement;
    if (!svg) return 1;
    const vb = svg.viewBox.baseVal;
    const drawn = svg.getBoundingClientRect().width;
    if (!vb || !vb.width || !drawn) return 1;
    return drawn / vb.width;
  };

  const out = [];
  document.querySelectorAll('body *').forEach((el) => {
    const own = [...el.childNodes].filter((n) => n.nodeType === 3)
      .map((n) => n.textContent.trim()).join('');
    if (!own) return;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none') return;
    if (parseFloat(cs.opacity) < 0.9) return;               // mid-animation
    if (el.closest('[aria-hidden="true"]')) return;         // decorative
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) return;
    const fg = parse(cs.color);
    if (!fg) return;
    const bg = bgOf(el);
    const l1 = lum(over(fg, bg)), l2 = lum(bg);
    const [hi, lo] = l1 > l2 ? [l1, l2] : [l2, l1];
    const ratio = (hi + 0.05) / (lo + 0.05);
    // AA's threshold is set by the size the text is PAINTED at. For HTML that is
    // the computed font-size, but inside an SVG the computed size is in user
    // units and the whole drawing is then scaled to fit its column: a 26px label
    // in a 560-unit viewBox paints at ~15.6px in a 335px column. Taking the
    // computed value there would apply the large-text 3.0 threshold to text that
    // renders as normal body copy and needs 4.5, which is the gate quietly
    // green-lighting a real AA failure.
    const size = parseFloat(cs.fontSize) * svgScale(el);
    const bold = parseInt(cs.fontWeight, 10) >= 700;
    const need = size >= 24 || (bold && size >= 18.66) ? 3.0 : 4.5;
    if (ratio < need) {
      out.push({
        ratio: Math.round(ratio * 100) / 100, need, size: Math.round(size),
        text: own.slice(0, 32),
        // `className` is an SVGAnimatedString on an SVG element, so stringifying
        // it reports every SVG failure as "[object". The attribute is a string
        // on both.
        sel: el.tagName.toLowerCase() + '.' + (el.getAttribute('class') || '').split(' ')[0],
      });
    }
  });
  return out.slice(0, 6);
}
"""

# Routes that exist in the Jekyll site but have not been migrated to Astro yet.
# A 404 on one of these is a "not built yet", not a broken link. Empty as of
# tickets 04 and 05: every page the Jekyll site serves now has an Astro route,
# so from here a 404 on an internal link is a real failure.
PENDING: set[str] = set()


# --------------------------------------------------------------------------
# Per-route expectations.
#
# A row states what must be true of the page a visitor RECEIVES: heading levels,
# named sections, figures, alt text, links, copy. A row never names a class, a
# component or a file, so the table survives a redesign and still catches a
# regression. Every ticket adds its route's row and is finished when the gate
# passes with that row in place.
#
# Keys, all optional:
#   headings   {"h1": 1, ...}  exact count of each heading level that is listed
#   ids        ["main", ...]   element ids that must exist (fragment targets and
#                              named sections)
#   figures    int             exact count of <figure>
#   alt        True            every picture says what it shows: an <img> carries
#                              non-empty alt text and an svg[role="img"] carries
#                              an accessible name, unless it is explicitly
#                              decorative (aria-hidden or role="presentation")
#   links      ["/about/"]     internal links that must be present on the page,
#                              and must resolve unless still listed in PENDING
#   text       ["substring"]   copy that must appear in the rendered text, matched
#                              case- and whitespace-insensitively so that a
#                              text-transform or a reflow is not a copy regression
#   reachable  ["/a/"]        links a visitor must be able to actually get to,
#                              checked at every viewport by hit-testing the anchor
#                              at each step of the scroll-through. Presence in the
#                              DOM is not reachability: a card clipped by an
#                              overflow-hidden parent with no scroll affordance
#                              passes `links` and fails this
#   min_text   int             floor on rendered text length, used by the no-JS
#                              check (default MIN_TEXT)
MIN_TEXT = 200
# The trailing-empty budget, in CSS pixels.
#
# Measured, not picked: across the eight routes at three viewports the real
# trailing gaps run 64px (a section ending on its pb-16 rule) to 187px, which is
# /404.html at 768, where a deliberately centred short page leaves its own slack
# under the last link. 260 clears that with room for a viewport the table does
# not cover, and still fails on anything approaching half a screen.
MAX_TRAILING_EMPTY = 260

EXPECTATIONS: dict[str, dict] = {
    "/": {
        # One hero h1; About, Selected work and Contact; one h3 per project.
        "headings": {"h1": 1, "h2": 3, "h3": 4},
        "ids": ["main", "marquee", "rail"],
        "figures": 0,
        "alt": True,
        "links": [
            "/about/",
            "/process/",
            "/projects/quote-generator/",
            "/projects/label-maker/",
            "/projects/billing-analyzer/",
            "/projects/rental-pipeline/",
        ],
        # The work rail is horizontal. Every case study has to be gettable at
        # 375 as well as 1440, which is where the preview lane was broken.
        "reachable": [
            "/projects/quote-generator/",
            "/projects/label-maker/",
            "/projects/billing-analyzer/",
            "/projects/rental-pipeline/",
        ],
        "text": [
            "Dustin Jones",
            "Available now for part-time and contract work",
            "Sixteen parsers into one schema",
        ],
    },
    # Served by the host on any unknown path, so it is a real page and gets a row.
    "/404.html": {
        "headings": {"h1": 1},
        "ids": ["main"],
        "figures": 0,
        "alt": True,
        "links": ["/", "/about/", "/process/"],
        "reachable": ["/"],
        "text": ["Page not found"],
    },

    # ── prose pages ───────────────────────────────────────────────────────
    "/process/": {
        # One display title, one h2 per section of the argument.
        "headings": {"h1": 1, "h2": 4, "h3": 0},
        "ids": ["main"],
        "figures": 0,
        "alt": True,
        "links": ["/", "/about/", "/projects/quote-generator/"],
        "reachable": ["/projects/quote-generator/"],
        "text": [
            "How I work",
            "Most of the lines in my recent projects were not typed by me",
            # The whole chain has to survive as rows a visitor can read, not as a
            # table that collapsed to nothing at 375.
            "A design interview",
            "The spec becomes tracer-bullet tickets",
            "The loop, unattended, against the remaining tickets",
            "A completion claim is not evidence",
            "Planning and doing should not share a session",
            "If an agent writes the code, what exactly do you do?",
        ],
    },
    "/about/": {
        "headings": {"h1": 1, "h2": 0, "h3": 0},
        "ids": ["main"],
        # The portrait is a bare image; the one figure is the pull quote, which is
        # a figure because it has an attribution to caption it with.
        "figures": 1,
        "alt": True,
        "links": ["/", "/process/"],
        "reachable": ["/process/"],
        "text": [
            # The gap is gestured at and never explained. This row asserts the
            # gesture is still on the page; nothing may explain it.
            "I started this degree years ago, stopped, and came back to it",
            "taught skiing professionally for Vail Resorts for five seasons",
            "Its six roles are a model of the organization",
            # The sourced claim and its attribution have to travel together, or
            # the page is back to an uncited line mid-paragraph.
            "Most programmers would have trouble explaining what they do",
            "Ward Cunningham",
            "The Pragmatic Programmer",
            "Available now",
        ],
    },

    # ── case studies ──────────────────────────────────────────────────────
    # Each row is the same shape: the project title as the one h1, one h2 per
    # section of the argument, the figure count, the before/after a skimmer is
    # supposed to leave with, and the pull quote. Metrics are asserted by their
    # label, so a value that stops being traceable to the prose cannot be
    # quietly swapped for a rounder one without this row noticing.
    "/projects/quote-generator/": {
        "headings": {"h1": 1, "h2": 6, "h3": 0},
        "ids": ["main"],
        "figures": 4,
        "alt": True,
        "links": ["/", "/projects/label-maker/"],
        "reachable": ["/projects/label-maker/"],
        "text": [
            "Quote Generator",
            "Sole developer",
            "A twenty-to-thirty-five-email thread, retyped into a workbook by hand",
            "A structured record the specialist reviews and decides on.",
            "emails replaced by one link",
            "roles modelling the org",
            "of manual assembly removed",
            "A better model does not fix a livelock",
        ],
    },
    "/projects/label-maker/": {
        "headings": {"h1": 1, "h2": 4, "h3": 0},
        "ids": ["main"],
        "figures": 3,
        "alt": True,
        "links": ["/", "/projects/billing-analyzer/"],
        "reachable": ["/projects/billing-analyzer/"],
        "text": [
            "Label Maker",
            "Copy rows, increment barcodes, repeat per patient",
            "Fill in a short form. Download the sheet.",
            "HTML file, no install",
            "network calls at runtime",
            "A file you can email is a tool people can start using the same afternoon.",
        ],
    },
    "/projects/billing-analyzer/": {
        "headings": {"h1": 1, "h2": 2, "h3": 0},
        "ids": ["main"],
        "figures": 4,
        "alt": True,
        "links": ["/", "/projects/label-maker/", "/projects/rental-pipeline/"],
        "reachable": ["/projects/rental-pipeline/"],
        "text": [
            "Billing Analyzer",
            "Open four files, add it up, hope",
            "Drop the files on the page. Read the whole account.",
            "tabs per year, reconciled",
            "dependencies at runtime",
            "Indexing by column position on a human-maintained file is a bug with a delay on it.",
        ],
    },
    # No outcome pair on the collection for this one, so no before/after block is
    # rendered. That is the row that proves the component is driven by the data
    # rather than always drawn.
    "/projects/rental-pipeline/": {
        "headings": {"h1": 1, "h2": 2, "h3": 0},
        "ids": ["main"],
        # The one figure is the pipeline diagram. This study has no UI to
        # screenshot, so a figure count of zero here is the "no visual at all"
        # state the diagram exists to fix, and this row is what keeps it fixed.
        "figures": 1,
        # This page's visual is drawn inline rather than loaded as a file, so
        # `alt` is carrying the diagram's accessible name here, not an <img>.
        "alt": True,
        "links": ["/", "/projects/quote-generator/"],
        "reachable": ["/projects/quote-generator/"],
        "text": [
            "Rental Pipeline",
            "parsers into one schema",
            "source systems",
            "no two agreeing on what a spreadsheet is",
            # The diagram's caption, which is also the sighted reader's version
            # of the description the SVG gives assistive technology.
            "Every input arrives in its own format and everything downstream reads one",
        ],
    },

}


# Drives the page through a full scroll so every ScrollTrigger fires, and probes
# reachability while it goes.
#
# Reachability has to be sampled DURING the scroll, not after it: on a wide
# screen the work rail is pinned and scrubbed, so a given card is only on screen
# for part of the scroll and a single check at the top or the bottom would miss
# it. Hit-testing rather than measuring a rect is what catches the real failure
# mode, which is a card clipped by an overflow-hidden ancestor: it has a
# perfectly good bounding box, it is just not on the screen and nothing can
# scroll it there.
SCROLL_THROUGH = r"""
async (hrefs) => {
  const reached = new Set();
  const targets = hrefs
    .map((h) => [h, [...document.querySelectorAll('a[href]')]
      .find((a) => a.getAttribute('href') === h)])
    .filter(([, el]) => el);

  const probe = () => {
    for (const [href, el] of targets) {
      if (reached.has(href)) continue;
      const r = el.getBoundingClientRect();
      // Clamp the probe point into the visible part of the rect, so a card that
      // is only half on screen still counts.
      const x = Math.round((Math.max(r.left, 0) + Math.min(r.right, innerWidth)) / 2);
      const y = Math.round((Math.max(r.top, 0) + Math.min(r.bottom, innerHeight)) / 2);
      if (x < 0 || y < 0 || x >= innerWidth || y >= innerHeight) continue;
      if (Math.min(r.right, innerWidth) - Math.max(r.left, 0) < 2) continue;
      if (Math.min(r.bottom, innerHeight) - Math.max(r.top, 0) < 2) continue;
      const hit = document.elementFromPoint(x, y);
      if (hit && (hit === el || el.contains(hit) || hit.closest('a') === el)) reached.add(href);
    }
  };

  probe();
  // A third of a viewport per step. A full 0.6 can translate a scrubbed rail by
  // more than a card's width between probes and skip straight past one.
  const step = window.innerHeight * 0.33;
  for (let y = 0; y < document.body.scrollHeight; y += step) {
    window.scrollTo(0, y);
    await new Promise((r) => setTimeout(r, 90));
    probe();
  }
  window.scrollTo(0, document.body.scrollHeight);
  await new Promise((r) => setTimeout(r, 500));
  probe();

  // Second chance for anything still unreached. A card can live in a container
  // that scrolls horizontally, which a vertical sweep never touches.
  //
  // Deliberately NOT scrollIntoView: that scrolls an `overflow: hidden` box too,
  // because hidden boxes are still programmatically scrollable. It would report
  // the exact bug this check exists for as reachable. Only containers a visitor
  // can actually drive are used, which means overflow-x auto or scroll.
  const userScrollableX = (el) => {
    const chain = [];
    for (let n = el.parentElement; n; n = n.parentElement) {
      const ox = getComputedStyle(n).overflowX;
      if ((ox === 'auto' || ox === 'scroll') && n.scrollWidth > n.clientWidth + 1) chain.push(n);
    }
    return chain.reverse();   // outermost first
  };
  for (const [href, el] of targets) {
    if (reached.has(href)) continue;
    for (const c of userScrollableX(el)) {
      const er = el.getBoundingClientRect(), cr = c.getBoundingClientRect();
      c.scrollLeft += (er.left + er.width / 2) - (cr.left + cr.width / 2);
    }
    const er = el.getBoundingClientRect();
    window.scrollBy(0, (er.top + er.height / 2) - window.innerHeight / 2);
    await new Promise((r) => setTimeout(r, 150));
    probe();
  }
  // `found` separately, so a typo in an expectation row reads as a typo and not
  // as a layout bug.
  return { reached: [...reached], found: targets.map(([h]) => h) };
}
"""


STRUCTURE_SWEEP = r"""
() => {
  const count = (s) => document.querySelectorAll(s).length;
  const decorative = (el) =>
    el.closest('[aria-hidden="true"]') !== null || el.getAttribute('role') === 'presentation';

  // What a screen reader would announce this element as. An inline SVG standing
  // in for a picture has no `alt` to read, so its name is aria-label, the text
  // of whatever aria-labelledby points at, or its own <title>.
  const accessibleName = (el) => {
    const label = (el.getAttribute('aria-label') || '').trim();
    if (label) return label;
    const referenced = (el.getAttribute('aria-labelledby') || '')
      .split(/\s+/).filter(Boolean)
      .map((id) => (document.getElementById(id)?.textContent || '').trim())
      .join(' ').trim();
    if (referenced) return referenced;
    return (el.querySelector(':scope > title')?.textContent || '').trim();
  };
  return {
    headings: Object.fromEntries(
      ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].map((h) => [h, count(h)])
    ),
    headingText: Object.fromEntries(
      ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].map((h) => [
        h,
        [...document.querySelectorAll(h)].map((e) => (e.textContent || '').trim().slice(0, 48)),
      ])
    ),
    ids: [...document.querySelectorAll('[id]')].map((e) => e.id),
    figures: count('figure'),
    // A picture is a picture whether it arrived as a file or was drawn inline, so
    // an `svg[role="img"]` is held to the same rule as an `<img>`: it has to say
    // what it shows. Without this half, a row's `alt: True` is vacuous on a page
    // whose only visual is an inline diagram.
    badAlt: [
      ...[...document.querySelectorAll('img')]
        .filter((i) => !decorative(i) && !(i.getAttribute('alt') || '').trim())
        .map((i) => (i.getAttribute('src') || '(no src)').split('/').pop()),
      ...[...document.querySelectorAll('svg[role="img"]')]
        .filter((s) => !decorative(s) && !accessibleName(s))
        .map((s) => 'svg.' + ((s.getAttribute('class') || '(no class)').split(' ')[0])),
    ],
    links: [...document.querySelectorAll('a[href]')].map((a) => a.getAttribute('href')),
    text: document.body.innerText,
    // The published strings that `text` above does NOT contain. Alt text, a
    // caption's `title`, the tab title and the meta description are prose a
    // visitor or a screen reader is handed, and are held to the same editorial
    // rules as a paragraph; checking `innerText` alone would let an em-dash
    // hide in any of them. Body text is not repeated here, because `text`
    // already carries it.
    published: [
      { where: '<title>', text: document.title },
      // Every social description and title too, not just the one meta the crawler
      // reads. They are prose a stranger meets in a link preview, and a page that
      // ever passes a distinct og: string would otherwise be scanned nowhere.
      ...[...document.querySelectorAll('meta[name][content], meta[property][content]')]
        .map((m) => ({
          key: (m.getAttribute('name') || m.getAttribute('property') || '').toLowerCase(),
          text: m.getAttribute('content') || '',
        }))
        .filter((m) => /description|title/.test(m.key))
        .map((m) => ({ where: 'meta ' + m.key, text: m.text })),
      ...[...document.querySelectorAll('img')].flatMap((i) => [
        { where: 'img alt', text: i.getAttribute('alt') || '' },
        { where: 'img title', text: i.getAttribute('title') || '' },
      ]),
      ...[...document.querySelectorAll('svg title, svg desc')]
        .map((e) => ({ where: 'svg ' + e.tagName.toLowerCase(), text: e.textContent || '' })),
      ...[...document.querySelectorAll('[aria-label]')]
        .map((e) => ({ where: 'aria-label', text: e.getAttribute('aria-label') || '' })),
    ].filter((p) => p.text.trim()),
  };
}
"""

# One Tab's worth of state. Everything the keyboard sweep needs to judge the
# element that now has focus, read in one round trip.
#
# `frac` is the share of the focused element's own box that is actually inside
# the viewport. A focus ring on a card sitting off the right edge of a pinned,
# scrubbed rail is a ring nobody can see, and it has a perfectly good bounding
# box, so measuring the rect alone would call it fine.
FOCUS_STEP = r"""
() => {
  const el = document.activeElement;
  if (!el || el === document.body || el === document.documentElement) return null;
  // Read the walk's state, then write it, rather than doing both inside the
  // object literal below, where the answers would depend on property order.
  const prev = window.__vPrev || null;
  const first = window.__vFirst || null;
  if (!window.__vFirst) window.__vFirst = el;
  window.__vPrev = el;
  const cs = getComputedStyle(el);
  const r = el.getBoundingClientRect();
  const w = Math.max(0, Math.min(r.right, innerWidth) - Math.max(r.left, 0));
  const h = Math.max(0, Math.min(r.bottom, innerHeight) - Math.max(r.top, 0));
  // Against the box clipped to the viewport, so an element taller or wider than
  // the screen is judged on how much of it COULD be shown, not on its own size.
  const area = Math.max(1, Math.min(r.width, innerWidth) * Math.min(r.height, innerHeight));
  const ringWidth = parseFloat(cs.outlineWidth) || 0;
  // `outline: 2px solid transparent` is a real pattern (it preserves a ring in
  // forced-colors mode) and it is not a focus ring anybody can see, so the
  // colour has to be read as well as the width.
  const ringAlpha = (() => {
    const c = cs.outlineColor;
    if (!c || c === 'transparent') return 0;
    const m = c.match(/-?[\d.]+/g);
    if (!m) return 1;
    if (/^rgba?\(/.test(c) && m.length > 3) return Number(m[3]);
    if (/^(oklab|oklch|color|hsla?|lab|lch)\(/.test(c) && /\//.test(c)) {
      return Number(c.split('/').pop().match(/-?[\d.]+/)?.[0] ?? 1);
    }
    return 1;
  })();
  return {
    tag: el.tagName.toLowerCase(),
    href: el.getAttribute('href'),
    label: (el.innerText || el.getAttribute('aria-label') || '').trim().replace(/\s+/g, ' ').slice(0, 40),
    ring: cs.outlineStyle !== 'none' && ringWidth >= 1 && ringAlpha > 0,
    ringDesc: cs.outlineStyle + ' ' + cs.outlineWidth + ' ' + cs.outlineColor,
    frac: Math.round((w * h / area) * 100) / 100,
    ariaHidden: !!el.closest('[aria-hidden="true"]'),
    // Document order, so "focus order follows reading order" is a measurement
    // rather than a reading of the source, and survives any redesign that moves
    // an element without moving its markup.
    afterPrevious: !prev || !!(prev.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING),
    // Tab that did not move focus: the definition of a trap.
    stuck: prev === el,
    // Back to where the sweep started, so the tab ring closed and the page has
    // no more focusable elements to visit.
    wrapped: !!first && first === el,
  };
}
"""

# How much unmarked ground a route ends on.
#
# Ticket 11's four faults were all found by a human reading these screenshots,
# and this is the one of them a machine can hold: a page whose last painted thing
# sits a screenful above its footer has almost always lost a section's padding
# argument rather than composed a rest. It is measured as a TRAILING gap on
# purpose. The mid-page void a pinned section leaves in a full-page screenshot is
# the pin spacer holding the scrub distance, which is real page and not empty to
# anyone who scrolls, so anything that looks for the biggest empty band anywhere
# on the page fails the home route at 1440 for doing exactly what it should.
#
# "Painted" means a text leaf, a replaced element, or a rule. A section's own
# bottom padding is legitimately part of the gap, which is why the threshold sits
# well above the largest one on the site rather than at zero.
TRAILING_EMPTY = r"""
() => {
  const main = document.querySelector('main');
  const footer = document.querySelector('footer');
  if (!main || !footer) return null;
  const sy = window.scrollY;
  let bottom = 0;
  let who = '';
  for (const el of main.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const paints =
      (el.children.length === 0 && (el.textContent || '').trim().length > 0) ||
      ['IMG', 'SVG', 'VIDEO', 'CANVAS', 'HR'].includes(el.tagName.toUpperCase()) ||
      parseFloat(cs.borderBottomWidth) > 0;
    if (!paints) continue;
    const r = el.getBoundingClientRect();
    if (!r.width && !r.height) continue;
    if (r.bottom + sy > bottom) {
      bottom = r.bottom + sy;
      who = el.tagName.toLowerCase() + ' "' + (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 32) + '"';
    }
  }
  return { gap: Math.round(footer.getBoundingClientRect().top + sy - bottom), last: who };
}
"""

# Decorative structure. Two things the accessibility tree gets wrong in opposite
# directions, both invisible to a screenshot and to a per-route row.
A11Y_SWEEP = r"""
() => {
  const norm = (t) => (t || '').replace(/\s+/g, ' ').trim();

  // 1. A strip of content duplicated to make a seamless loop is read out twice
  //    unless the copy is hidden. Siblings with identical text are the shape of
  //    that bug wherever it appears, so this looks for the shape rather than for
  //    a named marquee.
  const announcedTwice = [];
  document.querySelectorAll('*').forEach((parent) => {
    const kids = [...parent.children].filter(
      (k) => !k.closest('[aria-hidden="true"]') && norm(k.textContent).length >= 20,
    );
    const seen = new Map();
    for (const k of kids) {
      const t = norm(k.textContent);
      if (seen.has(t)) announcedTwice.push(t.slice(0, 48));
      else seen.set(t, k);
    }
  });

  // 2. The opposite mistake: aria-hidden thrown over a subtree that carries real
  //    structure, which deletes it from the page a screen reader is given while
  //    leaving it on the screen.
  const hiddenContent = [];
  document.querySelectorAll('[aria-hidden="true"]').forEach((el) => {
    el.querySelectorAll('h1, h2, h3, h4, h5, h6, main, nav, [role="heading"]').forEach((inner) => {
      hiddenContent.push(inner.tagName.toLowerCase() + ' "' + norm(inner.textContent).slice(0, 40) + '"');
    });
    if (el.matches('h1, h2, h3, h4, h5, h6, main, nav')) {
      hiddenContent.push(el.tagName.toLowerCase() + ' "' + norm(el.textContent).slice(0, 40) + '"');
    }
  });

  // 3. Landmarks. A page a screen reader can navigate has all three.
  // A <header> or <footer> is only banner or contentinfo when it is NOT inside
  // sectioning content; inside an <article> it is that article's header and
  // carries no landmark role at all. Counting the tags alone would call a page
  // with a per-card header compliant while a screen reader finds no banner.
  // One comma selector per landmark, never a sum: a <header role="banner"> is one
  // landmark and matches both halves. <main> is deliberately absent from the
  // ancestor list, because it is neither sectioning content nor a sectioning
  // root, so a footer that is a child of main still carries contentinfo.
  const topLevel = (sel) =>
    [...document.querySelectorAll(sel)].filter(
      (el) => !el.parentElement?.closest('article, aside, nav, section'),
    ).length;
  const landmarks = {
    banner: topLevel('header:not([hidden]), [role="banner"]'),
    main: document.querySelectorAll('main, [role="main"]').length,
    contentinfo: topLevel('footer:not([hidden]), [role="contentinfo"]'),
  };

  return {
    announcedTwice: [...new Set(announcedTwice)].slice(0, 6),
    hiddenContent: [...new Set(hiddenContent)].slice(0, 6),
    landmarks,
  };
}
"""

# Runs in a context with JavaScript disabled. Playwright's own evaluation still
# works there; the page's scripts do not, which is the point.
NOJS_SWEEP = r"""
() => {
  // opacity does not inherit as a computed value, so an opacity:0 wrapper leaves
  // its children reading 1. Multiply up the tree to get what is actually seen.
  const effective = (el) => {
    let o = 1;
    for (let n = el; n && n !== document.documentElement; n = n.parentElement) {
      o *= parseFloat(getComputedStyle(n).opacity);
    }
    return o;
  };
  const invisible = [];
  document.querySelectorAll('body *').forEach((el) => {
    const own = [...el.childNodes].filter((n) => n.nodeType === 3)
      .map((n) => n.textContent.trim()).join('');
    if (!own) return;
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) return;   // also catches display:none subtrees
    if (effective(el) >= 0.05) return;
    invisible.push(own.slice(0, 40));
  });
  return { text: document.body.innerText, invisible: invisible.slice(0, 6) };
}
"""


# The share of the focused element's box that is on screen, read on its own so
# the settle poll below can ask again without disturbing the sweep's own state.
FOCUS_FRAC = r"""
() => {
  const el = document.activeElement;
  if (!el || el === document.body) return 1;
  const r = el.getBoundingClientRect();
  const w = Math.max(0, Math.min(r.right, innerWidth) - Math.max(r.left, 0));
  const h = Math.max(0, Math.min(r.bottom, innerHeight) - Math.max(r.top, 0));
  const area = Math.max(1, Math.min(r.width, innerWidth) * Math.min(r.height, innerHeight));
  return Math.round((w * h / area) * 100) / 100;
}
"""

# How much of a focused element has to be on screen. Half its own box: a focus
# ring on a card that is 15% visible off the right edge of a pinned rail is a
# ring the person who moved focus there cannot see.
FOCUS_VISIBLE = 0.5
# A page with more focusable elements than this is either enormous or trapping.
MAX_TABS = 80

# What the walk below should visit. Anything natively focusable that is rendered
# and not disabled, plus anything opted in with a non-negative tabindex.
FOCUSABLE_COUNT = r"""
() => [...document.querySelectorAll(
    'a[href], button, input, select, textarea, summary, [tabindex]:not([tabindex^="-"])'
  )]
  .filter((el) => {
    if (el.hasAttribute('disabled') || el.closest('[inert]')) return false;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 || r.height > 0;
  }).length
"""


def keyboard_sweep(page, tag: str, shot: Path) -> list[str]:
    """Tab through one rendered page and report what a keyboard visitor meets.

    This is the half of the accessibility floor a screenshot and a per-route row
    cannot see: whether focus is visible, whether it is ON SCREEN, whether it
    walks the page in reading order, and whether it ever comes back out.
    """
    bad: list[str] = []
    worst = (2.0, "")
    # How many stops a complete walk should have. Focus returning to the first
    # element is what a finished tab ring looks like AND what the canonical
    # modal trap looks like; the only thing that separates them is whether the
    # rest of the page was visited on the way round.
    expected_stops = page.evaluate(FOCUSABLE_COUNT)
    # Moving focus runs handlers the scroll-through never touches, so this page
    # gets its own console watch rather than trusting the one on the page above.
    errs: list[str] = []
    page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    page.on("requestfailed", lambda r: errs.append(f"requestfailed {r.url}"))

    # The skip link is the first thing a keyboard visitor meets on every route,
    # and the only way past a header they have already read.
    page.keyboard.press("Tab")
    page.wait_for_timeout(120)
    skip = page.evaluate(
        "() => ({ href: document.activeElement.getAttribute('href'),"
        " tag: document.activeElement.tagName.toLowerCase() })"
    )
    if skip.get("tag") != "a" or (skip.get("href") or "")[:1] != "#":
        bad.append(f"[skip-link] {tag}: the first Tab landed on {skip}, not on a skip link")
    else:
        page.screenshot(path=str(shot.with_name(shot.stem + "-skip.png")))
        page.keyboard.press("Enter")
        page.wait_for_timeout(400)
        landed = page.evaluate("() => document.activeElement.id || document.activeElement.tagName")
        target = skip["href"].lstrip("#")
        if landed.lower() not in (target.lower(), "main"):
            bad.append(
                f"[skip-link] {tag}: activating it left focus on \"{landed}\", "
                f"not on \"{target}\""
            )

    # Restart the walk from the top of the document so the run below is the tab
    # order a visitor actually gets, not whatever is left after the skip link.
    #
    # blur() alone is NOT enough, and getting this wrong is silent: it clears
    # focus but leaves Chrome's sequential focus navigation starting point where
    # the skip link put it, on <main>. The walk then began at the first link
    # INSIDE main and the header, the skip link and every primary nav link went
    # unchecked on every route. Focusing the body moves the starting point back
    # to the top of the document; the temporary tabindex is what makes the body
    # focusable enough to accept it, and is removed again so it never appears as
    # a tab stop of its own.
    page.evaluate(
        "() => { window.__vPrev = null; window.__vFirst = null;"
        " document.activeElement?.blur?.();"
        " document.body.setAttribute('tabindex', '-1');"
        " document.body.focus();"
        " document.body.removeAttribute('tabindex');"
        " window.scrollTo(0, 0); }"
    )
    page.wait_for_timeout(200)

    for i in range(MAX_TABS + 1):
        page.keyboard.press("Tab")
        page.wait_for_timeout(90)
        # A scrubbed section eases into position, so a single read right after
        # the Tab reports a card mid-flight as off screen. Poll until it settles.
        frac = page.evaluate(FOCUS_FRAC)
        waited = 0
        while frac < FOCUS_VISIBLE and waited < 1400:
            page.wait_for_timeout(120)
            waited += 120
            frac = page.evaluate(FOCUS_FRAC)
        step = page.evaluate(FOCUS_STEP)
        if step is None:
            break                       # out of the document, into browser chrome
        if step["wrapped"]:
            # Back at the start. A complete ring, unless most of the page was
            # never reached, which is a trap that cycles rather than sticks.
            if i < expected_stops:
                bad.append(
                    f"[focus-trap] {tag}: focus returned to the first element after {i} "
                    f"stop(s), with {expected_stops} focusable element(s) on the page"
                )
            break
        if step["stuck"]:
            bad.append(
                f"[focus-trap] {tag}: Tab did not move focus off "
                f"{step['tag']} \"{step['label']}\""
            )
            break
        where = f"{step['tag']} {step['href'] or step['label']!r}"
        if not step["ring"]:
            bad.append(f"[focus] {tag}: no visible focus ring on {where} ({step['ringDesc']})")
        if frac < FOCUS_VISIBLE:
            bad.append(
                f"[focus] {tag}: focusing {where} left only {int(frac * 100)}% of it on screen"
            )
        if step["ariaHidden"]:
            bad.append(f"[focus] {tag}: {where} is focusable but hidden from assistive technology")
        if not step["afterPrevious"]:
            bad.append(f"[focus-order] {tag}: focus jumped backwards in the document to {where}")
        if frac < worst[0]:
            worst = (frac, where)
            page.screenshot(path=str(shot))
    else:
        bad.append(f"[focus-trap] {tag}: still tabbing after {MAX_TABS} stops; focus never wrapped")

    bad.extend(f"[console] {tag} (keyboard): {e}" for e in errs)
    return bad


def em_dashes(published: list[dict], limit: int = 8) -> list[str]:
    """Every em-dash in anything the page publishes, quoted with enough context to
    find it and labelled with where it was found.

    Dustin reads an em-dash as a machine having written the sentence, so one is a
    failure rather than a note. Alt text, captions, the tab title and the meta
    description count: they are published prose, and a reader meets them the same
    way they meet a paragraph."""
    out: list[str] = []
    for item in published:
        text = item.get("text") or ""
        for i, ch in enumerate(text):
            if ch == "\u2014":
                quote = " ".join(text[max(0, i - 30):i + 31].split())
                out.append(f"{item.get('where', '?')}: ...{quote}...")
                if len(out) == limit:
                    return out
    return out


def normalize(text: str) -> str:
    """Fold case and collapse whitespace, so a text-transform or a line break in
    the rendered output is not read as missing copy."""
    return " ".join(text.split()).casefold()


def check_structure(path: str, spec: dict, got: dict) -> list[str]:
    """Compare one route's declared expectations against what it rendered."""
    bad: list[str] = []

    def fail(what: str, expected, actual) -> None:
        bad.append(f"[expect] {path}: {what}: expected {expected}, found {actual}")

    for level, want in (spec.get("headings") or {}).items():
        have = got["headings"].get(level, 0)
        if have != want:
            fail(f"{level} count", want, f"{have} {got['headingText'].get(level, [])}")

    ids = set(got["ids"])
    for wanted in spec.get("ids") or []:
        if wanted not in ids:
            fail(f'element id "{wanted}"', "present", f"absent (ids: {sorted(ids)})")

    if "figures" in spec and got["figures"] != spec["figures"]:
        fail("<figure> count", spec["figures"], got["figures"])

    if spec.get("alt") and got["badAlt"]:
        fail("a name on every picture", "all", f"missing on {got['badAlt']}")

    hrefs = set(got["links"])
    for wanted in spec.get("links") or []:
        if wanted not in hrefs:
            fail(f'link to "{wanted}"', "present", "no such href on the page")

    rendered = normalize(got["text"])
    for wanted in spec.get("text") or []:
        if normalize(wanted) not in rendered:
            fail(f'copy "{wanted}"', "present in rendered text", "absent")

    return bad


def main(paths: list[str]) -> int:
    if not DIST.exists():
        print("dist/ not found. Run `npm run build` first.", file=sys.stderr)
        return 2
    OUT.mkdir(exist_ok=True)
    httpd = serve(DIST, PORT)
    base = f"http://127.0.0.1:{PORT}"
    failures: list[str] = []
    checked_links: set[str] = set()
    pending_hits: set[str] = set()
    resolved: dict[str, int] = {}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for path in paths:
                spec = EXPECTATIONS.get(path, {})
                for theme in THEMES:
                    for vp_name, (w, h) in VIEWPORTS.items():
                        ctx = browser.new_context(
                            viewport={"width": w, "height": h},
                            device_scale_factor=2,
                            color_scheme="light" if theme == "light" else "dark",
                        )
                        ctx.add_init_script(
                            f"try{{localStorage.setItem('theme','{theme}')}}catch(e){{}}"
                        )
                        page = ctx.new_page()
                        errs: list[str] = []
                        page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
                        page.on("requestfailed", lambda r: errs.append(f"requestfailed {r.url}"))

                        page.goto(base + path, wait_until="load")
                        page.wait_for_timeout(1400)  # let entrance animations settle
                        tag = f"{path.strip('/').replace('/', '_') or 'index'}-{theme}-{vp_name}"

                        # 1. horizontal scroll. Re-measured after the scroll-through
                        #    below, because a pinned section can introduce overflow
                        #    that does not exist at the top of the page.
                        seen: set[str] = set()

                        def measure() -> None:
                            sw, cw = page.evaluate(
                                "() => [document.documentElement.scrollWidth, "
                                "document.documentElement.clientWidth]"
                            )
                            if sw > cw + 1:
                                msg = f"[h-scroll] {tag}: scrollWidth {sw} > clientWidth {cw}"
                                if msg not in seen:
                                    seen.add(msg)
                                    failures.append(msg)

                        def contrast() -> None:
                            for bad in page.evaluate(CONTRAST_SWEEP):
                                msg = (
                                    f"[contrast] {tag}: {bad['ratio']}:1 (need {bad['need']}) "
                                    f"{bad['size']}px {bad['sel']} \"{bad['text']}\""
                                )
                                if msg not in seen:
                                    seen.add(msg)
                                    failures.append(msg)

                        measure()

                        # 2. console / network
                        for e in errs:
                            failures.append(f"[console] {tag}: {e}")

                        # 3. WCAG AA contrast across every rendered text leaf.
                        #    Run twice: the sweep skips anything under opacity 0.9
                        #    as mid-animation, so at this point every [data-reveal]
                        #    below the fold is still at 0 and would never be
                        #    checked at all. The second pass is after the scroll.
                        contrast()

                        # 4. link crawl, once per path
                        if theme == "dark" and vp_name == "1440":
                            hrefs = page.eval_on_selector_all(
                                "a[href]", "els => els.map(e => e.getAttribute('href'))"
                            )
                            for href in hrefs:
                                if not href or href.startswith(("#", "mailto:", "http")):
                                    continue
                                if href in checked_links:
                                    continue
                                checked_links.add(href)
                                resp = ctx.request.get(base + href)
                                if resp.status >= 400:
                                    if href in PENDING:
                                        pending_hits.add(href)
                                    else:
                                        failures.append(
                                            f"[link] {path} -> {href}: HTTP {resp.status}"
                                        )

                        # Drive the page through a full scroll so every ScrollTrigger
                        # fires. Without this a full-page screenshot captures the
                        # reveals still at opacity 0, and any reveal that never
                        # fires at all would go unnoticed.
                        page.screenshot(path=str(OUT / f"{tag}-hero.png"))
                        walk = page.evaluate(SCROLL_THROUGH, spec.get("reachable") or [])
                        page.wait_for_timeout(700)

                        for href in spec.get("reachable") or []:
                            if href not in walk["found"]:
                                failures.append(
                                    f"[reach] {tag}: no link to \"{href}\" on the page at all"
                                )
                            elif href not in walk["reached"]:
                                failures.append(
                                    f"[reach] {tag}: link to \"{href}\" is on the page but was "
                                    f"never hit-testable during a full scroll-through"
                                )

                        stuck = page.evaluate(
                            """() => [...document.querySelectorAll('[data-reveal],[data-line]')]
                                .filter(e => parseFloat(getComputedStyle(e).opacity) < 0.5)
                                .map(e => (e.textContent || '').trim().slice(0, 40))"""
                        )
                        for t in stuck:
                            failures.append(f"[reveal] {tag}: never became visible: \"{t}\"")

                        # A hero display line is authored as ONE line. If it wraps,
                        # either the type is too big or SplitText has fragmented it
                        # into per-character inline-blocks that break mid-word.
                        for w in page.evaluate(
                            """() => [...document.querySelectorAll('[data-line]')].map((el) => {
                                const lh = parseFloat(getComputedStyle(el).lineHeight);
                                const n = lh ? Math.round(el.clientHeight / lh) : 1;
                                return n > 1 ? { text: (el.textContent||'').trim().slice(0,32), n } : null;
                            }).filter(Boolean)"""
                        ):
                            failures.append(
                                f"[wrap] {tag}: display line wrapped to {w['n']} lines: \"{w['text']}\""
                            )

                        # Everything is now in its end state, so sweep the parts of
                        # the page that were still animating the first time round.
                        contrast()
                        measure()

                        # Back to the top, and rewind any horizontal scroller the
                        # reachability probe drove, so the screenshot a human looks
                        # at shows the page as a visitor first meets it.
                        page.evaluate(
                            """() => {
                                window.scrollTo(0, 0);
                                document.querySelectorAll('*').forEach((el) => {
                                    if (el.scrollLeft) el.scrollLeft = 0;
                                });
                            }"""
                        )
                        page.wait_for_timeout(250)

                        # How much unmarked ground the route ends on. See
                        # TRAILING_EMPTY: a trailing gap, not the biggest gap.
                        trailing = page.evaluate(TRAILING_EMPTY)
                        if trailing and trailing["gap"] > MAX_TRAILING_EMPTY:
                            failures.append(
                                f"[trailing] {tag}: {trailing['gap']}px of empty page between "
                                f"the last painted thing ({trailing['last']}) and the footer, "
                                f"over a {MAX_TRAILING_EMPTY}px budget"
                            )

                        page.screenshot(path=str(OUT / f"{tag}.png"), full_page=True)

                        # 8. Keyboard. A fresh page in the same context: the sweep
                        #    has to start from a page as a visitor first meets it,
                        #    and the one above has been scrolled end to end.
                        kb = ctx.new_page()
                        kb.goto(base + path, wait_until="load")
                        kb.wait_for_timeout(1400)
                        failures.extend(
                            keyboard_sweep(kb, tag, OUT / f"{tag}-focus.png")
                        )
                        kb.close()
                        ctx.close()

                # 5. reduced motion: content must still be visible
                ctx = browser.new_context(
                    viewport={"width": 1440, "height": 900}, reduced_motion="reduce"
                )
                page = ctx.new_page()
                page.goto(base + path, wait_until="load")
                page.wait_for_timeout(800)
                hidden = page.evaluate(
                    """() => [...document.querySelectorAll('[data-reveal],[data-line]')]
                        .filter(e => parseFloat(getComputedStyle(e).opacity) < 0.5).length"""
                )
                if hidden:
                    failures.append(f"[reduced-motion] {path}: {hidden} element(s) stuck invisible")
                # Reduced motion is its own lane, not a subset of the animated
                # one: the scroll choreography is off, so a section that scrolls
                # or pins behaves differently and the keyboard has to be swept
                # again rather than assumed from the run above.
                rm_base = f"{path.strip('/').replace('/','_') or 'index'}-reducedmotion"
                for vp_name, (w, h) in VIEWPORTS.items():
                    rm_tag = f"{rm_base}-{vp_name}"
                    kb = ctx.new_page()
                    kb.set_viewport_size({"width": w, "height": h})
                    kb.goto(base + path, wait_until="load")
                    kb.wait_for_timeout(900)
                    failures.extend(keyboard_sweep(kb, rm_tag, OUT / f"{rm_tag}-focus.png"))
                    kb.close()
                page.screenshot(path=str(OUT / f"{path.strip('/').replace('/','_') or 'index'}-reducedmotion.png"), full_page=True)
                ctx.close()

                # 6. per-route expectations, plus the em-dash check. Both read
                #    the settled page once at the widest viewport; structure and
                #    copy do not vary by width. If a page ever grows a responsive
                #    display toggle, the copy only shown at a narrow width is
                #    scanned by neither, and this has to sweep every viewport.
                ctx = browser.new_context(viewport={"width": 1440, "height": 900})
                page = ctx.new_page()
                page.goto(base + path, wait_until="load")
                page.wait_for_timeout(1400)
                got = page.evaluate(STRUCTURE_SWEEP)
                failures.extend(check_structure(path, spec, got))

                # What the page hands assistive technology, in both directions:
                # nothing read out twice, nothing hidden that carries structure,
                # and the three landmarks a screen reader navigates by.
                a11y = page.evaluate(A11Y_SWEEP)
                for t in a11y["announcedTwice"]:
                    failures.append(
                        f"[a11y] {path}: duplicated sibling content is announced twice; "
                        f"the decorative copy needs aria-hidden: \"{t}\""
                    )
                for t in a11y["hiddenContent"]:
                    failures.append(
                        f"[a11y] {path}: aria-hidden is hiding real structure from "
                        f"assistive technology: {t}"
                    )
                for name, n in a11y["landmarks"].items():
                    if n != 1:
                        failures.append(
                            f"[a11y] {path}: expected exactly one {name} landmark, found {n}"
                        )
                for href in spec.get("links") or []:
                    if href not in resolved:
                        resolved[href] = ctx.request.get(base + href).status
                    if resolved[href] >= 400:
                        if href in PENDING:
                            pending_hits.add(href)
                        else:
                            failures.append(
                                f"[expect] {path}: link to \"{href}\": expected to resolve, "
                                f"found HTTP {resolved[href]}"
                            )
                # Metadata first, body text last. The quote list is capped, and a
                # page with a cap's worth of em-dashes in its prose would
                # otherwise report none of its alt text or meta descriptions,
                # sending a fixer round the loop twice to find them.
                published = [*got["published"], {"where": "body text", "text": got["text"]}]
                for quote in em_dashes(published):
                    failures.append(f"[em-dash] {path}: {quote}")
                ctx.close()

                # 7. no JavaScript. A failed script must never produce a blank page.
                ctx = browser.new_context(
                    viewport={"width": 1440, "height": 900}, java_script_enabled=False
                )
                page = ctx.new_page()
                page.goto(base + path, wait_until="load")
                nojs = page.evaluate(NOJS_SWEEP)
                floor = spec.get("min_text", MIN_TEXT)
                if len(nojs["text"].strip()) < floor:
                    failures.append(
                        f"[no-js] {path}: rendered {len(nojs['text'].strip())} chars of text, "
                        f"expected at least {floor}"
                    )
                for t in nojs["invisible"]:
                    failures.append(f"[no-js] {path}: text stuck invisible without JS: \"{t}\"")
                ctx.close()
            browser.close()
    finally:
        httpd.shutdown()

    print(f"\nscreenshots -> {OUT}")
    if pending_hits:
        print("\nnot yet migrated (expected during the Jekyll overlap):")
        for h in sorted(pending_hits):
            print("  " + h)
    if failures:
        print(f"\nFAIL ({len(failures)}):")
        for f in failures:
            print("  " + f)
        return 1
    print(f"\nPASS: {len(paths)} page(s) x {len(VIEWPORTS)} viewports x {len(THEMES)} themes")
    return 0


if __name__ == "__main__":
    # The route list is the expectations table. Explicit paths still work, for a
    # fast single-route loop; a path with no row gets the universal checks only.
    args = sys.argv[1:] or list(EXPECTATIONS)
    for a in args:
        if a not in EXPECTATIONS:
            print(f"note: {a} has no row in EXPECTATIONS; universal checks only.")
    raise SystemExit(main(args))
