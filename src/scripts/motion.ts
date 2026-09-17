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
 * Jump the page to an exact scroll position.
 *
 * Setting `window.scrollTo` behind Lenis's back leaves Lenis's own idea of the
 * scroll position stale, and the next wheel event snaps the page back to where
 * it thought it was. Anything that moves the page programmatically has to go
 * through here.
 */
export function scrollWindowTo(y: number) {
  if (lenis) lenis.scrollTo(y, { immediate: true, force: true });
  else window.scrollTo(0, y);
}

/**
 * A horizontal rail of cards: native horizontal scroll everywhere, and from
 * `lg` up a pinned, scrub-driven translation of the track by its overflow.
 * Shared by the home work rail and a case study's chapter rail.
 *
 * Registered partly OUTSIDE `withMotion`, because the keyboard handling below
 * is needed in the native lane too, and that lane exists under reduced motion.
 *
 * Keyboard: Chrome scrolls a horizontal scroller only part of the way towards a
 * newly focused card, and in the pinned lane the rail's position is a function
 * of PAGE scroll, so scrolling the card into view does nothing at all. So the
 * card is put on screen here, through whichever axis is live.
 */
export function horizontalRail(
  rail: HTMLElement,
  scroller: HTMLElement,
  track: HTMLElement,
  control?: HTMLElement | null,
) {
  // Never negative: on a very wide screen the track is narrower than the
  // viewport, and a negative distance hands ScrollTrigger an end before its start.
  const distance = () => Math.max(0, track.scrollWidth - scroller.clientWidth);
  // Set while the pinned lane owns the horizontal axis; null in the native one.
  let scrubStart: (() => number) | null = null;

  // How far along the rail is, in track pixels, through whichever axis is live.
  // In the pinned lane the rail's position IS page scroll, measured from where
  // the pin begins; in the native lane it is just the scroller's own offset.
  const offsetNow = () =>
    scrubStart
      ? Math.min(Math.max(window.scrollY - scrubStart(), 0), distance())
      : scroller.scrollLeft;

  const onFocusIn = (e: FocusEvent) => {
    const card = (e.target as HTMLElement | null)?.closest<HTMLElement>('a');
    // Keyboard only. `focusin` also fires on a click, and moving the rail out
    // from under a pointer mid-click is the opposite of helpful.
    if (!card || !track.contains(card) || !card.matches(':focus-visible')) return;
    // Measured against the track rather than read off offsetLeft, so the
    // scrub's own transform cancels out: both rects move together.
    const offset = card.getBoundingClientRect().left - track.getBoundingClientRect().left;
    const centred = offset - (scroller.clientWidth - card.offsetWidth) / 2;
    if (scrubStart) scrollWindowTo(scrubStart() + Math.min(Math.max(centred, 0), distance()));
    else scroller.scrollLeft = centred; // the scroller clamps it for us
  };
  scroller.addEventListener('focusin', onFocusIn);
  onTeardown(() => scroller.removeEventListener('focusin', onFocusIn));

  // The "Scroll" affordance in the rail header. It ships `hidden` and is only
  // revealed here, so it never offers a click that JavaScript did not arrive to
  // handle; without JS the rail is still natively scrollable. Registered outside
  // withMotion for the same reason the keyboard handling is: the native lane
  // exists under reduced motion, and the control has to work there too.
  if (control) {
    // One card plus the gap, so a click lands the next card where the last sat.
    const step = () => {
      const card = track.firstElementChild as HTMLElement | null;
      const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
      return card ? card.offsetWidth + gap : Math.round(scroller.clientWidth * 0.8);
    };

    const sync = () => {
      // Nothing to scroll past on a screen wide enough to hold the whole track.
      const scrollable = distance() > 0;
      control.hidden = !scrollable;
      // Within a pixel or two of the end, so float rounding still reads as done.
      const atEnd = scrollable && offsetNow() >= distance() - 2;
      control.toggleAttribute('disabled', atEnd);
      control.setAttribute('aria-disabled', String(atEnd));
    };

    const onClick = () => {
      const target = Math.min(offsetNow() + step(), distance());
      // In the pinned lane the horizontal axis is page scroll, and a raw window
      // scroll would be snapped back by Lenis on the next wheel event.
      if (scrubStart) scrollWindowTo(scrubStart() + target);
      else
        scroller.scrollTo({
          left: target,
          behavior: prefersReducedMotion() ? 'auto' : 'smooth',
        });
    };

    control.addEventListener('click', onClick);
    scroller.addEventListener('scroll', sync);
    window.addEventListener('scroll', sync, { passive: true });
    window.addEventListener('resize', sync);
    sync();
    onTeardown(() => {
      control.removeEventListener('click', onClick);
      scroller.removeEventListener('scroll', sync);
      window.removeEventListener('scroll', sync);
      window.removeEventListener('resize', sync);
      control.hidden = true;
    });
  }

  withMotion(() => {
    // matchMedia rather than a one-shot innerWidth read, so resizing across the
    // breakpoint sets the rail up or tears it down instead of stranding it.
    const mm = gsap.matchMedia();
    onTeardown(() => mm.revert());

    mm.add('(min-width: 1024px)', () => {
      if (distance() === 0) return;

      // The native scrollbar would fight the transform. gsap.set inside the
      // matchMedia scope, so reverting restores the scrollable fallback.
      gsap.set(scroller, { overflowX: 'hidden' });

      // Hidden overflow is still scrollable by script and by focus. Any
      // leftover scrollLeft stacks on the scrub transform and offsets the rail
      // for good, so hold it at zero while the scrub owns the axis.
      scroller.scrollLeft = 0;
      const hold = () => {
        if (scroller.scrollLeft !== 0) scroller.scrollLeft = 0;
      };
      scroller.addEventListener('scroll', hold);

      const scrub = gsap.to(track, {
        x: () => -distance(),
        ease: 'none',
        scrollTrigger: {
          trigger: rail,
          start: 'top top',
          // Clamped to a positive length: `+=0` is a degenerate pin.
          end: () => `+=${Math.max(1, distance())}`,
          pin: true,
          scrub: 0.6,
          invalidateOnRefresh: true,
          anticipatePin: 1,
        },
      });
      const st = scrub.scrollTrigger;
      if (st) scrubStart = () => st.start;

      return () => {
        scrubStart = null;
        scroller.removeEventListener('scroll', hold);
      };
    });
  });
}

