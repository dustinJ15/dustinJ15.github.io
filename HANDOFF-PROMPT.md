# Handoff: plan the next design pass on dustinJ15.github.io

You are picking up Dustin Jones's portfolio site mid-stream. Your first job is a **plan, not code**: read the
repo, look at the site in a browser, research what genuinely good developer portfolios do, and write a plan
for making this one look better. Then stop and show Dustin the plan.

Start by reading `CLAUDE.md` in the repo root. It is short, it is the law here, and it explains the gate, the
screen, the em-dash ban, the "no career-change framing" rule and the retired spreadsheet motif. Then read
`TODO.md` and `REVIEW-CHECKLIST.md`.

## Where things are right now

- **Repo:** `~/sync/code/personal/dustinJ15.github.io`. Astro 7, Tailwind v4, static, dark only, Obys-lane
  design (oversized Bricolage Grotesque display type, one acid accent, scroll choreography).
- **Dev server is running** at `http://127.0.0.1:4321/` with the current working tree. Leave it on that port.
  If it has died, `npm run dev -- --host 127.0.0.1 --port 4321`.
- **The gate** (`scripts/verify.py`) serves its own build on port **4390**, so it no longer evicts the dev
  server. `npm run verify` points at a Python venv that does not exist on this machine
  (`~/sync/code/work/quote-generator/.venv`). Use the scratch one instead:
  `npx astro check && npx astro build && /tmp/claude-1000/-home-dustin-sync-code-personal-dustinJ15-github-io/84a1d7f8-d3c2-4e8a-8313-46da7e6a80c9/scratchpad/pw/bin/python scripts/verify.py`.
  If that path is gone, make a venv anywhere outside the repo, `pip install playwright`,
  `playwright install chromium`, and consider making the venv path in `package.json` configurable.
  Screenshots land in `.verify/`; open them, the gate cannot judge looks.
- **Nothing is committed.** Two repos have uncommitted work from the last two sessions: this one, and
  `../career-hub` (private, no remote) where `resume/build_resume.py` gained a `--no-phone` flag and
  `scripts/shoot-offline-tools.py` now produces one billing capture. Do not commit or push anything
  without asking Dustin, per action. Note that **the site is live** and every push to `main` deploys.

## What the last two sessions did (2026-09-12 to 14)

1. A prose pass: the work is the subject, the author is the byline. Self-evaluation, interview framing,
   credentials repeated on two pages and eleven rhetorical "actually"s were cut.
2. Portfolio conventions: hero is now just the name ("DUSTIN / JONES"), a site-only resume PDF without the
   phone number at `public/Dustin-Jones-Resume.pdf`, an experience list on About, `public/og.png` share
   image, home bio and contact paragraph removed, case studies open on the outcome pair rather than a lede,
   quote generator trimmed by a third, Process page lost its "Used on" section, footer notes removed.
3. Billing analyzer is one tall capture instead of four crops. Quote generator has a chapter list (opt-in
   via `chapters: true` in front matter), fixed to the right of the prose from `xl`, current chapter
   highlighted by an IntersectionObserver, ids stamped on h2s by `src/plugins/case-study-markdown.mjs` using
   the shared slug in `src/plugins/slug.mjs`.

## Known problems, in priority order

1. **The chapter list collides with the screenshots.** On the quote generator at desktop width, figures
   span the prose's `wide` grid column and run underneath the fixed chapter nav on the right. Dustin saw
   it and laughed. Either the figures need a right boundary that respects the nav, or the nav needs a
   lane of its own (a real two-column layout rather than `position: fixed` over the prose grid). Look
   at `.prose` in `src/styles/global.css` (named grid lines `full`, `wide`, `content`) and the `#chapters`
   nav in `src/pages/projects/[id].astro`.
2. **A horizontal card rail for chapters was tried and rejected** ("doesn't look great"). Dustin asked for
   simpler, vertical, always visible, and to "lean on existing frameworks more": Tailwind utilities and
   browser features over bespoke GSAP work. Keep that preference in mind for everything you propose.
3. **The hero at 768** leaves a large void between the name and the ruled foot. The name is two rows and
   the hero is `min-h-[calc(100svh-6rem)]`. It passes the gate but reads empty on a tablet.
4. **The second design pass is still owed.** `TODO.md` backlog: "the Obys direction landed; the next pass
   is refinement rather than a redirection." Nobody has done it. The site has motion (per-line title rise,
   Bricolage width settle, custom cursor, marquee, pinned work rail on the home page) but the prose pages
   and case studies are plain by comparison.
5. **Case-study screenshots** are light UI on a near-black page inside drawn browser chrome. They work,
   but they are the least designed thing on the site. Every image is synthetic data; re-shooting goes
   through career-hub scripts (`shoot_clean.py` for the quoting app, `shoot-offline-tools.py` for the
   other two) and every new PNG must be opened and looked at before it ships, because the screen script
   cannot read an image. No screenshot with a per-item fee column ever ships.
6. **Housekeeping you will trip over:** `../career-hub/scripts/screen.sh .` reports hits inside
   `node_modules/` and `.astro/`; both are gitignored and it is noise, but confirm no hit is in a tracked
   file before any publish. The `src/data/site.ts` file was once found deleted from the working tree by
   accident; if the build fails on a missing import, check `git status` before anything else.

## What Dustin wants from you

- **Research first.** Look at genuinely good developer and studio portfolios (obys.agency is the stated
  reference; brittanychiang.com was the runner-up; find current ones too) and write down concretely what
  makes them read as finished: rhythm between sections, how images sit on dark ground, how a long case
  study is paced, how navigation stays out of the way. Compare against this site in the browser, at 375,
  768 and 1440, and say where it falls short.
- **Then a plan**, in `~/.claude/plans/`, using plan mode. Prioritised, concrete, per file. Fix the chapter
  collision first. Every item must survive the gate and the rules in `CLAUDE.md`. Say what needs a
  re-shoot and what does not. Do not propose a light theme, a skills grid, testimonials, fake counters,
  or the "spreadsheet" motif. No em-dashes anywhere, including this plan.
- Ask before anything irreversible. Committing and pushing are Dustin's calls, each time.
