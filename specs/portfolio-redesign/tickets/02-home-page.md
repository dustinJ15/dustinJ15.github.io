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

**Blocked by:** 01.

**Status:** ready-for-agent

- [ ] `/` serves the home page. `/preview/` no longer exists and nothing links to it.
- [ ] The hero fills the viewport, its display lines animate in on load, and the width settle
      is present. No display line wraps at 375, 768 or 1440.
- [ ] All four projects appear with year and stack, each linking to its case study, and their
      metadata is read from the content collection rather than repeated in the page.
- [ ] On a narrow screen the work rail scrolls normally and nothing is pinned or scrub-jacked.
- [ ] Availability and a contact route are visible without hunting.
- [ ] The base layout gives every page its own title and description, a canonical URL and
      social metadata, and no page is marked noindex.
- [ ] The skip link is reachable by keyboard on first tab and moves focus to the main content.
- [ ] A 404 route renders in the site's chrome.
- [ ] The gate passes with a row for `/`.
