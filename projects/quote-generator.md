---
title: Quote Generator
year: 2026
role: Sole developer
stack: Flask, SQLite, openpyxl, ReportLab, Playwright, GitHub Actions, Mergify, nginx
code: Private — employer work
summary: >-
  Winning lab work started with a twenty-to-thirty-five-email thread and ended with a specialist
  spending a day and a half building a workbook by hand. I replaced the thread with a record and
  the workbook with a system.
---

A contract research lab quotes a clinical study before it wins it. Getting to a quote meant a
business development lead extracting the specifics from the client over email — how many sites,
in which countries, which assays, what gets collected and shipped and stored, what isn't needed
at all. I was told those threads ran **twenty to thirty-five messages**, and I saw plenty of them.

Then that thread got handed to a proposal specialist, who built a pricing workbook from it by
hand. **About a day and a half per quote.** The team was trying to write thirty a month and
couldn't get there. And most quotes never become contracts — so the majority of that effort was
spent on work that would never be billed.

The failure I kept watching wasn't that the handoff was slow. It was that the handoff was
*incomplete*. Something would be missing — a country's site count, whether a sample type was
frozen or ambient — and the only place that answer existed was somewhere in a thread the
specialist couldn't search and hadn't been part of. So the extraction started over.

<div class="outcome">
  <p><span class="before">A twenty-to-thirty-five-email thread, retyped into a workbook by hand</span></p>
  <p><strong>A structured record the specialist reviews and decides on.</strong></p>
</div>

By the time I left, specialists told me it had cut their workload substantially. I won't put a
number on that one — nobody measured it, and the honest version is better than a made-up figure.
The day-and-a-half figure is what I was told on my first day; the improvement is what they told
me on my last.

## A thread is not a data structure

The client now fills in the intake themselves, through a single-use link that expires after a
week. Seven sections, and it can't be submitted half-finished. It lands on the business
development lead's dashboard, who reviews it, fills in the internal fields the client never
sees, and releases it to a specialist.

<figure>
  <img src="{{ '/assets/img/quote-intake-form.png' | relative_url }}"
       alt="A seven-section web intake form covering contact details, study details, per-region site counts, sample types, laboratory testing, optional services and attachments.">
  <figcaption>The client-facing intake. Seven sections, one single-use link, and it cannot be submitted half-finished. Top of the form; it continues for three more sections. Screenshot from a demo instance seeded with invented data.</figcaption>
</figure>

What the specialist opens is not a summary of a conversation. It's a **draft quote**. The line
items the study actually needs are already selected, quantities are already derived, and the kit
and shipping maths is already done. Their job is to check a document and make the calls that need
judgment — not to assemble one.

<figure>
  <img src="{{ '/assets/img/quote-builder-draft.png' | relative_url }}"
       alt="The quote builder: study information at the top, read-only derived kit and sample calculations, collapsible line-item groups, editable legal notes, and a running total in a sidebar.">
  <figcaption>What the specialist opens is a draft, not a summary. The kit and sample arithmetic above the line items is derived from the intake, and the line-item groups below it expand in place. Screenshot from a demo instance seeded with invented data.</figcaption>
</figure>

The Excel generator underneath all this was done in the first few days. It was the easy part, and
by a wide margin. Everything that took the rest of the summer was the part nobody thinks about
when they hear "it makes a spreadsheet."

## What actually took the summer: custody

The workbook wasn't the problem. The problem was that a quote passes through several people who
don't sit together, and in the old process nothing owned it. Every stage was somebody attaching a
file to an email and hoping the recipient had the current one.

So the system's real job is **custody** — at every moment, one clear answer to who holds this,
what they can change, and what happens when they let go.

**Opening the builder is a handoff, not a page load.** The moment a specialist opens a quote, one
write claims it *and* flips the business lead's dashboard from "sent to proposal specialist" to
"drafting in progress" — and closes the lead's ability to keep editing the intake underneath
them. The claim and the signal are the same event, so they cannot disagree. The check runs inside
the transaction, so a lead who saves at the same instant loses cleanly rather than silently
winning.

**Sending work back is two different things, deliberately.** Before a client signs, a business
lead asking for a revision *flags* the quote and lets the specialist decide when to reopen it —
the quote is still theirs. After a client signs, a kicked-back change order is a *direct push*
into the drafting queue, and it leaves the specialist's existing draft untouched so they resume
rather than restart. Same authority check, deliberately separate fields, so the two can never
entangle. Revisions and change orders are two sides of one coin, and the difference between them
is entirely about whether a client has signed.

**One function answers whose desk it is on.** It takes a quote and returns one of three answers.
The attention queue, the row highlighting, the "waiting on you" filter and the reminder digest all
read that same answer — so they agree by construction, rather than by four separate pieces of
logic that happen to match today.

<figure>
  <img src="{{ '/assets/img/quote-dashboard-lead.png' | relative_url }}"
       alt="A business development dashboard with an attention queue of three quotes, each showing status, outcome buttons and a due date, above a full list of that user's quotes.">
  <figcaption>The business lead's view. The attention queue, the row highlighting and the reminder digest all read the same answer to the question of whose desk a quote is on.</figcaption>
</figure>

