# CLAUDE.md: working notes for this repo

**This file is public.** So is everything else here, the moment the repo goes up. Never write
employer internals, screening patterns, or personal detail into this repo. The private context
lives next door in `../career-hub/` (local-only git, no remote, ever) and is read on demand.

---

## What this is

Dustin Jones's portfolio. **Astro 7, static output, Tailwind v4 through `@tailwindcss/vite`,
TypeScript, no React.** Eight routes: home, process, about, four case studies and a 404.

Two things carry the site. The writing is the differentiator: the case studies argue rather than
list, and the quote-generator page admits an approach that failed and explains why the dumber fix
was right. The design is what buys the writing a reader: near-black ground, one acid-lime accent,
oversized display type and real scroll choreography. Impact goes where it is free. Restraint goes
where it would cost reading, so case-study prose stays calm and set at a measure.

The Jekyll site this replaced was deleted in ticket 10. Nothing here builds with Ruby any more.

## Hard rules

1. **Never push, create a repo, change visibility, or enable Pages without asking Dustin first,
   per action.** Not "once at the start". Each time.
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
4. **No em-dashes in anything Dustin reads.** He reads them as an AI tell. The site copy is
   clean as of ticket 08 and `npm run verify` fails on one, in alt text and meta descriptions
   as well as body copy. Removing one is never mechanical: rewrite the sentence so the
   punctuation is not missed.
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
  The route does not END on a screenful of nothing: the gap between the last painted thing in
  `main` and the footer is capped. That one is deliberately a *trailing* measurement, because
  the mid-page void a pinned section leaves in a full-page screenshot is the pin spacer holding
  the scrub distance, and is not empty to anyone who scrolls.
- The per-route expectations, from the `EXPECTATIONS` table at the top of `scripts/verify.py`.
  A row states what must be true of the page a visitor receives: heading counts, named sections,
  figure count, non-empty alt text, links that must be present, links that must be *reachable*
  and not merely in the DOM, copy that must appear. **A row
  never names a class, a component or a file**, so the table survives a redesign and still catches
  a regression. Adding a page means adding its row; a ticket is finished when the gate passes
  with its row in place.
- The em-dash check. It fails the build, and it reads everything the page publishes, not only
  what is painted: body text, alt text, captions, the tab title and the meta description.

The gate is a floor, not a judge. It cannot tell you whether the design is good, and the screen
script cannot read a PNG, so the screenshots it writes to `.verify/` still have to be opened and
looked at.

Playwright lives in `~/sync/code/work/quote-generator/.venv/bin/python`; `npm run verify` calls
it by that path unless `VERIFY_PYTHON` points at another interpreter with Playwright installed
(`VERIFY_PYTHON=/path/to/venv/bin/python npm run verify`). Nothing is installed system-wide.

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

Chosen 2026-08-28 and landed over tickets 02 to 11. Do not undo these casually.

**The token contract, and where a colour belongs.** Every colour, font and measure is a custom
property on `:root` in `src/styles/global.css`, mapped into Tailwind through `@theme inline` so
the generated utility keeps the `var()` reference instead of baking a resolved value. **A new
colour is added there and nowhere else.** Components read token names; they never hard-code a hex
value and never branch on theme. `--ink-faint` carries all the mono metadata and sits at the WCAG
AA floor: it must not be darkened, and the gate will catch you if it is.

**Dark only.** There is no light palette and no theme toggle. The acid-on-black is the identity
and a light variant dilutes it. A `dark:` variant exists as an escape hatch, but the semantic
tokens are the intended mechanism.

**Type.** Bricolage Grotesque Variable for display, Inter Variable for body, JetBrains Mono
Variable for metadata, all self-hosted through Fontsource, which is why the site has no
third-party network dependency at all. Bricolage carries both a width and a weight axis, and that
is what makes the hero settle from condensed to full width on load. Swapping it for a static face
removes the animation. The scale is fluid and clamp-based throughout.

