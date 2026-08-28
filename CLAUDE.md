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
# Build. Ruby 4.0 cannot install Jekyll locally (http_parser.rb won't compile), so use podman:
podman run --rm -v "$PWD":/srv/jekyll:Z -w /srv/jekyll docker.io/jekyll/jekyll:4 jekyll build

# Preview the built output
cd _site && python3 -m http.server 8899

# Screen (from the repo root)
../career-hub/scripts/screen.sh .
```

There is no test suite. The QA loop is: build, screen, grep the built `_site/` by hand (it is
excluded from the screen by design), click every link, and check 375px and 1440px for horizontal
scroll. Measure that rather than eyeballing it — compare `document.documentElement.scrollWidth`
against `clientWidth` on every page at both widths.

There is a Playwright in `~/sync/code/work/quote-generator/.venv/bin/python` if you need to drive
a browser. Nothing is installed system-wide.

## Design decisions, and why

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
