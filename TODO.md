# TODO: the site

Source of truth for **site work**. Resume, LinkedIn and job-search tasks live in
`../career-hub/workflow/STATE.md`; keep them there.

Check items off as they land. Anything marked 🔒 **needs Dustin's approval before you do it**,
and approval is per action, not once.

---

## Next

- [ ] **Work through `REVIEW-CHECKLIST.md`.** It is the list of things the gate cannot judge:
      design calls to look at, the dark-mode read on a real screen, a real screen-reader pass, and
      the seven re-shot screenshots the supervising session has not opened yet. Nothing there
      blocks publishing, but it is the last human read before it.
- [ ] 🔒 **Publish.** Create `dustinJ15/dustinJ15.github.io` as a public repo, push, enable Pages.
      Ask before creating, ask again before pushing, and ask again before enabling Pages. Three
      separate approvals. This is the least reversible thing in the list; un-publishing does not
      un-clone. Run `../career-hub/scripts/screen.sh .` immediately before.
      The deploy workflow now builds on every push to `main`, so the first push is also the first
      deploy. Set Pages to the GitHub Actions source **before** that first push, or the run fails
      at `configure-pages` with "Get Pages site failed". Enabling Pages is not automated on
      purpose; it is Dustin's to do.
- [ ] **Verify live.** Load `https://dustinJ15.github.io` in a real browser, logged out, and click
      every link again. Live is a different environment from local. Then check it on a phone,
      which is the actual use case.
- [ ] **Tell career-hub.** Once the site resolves, task 41 there flips `INCLUDE_SITE = True` in
      `resume/build_resume.py` and rebuilds, and task 32 adds the site to LinkedIn Featured.
      Do not flip it before the site loads; it prints a dead URL on every copy.

## Backlog, not blocking

- [ ] **No `og:image`.** Social shares are text-only. Adding one means a real image at a stable
      URL and an absolute `og:image` in `BaseLayout`.
- [ ] **A second design pass.** Dustin: "we are going to spend some time in the future making
      this better." The Obys direction landed; the next pass is refinement rather than a
      redirection.

## Done

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
