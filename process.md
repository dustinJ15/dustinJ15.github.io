---
layout: default
title: Process
permalink: /process/
description: >-
  How I work with agentic coding tools — the plan/execute split, claim files, and the
  verification gate that makes machine-written code safe to merge.
---

# How I work

I use agentic coding tools heavily. Most of the lines in my recent projects were not typed by me.

I think the honest version of that is more interesting than either of the dishonest ones. The
work I actually do is designing the harness — the specs, the gate, the isolation, the honesty
rules — that makes what a machine writes safe to merge. The bottleneck stopped being how fast
code gets written a while ago. It's whether you can trust it.

## The chain

I adapted this from [Matt Pocock's skills](https://github.com/mattpocock/skills), and it's a
sequence of separate sessions rather than one long conversation:

<div class="scroll-x" markdown="1">

| Step | What happens |
| --- | --- |
| `/grill-me` | A design interview. Thirty to eighty questions, one at a time, until the idea stops being vague. |
| `/to-spec` | The interview becomes a written spec. |
| `/to-tickets` | The spec becomes tracer-bullet tickets with explicit blocking edges. |
| `/implement` | One ticket: tests first, then the gate, then review, then commit. |
| `ralph-once.sh` | The loop, supervised — one ticket at a time, watched. |
| `afk-ralph.sh` | The loop, unattended, against the remaining tickets. |

</div>

My adaptation drops the issue tracker. Specs and tickets are markdown under `specs/<slug>/`,
committed alongside the code, so the reasoning arrives in the same diff as the change.

The grilling step is the one I'd keep if I could only keep one. Most bad output traces back to a
plan that was vague in a way nobody noticed, and being asked eighty questions is an efficient way
to find out you don't actually know what you want.

## What I learned by it going wrong

**A completion claim is not evidence.** An agent will report a task as done, sincerely, and be
wrong. So the rule in my repos is that a claim of completion without the command output behind it
doesn't count. That's why there's one command — `check.py` — that runs the whole gate: tests,
linting, type checking, security scan. Not because a human couldn't run four commands, but
because "green" needs a single unambiguous definition that both a person and a machine can reach.

**Two sessions will collide.** On one project, two sessions worked the same checkout for twenty
minutes before either noticed. Plans are now claimed atomically before any work starts —
`( set -o noclobber; : > <plan>.claim )`, which either succeeds or fails and cannot do both —
and execution happens in a git worktree, so two sessions can't share a working tree at all.

**Planning and doing should not share a session.** A session that has been writing code is
invested in the code it wrote. So planning happens in one session that writes only a plan file
and touches nothing else, then the context is cleared, and a different session executes it. The
plan has to be good enough to hand to a stranger, because it is being handed to one.

**Be honest about what you actually verified.** The defect backlog on my largest project grades
every entry: **CONFIRMED** (a human saw it), **AGENT-VERIFIED** (a machine reproduced it), or
**REPORTED** (someone said so). Without that, a plausible-sounding report and a reproduced bug
look identical three weeks later.

## Where it's been used

**[claude-dotfiles](https://github.com/dustinJ15/claude-dotfiles)** — the skills themselves,
installable, synced across machines.

**Label Maker** — the first real use. `specs/` and eleven tickets, and the commit log reads
"Ticket 01" through "Ticket 11." The workflow leaves fingerprints in git, which is a nice
property when someone asks how something was built.

**[Quote Generator]({{ '/projects/quote-generator/' | relative_url }})** — where it had to hold
up under production pressure: 537 commits and 155 merged pull requests in eight weeks, every one
through the gate, behind a merge queue, with a test suite larger than the application.

## The obvious objection

*If an agent writes the code, what exactly do you do?*

I decide what to build and why, and that turns out to be most of it. I write the spec that makes
a vague idea buildable, design the tests that define correct, build the gate that makes the
answer unambiguous, and review every diff before it merges. When the merge queue stalled for a
reason nothing reported, no agent found that. I did.

I can also write the code. I've done it the other way, on a multiplayer game engine in C with
hand-rolled netcode, and I'd rather have both skills than pick a side.
