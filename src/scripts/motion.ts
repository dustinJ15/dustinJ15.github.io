/**
 * Shared motion runtime for the preview lanes.
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
import Lenis from 'lenis';

gsap.registerPlugin(ScrollTrigger);

export const prefersReducedMotion = () =>
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

let lenis: Lenis | null = null;
let ctx: gsap.Context | null = null;

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
  ctx = gsap.context(build);
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
  ctx?.revert();
  ctx = null;
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
