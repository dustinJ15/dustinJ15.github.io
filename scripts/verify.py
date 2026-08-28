#!/usr/bin/env python3
"""
Verification gate for the site. Serves the built `dist/` and drives it with
Playwright. This is the objective floor a ticket must clear; it does not judge
whether the design is good.

Checks, per page x viewport x theme:
  1. No horizontal scroll  (scrollWidth <= clientWidth). Measured, never eyeballed.
  2. No console errors, no failed requests.
  3. Body copy contrast >= 4.5:1.
  4. Renders with prefers-reduced-motion forced: content present, not blank.
Plus a link crawl from the entry pages.

Screenshots land in .verify/ (gitignored) for a human to look at.

Run:  npm run verify            (all preview lanes)
      npm run verify -- /about/ (specific paths)
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
    const alphaOf = (n, i) => (n.length > i ? (v.includes('/') ? n[i] : n[i]) : 1);
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
      const n = nums(v);
      return [g2(n[0] <= 0.0031308 ? n[0] : n[0]), 0, 0, 1].length && [
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
# Emptied as tickets land; a 404 here is a "not built yet", not a broken link.
PENDING = {"/process/", "/about/", "/projects/quote-generator/", "/projects/label-maker/",
           "/projects/billing-analyzer/", "/projects/rental-pipeline/"}


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

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for path in paths:
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

                        # 1. horizontal scroll
                        sw, cw = page.evaluate(
                            "() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]"
                        )
                        if sw > cw + 1:
                            failures.append(f"[h-scroll] {tag}: scrollWidth {sw} > clientWidth {cw}")

                        # 2. console / network
                        for e in errs:
                            failures.append(f"[console] {tag}: {e}")

                        # 3. WCAG AA contrast across every rendered text leaf
                        for bad in page.evaluate(CONTRAST_SWEEP):
                            failures.append(
                                f"[contrast] {tag}: {bad['ratio']}:1 (need {bad['need']}) "
                                f"{bad['size']}px {bad['sel']} \"{bad['text']}\""
                            )

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
                        page.evaluate("""async () => {
                            const step = window.innerHeight * 0.6;
                            for (let y = 0; y < document.body.scrollHeight; y += step) {
                                window.scrollTo(0, y);
                                await new Promise((r) => setTimeout(r, 90));
                            }
                            window.scrollTo(0, document.body.scrollHeight);
                            await new Promise((r) => setTimeout(r, 500));
                        }""")
                        page.wait_for_timeout(700)

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

                        page.evaluate("() => window.scrollTo(0, 0)")
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
    args = sys.argv[1:] or ["/preview/1/", "/preview/2/", "/preview/3/"]
    raise SystemExit(main(args))
