# Layout profiles

Every template has one `layout` value in its front matter. The reviewed Word files already apply it, and `scripts/fill_template.py fill ... --docx` renders a filled draft the same way. When you produce text by hand, keep these rules.

Rules or data as of the source snapshot verified 2026-09-21. "Rule" below means a Rule of the Supreme Court of Virginia; "house choice" means a design decision of this library, not a requirement. Verify current rules and any local requirements before filing.

## Shared house style

- US Letter paper, one-inch margins, black Times New Roman, bottom-center page numbers. These are house choices; Rule 1:16 does not prescribe the font or margins.
- Bold title (`# ` line) centered; modest bold headings (`## ` lines); editable Word numbering for `1.` paragraphs.
- Keep signature blocks, certificates, judge's signature lines and notarial blocks together on one page.

## COURT (91 templates)

Court papers for a Virginia court: pleadings, motions, discovery papers, proposed orders, notices.

- Double-spaced, including caption and signature (Rule 1:16(a)(1) requires double-spaced typed material for filings, except quotations, subject to electronic-filing provisions). Served-but-unfiled discovery uses the same spacing for consistency.
- 12-point type (house choice).
- Caption: court line first (for example `VIRGINIA: IN THE CIRCUIT COURT OF [LOCALITY]`, bold), then a borderless three-column caption: party text left, `)` separators, case number right. In the text format each caption row is one line with `|` between the left and right columns. This arrangement follows an official appendix example (Part Five Appendix Form 1); it is an observed convention, not a mandated form.
- Signature block indented about three inches, starting at `Respectfully submitted`. Counsel details: name, VSB number, firm, address, telephone, email, and fax only if regularly used (Rules 1:4, 1:5; Va. Code § 8.01-271.1).
- Certificates of service state actual date and method; never pre-complete them (Rules 1:12, 1:17).
- Leave the case number blank (`Case No. ______`) unless the real number is supplied. The clerk assigns it.

## LETTER (91 templates)

Correspondence to insurers, providers, agencies, clients and opposing counsel.

- Single-spaced block format with a blank line (8 pt) between paragraphs; no court caption.
- Order: firm letterhead lines, date, recipient block, bold `Re:` line, salutation, body, `Sincerely,`, signer and firm.
- The `Telephone: [NUMBER] | Email: [ADDRESS]` line in letterhead is one line with a literal separator, not a caption.

## DOCUMENT (33 templates)

Plain documents: agreements, releases, authorizations, intake forms, statements, summaries, ledgers.

- Single-spaced with 6 pt after each paragraph; descriptive title; short labeled sections; no court caption or letter salutation.
- Execution blocks (signature, printed name, date) stay blank for the actual signer.

## APPELLATE (5 templates)

Full appellate briefs and petitions: `/opening-brief`, `/appellee-brief`, `/reply-brief`, `/rehearing`, `/cert-petition`.

- At least 14-point type (Rules 5:6 and 5A:4 as applied in the source); double-spaced body; headings and assignments of error single-spaced.
- Three sections: an unnumbered cover, front matter numbered in lower-case roman numerals (tables of contents and authorities, with dot-leader page references), and an arabic-numbered body.
- The text marks the section breaks with `<!-- frontmatter -->` and `<!-- body -->`. Keep each marker exactly once and in that order.
- Table page references, the word count, record citations, PDF bookmarks and VACES packaging are case-specific. A Word draft is not a completed filing package.

## APPELLATE_PAPER (2 templates)

Ordinary appellate papers without a brief cover: `/oral-argument`, `/record-appeal`.

- At least 14-point type; double-spaced body; headings and assignments of error single-spaced; no cover or roman front matter.

## Text format (all profiles)

Templates are line-oriented. One line is one paragraph.

| Line | Meaning |
|---|---|
| `# Title` | centered bold title |
| `## Heading` | bold section heading |
| `1. Text` | numbered paragraph (Word numbering) |
| `left text \| right text` | caption row in COURT and APPELLATE layouts |
| `<!-- pagebreak -->` | start a new page (for example, jury pages separate from the counsel submission) |
| `<!-- frontmatter -->`, `<!-- body -->` | APPELLATE section breaks |
| `[FIELD NAME]` | fact to supply from the case; stays bracketed if unknown |
| `______` | blank for the clerk, signer or a handwritten date; leave it |

## Rule checks the template cannot do for you

The source app sorted court rules into three groups. Use the same split when reviewing a draft:

- **Structural** (the draft itself must satisfy): caption contents, pleading and element requirements, jurisdiction and venue facts, notice-of-claim requirements, motion practice, page limits.
- **Typographic** (handled by the layout profile): font, line spacing, margins, signature block.
- **External** (attorney must check outside the draft): filing requirements, certificate of service, tables of authorities, exhibit formatting, electronic filing, proposed orders, briefing schedules, and every deadline (limitations, responsive pleading, discovery responses, service, appeal, expert disclosure).
