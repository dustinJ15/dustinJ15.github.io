# 03: Case-study pages at `/projects/<id>/`

**What to build:** All four case studies read end to end in the new design. Each opens with a
choreographed full-viewport title carrying the project name, year, role and stack, states its
before and after near the top so a skimming reader gets the outcome without reading the
argument, and then settles into calm prose at a comfortable measure. Section headings become
display moments that reveal on scroll. Screenshots break full-bleed inside a dark browser-chrome
frame. One or two sentences per study are pulled out as large display quotes.

The reading experience is the point of these pages, so the restraint is deliberate: paragraphs
get at most a gentle fade, never a line-by-line reveal, nothing is pinned inside the argument,
and nothing scroll-triggered gates the first paint of body text.

The before/after outcome is a designed component driven by the structured field on the content
collection, not a strikethrough with a border hand-rolled in the markdown.

Every project's header metadata comes from the collection, which is also what the home page work
rail reads, so the two cannot drift.

Images stay in the Jekyll asset directory for now and are imported from there through Astro's
image pipeline, which handles it fine. They move under `src` only when Jekyll is deleted, so no
duplicate binaries enter git history. Re-shooting them is ticket 07; this ticket uses what
exists. Rental-pipeline has no visual and does not get a placeholder; its diagram is ticket 06.

Adding a fifth case study later must mean dropping one markdown file in and nothing else.

**Blocked by:** 02.

**Status:** ready-for-agent

- [ ] All four case studies render at `/projects/<id>/` and are reachable from the home page.
- [ ] Each page's title block carries the project name, year, role and stack, all read from the
      content collection.
- [ ] The before/after outcome is a designed component and appears near the top, above the body
      of the argument.
- [ ] Body copy sets at a readable measure and is fully visible before any scroll-triggered
      animation runs.
- [ ] Figures render full-bleed in dark browser chrome with their existing alt text and captions
      carried over, and are legible at 1440.
- [ ] At least one pull quote per study, drawn from that study's own prose.
- [ ] Nothing is pinned and no reveal fires inside the prose beyond a fade.
- [ ] Metrics render only where the collection supplies them, and every value shown is traceable
      to a sentence in that case study.
- [ ] The Jekyll project pages still build and are untouched.
- [ ] The gate passes with a row per case study naming its heading structure and figure count,
      and asserting every figure has non-empty alt text.
