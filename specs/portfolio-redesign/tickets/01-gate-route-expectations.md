# 01: Per-route expectations in the verification gate

**What to build:** One command tells Dustin whether the site is broken. `npm run verify`
stops running a hard-coded list of preview paths and instead reads a declarative table of
routes, where each route names what must be true of its own rendered output. Running the
command type-checks, builds, serves the built output and sweeps every route in the table at
every viewport, then prints one pass or a list of concrete failures. Every ticket after this
one adds its route's row and is finished when the gate passes with that row in place.

The universal checks already in the harness stay exactly as they are: no horizontal scroll
measured as scrollWidth against clientWidth, no console errors or failed requests, WCAG AA
contrast on every rendered text leaf at the threshold for its size and weight, internal links
resolve, reduced motion leaves nothing invisible, and after a full scroll-through every reveal
has fired and no display line has wrapped. This ticket adds the per-route layer on top and two
new universal checks that the whole site needs and no single page ticket owns.

Expectations are stated as rendered structure, never implementation. A row says "one h1, four
figures, every figure has non-empty alt text, and a link to /about/ resolves". A row never
names a class, a component or a file. The point is that the table survives a redesign and
still catches a regression.

The two new universal checks:

- **Renders with JavaScript disabled.** Load each route in a context with JS off and assert
  the page's text content is present and nothing is left at opacity 0. A failed script must
  never produce a blank page.
- **No em-dash in rendered text.** Advisory for now, printed but not failing, because the
  existing copy still carries them and ticket 08 is what removes them. Ticket 08 flips it to
  a failure.

Seed the table with a row for the preview lane that exists today, so the gate passes the
moment this lands.

**Blocked by:** None. Can start immediately.

**Status:** done

- [x] A single documented command runs the type check, the build and the sweep, and exits
      non-zero if any of the three fails.
- [x] The route list comes from the expectations table, not from a literal in the argument
      handling. Passing explicit paths still works for a fast single-route loop.
- [x] Each route's expectations are declared in one place, in terms of rendered structure:
      heading count and level, named sections present, figure count, alt text non-empty,
      internal links that must resolve.
- [x] A missing or wrong expectation reports the route, the expectation and what was actually
      found, specifically enough to act on without opening a browser.
- [x] Every route renders its content with JavaScript disabled, and the check fails if a route
      comes back blank or with content stuck invisible.
- [x] Em-dashes in rendered text are reported per route as advisory, with the offending text.
- [x] The existing universal checks and the screenshot output are unchanged in behaviour.
- [x] The gate passes on the current tree with a row for the existing preview lane.
