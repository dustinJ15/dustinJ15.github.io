# CLAUDE.md — working notes for this repo

**This file is public.** So is everything else here, the moment the repo goes up. Never write
employer internals, screening patterns, or personal detail into this repo. The private context
lives next door in `../career-hub/` (local-only git, no remote, ever) and is read on demand.

---

## What this is

Dustin Jones's portfolio. Jekyll, hand-written CSS, **no theme, no framework, no build step
beyond Jekyll itself.** Seven pages: home, process, about, and four case studies.

The site's differentiator is the writing. The case studies argue rather than list — the
quote-generator page admits an approach that failed and explains why the dumber fix was right.
**Every design and content decision protects the reading experience.** That is the whole brief.

## Hard rules

1. **Never push, create a repo, change visibility, or enable Pages without asking Dustin first,
   per action.** Not "once at the start" — each time.
2. **Never publish employer internals.** Naming Frontage Laboratories is fine and deliberate.
   Describing how their systems work internally, or reproducing anything specific to their
   business or their clients, is not. Same rule for `rental-pipeline`, which is separate work
   with its own client data.
3. **Run the screen before every publish.** It lives outside this repo on purpose, so the list of
   strings being screened for is never itself published:
   ```bash
   ../career-hub/scripts/screen.sh .
   ```
   It exits non-zero on a hit and screens file *names* as well as contents. Passing it is
   necessary, not sufficient: **it cannot read a PNG.** Every image must be opened and looked at.
4. **No em-dashes in anything Dustin reads.** He reads them as an AI tell. (Existing page copy
   still contains some; that is a known cleanup, not a licence to add more.)
5. **No career-change framing.** He started a CS degree, stopped, came back to it. It is a
   return. The gap is gestured at and never explained, and no page ever says why.
6. **The "I replace manual spreadsheet processes" motif is retired**, including the variant
   "I build the tool that deletes the spreadsheet". He rejected it twice. Do not reintroduce it.

## Commands

```bash
# The Astro site
npm run dev                  # dev server
npm run build                # build to dist/
npm run verify               # THE GATE: astro check, then build, then the sweep
npm run verify -- /about/    # same, swept against one route for a fast loop

# The Jekyll site, until ticket 10 deletes it. Ruby 4.0 cannot install Jekyll
# locally (http_parser.rb won't compile), so use podman:
podman run --rm -v "$PWD":/srv/jekyll:Z -w /srv/jekyll docker.io/jekyll/jekyll:4 jekyll build
cd _site && python3 -m http.server 8899

# Screen. From the repo root, on tracked plus untracked-not-ignored files only:
# node_modules matches a screened token hundreds of times and is noise.
../career-hub/scripts/screen.sh .
```

**`npm run verify` is the one command that says whether the site is broken.** It type-checks,
builds, serves `dist/` and drives every route with Playwright, and exits non-zero if any of the
three stages fails. It runs, per route:

- The universal checks. No horizontal scroll, measured as `scrollWidth` against `clientWidth`.
  No console errors or failed requests. WCAG AA contrast on every rendered text leaf at the
  threshold for its size and weight. Internal links resolve. Reduced motion leaves nothing
  invisible. After a full scroll-through every reveal has fired and no display line has wrapped.
  The page renders with JavaScript disabled: text present, nothing stuck at opacity 0.
- The per-route expectations, from the `EXPECTATIONS` table at the top of `scripts/verify.py`.
  A row states what must be true of the page a visitor receives: heading counts, named sections,
  figure count, non-empty alt text, links that must be present, links that must be *reachable*
  and not merely in the DOM, copy that must appear. **A row
  never names a class, a component or a file**, so the table survives a redesign and still catches
  a regression. Adding a page means adding its row; a ticket is finished when the gate passes
  with its row in place.
- The em-dash advisory. Printed, not failing, because the existing copy still carries them.
  Ticket 08 removes them and flips it to a failure.

The gate is a floor, not a judge. It cannot tell you whether the design is good, and the screen
script cannot read a PNG, so the screenshots it writes to `.verify/` still have to be opened and
looked at.

Playwright lives in `~/sync/code/work/quote-generator/.venv/bin/python`; `npm run verify` calls
it by that path. Nothing is installed system-wide.

## Design direction: the reference sites

**Chosen 2026-08-28 from three working previews.** The direction is the **Obys lane**. If you are
an agent picking this up cold, look at these before touching the design. They are the intent.

