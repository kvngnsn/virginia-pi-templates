# virginia-pi-templates

An open library of 222 reviewed Virginia personal-injury drafting templates, with a Claude skill that drafts from them and an offline browser for previewing and filling them.

## What it does

- **222 templates** as clean text (`templates/<category>/<slug>.md`) and matching Word files (`templates/<category>/docx/<slug>.docx`): pleadings, discovery, motions, trial and appellate papers, insurance and records letters, Medicare, Medicaid, ERISA and other lien correspondence, and settlement documents.
- **Reasoning for each template** (`reasoning/<slug>.md`): the requirements it relies on, conditional decisions, required case inputs and primary sources.
- **65 routes without drafts** (`templates/ROUTES.md`): official forms, clerk-issued process, agency processes, specialist work, procedure choices and aliases. Each says what to use instead; no substitute drafts were written.
- **A Claude skill** (`SKILL.md`): picks the template, collects facts, fills bracketed fields only with supplied facts, leaves the rest bracketed and lists them, applies the layout rules, and outputs Markdown and optionally .docx.
- **A static browser** (`docs/`): search and filter, preview, download .docx and .md, and fill the fields in a form, then copy or download the filled text. No network calls.

Demo: https://kvngnsn.github.io/virginia-pi-templates/

| Category | Templates |
|---|---:|
| Client and case management | 13 |
| Investigation and records requests | 15 |
| Insurance claims and correspondence | 16 |
| Medical records and bills | 6 |
| Liens, Medicare, Medicaid and benefit recovery | 44 |
| Demands, negotiation and ADR | 11 |
| Settlement documents and disbursement | 17 |
| Pleadings and service | 16 |
| Discovery | 30 |
| Motions and orders | 20 |
| Pretrial and trial | 16 |
| Post-trial, judgment and appeals | 18 |

Full list with commands, court, layout and page counts: [templates/INDEX.md](templates/INDEX.md).

## Quick start

Install as a Claude skill:

```sh
git clone https://github.com/kvngnsn/virginia-pi-templates ~/.claude/skills/virginia-pi-templates
```

Then ask, for example, "Draft a notice of representation to the liability insurer for my Virginia client" or "Fill /medicare-cpl with these facts".

Use the script directly (Python 3.8+, standard library; `pip install python-docx` only for .docx output):

```sh
python3 scripts/fill_template.py list --search "policy limits"
python3 scripts/fill_template.py fields complaint
python3 scripts/fill_template.py fill complaint --values examples/complaint/values.json --out draft.md --docx draft.docx
python3 scripts/fill_template.py check draft.md --values examples/complaint/values.json
```

Open `docs/index.html` in a browser to use the template browser offline.

## How it works

- Each template file has front matter (title, command, category, court, layout, pages, scope) followed by line-oriented text: `# Title`, `## Heading`, `1.` numbered paragraphs, `|` caption rows and `<!-- pagebreak -->` / `<!-- frontmatter -->` / `<!-- body -->` markers. `[BRACKETED FIELDS]` mark facts that must come from the case.
- Fill keys: `"FIELD"` fills every occurrence, `"FIELD@word"` only occurrences after that word (for reused names like `[NUMBER]` after `Telephone:` versus `VSB No.`), `"FIELD#2"` only the second one. Empty values leave the field bracketed. The browser form uses the same rules.
- Layout profiles (`references/layout-profiles.md`): **COURT** double-spaced with a borderless caption; **LETTER** single-spaced block letter; **DOCUMENT** single-spaced plain document; **APPELLATE** 14-point brief with cover, roman front matter and arabic body; **APPELLATE_PAPER** 14-point appellate paper without a cover. The Word files and `--docx` output apply them.
- `scripts/build_index.py` regenerates `templates/INDEX.md`, `templates/ROUTES.md`, `docs/templates.json`, `docs/routes.json`, `docs/data.js` and the downloadable copies in `docs/docx/`.

## Limits and "verify" notes

- **Data date.** Template text, citations and sources are as of the source snapshot verified September 21, 2026 (source snapshot, November 2026). They have not been re-verified for this release. Verify every statute, rule, form edition and deadline against current official sources.
- **Not attorney-certified.** The templates were drafted from cited requirements and reviewed as blank documents. No case-filled output has been legally reviewed. A blank-template review does not establish that a filled draft is correct.
- **Scope.** Each template states its scope. Court papers marked "Virginia Circuit Court" are for that court; other courts, federal practice, minors, estates, wrongful death and government defendants usually need adaptation.
- **Routes.** Official forms (22 Virginia court and federal forms), clerk-issued process, agency documents (for example Medicare recovery demands) and specialist instruments (trusts, annuities, qualified settlement funds, MSA allocations) are listed in ROUTES.md without drafts. Form numbers there come from the source snapshot; check the publisher for the current form.
- **Not included.** The source app's case database, AI generation pipeline, native PDF form fillers, demand-package assembler, medical-records spreadsheet export and calculators are not part of this library.
- **Field names.** Some fields reuse generic names (`[NUMBER]`, `[DATE]`, `[ADDRESS]`). Use the context keys shown by `fill_template.py fields` so one value does not land in every slot.

## Tests

```sh
python3 -m unittest discover -s tests
```

Covers the bracket-field filler, the draft checker, .docx rendering (skipped without python-docx), example reproduction, index integrity (every index entry has its .md, .docx, reasoning file and site copy; generated files are current) and a scrub guard for emails, phone numbers, local paths and secrets.

## Provenance

Extracted from AttorneyOS, a Virginia personal-injury litigation app (2025–2026).

## Disclaimer

Not legal advice. Every output is a draft for attorney review. Verify against official sources: the Code of Virginia, the Rules of the Supreme Court of Virginia, local rules and current forms. For anything touching medical records, run the tools locally and do not send protected health information to third-party services without authorization.

## License

MIT, Copyright (c) 2026 kvngnsn. The template text, Word files and reasoning notes are offered as-is for reuse under the same license. See [LICENSE](LICENSE).
