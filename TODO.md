# TODO — the site

Source of truth for **site work**. Resume, LinkedIn and job-search tasks live in
`../career-hub/workflow/STATE.md`; keep them there.

Check items off as they land. Anything marked 🔒 **needs Dustin's approval before you do it**,
and approval is per action, not once.

---

## Next

- [ ] 🔒 **Publish.** Create `dustinJ15/dustinJ15.github.io` as a public repo, push, enable Pages.
      Ask before creating, then ask again before enabling Pages. This is the least reversible
      thing in the list; un-publishing does not un-clone.
- [ ] **Verify live.** Load `https://dustinJ15.github.io` in a real browser, logged out, and click
      every link again. Live is a different environment from local: relative paths and `baseurl`
      behave differently. Then check it on a phone, which is the actual use case.
- [ ] **Tell career-hub.** Once the site resolves, task 41 there flips `INCLUDE_SITE = True` in
      `resume/build_resume.py` and rebuilds, and task 32 adds the site to LinkedIn Featured.
      Do not flip it before the site loads; it prints a dead URL on every copy.

## Done

- [x] **About page written** from the interview transcript. Return framing, no career-change
      language, no health detail, no em-dashes.
- [x] **Screenshots, all four case studies.** Quote generator (4), billing analyzer (4),
      label maker (3). All synthetic data, all opened and read individually before placing.
      Re-shot in ticket 07 at one viewport, 1500 by 950 at 2x, and served as lazy WebP.
- [x] **QA.** Screen passes, Jekyll builds clean, seven pages, every link resolves, no horizontal
      scroll at 375px or 1440px.
- [x] **Home page opening rewritten.** The spreadsheet motif is dead site-wide, including the
      copy in `_config.yml`'s meta description.
- [x] **Design direction A.** Display face, real type scale, portrait above the fold.

## Backlog, not blocking

- [x] **Strip the em-dashes from page copy.** Gone from every Astro page, including alt text,
      captions, tab titles and meta descriptions. The gate's em-dash check now fails the build
      rather than advising, so one cannot come back. Ticket 08.
- [x] **`rental-pipeline` has no screenshot.** The other three case studies do now. It is a
      pipeline rather than a UI, so it got a hand-authored inline SVG of sixteen inputs
      converging on one schema instead. Ticket 06.
- [ ] **Dark mode has never been reviewed on a real screen.** The tokens are all defined and the
      palette swaps, but nobody has looked at it. Check the figures especially: screenshots are
      light-background images sitting on a dark page.
- [ ] **A second design pass.** Dustin: "we are going to spend some time in the future making
      this better. It will work for now." Directions B (technical, high contrast, IBM Plex
      Sans + Mono, numbered projects) and C (warm, personal, Source Serif, terracotta, large
      portrait) were built and set aside; the 2026-08-28 entry in `../career-hub/workflow/LOG.md`
      describes both well enough to rebuild.
- [ ] **Consider Astro** if this ever grows a blog or many more project pages. Not before; at
      seven pages it is a migration for a benefit nobody feels, and GitHub Pages builds Jekyll
      with no config at all.
