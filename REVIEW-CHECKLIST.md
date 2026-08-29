# Human-eye checklist — the redesign

Things the gate cannot judge and agents deliberately left for Dustin. Work through this before
the publish ticket. Nothing here blocks the remaining tickets.

## Design calls to look at

- [ ] **`/about/` H1 is entirely acid lime.** `PageTitle` accents the last line; a one-line title
      makes that unconditional. One line to make it ink if it is too loud for a prose page.
- [ ] **The portrait's accent wash gives skin an olive cast.** Grayscale plus accent wash stops the
      photo reading as a hole punched in the page, but it is a taste call.
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

## Known gaps, owned by later tickets

- [ ] **No `og:image`.** Astro's output does not include the Jekyll `assets/` tree during the
      overlap, so any URL would 404. Ticket 07 or 10. Social shares are text-only until then.
- [ ] **Screenshots are the old shoots at two different widths** (1366 and 1800). They read at 1440
      and are small at 375. Ticket 07 re-shoots at one width.

## Live, after publish

- [ ] Load the site logged out in a real browser and click every link. Relative paths behave
      differently live.
- [ ] Check it on a phone, which is the actual use case.
