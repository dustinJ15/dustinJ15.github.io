# TODO: the site

Source of truth for **site work**. Resume, LinkedIn and job-search tasks live in
`../career-hub/workflow/STATE.md`; keep them there.

Check items off as they land. Anything marked 🔒 **needs Dustin's approval before you do it**,
and approval is per action, not once.

---

## Next

- [ ] **Work through `REVIEW-CHECKLIST.md`.** It is the list of things the gate cannot judge:
      design calls to look at, the dark-mode read on a real screen, a real screen-reader pass, and
      the re-shot screenshots the supervising session has not opened yet. Nothing there blocks a
      deploy, but it is the human read the gate cannot stand in for.
- [ ] **Verify live, logged out.** Load `https://dustinJ15.github.io` in a real browser, logged
      out, and click every link. Live is a different environment from local. Only Dustin can do
      this. The phone half is already closed: he confirmed 2026-08-28 that it looks right there.

**The site is published.** It went live 2026-08-28, and every push to `main` redeploys it. So
`../career-hub/scripts/screen.sh .` and `npm run verify` both have to pass **before** any push,
not before some future first one, and 🔒 **every push needs Dustin's approval**. Un-publishing
does not un-clone.

## Backlog, not blocking

- [ ] Nothing queued. The next pass is whatever the review checklist turns up.

## Done

- [x] **README rewritten for a stranger, 2026-09-17.** The footer's new `Source` link means a
      reader can arrive at the repo cold, so the README opens on what the site is and what is
      interesting about it rather than on `npm install`, and `scripts/verify.py` gets a section
      instead of a line. The working content stayed: Local, Structure, Adding a project and the
      publishing rules, all corrected where they had gone stale.
- [x] **Published, 2026-08-28.** `dustinJ15/dustinJ15.github.io` is public, Pages is on the
      GitHub Actions source, and the deploy ran in 44 seconds. Task 40 in career-hub.
- [x] **career-hub told, 2026-08-28 and 2026-09-17.** Task 41 flipped `INCLUDE_SITE = True` in
      `resume/build_resume.py` and rebuilt all four variants, each still one page and each
      printing the site on the contact line. Task 32 added the site to LinkedIn Featured.
- [x] **Pre-publish trims, 2026-09-15.** Quote generator study cut by a fifth: the three
      build-process sections are one, "How it was built", and the defect ledger lives on Process
      alone. Third metric is `1.5` with the unit in the label, so the tiles share a baseline. Stack
      marquee removed from the home page. Every private-code study links Process from its Code line.
- [x] **Second design pass, 2026-09-14.** Chapter list is a sticky second column from xl
      (`Chapters.astro`), shared by the case studies and Process; About keeps its availability in
      the same lane. Hero cap at 12rem below lg so the name fills a tablet. Case-study figures
      matted and capped at 80svh with in-frame scrolling. Process chain numbered, its four rules
      set as ruled h3s. Home cards carry a thumbnail from an existing capture (`thumb` in front
      matter, optional). `VERIFY_PYTHON` overrides the gate's interpreter.
- [x] **Portfolio conventions pass, 2026-09-12.** Hero is the name. Resume PDF at
      `public/Dustin-Jones-Resume.pdf`, built in career-hub with `build_resume.py general
      --no-phone` and copied over by hand; after any resume change, rebuild with the flag and
      re-copy it. Experience list on About (titles and dates only). Share image at
      `public/og.png`. Six verbosity cuts: home bio and private-code paragraph gone, case
      studies open on the outcome pair, quote generator trimmed by a third, Process lost
      "Used on", footer notes gone from every study.
- [x] **Billing analyzer is one capture** (2026-09-14), header through the activity calendar,
      cropped above the tables that carry per-item totals. `shoot-offline-tools.py` in
      career-hub produces the same file. The quote generator has a chapter list, fixed beside
      the prose from xl and in flow below it, opted in with `chapters: true` in front matter.
- [x] **The portfolio prose pass, 2026-09-12.** The work is the subject and the author is the
      byline. Self-evaluation ("I'd defend hardest", "proud of", "the habit I'd bring to a team"),
      interview framing ("The obvious objection"), the second GPA mention, the senior
      vice-president name-drop and eleven rhetorical "actually"s are gone. Headings name a
      problem or a mechanism. Availability is one plain line at the end of About; the hero
      button now points at the work. New hero: "Tools for a clinical lab, a property firm, and
      the people who run them." Gate rows updated to match.
- [x] **The redesign, tickets 01 to 11.** The site is Astro 7, Tailwind v4, dark only, in the
      Obys direction. Eight routes: home, process, about, four case studies and a 404. See
      `specs/portfolio-redesign/`.
- [x] **The verification gate.** `npm run verify` type-checks, builds, and drives every route at
      375, 768 and 1440 with Playwright: no horizontal scroll, no console errors, WCAG AA
      contrast, links resolve and are reachable, reduced motion leaves nothing invisible, the
      page renders with JavaScript off, no route ends on a screenful of nothing, and the
      per-route expectations table holds. Tickets 01 and 09.
- [x] **Jekyll deleted.** Layouts, includes, config, Gemfiles, page sources and build output are
      gone, the images moved under `src/assets/img/`, and the deploy workflow builds on push to
      `main`. One site, one build. Ticket 10.
- [x] **Em-dashes gone** from every page, including alt text, captions, tab titles and meta
      descriptions. The gate fails on one, so they cannot come back. Ticket 08.
- [x] **Screenshots, all four case studies.** Quote generator (4), billing analyzer (4), label
      maker (3), all synthetic data, re-shot at one viewport at 1500 by 950 at 2x and served as
      lazy responsive WebP. `rental-pipeline` is a pipeline rather than a UI, so it got a
      hand-authored inline SVG of sixteen inputs converging on one schema. Tickets 06 and 07.
- [x] **About page written** from the interview transcript. Return framing, no career-change
      language, no health detail. The Pragmatic Programmer line is now a cited display pull
      quote rather than an uncited sentence.
- [x] **The spreadsheet motif is dead site-wide**, in copy and in meta descriptions.
