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

**Status:** done

- [x] Every screenshot on the site is re-shot at one consistent viewport width.
- [x] All source data is synthetic. No real client data, pricing, legal text or item name is in
      any shipped image.
- [x] No shipped image shows a fee column.
- [x] The employer logo does not appear in any image.
- [x] Every image was opened and looked at by a person before being placed, and that is stated
      in the ticket's completion.
- [x] Images serve as WebP at appropriate sizes and load lazily below the fold.
- [x] Each screenshot is legible at 1440 inside its browser-chrome frame.
- [x] Nothing under career-hub was modified.
- [x] The screen passes on the publishable surface, and the gate passes with the figure counts
      unchanged.

## How it was shot

All eleven screenshots were taken at **1500 x 950 CSS pixels at a device pixel ratio of 2**, then
cropped at a card boundary and resampled to a single delivered width of 2400px. One viewport, one
delivered width; what varies between figures is only how tall the thing being pictured is.

Both career-hub shoot scripts ran unmodified and nothing under career-hub was touched. The
quoting app went through `shoot_clean.py`, which rewrote 53 catalog fees, replaced the 8 legal
notes with invented ones and patched 4 hardcoded fee literals in the shoot tool's own source
before the browser opened. The offline tools went through `shoot-offline-tools.py`, which
reported `logos blanked: 1` on the envelope preview. tools/shoot.py hardcodes a 1366x900 window
at 1x, so each script was driven by a small wrapper in the scratchpad that forces the browser
viewport and nothing else: every sanitising step still runs, because it hangs off the imported
module rather than being reimplemented.

The `data/` directory the quoting app recreates inside its own checkout on import was deleted
afterwards, as the career-hub log requires. That repository is back to the three deletions it
started with.

**Every one of the eleven images was opened and read individually, at full size, before it was
placed.** No fee column appears in any of them: the twelve line-item groups on the quote builder
are collapsed, the running total reads $0.00, and the billing analyzer's contract-rates panel is
a closed disclosure. Study IDs are `SHOOT-*` and `DEMO-4471C002`, the sponsor is ACME Pharma,
users are "Shoot BD/PM/Specialist" with no email addresses, and the label preview's employer logo
is a grey block. The employer's name appears in app chrome, which is deliberate and allowed.

Two pieces of copy moved to stay true to what the new crops show: the intake caption now says
four sections continue below rather than three, and the quote-builder alt text names twelve
collapsible line-item groups instead of legal notes, which the crop no longer reaches.

**Not done here: `og:image`.** Ticket 02 left it open between this ticket and 10. It belongs to
10. The images are still in the Jekyll asset tree and only reach Astro's output because a case
study imports them; a social card is a new asset with an absolute URL, and 10 is the ticket that
moves the images under `src/` and turns the deploy on.
