# dustinJ15.github.io

Personal site for [Dustin Jones](https://github.com/dustinJ15), software engineer, Denver.
Astro, Tailwind v4, static output, deployed to GitHub Pages.

Working notes for anyone (or any agent) editing this repo are in **`CLAUDE.md`**. The site
checklist is in **`TODO.md`**.

## Local

```bash
npm install
npm run dev      # dev server
npm run build    # static build to dist/
npm run verify   # the gate: astro check, build, then a Playwright sweep of every route
```

`npm run verify` is the one command that says whether the site is broken. It writes screenshots to
`.verify/` for a human to look at, which is a deliverable of the gate rather than a substitute
for it.

## Structure

```
src/pages/               one file per route, plus projects/[id].astro
src/layouts/             BaseLayout: head, header, skip link, footer, motion boot
src/components/          PageTitle, Outcome, Metrics
src/content/projects/    one markdown case study per project
src/content.config.ts    the zod schema; the source of truth for project metadata
src/styles/global.css    the token contract, mapped into Tailwind with @theme inline
src/scripts/motion.ts    GSAP and Lenis, plus the reduced-motion and teardown contract
src/assets/img/          portrait, plus screenshots from synthetic data only
scripts/verify.py        the gate, including the per-route expectations table
```

## Adding a project

Drop a `.md` file in `src/content/projects/`. The schema in `src/content.config.ts` rejects
malformed front matter at build time. The home page work list and the case-study page both read
the collection, so there is no second place to update. Then add the route's row to `EXPECTATIONS`
in `scripts/verify.py`.

## Before publishing anything

Three of the four case studies describe tools built at Frontage Laboratories. Naming the employer
is fine; describing their internals is not. No pricing or margin, internal identifiers, study
IDs, client names, hostnames, IPs, or coworker names may appear on the site or inside an image.
`rental-pipeline` is separate work with its own client data, and the same rules apply.

Run the screening script before every publish. It lives outside this repo on purpose, so the list
of strings being screened for is never itself published:

```bash
../career-hub/scripts/screen.sh .
```

It screens file names as well as contents, and it **cannot read a PNG**. Every image has to be
opened and looked at by a human or a model that can see it. `src/assets/img/` is synthetic data
only.
