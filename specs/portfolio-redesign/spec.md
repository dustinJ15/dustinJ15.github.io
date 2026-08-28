# Portfolio redesign: Obys direction, Jekyll to Astro

Status: agreed 2026-08-28. Phase 1 (three preview lanes) is complete and the direction is picked.
This spec covers everything after that pick.

---

## Problem Statement

The site is honest and the writing is good, and it looks like a document.

It is seven pages of hand-written CSS with no build step, no JavaScript, a hard 36rem text column
and no motion of any kind. It was built under a brief that said the design must never compete with
the writing, and it succeeded at that and at nothing else. Dustin's verdict on it is "super
boring," and he is right: a stranger landing on it has no reason to believe the person who built
it can make something people want to look at.

That matters because of who reads it. A recruiter skims. A hiring manager forms an impression in
seconds and then decides whether to read the argument underneath. The current site loses that
first exchange, and the case studies, which are the actual differentiator, never get read.

The old brief also produced real debts: dark mode has never been looked at on a screen, one case
study has no visual at all, the copy carries fifty em-dashes that Dustin reads as an AI tell, and
a quotation that anchors the About page is uncited and visually flat.

## Solution

Rebuild the site in Astro with Tailwind v4, in the **Obys direction**: near-black ground, a single
acid-lime accent, oversized display type, asymmetric layout, and real scroll choreography. Dark
only. The reference sites are recorded in CLAUDE.md so the intent survives this conversation.

The home page leads with a full-viewport display hero that assembles on load, a marquee of the
stack, and a horizontal work rail scrubbed by vertical scroll. The case studies get the same
chrome, a choreographed title, display section headings, full-bleed figures in dark browser
chrome, and large pull quotes, while the argument itself stays calm and readable. Impact goes
where it is free; restraint goes where it would cost reading.

Every word gets an editorial pass. The screenshots get re-shot at one consistent width, framed so
they read as intentional on a dark page, and served as WebP. The one case study with no visual
gets a diagram.

## User Stories

**The visitor**

1. As a first-time visitor, I want the home page to look deliberate within a second of landing, so that I believe the person who built it can build things worth looking at.
2. As a visitor, I want the opening line to tell me what this person does, so that I do not have to infer it from a project list.
3. As a visitor, I want to see the four pieces of work without scrolling past a wall of biography, so that I can judge quickly whether to read further.
4. As a visitor, I want each work entry to carry its year and stack, so that I can place it without opening it.
5. As a visitor, I want the motion to feel like craft rather than delay, so that I never wait on an animation to read something.
6. As a visitor on a phone, I want the display type to fit its line, so that words never break mid-word.
7. As a visitor, I want to reach any case study in one click from the home page, so that nothing is buried.
8. As a visitor, I want to know immediately that Dustin is available and how to contact him, so that acting on interest takes no searching.

**The recruiter and hiring manager**

9. As a recruiter skimming, I want each case study to state its before and after near the top, so that I get the outcome without reading the whole argument.
10. As a hiring manager, I want the case-study prose to set at a readable measure with no motion in the body, so that I can actually read the reasoning.
11. As a hiring manager, I want screenshots large enough to read, so that the interface being described is legible rather than decorative.
12. As a hiring manager, I want a quoted claim to be attributed, so that I can tell a sourced idea from an unsourced one.
13. As a hiring manager, I want the stack listed on a case study to match the stack listed on the home page, so that I do not have to reconcile two versions.
14. As a technical reader, I want a case study about a pipeline to show the pipeline, so that I understand the shape of the work without a UI to look at.
15. As a reader on a slow connection, I want the images to be modern formats and lazy, so that the page is usable before everything downloads.

**Accessibility and resilience**

16. As a visitor with prefers-reduced-motion set, I want the full content visible with no animation, so that the site is usable and nothing is stuck invisible.
17. As a keyboard user, I want a visible focus ring on every interactive element and a working skip link, so that I can navigate without a pointer.
18. As a screen-reader user, I want every figure to carry real alt text and decorative elements to be hidden, so that the page reads coherently.
19. As a visitor with low vision, I want all text to meet WCAG AA contrast, including the mono metadata the design leans on, so that nothing is unreadable by design.
20. As a visitor with JavaScript blocked, I want the page to render its content, so that a failed script never produces a blank page.
21. As a visitor on any width from 375px up, I want no horizontal scroll, so that the page does not slide under my thumb.

**Dustin as maintainer**

22. As Dustin, I want to add a case study by dropping one markdown file in, so that adding work does not mean touching layout.
23. As Dustin, I want project metadata to have one source of truth, so that the home page and the case study cannot disagree.
24. As Dustin, I want a single command that tells me whether the site is broken, so that "is this done" is not a judgement call.
25. As Dustin, I want no em-dashes anywhere in the copy, so that the writing does not read as machine-written.
26. As Dustin, I want the site never to describe employer internals, so that publishing it carries no risk to my job.
27. As Dustin, I want every screenshot to be synthetic, so that no client data is ever published.
28. As Dustin, I want nothing pushed or published without my say-so, per action, so that the least reversible steps stay mine.
29. As Dustin, I want the site to keep building while the migration is in progress, so that I am never left without a working site.

