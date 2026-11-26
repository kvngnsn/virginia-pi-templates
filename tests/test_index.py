import json
import re
import sys
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_index  # noqa: E402
from fill_template import parse_front_matter  # noqa: E402

LAYOUTS = {"COURT", "LETTER", "DOCUMENT", "APPELLATE", "APPELLATE_PAPER"}
ROUTE_KINDS = {"official-form", "official-process", "clerk-process", "specialist", "choose-template", "alias", "not-included"}


def load_json(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def load_data_js():
    text = (ROOT / "docs" / "data.js").read_text(encoding="utf-8")
    start = text.index("window.VPT_DATA = ") + len("window.VPT_DATA = ")
    return json.loads(text[start:text.rindex(";")])


class IndexIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = load_json("docs/templates.json")
        cls.routes = load_json("templates/routes.json")
        cls.entries = cls.index["templates"]

    def test_count_matches_template_files(self):
        files = sorted((ROOT / "templates").glob("*/*.md"))
        self.assertEqual(len(files), 222)
        self.assertEqual(self.index["count"], len(self.entries))
        self.assertEqual(len(self.entries), len(files))

    def test_every_entry_has_its_files(self):
        for e in self.entries:
            with self.subTest(e["slug"]):
                self.assertTrue((ROOT / e["path"]).is_file())
                self.assertTrue((ROOT / e["docx_path"]).is_file())
                self.assertTrue((ROOT / e["reasoning_path"]).is_file())
                site_copy = ROOT / "docs" / "docx" / f"{e['slug']}.docx"
                self.assertEqual(site_copy.read_bytes(), (ROOT / e["docx_path"]).read_bytes())

    def test_entry_fields_are_valid_and_unique(self):
        slugs = [e["slug"] for e in self.entries]
        self.assertEqual(len(slugs), len(set(slugs)))
        for e in self.entries:
            with self.subTest(e["slug"]):
                self.assertEqual(e["command"], "/" + e["slug"])
                self.assertIn(e["layout"], LAYOUTS)
                self.assertIsInstance(e["pages"], int)
                self.assertGreaterEqual(e["pages"], 1)
                self.assertTrue(e["title"] and e["scope"] and e["court"] and e["category_label"])
                self.assertEqual(Path(e["path"]).parent.name, e["category"])

    def test_index_matches_front_matter_and_site_data(self):
        site = {t["slug"]: t for t in load_data_js()["templates"]}
        self.assertEqual(set(site), {e["slug"] for e in self.entries})
        for e in self.entries:
            raw = (ROOT / e["path"]).read_text(encoding="utf-8")
            meta, body = parse_front_matter(raw)
            self.assertEqual(meta["title"], e["title"])
            self.assertEqual(site[e["slug"]]["md"], raw)
            self.assertTrue(body.strip(), e["slug"])

    def test_generated_outputs_are_current(self):
        self.assertEqual(build_index.main(["--check"]), 0, "run: python3 scripts/build_index.py")

    def test_index_md_lists_every_template(self):
        text = (ROOT / "templates" / "INDEX.md").read_text(encoding="utf-8")
        for e in self.entries:
            self.assertIn(f"`{e['command']}`", text)

    def test_routes_are_separate_from_templates(self):
        slugs = {e["slug"] for e in self.entries}
        route_slugs = [r["slug"] for r in self.routes]
        self.assertEqual(len(route_slugs), len(set(route_slugs)))
        for r in self.routes:
            with self.subTest(r["slug"]):
                self.assertNotIn(r["slug"], slugs, "a route must not also be a drafting template")
                self.assertIn(r["kind"], ROUTE_KINDS)
                self.assertTrue(r["what_to_do"].strip())
                if r.get("alias_of"):
                    target = r["alias_of"].lstrip("/")
                    self.assertTrue(target in slugs or target in route_slugs, target)
                if r.get("reasoning"):
                    self.assertTrue((ROOT / r["reasoning"]).is_file())

    def test_reasoning_links_resolve(self):
        for path in list((ROOT / "reasoning").glob("*.md")) + list((ROOT / "reasoning" / "routes").glob("*.md")):
            text = path.read_text(encoding="utf-8")
            for target in re.findall(r"\]\((?!https?://|#)([^)]+)\)", text):
                with self.subTest(file=path.name, target=target):
                    self.assertTrue((path.parent / target.split("#")[0]).exists())


class DocxMetadata(unittest.TestCase):
    def test_docx_properties_are_cleared(self):
        for path in sorted((ROOT / "templates").glob("*/docx/*.docx")):
            with zipfile.ZipFile(path) as z:
                names = set(z.namelist())
                core = z.read("docProps/core.xml").decode("utf-8")
                app = z.read("docProps/app.xml").decode("utf-8")
            with self.subTest(path.name):
                self.assertIn("<dc:creator></dc:creator>", core)
                self.assertIn("<cp:lastModifiedBy></cp:lastModifiedBy>", core)
                self.assertNotRegex(app, r"<Company>[^<]+</Company>")
                self.assertNotRegex(app, r"<Manager>[^<]+</Manager>")
                self.assertNotIn("docProps/thumbnail.jpeg", names)


if __name__ == "__main__":
    unittest.main()
