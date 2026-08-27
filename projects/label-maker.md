---
title: Label Maker
year: 2026
role: Sole developer
stack: JavaScript, ExcelJS, PizZip, python-docx
code: Private — employer work
summary: >-
  Barcode and aliquot label sheets that were being expanded by hand, patient by patient.
  Replaced with one HTML file a coworker double-clicks.
---

A clinical lab prints a lot of labels. Every study needs barcode sheets for each patient, child
aliquot labels for every sample that gets split, envelope labels, and bag labels — each with
running packet numbers and sequential barcodes, each from an approved template.

That expansion was happening by hand. Someone would take a QC'd single-patient template, copy the
rows, and increment the numbers, once per patient, once per study.

<div class="outcome">
  <p><span class="before">Copy rows, increment barcodes, repeat per patient</span></p>
  <p><strong>Fill in a short form. Download the sheet.</strong></p>
</div>

## One file, no install

The whole product is a single `.html` file. You double-click it, or a coworker sends it over
Teams and *they* double-click it. It runs offline, uploads nothing, and needs no server, no
install, and no IT ticket.

That last part is the design decision I'd defend hardest. A web app would have needed hosting,
an approval process, and a login — three places for adoption to die. A file you can email is a
tool people can start using the same afternoon.

## Rewriting Excel and Word without breaking them

`.xlsx` and `.docx` are zipped XML, which means a browser can read and write them directly with
no server round-trip.

- **Excel sheets** go through [ExcelJS](https://github.com/exceljs/exceljs), which copies the
  template's styles, number formats, and column widths, and shifts formula row-references as it
  stamps each new patient block. Barcodes are kept as text — the moment Excel decides a barcode
  is a number, leading zeros disappear and the sheet is wrong in a way nobody notices until
  it's printed.
- **Word labels** go through [PizZip](https://github.com/open-xml-templating/pizzip), and the
  constraint there is stricter: the approved template has to survive **byte-for-byte**. Only the
  per-study text and the packet numbers get swapped in; pages are duplicated for larger ranges
  and unused trailing labels are blanked. In a regulated lab, "we regenerated the template" is a
  finding, not a shortcut.

Both libraries and both Word templates are inlined into the single output file at build time, so
the thing that ships has no dependencies at all.

## Small details that decide whether it works

- **Leading zeros set the width.** Typing `001` means three digits; typing `1` means one. The
  number you type *is* the format spec, so nobody has to think about padding.
- **Rows-per-patient is auto-detected** from the uploaded template rather than configured.
- **Trailing blank rows are ignored.** A manifest usually has a few empty rows left behind by a
  dragged formula. Without that check, every one becomes a phantom child aliquot.
- **Files name themselves** from the inputs, so what lands in Downloads is already the name it
  needs on the shared drive.

## The part I didn't expect to be doing

The tool is used in a regulated environment, which means it needed a formal computer-system
validation package under **21 CFR Part 11** before anyone could rely on it. I wrote and executed
it: validation plan, user requirement specification, system risk assessment and mitigation,
test-script specification, incident log and incident report forms, validation report, release
memo, bi-annual review, and a use-and-QC SOP.

I had no regulatory background going in. The useful surprise was how much of it is just
engineering discipline written in a different dialect — a requirement you can test, a risk you
can name, and evidence that the test actually ran. The paperwork is unfamiliar. The idea that a
claim needs evidence behind it is not.

<p class="note">
Built for an employer, so the code and the templates stay private. Everything here describes
the engineering, not the client's data.
</p>