**A future agent**

30. As an agent picking this up cold, I want the design direction and its reference sites named in CLAUDE.md, so that I can see the intent rather than guess it.
31. As an agent, I want superseded rules marked as superseded, so that I do not follow a brief that has been inverted.
32. As an agent, I want the token contract documented, so that I add a colour in the one place it belongs.
33. As an agent, I want the verification gate to encode each page's expectations, so that I can tell whether my change broke something without opening a browser.

## Implementation Decisions

**Stack.** Astro 7 with static output, Tailwind v4 through the `@tailwindcss/vite` plugin, and
TypeScript. The `@astrojs/tailwind` integration is deprecated and must not be used. No React: the
site has no state, and Astro components plus vanilla TS islands cover every interaction. GSAP
(ScrollTrigger, SplitText) drives choreography, Lenis provides the smooth-scroll substrate, and
Motion covers spring micro-interactions. Fonts are self-hosted through Fontsource, which removes
the Google Fonts request that was the old site's only third-party dependency.

**Dark only.** There is no light palette and no theme toggle. The acid-on-black is the identity
and a light variant dilutes it. This halves the design surface and the verification matrix.

**The token contract.** Every colour, font and measure is a custom property on `:root`, mapped
into Tailwind through `@theme inline` so the utilities keep the `var()` reference rather than
baking a resolved value. Components never branch on theme and never hard-code a colour. This
shape came out of the Phase 1 prototype, where it let three visually unrelated lanes share one
component vocabulary:

```
:root {
  --bg: #090909;  --surface: #121212;  --line: #262626;
  --ink: #f4f4f0; --ink-soft: #918f88; --ink-faint: #8a8880;
  --accent: #d6ff4b; --accent-contrast: #090909;
}
@theme inline { --color-bg: var(--bg); /* ... */ }
```

`--ink-faint` carries all the mono metadata and sits at the WCAG AA floor. It must not be
darkened; Phase 1 found it failing at 3.65:1 before it was raised.

**Type.** Bricolage Grotesque Variable for display, Inter Variable for body, JetBrains Mono
Variable for metadata. Bricolage is a deliberate stand-in for Obys's unlicensable custom faces,
chosen because it carries both a width and a weight axis, which is what makes the hero settle from
condensed to full width on load. Swapping it for a static face removes that animation. The scale
is fluid and clamp-based throughout; the old site had no fluid type at all.

**Measure.** The 36rem column stops being a site-wide constant. Prose sections opt into a measure;
heroes, work lists and figures use the full viewport. Case-study body copy keeps a comfortable
measure because reading is what those pages are for.

**Content as the single source of truth.** Case studies are markdown in a content collection with
a zod schema. `stack` is an array, `code` is a structured label plus optional href, and `tagline`,
`outcome` and `metrics` are first-class fields. The home page work list and the case-study header
both read from the collection, so they cannot disagree. `metrics` values must be traceable to a
sentence in the case study; nothing invented.

**Home page.** Full-viewport hero whose display lines assemble character by character inside word
wrappers, with a width-axis settle. Marquee strip of the stack. Asymmetric About block. Horizontal
work rail pinned and scrubbed by vertical scroll on wide screens, degrading to a normal scroll on
narrow ones. Oversized contact block.

**Case studies.** The agreed treatment is Obys chrome with calm prose. Choreographed full-viewport
title carrying the project name, year, role and stack. The outcome before/after becomes a designed
component instead of a strikethrough with a border. Section headings become display moments that
reveal on scroll. Figures break full-bleed inside a dark browser-chrome frame. One or two lines per
study are pulled out as large display quotes. Paragraphs themselves stay at a readable measure with
at most a gentle fade; no line-by-line reveals, no pinning inside the argument.

**Motion policy.** Reduced motion wins, always, and it is a real fallback: every reveal's end state
is the default state, so disabling animation can never blank the page. Content is only hidden once
JavaScript has confirmed it can animate it back, which means a no-JS visitor sees everything.
Nothing scroll-triggered gates the first paint of body text. GSAP contexts and the Lenis instance
are torn down on Astro's before-swap event so view transitions cannot leak listeners or stack a
second smooth-scroll.

