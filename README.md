# dustinJ15.github.io

Personal site. Jekyll, hand-written CSS, no theme and no framework.

**Not deployed yet.** See `../career-hub/workflow/STATE.md` for the gated publish steps.

## Local preview

```bash
bundle install
bundle exec jekyll serve
# http://localhost:4000
```

## Structure

```
_config.yml            site config; no theme
_layouts/              default.html, project.html
assets/css/main.css    all styling, hand-written
assets/img/            screenshots (synthetic data only) — currently empty
index.md               landing page
projects/*.md          one case study per project
process.md             the agentic development workflow
about.md               background
```

## Adding a project

Drop a `.md` file in `projects/`. Front matter: `title`, `year`, `role`, `stack`, `code`,
`summary`. The `project` layout is applied automatically. Then add an entry to the work list
in `index.md`.

## Before publishing anything

Three of the four case studies describe tools built at Frontage Laboratories. Naming the
employer is fine; describing their internals is not. No pricing or margin, internal identifiers,
study IDs, client names, hostnames, IPs, or coworker names may appear on the site or inside an
image. `rental-pipeline` is separate work with its own client data — same rules apply.

Run the screening script before every publish — it lives outside this repo on purpose, so the
list of strings being screened for is never itself published:

```bash
../career-hub/scripts/screen.sh .
```

One page carries a visible **DRAFT** note and must not ship until rewritten from a `/grill-me`
session: `about.md`. (`projects/quote-generator.md` was rewritten in `feb96b5`; its DRAFT notice
and every `[GRILL]` marker are gone.)
