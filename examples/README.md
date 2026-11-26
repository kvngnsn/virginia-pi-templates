# Worked examples

All names, firms, insurers, addresses, bar numbers and phone numbers here are fictional.

Each folder has:

- `request.md` - what the user asked for (synthetic).
- `values.json` - the fill keys built only from that request. Empty values leave the field bracketed.
- `expected-draft.md` - output of `scripts/fill_template.py fill`.
- `expected-report.json` - the script's machine report (unresolved fields, check warnings).
- `expected-report.md` - the report the skill gives the user, including conditional content it handled by hand.

Reproduce:

```sh
python3 scripts/fill_template.py fill complaint --values examples/complaint/values.json --out /tmp/complaint.md
python3 scripts/fill_template.py fill rep-adverse --values examples/rep-adverse/values.json --out /tmp/rep-adverse.md
```

`tests/test_fill_template.py` checks that these commands still produce the expected drafts.
