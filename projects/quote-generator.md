---
title: Quote Generator
year: 2026
role: Sole developer
stack: Flask, SQLite, openpyxl, ReportLab, Playwright, GitHub Actions, Mergify
code: Private — employer work
summary: >-
  Preparing a client quote took hours of manual Excel work. Now an intake form feeds a rules
  engine that pre-populates a draft, and it's a five-minute review.
---

<p class="note">
<strong>DRAFT — not ready to publish.</strong> The facts below are verified from the repository.
The reasoning sections marked <strong>[GRILL]</strong> need Dustin's actual thinking, not a
plausible reconstruction of it. Run <code>/grill-me</code> against this page, then rewrite.
Delete this note before the site goes live.
</p>

Quoting a clinical study at a contract research lab meant building a workbook by hand: pick the
line items, work out kit and shipping quantities, apply the right rates, produce a cost estimate,
a payment schedule, and a test schedule. Hours per quote, every quote, and the person doing it
was the constraint.

<div class="outcome">
  <p><span class="before">Hours of manual workbook assembly, per quote</span></p>
  <p><strong>A five-minute review of a pre-populated draft.</strong></p>
</div>

## How it works

An **intake form** starts a quote. There are three ways in: an internal specialist fills it
directly, or a client gets a single-use link that expires in seven days and their submission
lands in a proofreading queue before it becomes a draft.

The intake answers feed a **rules engine**. Line items carry their own auto-select rules, written
as [json-logic](https://jsonlogic.com/) and evaluated against a controlled vocabulary of intake
answers, so the set of line items on a quote is derived rather than remembered. Kit and shipping
quantities are computed from the study design. The rules live in the database and are editable
from an admin page — changing what auto-selects doesn't require a deploy, or an engineer.

What comes out is a **draft quote**, not a blank form. The reviewer's job becomes checking a
document instead of building one.

**Generation** produces an Excel workbook — cost estimate, payment schedule, test schedule,
version history, and an edit-history audit sheet — plus an optional client-facing PDF. Once a
quote is awarded it's frozen, and changes go through a three-phase change-order wizard that
applies against the frozen snapshot and shows every difference as *was → now*.

Six roles, each seeing a different slice: admin, proposal specialist, project manager, business
development, and two elevated variants.

**[GRILL]** — Why a rules engine instead of hardcoded logic? Who actually edits the rules now?
Did anyone use the admin page, or did it stay yours?

## Choices worth defending

**No frontend framework.** Vanilla JavaScript, no build step, no CDN, no `node_modules` in the
served app. **[GRILL]** — was this a constraint you were handed, or a call you made?

**No ORM.** Raw `sqlite3` with hand-written versioned migrations.
**[GRILL]** — why?

**A rules engine at all.** Storing behavior as data means a non-engineer can change it, at the
cost of being able to express only what the rule format supports, and of harder debugging when
a rule is wrong.

## Making it safe to move fast

I was the only developer, working in eight weeks, on something that would produce client-facing
pricing documents. So most of the engineering went into being able to trust the changes.

**One command.** `check.py` runs pytest, flake8, mypy, bandit, and the JavaScript tests. CI runs
*exactly that command* — so "green locally" means "green in CI," and there is no second, subtly
different definition of correct.

**870 tests**, across 43 unit files, 14 Playwright browser end-to-end tests, and 6 zero-dependency
`node --test` files. The suite ended up larger than the application. Fast tests run in parallel
by default; the browser tests are marked and excluded from the default run because they share one
browser and have to run serially.

**A merge queue.** Every change rebased onto main and re-tested before landing, on a Python 3.12
and 3.14 matrix.

Over eight weeks: **537 commits, 324 pull requests, 155 merged.**

## The week the merge queue stopped

The CI matrix published its results as `check (3.12)` and `check (3.14)`. The merge queue was
waiting on a status context named plain `check` — which, it turned out, had never existed. Nothing
could merge, and nothing was broken.

The fix was an aggregator job that reports the bare `check` context. The part I'm actually pleased
with is `tests/test_ci_contract.py`: a test that asserts the CI job naming can't drift again. The
CI configuration became something the test suite has an opinion about.

Then, on 6 August, GitHub Actions had an incident and webhook delivery dropped to roughly 15%.
The merge queue's check timeout was derived rather than set — about nine minutes — and under
delayed webhooks that cascaded into queue-wide failure. It's now pinned at 45 minutes, with a
comment explaining why, because the next person to find that number should not have to rediscover
the outage.

**[GRILL]** — how long was the queue actually stuck? How did you work out what was wrong?

## Built by agents, reviewed by a human

The repository's own `CLAUDE.md` says it outright: *"This repo is written by agents and reviewed
by a human."* Most of the lines were written by an agent working from a plan I wrote, and the
interesting engineering is the harness that makes that safe — the plan/execute split, the claim
files, the gate every change has to pass. That has [its own page]({{ '/process/' | relative_url }}).

<p class="note">
Built for an employer, so the code stays private. Everything here describes the engineering —
no pricing, no client data, no infrastructure detail.
</p>
