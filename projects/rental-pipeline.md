---
title: Rental Pipeline
year: 2026
role: Sole developer
stack: Python, Docker, pandas
code: <a href="https://github.com/dustinJ15/rental-pipeline-public">rental-pipeline-public</a>
summary: >-
  Four property management systems, four report formats, and files that lied about what they
  were. Sixteen parsers into one schema.
---

A property management firm pulled operational reports out of four different systems — Yardi,
ResMan, Entrata, and RealPage — and wanted them in one place for BI dashboards. Four vendors,
four report types each, and no two agreeing on what a spreadsheet is.

I built a Dockerized Python ETL pipeline: sixteen parsers, one normalized schema per report type.

## What the files actually were

The interesting part of an ETL job is never the transformation. It's what arrives.

- **HTML wearing an `.xls` extension.** Several exports were HTML tables that Excel opens
  helpfully enough that nobody had ever noticed.
- **Merged-cell headers**, so the column a value belongs to isn't the cell above it.
- **Status blocks embedded mid-table**, splitting one logical table into several physical ones.

## Not trusting the run

A pipeline that runs unattended has to be able to say whether it worked:

- **File fingerprinting**, so a re-dropped file doesn't get ingested twice.
- **Configurable row-count validation** — a report that suddenly has a tenth of its usual rows is
  a failure, not a small day.
- **Per-run ingestion logging**, so a wrong number downstream can be traced to the run that
  produced it.
- **Unit matching against a master property index**, reaching 96–99% match rates across systems
  that each name the same unit differently.

Computed KPI fields — days-to-complete, AR aging buckets, days vacant — are derived in the
pipeline rather than in each dashboard, so every consumer gets the same definition.

<p class="note">
The working repo contains real client data and stays private.
<a href="https://github.com/dustinJ15/rental-pipeline-public">rental-pipeline-public</a> is the
sanitized version, with synthetic sample data.
</p>
