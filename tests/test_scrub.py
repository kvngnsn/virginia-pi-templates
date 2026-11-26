"""Guard against personal data, local paths and secrets creeping into the repo."""
import re
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".json", ".js", ".html", ".css", ".py", ".txt", ".yml", ".yaml"}
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+\.)+[A-Za-z]{2,}")
PHONE = re.compile(r"\(?\b(\d{3})\)?[-. ]\d{3}[-. ]\d{4}\b")
BANNED = re.compile(r"/Users/|supabase|sk-[A-Za-z0-9]{10,}|AIza[0-9A-Za-z_-]{10,}|attorneyos\.org|precision", re.I)


def text_files():
    for p in ROOT.rglob("*"):
        if p.is_file() and ".git" not in p.parts and p.suffix in TEXT_SUFFIXES and p.name != "test_scrub.py":
            yield p


def docx_texts():
    for p in ROOT.rglob("*.docx"):
        if ".git" in p.parts:
            continue
        with zipfile.ZipFile(p) as z:
            for name in z.namelist():
                if name.endswith((".xml", ".rels")):
                    yield p, name, z.read(name).decode("utf-8", "ignore")


class Scrub(unittest.TestCase):
    def check(self, label, text):
        for m in EMAIL.finditer(text):
            self.assertRegex(m.group(0), r"@example\.(com|org)$", label)
        for m in PHONE.finditer(text):
            self.assertEqual(m.group(1), "555", f"{label}: {m.group(0)}")
        self.assertIsNone(BANNED.search(text), label)

    def test_text_files(self):
        for p in text_files():
            with self.subTest(str(p.relative_to(ROOT))):
                self.check(str(p), p.read_text(encoding="utf-8", errors="ignore"))

    def test_docx_parts(self):
        for p, name, text in docx_texts():
            with self.subTest(f"{p.name}:{name}"):
                self.check(f"{p}:{name}", text)

    def test_no_env_or_tool_folders(self):
        for p in ROOT.rglob("*"):
            if ".git" in p.parts:
                continue
            self.assertFalse(p.name.startswith(".env"), str(p))
            self.assertNotIn(p.name, {".claude", ".work", ".vercel"}, str(p))


if __name__ == "__main__":
    unittest.main()