/**
 * Scroll to an in-page anchor through the smooth scroller.
 *
 * A native `#fragment` jump moves the window behind Lenis's back and the next
 * wheel event snaps it home again, so anchor links inside `root` are routed
 * through `scrollWindowTo`. Under reduced motion there is no Lenis and the
 * fallback is a plain jump, which is what the browser would have done.
 */
export function routeAnchors(root: HTMLElement, offset = 24) {
  const onClick = (e: MouseEvent) => {
    const a = (e.target as HTMLElement | null)?.closest<HTMLAnchorElement>('a[href^="#"]');
    if (!a) return;
    const target = document.getElementById(decodeURIComponent(a.hash.slice(1)));
    if (!target) return;
    e.preventDefault();
    history.replaceState(null, '', a.hash);
    scrollWindowTo(target.getBoundingClientRect().top + window.scrollY - offset);
    target.setAttribute('tabindex', '-1');
    target.focus({ preventScroll: true });
  };
  root.addEventListener('click', onClick);
  onTeardown(() => root.removeEventListener('click', onClick));
}

/**
 * A chapter list beside an argument. Anchors go through the smooth scroller,
 * and the browser's IntersectionObserver marks the chapter being read.
 * Registered outside `withMotion`: the list exists under reduced motion too.
 *
 * The current chapter is the last heading above a line 40% down the viewport.
 * The observer fires whenever a heading crosses that line (`rootMargin` trims
 * the root to it); the decision is then made from every heading's position, so
 * a fast scroll that skips a callback cannot leave a stale one marked.
 */
export function chapterNav(nav: HTMLElement) {
  routeAnchors(nav);
  const links = [...nav.querySelectorAll<HTMLAnchorElement>('a[href^="#"]')];
  const headings = links
    .map((a) => document.getElementById(a.hash.slice(1)))
    .filter((h): h is HTMLElement => h !== null);
  const LINE = 0.4;
  const mark = () => {
    const current = headings.filter((h) => h.getBoundingClientRect().top <= innerHeight * LINE).at(-1);
    links.forEach((a) => {
      if (a.hash.slice(1) === current?.id) a.setAttribute('aria-current', 'true');
      else a.removeAttribute('aria-current');
    });
  };
  const spy = new IntersectionObserver(mark, { rootMargin: `0px 0px -${100 - LINE * 100}% 0px` });
  headings.forEach((h) => spy.observe(h));
  onTeardown(() => spy.disconnect());
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

  // The beat is per VISUAL LINE, not per `[data-line]`, and the two stopped being
  // the same thing when the home hero grew rows: at lg "and the" and "pipelines"
  // are two `[data-line]`s sitting side by side on one line, and delaying by
  // index rose one half of that line 90ms after the other. Grouping by the top
  // edge of the rendered box is what a reader sees as a line, whichever width
  // they are at, and it leaves every one-line-per-element title exactly as it was.
  const splits = lines.map((l) => new SplitText(l, { type: 'words,chars' }));
  const tops = lines.map((l) => Math.round(l.getBoundingClientRect().top));
  const rows = [...new Set(tops)].sort((a, b) => a - b);
  gsap.set(lines, { opacity: 1 });
  splits.forEach((s, i) => {
    gsap.from(s.chars, {
      yPercent: 115,
      opacity: 0,
      duration: 1.1,
      ease: 'expo.out',
      stagger,
      delay: 0.1 + rows.indexOf(tops[i]) * 0.09,
    });
  });

  // Every heading that owns one of those lines, not `h1` by tag: a page may have
  // display lines outside the h1, and tweening the tag would settle headings
  // with no lines in them while leaving a second display block rising without
  // its settle. Deduped, because the lines of one heading share it.
  const headings = new Set<Element>();
  for (const line of lines) {
    const owner = line.closest('h1, h2, h3') ?? line.parentElement;
    if (owner) headings.add(owner);
  }
  if (headings.size) {
    gsap.fromTo(
      [...headings],
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