**Images.** Re-shot at one consistent viewport through the career-hub pipeline, which is the only
place they can be generated because it depends on private repos. The 2026-08-28 log entry must be
read before touching the quoting-app shoot: a naive shoot leaks real pricing. The image-blanking
step in the offline-tools shoot stays, because the label preview renders the employer logo. Nothing
with a visible fee column ships. Astro's image pipeline handles WebP and lazy loading. A figure
component wraps each screenshot in dark browser chrome. Rental-pipeline gets a hand-authored inline
SVG of sixteen parsers converging on one schema. During the overlap the images stay in the
Jekyll asset directory and Astro imports them from there, which its pipeline handles fine;
they move under src only when Jekyll is deleted, so no duplicate binaries enter git history.

**Copy.** A full editorial pass across all seven pages. Every em-dash goes. The Pragmatic Programmer
line on the About page becomes a properly attributed display pull quote rather than an uncited
sentence mid-paragraph. Alt text is published text and gets the same editorial rules.

**Deployment.** A GitHub Actions workflow builds and deploys to Pages. It is deliberately
manual-dispatch only until the Jekyll site is deleted, so that landing anything on main cannot
silently replace the live site. Nothing is pushed, no repo is created and Pages is not enabled
without asking, per action.

**Migration order.** Astro is built alongside Jekyll, which keeps building throughout. Jekyll is
deleted only in the final ticket, once every page has an Astro equivalent that passes the gate.

## Testing Decisions

**What makes a good test here.** This is a static content site: there is almost no pure logic to
unit-test, and the meaningful behaviour only exists in the rendered artifact. So tests assert what
a visitor receives from the built output, never how a component is implemented. A test that
asserted a class name or a component's internal structure would break on every design change while
catching nothing; a test that asserts "this page has one h1, four figures, and every figure has
non-empty alt text" survives a redesign and catches real regressions.

**One seam.** `npm run verify` is the single behavioural seam: Playwright driving the built output
over a local server. It already exists and was built during Phase 1, where it caught four real
bugs before any human looked at a screenshot. It runs every page at 375, 768 and 1440 and asserts:

- No horizontal scroll, measured as scrollWidth against clientWidth, never eyeballed.
- No console errors and no failed requests.
- WCAG AA contrast on every rendered text leaf, at the correct threshold for its size and weight,
  compositing alpha layers and converting oklab, because Tailwind's opacity modifiers compute to it.
- Every internal link resolves.
- With reduced motion forced, no element is left invisible.
- After a full scroll-through, every reveal has fired and no display line has wrapped.

It also writes screenshots for a human to look at, which is a deliverable of the gate, not a
substitute for it.

**Per-page expectations.** The seam gains a declarative expectations table: each route names what
must be true of it, in terms of rendered structure rather than implementation. A ticket adds its
rows and is complete when the gate passes with them. This is what makes tickets objectively
checkable instead of signed off by eye, and it stays one seam and one command.

**Gates that come free.** `astro check` covers types, and the content collection's zod schema
rejects malformed front matter at build time. These are existing seams and are preferred to new
ones. Front-matter drift is caught by the schema, not by a test.

**Prior art.** There is none in this repo; the old QA loop was manual and is described in
CLAUDE.md. The verification script written in Phase 1 is the prior art for everything that follows,
and its structure should be extended rather than duplicated.

**Not automated.** Whether the design is good. The gate is a floor, not a judge. Every new
screenshot must still be opened and looked at by a person, because the screen script cannot read a
PNG, and `screen.sh` must pass on the publishable surface before anything is committed.

## Out of Scope

- A light palette or a theme toggle. Dark only was decided; the token contract makes it cheap to add later.
- A blog, tags, search, pagination, or a CMS. Seven pages stay seven pages.
- Analytics, tracking, cookie banners, or any third-party script.
- Pushing, creating the repo, or enabling Pages. Those need per-action approval and are not part of this work.
- Changing anything in career-hub, including fixing the screen script's node_modules false positives.
- Re-shooting with anything other than synthetic data. There is no version of this where real client data is acceptable.
- Any screenshot showing a fee column, invented or not.
- Explaining the gap in the degree, or framing any of it as a career change. It is a return.
- Reintroducing the retired spreadsheet motif in any form.
- Restoring the deleted Chiang and Hybrid lanes.

## Further Notes

**Approval gates.** Three points hand control back: after the spec (here), after tickets are
generated, and before any push, repo creation, or Pages enablement. The last is per action, never
batched.

**The screen script and node_modules.** Now that the repo has a node_modules directory, running
`screen.sh` at the repo root returns hundreds of false positives from third-party code matching a
short screened token. The workaround is to screen the publishable surface, which is tracked files
plus untracked-not-ignored files, and which passes clean. Fixing the script itself is a career-hub
change and is out of scope here.

**Phase 1 is uncommitted.** The scaffold, tokens, the Obys preview, the verification harness and
the CLAUDE.md changes are in the working tree and not yet committed.

**No autonomous loop.** `ralph-init` has not been run here and should not be. There was no test
suite before this work, visual quality is not a gate a loop can evaluate, and the subjective
decision has already been spent. Tickets are implemented supervised.
