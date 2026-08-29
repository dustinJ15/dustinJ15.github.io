/**
 * Shared motion runtime for the site.
 *
 * Contract, in order of importance:
 *   1. Reduced motion wins. Nothing is hidden, nothing is scroll-jacked.
 *   2. Content is never hidden before we KNOW we can animate it back. The
 *      `data-motion="on"` flag is what arms the CSS that hides `[data-reveal]`,
 *      and it is set from JS, so no-JS and reduced-motion visitors see the page.
 *   3. Everything is torn down on `astro:before-swap` so view transitions do not
 *      leak ScrollTriggers or a second Lenis instance.
 */
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { SplitText } from 'gsap/SplitText';
import Lenis from 'lenis';

gsap.registerPlugin(ScrollTrigger, SplitText);

export const prefersReducedMotion = () =>
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

let lenis: Lenis | null = null;
/** One per `withMotion` call. The layout and the page each register their own. */
const contexts: gsap.Context[] = [];

/**
 * Anything a page sets up that GSAP does not own: DOM listeners, matchMedia
 * queries, observers. Registered here so `teardown` is the single place that
 * undoes a page, rather than each page hoping it remembered.
 */
const cleanups: Array<() => void> = [];

export function onTeardown(fn: () => void) {
  cleanups.push(fn);
}

/** Module scope, not a local, so teardown can actually remove it again. */
const tick = (time: number) => lenis?.raf(time * 1000);

/** Smooth scroll, driven by GSAP's ticker so ScrollTrigger stays in sync. */
export function startSmoothScroll() {
  if (prefersReducedMotion() || lenis) return null;
  lenis = new Lenis({ duration: 1.05, smoothWheel: true });
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add(tick);
  gsap.ticker.lagSmoothing(0);
  return lenis;
}

/**
 * Arms the reveal CSS and runs `build` inside a GSAP context.
 * If motion is off, `build` never runs and the page renders in its end state.
 */
export function withMotion(build: (self: gsap.Context) => void) {
  if (prefersReducedMotion()) return;
  document.documentElement.dataset.motion = 'on';
  contexts.push(gsap.context(build));
}

/**
 * The display-title entrance, shared by the home hero, the case studies and the
 * prose pages: every `[data-line]` rises character by character out of the mask
 * it sits in, and the heading settles from condensed to full width along
 * Bricolage's wdth axis. Swapping the face for a static one removes that settle.
 *
 * Arriving anywhere on the site should feel like the same site, so this lives in
 * one place rather than being retyped per page.
 */
export function revealDisplayTitle(stagger = 0.02) {
  const lines = gsap.utils.toArray<HTMLElement>('[data-line]');
  if (!lines.length) return;

  const splits = lines.map((l) => new SplitText(l, { type: 'words,chars' }));
  gsap.set(lines, { opacity: 1 });
  splits.forEach((s, i) => {
    gsap.from(s.chars, {
      yPercent: 115,
      opacity: 0,
      duration: 1.1,
      ease: 'expo.out',
      stagger,
      delay: 0.1 + i * 0.09,
    });
  });

  // The heading itself, not `h1` by tag: a page may have display lines that are
  // not in the h1, and tweening every h1 on the page would catch them all.
  const heading = lines[0].closest('h1, h2') ?? lines[0].parentElement;
  if (heading) {
    gsap.fromTo(
      heading,
      { fontStretch: '75%' },
      { fontStretch: '100%', duration: 1.6, ease: 'expo.out' },
    );
  }
}

/** Standard entrance: fade + rise, staggered, triggered on scroll. */
export function revealOnScroll(selector: string, opts: gsap.TweenVars = {}) {
  gsap.utils.toArray<HTMLElement>(selector).forEach((el) => {
    gsap.fromTo(
      el,
      { opacity: 0, y: 28 },
      {
        opacity: 1,
        y: 0,
        duration: 0.9,
        ease: 'expo.out',
        scrollTrigger: { trigger: el, start: 'top 88%', once: true },
        ...opts,
      },
    );
  });
}

export function teardown() {
  // Page-registered cleanups run first: they may hold references to nodes GSAP
  // is about to revert. Each one is isolated, and the rest of teardown sits in
  // a finally, because one throwing cleanup skipping the ticker and Lenis
  // teardown below reinstates the per-frame leak fixed in fa6f9c0, one more
  // instance per navigation.
  try {
    while (cleanups.length) {
      try {
        cleanups.pop()!();
      } catch (e) {
        console.warn('teardown: a page cleanup threw', e);
      }
    }
  } finally {
    tearDownMotionRuntime();
  }
}

function tearDownMotionRuntime() {
  while (contexts.length) contexts.pop()!.revert();
  ScrollTrigger.getAll().forEach((t) => t.kill());
  // Both of these are global state on the ticker, not on the Lenis instance.
  // Destroying Lenis without removing them leaves a callback running on every
  // frame forever, one more per navigation once view transitions are on.
  gsap.ticker.remove(tick);
  gsap.ticker.lagSmoothing(500, 33);
  lenis?.destroy();
  lenis = null;
  delete document.documentElement.dataset.motion;
}

document.addEventListener('astro:before-swap', teardown);
