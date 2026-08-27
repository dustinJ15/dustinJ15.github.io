# dustinJ15.github.io

Personal site. Jekyll, hand-written CSS, no theme and no framework.

**Not deployed yet.** See `../career-hub/TODO.md` for the gated publish steps.

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
assets/img/            screenshots (synthetic data only)
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

The three tools described here were built for an employer. No pricing, internal identifiers,
hostnames, IPs, or coworker names may appear on the site or inside an image.

Run the screening script before every publish — it lives outside this repo on purpose, so the
list of strings being screened for is never itself published:

```bash
../career-hub/scripts/screen.sh .
```

Two pages carry visible **DRAFT** notes and must not ship until rewritten from a `/grill-me`
session: `about.md` and `projects/quote-generator.md`.
