---
layout: default
title: Work
---

<div class="hero">
  <img class="portrait"
       src="{{ '/assets/img/dustin-jones.jpg' | relative_url }}"
       srcset="{{ '/assets/img/dustin-jones-500.jpg' | relative_url }} 500w, {{ '/assets/img/dustin-jones.jpg' | relative_url }} 1000w"
       sizes="(max-width: 36rem) 7rem, 8.5rem"
       alt="Dustin Jones" width="1000" height="1190">
  <div class="hero-text">
    <p class="intro">I build full-stack applications and the pipelines that keep them reliable.</p>
    <p class="availability">
      <strong>Available now</strong> for part-time and contract work, Denver or remote.
      <a href="mailto:DBJ2297@gmail.com">DBJ2297@gmail.com</a>
    </p>
  </div>
</div>

Last summer I shipped three production tools in eight weeks at Frontage Laboratories, a clinical
CRO. The largest replaced a day-and-a-half manual quoting process: intake form, rules engine,
Excel and PDF at the end. Tested, containerized, gated behind CI.

I'm finishing a B.S. in Computer Science at MSU Denver, 4.0 GPA, December 2027. Before this I
built ETL pipelines for a property management firm, and before *that* I taught skiing
professionally for five seasons.

## Selected work

<div class="work">

  <div class="work-item">
    <div class="work-year">2026</div>
    <div class="work-body">
      <h3><a href="{{ '/projects/quote-generator/' | relative_url }}">Quote Generator</a></h3>
      <p>Quoting a clinical study meant a thirty-email thread, then a specialist building a
      pricing workbook by hand. Now a single-use client intake link feeds a rules engine that
      pre-populates the draft, and the specialist reviews and decides instead of assembling.</p>
      <p class="work-stack">Flask · SQLite · openpyxl · Playwright · GitHub Actions · nginx</p>
    </div>
  </div>

  <div class="work-item">
    <div class="work-year">2026</div>
    <div class="work-body">
      <h3><a href="{{ '/projects/label-maker/' | relative_url }}">Label Maker</a></h3>
      <p>Barcode and aliquot label sheets, expanded by hand patient by patient. Now it's a short
      form and a download — from a single HTML file that runs offline.</p>
      <p class="work-stack">JavaScript · ExcelJS · PizZip · 21 CFR Part 11 validation</p>
    </div>
  </div>

  <div class="work-item">
    <div class="work-year">2026</div>
    <div class="work-body">
      <h3><a href="{{ '/projects/billing-analyzer/' | relative_url }}">Billing Analyzer</a></h3>
      <p>A twelve-tab-per-year billing workbook nobody could read across years. Drop the files
      in and read the whole account.</p>
      <p class="work-stack">JavaScript · ExcelJS · hand-built SVG charts · node:test</p>
    </div>
  </div>

  <div class="work-item">
    <div class="work-year">2026</div>
    <div class="work-body">
      <h3><a href="{{ '/projects/rental-pipeline/' | relative_url }}">Rental Pipeline</a></h3>
      <p>Four property management systems, four report formats, and files that lied about what
      they were. Sixteen parsers into one schema.</p>
      <p class="work-stack">Python · Docker · ETL</p>
    </div>
  </div>

</div>

## Elsewhere

How I work is its own page — I use agentic tooling heavily, and the
[interesting part]({{ '/process/' | relative_url }}) is the harness that makes what it writes
verifiable.

Code lives at [github.com/dustinJ15](https://github.com/dustinJ15). The three tools above were
built for an employer and stay private; the writeups describe the engineering without the
client's data.