An award freezes the quote. What was sold is snapshotted once, and every route that could
otherwise modify it refuses — checked on the way in for a clear error, and again inside the
transaction, which is the check that actually holds. After that, amendments go through change
orders, which baseline against exactly what was signed rather than against whatever the quote
looks like now.

## Building the customer a seat, not a page

I was an intern with an end date. Anything I hardcoded would need an engineer to change after I
left, and there was not going to be an engineer.

So the admin surface is not a settings page — it is a whole role. An administrator can edit the
catalogue and its pricing, change **which line items auto-select and the arithmetic that fills
their quantities** through a visual editor with no formula typing, change what the client-facing
intake form asks, edit the legal footnotes printed on every quote, manage users and roles, and
work the internal cost and markup figures. None of it requires a deploy, a migration, or me.

That is the part I would defend hardest, because it is the part that got used. My manager, the
company's senior vice-president, and the colleague I ran standups with all worked in that console
directly. The rules that decide what a quote contains stopped being something only a developer
could change.

<figure>
  <img src="{{ '/assets/img/quote-admin-roles.png' | relative_url }}"
       alt="A user administration table listing six accounts, each with a role selector showing Admin, Business Development, Project Manager, Proposal Specialist, Super BD team lead and Super PM team lead.">
  <figcaption>Six roles, editable by an administrator. The roles are less a security boundary than a model of how the work actually moves between people.</figcaption>
</figure>

There is a real cost to storing behaviour as data: you can only express what the format supports,
and a wrong rule is harder to debug than wrong code. I took that trade knowingly. The compensating
move is that the editor can only build rules the system will accept — variables that cannot be
known yet are refused with a sentence explaining why, rather than saved as a rule that would
silently never fire.

## Choices worth defending

**No frontend framework, no build step, no CDN.** For most of the project the application was
destined for an internal Windows VM I did not control, where every dependency was a request into
someone else's queue. So I built something that needed almost nothing installed. The JavaScript
carrying real logic is isolated into modules with no DOM access, so it is unit-tested directly
rather than through a browser.

That constraint paid off in a way I had not planned. When we finally got a Linux server instead, I
had to port the whole application and stand up production in the **last week of the internship** —
and there was nothing to install.

**No ORM.** Raw SQL with hand-written versioned migrations. Not a principle — the queries are
simple, and an ORM's value shows up on complex relational models. This is not one. It was not
worth it.

**I owned the whole stack.** Front end, web server, application server, the app itself, and the
database. IT provided a DNS record.

## Running five agents without it being reckless

Most of this code was written by AI agents working from plans I wrote. That is the part of the
project I would most want to talk through, because how it went is not how people assume.

It started as one agent on one task, with daily standups. The backbone shipped fast, the
stakeholders saw the pace, and the scope grew — then grew again. So I went parallel, several
agents on separate tickets at once, and I had **another agent doing the rebasing and opening the
pull requests.**

That was the wrong answer, and recognising it is the thing I am actually proud of. Agents pushing
to a shared branch thrash: whoever lands first moves the target, so everyone else is instantly
stale. That is a livelock — a *serialisation* problem, not a code problem. A better model does not
fix a livelock, it just runs an expensive one. I had reached for a smarter agent when the answer
was a dumber, deterministic one.

I had learned the actual solution in a classroom. Continuous integration and a merge queue: every
change tested against the state it will really land in, one at a time, automatically. I swapped an
LLM for a bot and got a better result for less money.

After that I could run five or six agents at once without it being reckless, because nothing
merged without passing the same gate. **One command runs the whole gate** — tests, linting, type
checking, security scanning — and CI runs that exact command, so "green on my machine" and "green
in CI" cannot drift apart. There is only one definition of green.

Over eight weeks: **537 commits, 324 pull requests, 155 merged. 1,512 unit tests, 38 browser
tests, and 141 more covering the pure JavaScript.** The test suite ended up larger than the
application.

Two infrastructure failures are worth a sentence each. Splitting CI across two Python versions
renamed the status check the merge queue was waiting on, so nothing could merge for thirty-eight
minutes — the fix was a job that reports the expected name, plus a test that fails the build if
that contract ever drifts again. Separately, during a GitHub Actions outage the queue's timeout
was being derived from our own CI speed, which meant a *fast* pipeline got a *short* timeout —
shorter than the outage's backlog. The queue ejected its own head, which cancelled the checks it
was waiting for, and drained itself. It is now pinned to an explicit value, with a comment saying
why.

## Verification is the actual skill

When a machine writes most of the code, the interesting engineering is whatever makes its output
checkable. The repository's own instructions say it outright: this is written by agents and
reviewed by a human.

What that meant in practice is that I kept a ledger of every defect an agent reported, tagged by
whether it had been **reproduced** or merely **read off the source**. Several turned out to be
wrong — the code had been read correctly and the conclusion drawn from it was false. Chasing one
of those wrong reports uncovered two real bugs hiding behind it, one of which nobody had filed at
all.

I kept the wrong ones on the record instead of deleting them, because the reasoning is what stops
them being filed again. That habit — treating "we have not actually confirmed this" as a fact
worth writing down — is the thing I would bring to a team, more than any particular framework.

<p class="note">
Built for an employer, so the code stays private. Everything above describes the engineering —
no pricing, no client data, no infrastructure detail, and no code.
</p>
