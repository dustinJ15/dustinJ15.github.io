---
title: Rental Pipeline
order: 4
year: 2026
role: Sole developer
stack:
  - Python
  - Docker
  - pandas
code:
  label: rental-pipeline-public
  href: https://github.com/dustinJ15/rental-pipeline-public
summary: >-
  Four property management systems, four report formats, and files that lied about what they
  were. Sixteen parsers into one schema.
tagline: >-
  Four property management systems, four report formats, and files that lied about what they
  were. Sixteen parsers into one schema.
metrics:
  - value: "16"
    label: parsers into one schema
  - value: "4"
    label: source systems
---

A property management firm ran four different systems: Yardi, ResMan, Entrata, and RealPage. It
pulled operational reports out of all four and wanted them in one place for BI dashboards. Four
vendors, four report types each, and no two agreeing on what a spreadsheet is.

I built a Dockerized Python ETL pipeline: sixteen parsers, one normalized schema per report type.

<figure class="diagram" data-reveal>
<svg class="d-svg" viewBox="0 0 560 640" role="img" aria-labelledby="pipeline-shape-title" aria-describedby="pipeline-shape-desc">
<title id="pipeline-shape-title">Sixteen parsers converging on one schema</title>
<desc id="pipeline-shape-desc">A column of sixteen blocks, set as four groups of four, runs down the left. A line leaves each block and all sixteen converge on a single point, which feeds one bordered block on the right: the normalized schema every consumer downstream reads.</desc>
<g aria-hidden="true">
<rect class="d-tile" x="20" y="60" width="88" height="22" />
<rect class="d-tile" x="20" y="92" width="88" height="22" />
<rect class="d-tile" x="20" y="124" width="88" height="22" />
<rect class="d-tile" x="20" y="156" width="88" height="22" />
<rect class="d-tile" x="20" y="200" width="88" height="22" />
<rect class="d-tile" x="20" y="232" width="88" height="22" />
<rect class="d-tile" x="20" y="264" width="88" height="22" />
<rect class="d-tile" x="20" y="296" width="88" height="22" />
<rect class="d-tile" x="20" y="340" width="88" height="22" />
<rect class="d-tile" x="20" y="372" width="88" height="22" />
<rect class="d-tile" x="20" y="404" width="88" height="22" />
<rect class="d-tile" x="20" y="436" width="88" height="22" />
<rect class="d-tile" x="20" y="480" width="88" height="22" />
<rect class="d-tile" x="20" y="512" width="88" height="22" />
<rect class="d-tile" x="20" y="544" width="88" height="22" />
<rect class="d-tile" x="20" y="576" width="88" height="22" />
<path class="d-wire" d="M108 71 C 236 71 248 329 366 329" />
<path class="d-wire" d="M108 103 C 236 103 248 329 366 329" />
<path class="d-wire" d="M108 135 C 236 135 248 329 366 329" />
<path class="d-wire" d="M108 167 C 236 167 248 329 366 329" />
<path class="d-wire" d="M108 211 C 236 211 248 329 366 329" />
<path class="d-wire" d="M108 243 C 236 243 248 329 366 329" />
<path class="d-wire" d="M108 275 C 236 275 248 329 366 329" />
<path class="d-wire" d="M108 307 C 236 307 248 329 366 329" />
<path class="d-wire" d="M108 351 C 236 351 248 329 366 329" />
<path class="d-wire" d="M108 383 C 236 383 248 329 366 329" />
<path class="d-wire" d="M108 415 C 236 415 248 329 366 329" />
<path class="d-wire" d="M108 447 C 236 447 248 329 366 329" />
<path class="d-wire" d="M108 491 C 236 491 248 329 366 329" />
<path class="d-wire" d="M108 523 C 236 523 248 329 366 329" />
<path class="d-wire" d="M108 555 C 236 555 248 329 366 329" />
<path class="d-wire" d="M108 587 C 236 587 248 329 366 329" />
<circle class="d-node" cx="366" cy="329" r="5" />
<path class="d-out" d="M374 329 H 394" />
<path class="d-node" d="M392 322 L401 329 L392 336 Z" />
<rect class="d-box" x="401" y="269" width="139" height="120" />
<path class="d-row-key" d="M417 297 H 471" />
<path class="d-row" d="M417 317 H 524" />
<path class="d-row" d="M417 337 H 524" />
<path class="d-row" d="M417 357 H 524" />
</g>
<text class="d-label" x="20" y="34">Sixteen parsers</text>
<text class="d-label d-label-out" x="540" y="250" text-anchor="end">One schema</text>
</svg>
<figcaption>The shape of the job. Every input arrives in its own format and everything downstream reads one.</figcaption>
</figure>

## What the files were

The interesting part of an ETL job is never the transformation. It's what arrives.

- **HTML wearing an `.xls` extension.** Several exports were HTML tables that Excel opens
  helpfully enough that nobody had ever noticed.
- **Merged-cell headers**, so the column a value belongs to isn't the cell above it.
- **Status blocks embedded mid-table**, splitting one logical table into several physical ones.

> Four vendors, four report types each, and no two agreeing on what a spreadsheet is.

## Not trusting the run

A pipeline that runs unattended has to be able to say whether it worked:

- **File fingerprinting**, so a re-dropped file doesn't get ingested twice.
- **Configurable row-count validation**, so a report that suddenly has a tenth of its usual rows
  fails the run rather than passing as a small day.
- **Per-run ingestion logging**, so a wrong number downstream can be traced to the run that
  produced it.
- **Unit matching against a master property index**, reaching 96–99% match rates across systems
  that each name the same unit differently.

Computed KPI fields such as days-to-complete, AR aging buckets and days vacant are derived in the
pipeline rather than in each dashboard, so every consumer gets the same definition.
