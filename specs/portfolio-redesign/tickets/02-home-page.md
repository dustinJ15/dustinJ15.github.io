# 02: Home page at `/`, on real site chrome

**What to build:** A visitor typing the site's address lands on the finished home page rather
than a preview route. The page opens with a full-viewport display hero whose lines assemble on
load and settle from condensed to full width, states in one line what Dustin does, and says he
is available with a way to act on it. Below it: a marquee of the stack, an asymmetric about
block, a horizontal work rail of the four projects scrubbed by vertical scroll on wide screens
and scrolling normally on narrow ones, and an oversized contact block. Every case study is one
click away and no biography is in the path to them.

The preview layout becomes the real base layout every page will use: per-page title and
description, canonical and social metadata, a skip link that lands on the main content, and a
footer. The `noindex` that was correct for a preview comes off. A 404 route renders in the same
chrome.

The work rail's entries take their year, stack and tagline from the content collection, so the
home page and the case study cannot disagree about a project.

Delete the preview route and its layout when the real one supersedes them. The Jekyll home page
stays where it is and keeps building; this ticket does not touch it.

Copy in this ticket is the ported Jekyll copy. The editorial pass is ticket 08 and this ticket
does not pre-empt it, beyond removing an em-dash if the port introduces one.

**Carried over from the ticket 01 review.** These are live bugs in the preview lane that this
ticket replaces, found by `/code-review` on 2026-08-28. They are recorded here because the code
that carries them is the code this ticket rewrites, so fixing them separately would be wasted
work. The rail bug is the serious one.

- **Three of the four case studies are unreachable on a phone.** The rail only becomes
  horizontal when `window.innerWidth >= 768`. Below that the track is `w-max` inside an
  `overflow-hidden` parent with no `overflow-x: auto` and no transform. Measured at 375px:
  track `scrollWidth` 1282, cards at x `20..313`, `337..629`, `653..946`, `970..1262`, so cards
  two through four are clipped with no way to reach them. Note that the gate did not catch this:
  `overflow-hidden` means there is no document-level horizontal scroll, and a `links` expectation
  only checks that the href is in the DOM. The row for `/` needs an expectation that every work
  entry is actually reachable, not merely present.
- **The rail's scroll distance goes negative on a very wide screen.** It is computed as
  `railTrack.scrollWidth - window.innerWidth + 64`, which is 475 at 1440 with four cards but
  turns negative above roughly 1915px, handing ScrollTrigger an end before its start on a pinned
  section. The gate tops out at 1440 and will not see it.
- **The custom cursor's listeners are never torn down.** The `pointermove` listener on `window`
  and the per-anchor `pointerenter`/`pointerleave` listeners are not registered with
  `motion.ts`'s teardown, so after an `astro:before-swap` the detached `#cursor` node keeps being
  tweened and a second set of listeners is added. The equivalent leak in `motion.ts` itself was
  fixed on 2026-08-28; this one was left because the code moves in this ticket.

**Blocked by:** 01.

**Status:** done

- [x] `/` serves the home page. `/preview/` no longer exists and nothing links to it.
- [x] The hero fills the viewport, its display lines animate in on load, and the width settle
      is present. No display line wraps at 375, 768 or 1440.
- [x] All four projects appear with year and stack, each linking to its case study, and their
      metadata is read from the content collection rather than repeated in the page.
- [x] On a narrow screen the work rail scrolls normally and nothing is pinned or scrub-jacked,
      and all four entries are reachable at 375px. The gate's row for `/` asserts reachability,
      not just that the links are in the DOM.
- [x] The rail's scroll distance is never negative, at any viewport width the design supports.
- [x] Every listener the page adds, the custom cursor's included, is removed on
      `astro:before-swap`.
- [x] Availability and a contact route are visible without hunting.
- [x] The base layout gives every page its own title and description, a canonical URL and
      social metadata, and no page is marked noindex.
- [x] The skip link is reachable by keyboard on first tab and moves focus to the main content.
- [x] A 404 route renders in the site's chrome.
- [x] The gate passes with a row for `/`.

**Landed 2026-08-28.** Notes on what the acceptance criteria turned into:

- The rail is a native `overflow-x: auto` scroller by default, at every width and with no
  JavaScript at all. Above 1024px a `gsap.matchMedia` scope pins the section, scrubs the track
  and sets the scroller to `overflow-x: hidden` for the duration; reverting the scope restores
  the scrollable fallback, so a resize back down, reduced motion and a no-JS load all land on
  the same reachable rail.
- The pin distance is `max(0, track.scrollWidth - scroller.clientWidth)` and the trigger's end
  is clamped to at least 1. Measured at 1600, 1920, 2200 and 2560: pinned with a positive
  distance at 1600, and above roughly 1900 the track fits, so no pin is created at all and no
  negative end can exist.
- The gate gained a `reachable` expectation key. It probes hit-testability at every step of the
  scroll-through, then gives anything still unreached a second chance by driving only the
  scroll containers a visitor can actually drive, which is `overflow-x: auto` or `scroll`.
  Deliberately not `scrollIntoView`: that scrolls an `overflow: hidden` box too, and reported
  the original bug as reachable when it was tried. Reintroducing `overflow-hidden` on the
  scroller makes the gate fail on cards three and four at 375 and 768, which is the bug.
- The custom cursor moved into the base layout, and all of its listeners hang off one
  `AbortController` registered with a new `onTeardown` hook in `motion.ts`. Verified: after
  dispatching `astro:before-swap`, a `pointermove` no longer moves the cursor.
- Two things beyond the ticket, both from looking at the screenshots. The hero's availability
  line was a `[data-reveal]` sitting at the very bottom of the first screenful, so the one line
  that says he is available was faded out on landing; it is now static. And the display scale
  went from `8.4vw` to `9.4vw`, which only affects widths below about 1430 where the clamp was
  not yet at its cap; the hero was small on a phone.
- Not done here: there is no `og:image`. The Jekyll `assets/` directory is not in Astro's
  output during the overlap, so any URL would 404. Ticket 07 or 10 is where that lands.

**Four findings from `/code-review`, all fixed in the same landing:**

- An `overflow: hidden` box is still programmatically scrollable, so the pinned rail could carry
  a `scrollLeft` from a narrow-width session, or one the browser adds itself to reveal a focused
  card, and stack it under the scrub transform for the rest of the session. The pinned scope now
  zeroes `scrollLeft` and holds it there, and removes the holding listener when it reverts.
  Measured: scroll the rail to 600 at 900px, resize to 1440, `scrollLeft` is 0 and the transform
  is identity; tab to the last card, still 0; resize back to 700 and the scroller is `auto` again.
- `teardown()` ran the page cleanups unguarded and ahead of everything else, so one throwing
  cleanup would skip the GSAP ticker and Lenis teardown and reinstate the per-frame leak fixed
  in `fa6f9c0`. Each cleanup is isolated now and the runtime teardown sits in a `finally`.
- The 404 route self-canonicalised to `/404/`, a URL that does not exist. It is `noindex` with
  no canonical and no `og:url`; every other route is unchanged.
- The gate could not tell "this link is unreachable" from "this link is not on the page",
  so a typo in an expectation row read as a layout bug. It now reports the two separately.
