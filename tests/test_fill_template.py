import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import fill_template as ft  # noqa: E402

SAMPLE = "\n".join([
    "VIRGINIA: IN THE CIRCUIT COURT OF [LOCALITY]",
    "[PLAINTIFF NAME], Plaintiff |",
    "v. | Case No. ______",
    "Plaintiff [FULL NAME] sues Defendant [FULL NAME].",
    "[DATE]",
    "On [DATE], the collision occurred.",
    "[SERVICE LIST]",
    "Telephone: [NUMBER] | VSB No. [NUMBER]",
])


class FillTests(unittest.TestCase):
    def test_plain_key_fills_every_occurrence(self):
        out, left = ft.fill(SAMPLE, {"DATE": "May 1, 2026"})
        self.assertEqual(out.count("May 1, 2026"), 2)
        self.assertNotIn("DATE", [u["name"] for u in left])

    def test_brackets_and_case_in_keys_are_ignored(self):
        out, _ = ft.fill(SAMPLE, {"[locality]": "Arlington County"})
        self.assertIn("CIRCUIT COURT OF Arlington County", out)

    def test_context_key_targets_the_preceding_word(self):
        out, left = ft.fill(SAMPLE, {"FULL NAME@Plaintiff": "Dana Doe", "FULL NAME@Defendant": "Riley Roe"})
        self.assertIn("Plaintiff Dana Doe sues Defendant Riley Roe.", out)
        self.assertNotIn("FULL NAME", [u["name"] for u in left])

    def test_line_start_context(self):
        out, _ = ft.fill(SAMPLE, {"DATE@^": "June 2, 2026", "DATE@On": "May 1, 2026"})
        self.assertIn("\nJune 2, 2026\n", out)
        self.assertIn("On May 1, 2026, the collision", out)

    def test_occurrence_key_and_precedence(self):
        values = {"NUMBER": "x", "NUMBER@No.": "00000", "NUMBER#1": "(555) 555-0100"}
        out, _ = ft.fill(SAMPLE, values)
        self.assertIn("Telephone: (555) 555-0100 | VSB No. 00000", out)

    def test_empty_and_missing_values_stay_bracketed_and_are_reported(self):
        out, left = ft.fill(SAMPLE, {"LOCALITY": "", "PLAINTIFF NAME": None})
        self.assertIn("[LOCALITY]", out)
        self.assertIn("[PLAINTIFF NAME]", out)
        names = [u["name"] for u in left]
        self.assertEqual(names[:2], ["LOCALITY", "PLAINTIFF NAME"])
        self.assertEqual({u["name"]: u["count"] for u in left}["DATE"], 2)

    def test_clerk_blanks_are_untouched(self):
        out, _ = ft.fill(SAMPLE, {"LOCALITY": "Fairfax County"})
        self.assertIn("Case No. ______", out)

    def test_multiline_value_kept_only_when_field_is_whole_line(self):
        out, _ = ft.fill(SAMPLE, {"SERVICE LIST": "A Counsel\nB Counsel", "PLAINTIFF NAME": "DANA\nDOE"})
        self.assertIn("\nA Counsel\nB Counsel\n", out)
        self.assertIn("DANA, DOE, Plaintiff |", out)

    def test_value_containing_brackets_is_reported_unresolved(self):
        _, left = ft.fill("Re: [MATTER]", {"MATTER": "[TBD]"})
        self.assertEqual(left, [{"name": "TBD", "count": 1}])

    def test_field_summary_lists_context_keys_for_reused_names(self):
        summary = {s["name"]: s for s in ft.field_summary(SAMPLE)}
        self.assertEqual(summary["FULL NAME"]["keys"], ["FULL NAME", "FULL NAME@Plaintiff", "FULL NAME@Defendant"])
        self.assertEqual(summary["DATE"]["keys"], ["DATE", "DATE@^", "DATE@On"])
        self.assertEqual(summary["LOCALITY"]["keys"], ["LOCALITY"])

    def test_front_matter_round_trip(self):
        meta, body = ft.parse_front_matter('---\ntitle: "A \\"quoted\\" title"\npages: 2\n---\nBody [X]\n')
        self.assertEqual(meta, {"title": 'A "quoted" title', "pages": 2})
        self.assertEqual(body, "Body [X]\n")

    def test_check_flags_unsupplied_case_number_service_date_and_address(self):
        text = "Case No. CL26-1234. Served this 15th day of July, 2026 at 4410 Sample Lane and 100 Sample Street."
        warnings = ft.check_draft(text, {"x": "100 Sample Street"})
        self.assertEqual(len(warnings), 3)
        self.assertTrue(any("CL26-1234" in w for w in warnings))
        self.assertFalse(any("100 Sample Street" in w for w in warnings))
        self.assertEqual(ft.check_draft("Case No. CL26-1234", {"case": "CL26-1234"}), [])


class TemplateFileTests(unittest.TestCase):
    def test_find_template_by_slug_and_command(self):
        self.assertEqual(ft.find_template("complaint").name, "complaint.md")
        self.assertEqual(ft.find_template("/medicare-cpl").name, "medicare-cpl.md")

    def test_examples_reproduce(self):
        for name in ["complaint", "rep-adverse"]:
            folder = ROOT / "examples" / name
            _, _, body = ft.load_template(name)
            values = json.loads((folder / "values.json").read_text())
            out, left = ft.fill(body, values)
            self.assertEqual(out, (folder / "expected-draft.md").read_text(), name)
            report = json.loads((folder / "expected-report.json").read_text())
            self.assertEqual(left, report["unresolved"], name)

    def test_cli_fill_writes_markdown_and_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            out, rep = Path(tmp) / "d.md", Path(tmp) / "r.json"
            with contextlib.redirect_stderr(io.StringIO()) as err:
                ft.main(["fill", "rep-adverse", "--values", str(ROOT / "examples/rep-adverse/values.json"),
                         "--out", str(out), "--report", str(rep)])
            self.assertIn("4 field(s) still bracketed", err.getvalue())
            self.assertIn("We represent Dana Doe", out.read_text())
            self.assertEqual(len(json.loads(rep.read_text())["unresolved"]), 4)

    @unittest.skipUnless(__import__("importlib").util.find_spec("docx"), "python-docx not installed")
    def test_render_docx_for_each_layout(self):
        from docx import Document
        samples = {"COURT": "complaint", "LETTER": "medicare-cpl", "DOCUMENT": "retainer",
                   "APPELLATE": "opening-brief", "APPELLATE_PAPER": "record-appeal"}
        with tempfile.TemporaryDirectory() as tmp:
            for layout, slug in samples.items():
                _, meta, body = ft.load_template(slug)
                self.assertEqual(meta["layout"], layout)
                target = Path(tmp) / f"{slug}.docx"
                self.assertTrue(ft.render_docx(body, layout, target, meta["title"]))
                doc = Document(str(target))
                self.assertEqual(doc.core_properties.author, "")
                size = doc.styles["Normal"].font.size.pt
                self.assertEqual(size, 14 if layout.startswith("APPELLATE") else 12)
                if layout == "APPELLATE":
                    self.assertEqual(len(doc.sections), 3)
                if layout == "COURT":
                    self.assertEqual(len(doc.tables[0].columns), 3)


if __name__ == "__main__":
    unittest.main()
