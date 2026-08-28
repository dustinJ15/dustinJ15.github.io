# 10: Delete Jekyll

**What to build:** The site becomes one site. Every page now has an Astro equivalent that passes
the gate, so the Jekyll layer comes out: its layouts, includes, config, Gemfiles, pages and build
output. The images move under the Astro source tree, which is safe now because the Jekyll copies
are going in the same change and no duplicate binaries enter git history.

The deploy workflow gets its push trigger. It has been manual-dispatch only so that landing
anything on main could not silently replace the live Jekyll site; that reason expires with this
ticket.

The gate's list of not-yet-migrated routes empties, because a 404 is no longer a "not built yet".

CLAUDE.md's design section is still marked superseded and still describes the old brief. It gets
rewritten to describe the site that now exists: the token contract and where a colour belongs,
the direction and its reference sites, the motion policy, the content collection as the single
source of truth for project metadata, and the gate as the way to tell whether a change broke
something. An agent picking this up cold should be able to read it and not follow an inverted
brief.

**Nothing is pushed, no repo is created and Pages is not enabled by this ticket.** Those need
Dustin's approval per action and are not part of this work. Flipping the workflow's trigger is a
file change; it is not a deploy.

**Blocked by:** 01, 02, 03, 04, 05, 06, 07, 08, 09.

**Status:** ready-for-agent

- [ ] All Jekyll files are removed: layouts, includes, config, Gemfiles, page sources and build
      output, plus the Jekyll-only entries in the ignore file.
- [ ] Images live under the Astro source tree and every page still renders them. No image exists
      in two places.
- [ ] The site builds clean and the gate passes on every route.
- [ ] The gate's not-yet-migrated route list is empty.
- [ ] The deploy workflow builds on push to the default branch, and the comment explaining why it
      was manual-only is gone.
- [ ] CLAUDE.md describes the site that exists: token contract, direction and references, motion
      policy, content collection as the single source of truth, and the verification gate. No
      section is left marked superseded.
- [ ] TODO.md reflects the finished migration and the remaining publish steps.
- [ ] Nothing was pushed, no repo was created and Pages was not enabled.
