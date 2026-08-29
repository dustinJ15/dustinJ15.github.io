# Human-eye checklist: the redesign

Things the gate cannot judge and agents deliberately left for Dustin. Work through this before
the publish ticket. Nothing here blocks the remaining tickets.

## Design calls to look at

- [ ] **The base layout added a site header** (wordmark plus Work / Process / About). Ticket 02
      named only a skip link and a footer. Without it there is no way back from `/about/`.
- [ ] **The work rail's `Scroll →` hint shows at every width**, not just desktop, because narrow
      screens genuinely scroll it too.
- [ ] **The case-study prose column is deliberately off centre.** Figures and headings open further
      right than left.
- [ ] **Case-study body is set in `--ink`, not the softer `--ink-soft` the home page uses.**
- [ ] **Pull quotes are lightly trimmed rather than strictly verbatim**, so they carry no em-dashes.
- [ ] **Dark mode has never been reviewed on a real screen.** Screenshots are light-background
      images sitting on a near-black page. Check the figures especially.

- [ ] **The 1440 full-page PNG shows a large void above the contact rule.** It is the pin spacer
      holding the scrub distance and no visitor ever sees it. If reading flat screenshots is the
      review loop, that band will keep looking like a bug. Check it with the viewport captures.
- [ ] **The larger about portrait upscales on HiDPI.** Source is 1000x1190; a 2x 1440 screen wants
      about 1220 at the new size. A larger export from the career-hub original fixes it. If the
      photograph's bright background now reads as a hole at 577px, the lever is `brightness`,
      not the accent wash, which was dropped deliberately.
- [ ] **The pinned rail centres its cards in a full-height section**, so about 200px sits above the
      label and 200px below the cards, and the lower band shows for a moment as the pin releases.
      Symmetric and deliberate, but a composition choice rather than a forced one.
- [ ] **The quote-builder screenshot is nearly two viewport-heights** inside its frame at 1440, so
      the pictured browser window is never seen whole. Cropping shorter costs the line-item groups
      the alt text and the argument both lean on.
- [ ] **Seven of the eleven re-shot screenshots have not been opened by the supervising session.**
      The implementing agent and its reviewer both opened all eleven. The four highest-risk ones
      were independently checked. The other seven are the three billing shots, two label-maker
      shots and the intake form.

Ticket 11 now owns the acid-lime `/about/` H1, the portrait's olive cast, the dead vertical space
above the contact block and the hero's scale at 375.

## Content and correctness

- [ ] **Every screenshot opened and read individually.** The screen script cannot read a PNG. This
      is a standing rule, not a one-off.
- [ ] **The Pragmatic Programmer quote on `/about/`.** An agent first misattributed it to Hunt and
      Thomas; it is Ward Cunningham's, from the foreword, and is now quoted verbatim and cited.
      Worth confirming by eye since it names real people.
- [ ] **The rental-pipeline prose names four vendor products** (Yardi, ResMan, Entrata, RealPage).
      Pre-existing published copy, not added by any agent, and they are commercial products rather
      than clients. Still worth a deliberate yes or no before publish.
- [ ] **The rental-pipeline diagram discloses nothing.** Sixteen inputs, one schema, no client, no
      source system, no field names.

- [ ] **The diagram sits left at 1440 with space to its right.** Deliberate: label legibility at
      375 sets its max-width, and the asymmetry is on-direction. One line if it should be bigger.

## The editorial pass, ticket 08

- [ ] **Two rewrites the agent flagged for a second read.** In `quote-generator.md`, "Their job is
      to check a document and make the calls that need judgment, not to assemble one" became "...
      that need judgment. Assembling one is no longer part of the job." The contrast survives but
      lands slower. And "That habit, treating 'we have not actually confirmed this' as a fact worth
      writing down, is the thing I would bring to a team" was reordered to "Treating 'we have not
      actually confirmed this' as a fact worth writing down is the habit I would bring to a team".
- [ ] **`about.astro` lost a line to the no-career-change rule.** "The strange part of the shift is
      that skiing was legible to anyone watching and programming is not" is now "Skiing was legible
      to anyone watching. Programming is not." Read it in place; it sets up the Cunningham quote.
- [ ] **`rental-pipeline` has no before/after block.** Deliberate: it is the case that proves the
      `Outcome` component is data driven rather than always drawn. Its tagline carries the outcome
      instead. Say if you want the block there.

## Accessibility, ticket 09

- [ ] **A real screen-reader test, which only a person can do.** Playwright reads Chrome's
      accessibility tree, which is not the same as NVDA, JAWS or VoiceOver speaking the page. Ten
      minutes with VoiceOver on the home page and one case study. Listen to the work-rail cards
      especially, since each announces as one long link (number, year, title, tagline, stack), and
      to the pipeline diagram's accessible name.
- [ ] **No-JS keyboard is imperfect and cannot be fixed.** With JavaScript off the rail is a plain
      scroller and Chrome only scrolls a newly focused card part of the way on screen. Every card
      is reachable and focusable; one may sit partly off screen. Accept or reject knowingly.

## Known gaps

- [ ] **No `og:image`.** Ticket 10 moved the images under `src/assets/img/`, where Astro
      fingerprints them, so there is still no stable URL to point at. Social shares are text-only.
      Tracked in `TODO.md` as backlog, not a blocker.

## Live, after publish

- [ ] Load the site logged out in a real browser and click every link. Relative paths behave
      differently live.
- [ ] Check it on a phone, which is the actual use case.
