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
  6. Em-dashes in rendered text. ADVISORY: printed, does not fail. Ticket 08
     removes the existing ones and flips this to a failure.
  7. Reachability: a link a route declares as reachable must be hit-testable at
     some point during the scroll-through, at every viewport. A link can be in
     the DOM, resolve, and still be clipped out of reach; that is a real bug the
     link crawl cannot see.
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
PORT = 4321

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
    const size = parseFloat(cs.fontSize);
    const bold = parseInt(cs.fontWeight, 10) >= 700;
    const need = size >= 24 || (bold && size >= 18.66) ? 3.0 : 4.5;
    if (ratio < need) {
      out.push({
        ratio: Math.round(ratio * 100) / 100, need, size: Math.round(size),
        text: own.slice(0, 32),
        sel: el.tagName.toLowerCase() + '.' + (el.className || '').toString().split(' ')[0],
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
#   alt        True            every <img> carries non-empty alt text, unless it
#                              is explicitly decorative (aria-hidden or
#                              role="presentation")
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
        "figures": 0,
        "alt": True,
        "links": ["/", "/projects/quote-generator/"],
        "reachable": ["/projects/quote-generator/"],
        "text": [
            "Rental Pipeline",
            "parsers into one schema",
            "source systems",
            "no two agreeing on what a spreadsheet is",
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
    badAlt: [...document.querySelectorAll('img')]
      .filter((i) => !decorative(i) && !(i.getAttribute('alt') || '').trim())
      .map((i) => (i.getAttribute('src') || '(no src)').split('/').pop()),
    links: [...document.querySelectorAll('a[href]')].map((a) => a.getAttribute('href')),
    text: document.body.innerText,
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


def em_dashes(text: str, limit: int = 5) -> list[str]:
    """Every em-dash in rendered text, quoted with enough context to find it."""
    out: list[str] = []
    for i, ch in enumerate(text):
        if ch == "\u2014":
            out.append(" ".join(text[max(0, i - 30):i + 31].split()))
            if len(out) == limit:
                break
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
        fail("non-empty alt on every image", "all", f"missing on {got['badAlt']}")

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
    advisories: list[str] = []
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
                        page.screenshot(path=str(OUT / f"{tag}.png"), full_page=True)
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
                page.screenshot(path=str(OUT / f"{path.strip('/').replace('/','_') or 'index'}-reducedmotion.png"), full_page=True)
                ctx.close()

                # 6. per-route expectations, plus the em-dash advisory. Both read
                #    the settled page once at the widest viewport; structure and
                #    copy do not vary by width.
                ctx = browser.new_context(viewport={"width": 1440, "height": 900})
                page = ctx.new_page()
                page.goto(base + path, wait_until="load")
                page.wait_for_timeout(1400)
                got = page.evaluate(STRUCTURE_SWEEP)
                failures.extend(check_structure(path, spec, got))
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
                for quote in em_dashes(got["text"]):
                    advisories.append(f"[em-dash] {path}: ...{quote}...")
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
    if advisories:
        print(f"\nadvisory, not failing ({len(advisories)}):")
        for a in advisories:
            print("  " + a)
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
