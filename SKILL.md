---
name: virginia-pi-templates
description: Drafts Virginia personal-injury documents from a library of 222 reviewed templates - complaints and other pleadings, discovery, demand and insurance letters, Medicare, Medicaid, ERISA and other lien correspondence, settlement agreements and releases, motions, trial papers and appellate briefs. Use when someone asks to draft, fill or pick a Virginia PI letter, pleading, motion or settlement document, names a command such as /complaint, /rfp or /medicare-cpl, or asks which template fits. Fills bracketed fields only with supplied facts and lists every field still missing.
---

# Virginia PI templates

Draft from the reviewed templates in `templates/`. Fill only what the user supplied. Leave the rest bracketed and say so.

Every output is a draft for attorney review, not legal advice. Template text, citations and sources are as of the source snapshot verified 2026-09-21 and are not re-verified.

## Files

- `templates/INDEX.md` - every template: title, command, category, court, layout, pages.
- `templates/ROUTES.md` - requests that must NOT be drafted (official forms, clerk-issued process, agency processes, specialist work, procedure choices, aliases).
- `templates/<category>/<slug>.md` - front matter (scope, court, layout) plus the template text.
- `reasoning/<slug>.md` - requirements, conditional decisions, required inputs and sources for that template.
- `references/choosing-a-template.md` - how to pick between similar templates.
- `references/layout-profiles.md` - COURT, LETTER, DOCUMENT, APPELLATE, APPELLATE_PAPER rules and the text format.
- `references/drafting-rules.md` - what may fill a bracket, what never may, and the self-check.
- `scripts/fill_template.py` - list, show fields, fill, render .docx, check a draft (stdlib; python-docx only for .docx).

## Workflow

### 1. Pick the template

1. Search the index: `python3 scripts/fill_template.py list --search "WORDS"` or read `templates/INDEX.md`.
2. If the request matches `templates/ROUTES.md`, stop drafting. Give the user that entry's "what to do" text and any official link. Do not write a substitute document.
3. Use `references/choosing-a-template.md` for near-duplicates (answer vs grounds, limits vs policylimits, rfp vs subpoena-biz, the Medicare and lien families, strike vs jnov).
4. Read the template's front matter. Check `scope` and `court` against the user's facts. If the facts fall outside scope (minor, estate, wrongful death, government defendant, federal court, another state), say so. Offer the closest template with the changes it needs, marked for review, or stop.
5. Tell the user which template you chose and why, in one line.

### 2. Collect the facts

1. Read `reasoning/<slug>.md`, section "Required case inputs" and the conditional decisions.
2. List the fields: `python3 scripts/fill_template.py fields <slug>`.
3. Map what the user already gave you (conversation and any documents they supplied) onto fields.
4. Ask once for the missing facts that matter most, grouped in plain language (parties, incident, insurer/claim, counsel block, amounts). Do not quiz field by field. If the user wants a draft now, proceed with gaps bracketed.

### 3. Fill

1. Write a values file (JSON). Keys:
   - `"FIELD NAME"` fills every occurrence.
   - `"FIELD NAME@word"` fills only occurrences after that word (`"NUMBER@Telephone:"`, `"FULL NAME@Defendant"`); `@^` means at the start of a line.
   - `"FIELD NAME#2"` fills only the second occurrence.
   Use context or occurrence keys for generic names (`NUMBER`, `DATE`, `ADDRESS`, `NAME`, `FULL NAME`).
2. Values are the user's facts, verbatim where possible. For narrative fields, write sentences from supplied facts only.
3. Never supply: invented facts, dates, amounts, fee terms, case numbers, service or certificate dates, signatures, consent, payment, enclosures, deadlines, or citations not in the template. See `references/drafting-rules.md`.
4. Leave unknown fields bracketed. Leave clerk and signature blanks (`______`) alone.
5. Run:

```sh
python3 scripts/fill_template.py fill <slug> --values values.json --out draft.md --docx draft.docx --report report.json
python3 scripts/fill_template.py check draft.md --values values.json
```

If python-docx is missing, the script writes the .md only and says so. Offer the .docx only when asked or when the user needs a Word file; the reviewed blank .docx in `templates/<category>/docx/` is always available.

If you cannot run scripts, fill the text by hand with the same rules and keep the line format.

### 4. Keep the layout

Apply the template's `layout` (see `references/layout-profiles.md`). Do not reflow the line format: keep `# ` and `## ` lines, `1.` numbering, `|` caption rows, and `<!-- pagebreak -->`, `<!-- frontmatter -->`, `<!-- body -->` markers exactly. Court papers are double-spaced with a caption; letters and plain documents are single-spaced; APPELLATE briefs keep cover, front matter and body sections at 14 point.

### 5. Report

End every draft with this report:

```
Template: <title> (<command>), layout <LAYOUT>, scope checked: <yes / outside scope because ...>
Files: <draft.md> [<draft.docx>]
Still bracketed (<n>): [FIELD], [FIELD], ...
Drafted from your facts (review): [FIELD], ...
Check flags: <output of check, or none>
Verify before use: deadlines and limitations, local rules and filing method, service, any citation, current form editions.
Draft for attorney review. Not legal advice. Verify against current Virginia statutes, rules and local practice.
```

If the matter involves medical records or health-plan data: work locally and do not send protected health information to third-party services without authorization.

## Example

`examples/complaint/` holds a synthetic request, its values file, the filled draft and the report. Run it with:

```sh
python3 scripts/fill_template.py fill complaint --values examples/complaint/values.json --out /tmp/complaint-filled.md
```
