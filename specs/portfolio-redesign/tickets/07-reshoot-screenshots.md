# 07: Re-shoot the screenshots

**What to build:** Every screenshot on the site is re-shot at one consistent viewport, so the
case studies stop looking like a collection of found images and the interfaces being described
are actually legible. They serve as WebP through the image pipeline and load lazily, so a
visitor on a slow connection has a usable page before everything downloads.

The shoots run from the career-hub pipeline, which is the only place they can run because it
depends on private repos. Two hazards there, both of which have bitten before:

- The quoting-app shoot leaks real pricing if run naively. Read the 2026-08-28 entry in the
  career-hub log before touching it. The wrapper that rewrites every fee, legal note and item
  name to invented values is not optional.
- The offline-tools shoot blanks every image before shooting, because the label preview renders
  the employer logo. That step stays.

Nothing with a visible fee column ships, invented or not. A stranger reading a picture cannot
tell an invented rate from a real one.

The screen script cannot read a PNG. Every image gets opened and looked at by a person before it
is placed, and that is a step in this ticket, not a formality after it.

Nothing in career-hub changes as part of this work.

**Blocked by:** 03.

**Status:** ready-for-agent

- [ ] Every screenshot on the site is re-shot at one consistent viewport width.
- [ ] All source data is synthetic. No real client data, pricing, legal text or item name is in
      any shipped image.
- [ ] No shipped image shows a fee column.
- [ ] The employer logo does not appear in any image.
- [ ] Every image was opened and looked at by a person before being placed, and that is stated
      in the ticket's completion.
- [ ] Images serve as WebP at appropriate sizes and load lazily below the fold.
- [ ] Each screenshot is legible at 1440 inside its browser-chrome frame.
- [ ] Nothing under career-hub was modified.
- [ ] The screen passes on the publishable surface, and the gate passes with the figure counts
      unchanged.
