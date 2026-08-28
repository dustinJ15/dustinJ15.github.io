# dustinJ15.github.io

Personal site for [Dustin Jones](https://github.com/dustinJ15) — software engineer, Denver.
Jekyll, hand-written CSS, no theme and no framework.

Working notes for anyone (or any agent) editing this repo are in **`CLAUDE.md`**. The site
checklist is in **`TODO.md`**.

## Local preview

Ruby 4.0 cannot install Jekyll locally (`http_parser.rb` won't compile), so build in a container:

```bash
podman run --rm -v "$PWD":/srv/jekyll:Z -w /srv/jekyll docker.io/jekyll/jekyll:4 jekyll build
cd _site && python3 -m http.server 8899
```

`bundle exec jekyll serve` works anywhere Jekyll installs cleanly.

## Structure

```
_config.yml            site config; no theme
_layouts/              default.html, project.html
assets/css/main.css    all styling, hand-written, ~330 lines
assets/img/            portrait, plus screenshots from synthetic data only
index.md               landing page
projects/*.md          one case study per project
process.md             the agentic development workflow
about.md               background
```

## Adding a project

Drop a `.md` file in `projects/`. Front matter: `title`, `year`, `role`, `stack`, `code`,
`summary`. The `project` layout is applied automatically. Then add an entry to the work list in
`index.md`.

## Before publishing anything

Three of the four case studies describe tools built at Frontage Laboratories. Naming the employer
is fine; describing their internals is not. No pricing or margin, internal identifiers, study
IDs, client names, hostnames, IPs, or coworker names may appear on the site or inside an image.
`rental-pipeline` is separate work with its own client data — the same rules apply.

Run the screening script before every publish. It lives outside this repo on purpose, so the list
of strings being screened for is never itself published:

```bash
../career-hub/scripts/screen.sh .
```

It screens file names as well as contents, and it **cannot read a PNG**. Every image has to be
opened and looked at by a human or a model that can see it. `assets/img/` is synthetic data only.