| Reference | What we took from it |
| --- | --- |
| **obys.agency** | The whole direction. Oversized display type, asymmetric layout, aggressive scale contrast, scroll choreography, custom cursor, marquee strips, near-black ground with a single acid accent. |
| **brittanychiang.com** | The runner-up (built as preview P1, deleted). Numbered work entries and mono-set metadata survive from it into the chosen lane. |

Obys uses custom licensed typefaces we cannot ship. **Bricolage Grotesque Variable** is the
deliberate stand-in: it carries both a width and a weight axis, which is what makes the hero
settle from condensed to full width on load. Do not swap it for a static face without
replacing that animation.

Two directions were built and deleted: P1 (brittanychiang lane, deep navy and teal) and P3
(a hybrid). Their palettes are in this file's git history at the Phase 1 commit if anyone
wants them back.

## Design decisions, and why

> **SUPERSEDED as of the 2026-08-28 redesign.** Everything in this section describes the old
> Jekyll site and its "protect the reading experience above all" brief. That brief was
> deliberately inverted: the site is moving to Astro + Tailwind v4, dark only, with heavy
> scroll choreography. Cards, shadows, gradients, scroll animation and Tailwind are all now
> allowed. The `--measure` rule is loosened. See the section above for the real direction.
> This section is kept only until the migration lands, and is rewritten then.

Chosen 2026-08-28 from three working directions. Do not undo these casually.

- **Fraunces** (Google Fonts) for the wordmark, `h1`/`h2`/`h3` and the intro line. **Charter**
  carries every word of body text. This is the site's only external dependency; it had none
  before, and adding a second one needs a reason.
- **`--measure: 36rem`**, about 70 characters. This is a legibility constant, not a style
  preference. Past ~75 characters the eye loses the line return. **The text column is narrow on
  purpose. Do not widen it because a page "looks empty".**
- **Figures break out to 52rem**, centred on the measure, collapsing back on narrow screens. A
  1366px screenshot rendered at 544px is unreadable, which is the only reason the breakout
  exists. Wide content escapes the measure; prose never does.
- **One accent** (`--accent`, a burnt orange). Dark mode is a full token swap in
  `assets/css/main.css`; anything new needs a value in both palettes.
- **No cards, no shadows, no gradients, no scroll-triggered animation.** Dustin flagged the
  AI-portfolio tells directly: gradient hero, emoji section headings, `rounded-2xl shadow-lg`
  card grids, fake stat counters, centered everything, "passionate developer" copy, bullet soup.
  Scroll fade-ins belong on that list too — they read as template and they delay content.
- **Tailwind is not an upgrade here.** It is the shortest path to exactly the card-grid look
  above. The hand-written CSS is an asset. Astro over Jekyll is a real improvement, but only
  worth the migration if this grows a blog or many more pages.

## Screenshots

`assets/img/` is synthetic-data-only, without exception. The three tools are employer work and
their real inputs are real client data.

The pipeline lives in career-hub because it depends on private repos:

- `../career-hub/scripts/shoot_clean.py` — the quoting app. Wraps its shoot tool and rewrites
  every fee, legal note and item name to invented values first. **A naive shoot leaks real
  pricing**; read the 2026-08-28 entry in `../career-hub/workflow/LOG.md` before touching it.
- `../career-hub/scripts/shoot-offline-tools.py` and `gen-billing-demo.js` — the label maker and
  the billing analyzer. Generates synthetic workbooks and drives the real apps.
  **It blanks every `<img>` before shooting**, because the label preview renders the employer
  logo. Keep that step.

Deliberately not shipped: any screenshot with a visible fee column. The figures in them are
invented, but a stranger reading a picture cannot tell an invented rate from a real one.

## Adding a project

Drop a `.md` in `projects/`. Front matter: `title`, `year`, `role`, `stack`, `code`, `summary`.
The `project` layout applies automatically via `_config.yml`. Add an entry to the work list in
`index.md`. Prose in Markdown; `<figure>` blocks in raw HTML with a real `alt` and a
`figcaption`. Alt text is published text, so the editorial rules apply to it too.

## Where the private context lives

`../career-hub/` — read on demand, do not load it all:

| Need | Read |
| --- | --- |
| Task status, what's next | `workflow/STATE.md` |
| Why a decision was made | `workflow/LOG.md` (append-only, newest at the bottom) |
| Who Dustin is, employment facts, guardrails | `HANDOFF.md` |
| The About page's source material | `interview-prep/about-grill-transcript.md` |
| Deep detail on the quoting app | `reference/quote-generator-deep-dive.md` |

Site work is tracked in `TODO.md` **here**. Everything else (resume, LinkedIn, job search) is
tracked in career-hub. When a site task lands that unblocks something over there, say so rather
than editing both.
