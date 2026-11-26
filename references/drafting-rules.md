# Drafting rules

These rules come from the shared reasoning (`reasoning/common.md`), the per-template reasoning files and the source app's placeholder and fabrication checks.

## What may fill a bracket

A bracketed field may be replaced only with:

- a fact the user stated in the conversation;
- a fact in a document the user supplied (records, orders, letters, the policy, the served discovery);
- for narrative fields (for example `[MATERIAL COLLISION FACTS]`, `[SUPPORTED NEGLIGENT ACTS OR OMISSIONS]`), sentences you write that restate only those supplied facts. Flag every such field as "drafted from supplied facts; review" in the report.

Everything else stays in brackets and goes on the unresolved list.

## Never supply

- Facts, dates, injuries, damages figures, amounts, percentages or fee terms the user did not give.
- Case numbers. The clerk assigns them; leave `Case No. ______` blank.
- Completed service, certificate dates, signatures, notarization, consent, conferral, production, payment, receipt of funds, enclosures or judicial action.
- Deadlines or limitations dates computed by you as fact. If the user asks, state the governing statute or rule the attorney must check and mark it "verify".
- Legal citations not already in the template. If the user asks you to add one, add it only if you can name its source, and mark it "verify". Citations already printed in a template were checked on 2026-09-21 in the source snapshot; they are not re-verified.
- Agency-issued or clerk-issued documents (see `templates/ROUTES.md`).

## Generic field names

Many templates reuse short names such as `[NUMBER]`, `[DATE]`, `[ADDRESS]`, `[NAME]`, `[FULL NAME]`. The same name can mean different things in one document (`VSB No. [NUMBER]` and `Telephone: [NUMBER]`; the letter date and the incident date). Use `fill_template.py fields SLUG` and fill these by context key (`NUMBER@Telephone:`) or occurrence (`DATE#2`), never by a plain name that would put one value in every slot.

## Optional and conditional content

Templates include conditional modules (jury demand, fax line "if regularly used", alternative response modules, cross-error sections). Keep only what applies to the actual facts. If unsure, keep it and say it needs a decision. Do not delete a required element to make a draft look complete.

## Self-check before you hand over a draft

Run `python3 scripts/fill_template.py check DRAFT.md --values VALUES.json`. It flags (from the source app's detector):

- text that looks like a court case number (`CL24-1234`, `Case No. 24-1234`, `2024-CV-123`) not found in the supplied values;
- a completed service date (`this 15th day of July, 2026`) not found in the supplied values;
- street addresses not found in the supplied values.

Then confirm by reading:

1. Every bracket you replaced traces to a supplied fact.
2. Names, dates and amounts are identical everywhere they repeat.
3. The scope still fits (court, parties, claim type).
4. The layout profile and markers are intact (`references/layout-profiles.md`).
5. The report lists unresolved fields, drafted narrative, and items to verify.

## Privacy

Medical records, health-plan data and client identifiers are sensitive. Work locally. Do not send protected health information to third-party services without authorization. The scripts make no network calls.