**Measure.** The old site's 36rem column is no longer a site-wide constant: sections opt into
`--measure`. Heroes, work rails and figures use the full viewport. Case-study body copy keeps a
comfortable measure, because reading is what those pages are for.

**Motion policy**, in `src/scripts/motion.ts`, in order of importance:

1. Reduced motion wins. Nothing is hidden and nothing is scroll-jacked.
2. Content is never hidden before JavaScript has confirmed it can animate it back. The
   `data-motion="on"` flag is what arms the CSS that hides `[data-reveal]`, and it is set from
   JS, so a no-JS visitor sees the whole page. **Do not hide anything in static CSS.**
3. Everything is torn down on `astro:before-swap`, so a view transition cannot leak a
   ScrollTrigger or stack a second Lenis instance. Anything that scrolls the page
   programmatically goes through `scrollWindowTo`, or Lenis snaps it back.

Nothing scroll-triggered gates the first paint of body text.

**The content collection is the single source of truth for project metadata.**
`src/content/projects/*.md` with the zod schema in `src/content.config.ts`. The home page work
list, the case-study header and the `<head>` description all read from it, so `stack` cannot
disagree with itself the way the old front matter did against the hand-written list on the home
page. `metrics` values must be traceable to a sentence in the case study. Nothing invented.

**Case-study markdown stays plain markdown.** An image with a title becomes a captioned figure in
dark browser chrome, via the rehype plugin in `src/plugins/case-study-markdown.mjs`. Do not write
raw `<figure>` HTML into a case study; that is what the old site did and it could not be
optimised.

**The AI-portfolio tells are still banned.** Dustin named them: gradient hero, emoji section
headings, `rounded-2xl shadow-lg` card grids, fake stat counters, centred everything, "passionate
developer" copy, bullet soup. Scroll choreography is now the direction, but a generic fade-up on
every block is the template look and is not.

## Screenshots

`src/assets/img/` is synthetic-data-only, without exception. Astro's image pipeline optimises
everything there to lazy, responsive WebP; nothing is served from `public/`. The three tools are employer work and
their real inputs are real client data.

`public/` holds exactly two files and both are binaries the screen cannot read: the resume PDF
(built in career-hub with `build_resume.py general --no-phone`, no phone number) and `og.png`.
Open both before every publish.

The pipeline lives in career-hub because it depends on private repos:

- `../career-hub/scripts/shoot_clean.py`, the quoting app. Wraps its shoot tool and rewrites
  every fee, legal note and item name to invented values first. **A naive shoot leaks real
  pricing**; read the 2026-08-28 entry in `../career-hub/workflow/LOG.md` before touching it.
- `../career-hub/scripts/shoot-offline-tools.py` and `gen-billing-demo.js`, the label maker and
  the billing analyzer. Generates synthetic workbooks and drives the real apps.
  **It blanks every `<img>` before shooting**, because the label preview renders the employer
  logo. Keep that step.

Deliberately not shipped: any screenshot with a visible fee column. The figures in them are
invented, but a stranger reading a picture cannot tell an invented rate from a real one.

## Adding a project

Drop a `.md` in `src/content/projects/`. The schema in `src/content.config.ts` is the contract and
the build fails on a malformed front matter: `title`, `order`, `year`, `role`, `stack` (array),
`code` (label plus optional href), `summary`, `tagline`, optional `outcome` (before and after) and
optional `metrics`. Nothing else needs touching: the home page work list and `/projects/[id]/`
both read the collection.

Prose in plain Markdown. A screenshot is an image with a title, `![alt](../../assets/img/x.png
"The caption.")`, which the rehype plugin turns into a captioned figure in browser chrome. Alt
text and captions are published text, so the editorial rules apply to them, em-dashes included.

Then add the route's row to `EXPECTATIONS` in `scripts/verify.py` and run the gate.

## Where the private context lives

`../career-hub/`, read on demand. Do not load it all:

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
