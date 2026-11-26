#!/usr/bin/env python3
"""Fill the [BRACKETED FIELDS] of a Virginia PI template and optionally render a .docx.

Standard library only for listing and filling. Rendering a .docx needs python-docx
(`pip install python-docx`); without it the script still writes the filled Markdown.

Commands
  list   [--category CAT] [--search WORDS]       show templates from the index
  fields SLUG [--json]                           show the fill keys a template accepts
  fill   SLUG --values VALUES.json [--out FILE.md] [--docx FILE.docx] [--report FILE.json]
  check  DRAFT.md [--values VALUES.json]         flag case numbers, service dates and street
                                                 addresses that are not in the supplied values

Fill keys (in VALUES.json)
  "FIELD NAME"          fills every [FIELD NAME]
  "FIELD NAME@context"  fills only occurrences whose preceding word is `context`
                        (`@^` = the field starts its line or follows another field)
  "FIELD NAME#3"        fills only the 3rd occurrence
Most specific key wins (#n, then @context, then the plain name). Empty values are
ignored, so the field stays bracketed. Anything left in brackets is reported as unresolved.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
FIELD_RE = re.compile(r"\[([^\[\]\n]+)\]")
LEFT_STRIP = "([{\"'“‘"


# --------------------------------------------------------------------------- parsing

def parse_front_matter(md):
    """Split a template file into (metadata dict, body text)."""
    if not md.startswith("---\n"):
        return {}, md
    end = md.index("\n---\n", 4)
    meta = {}
    for line in md[4:end].split("\n"):
        if not line.strip():
            continue
        key, _, raw = line.partition(":")
        raw = raw.strip()
        try:
            meta[key.strip()] = json.loads(raw)
        except ValueError:
            meta[key.strip()] = raw
    return meta, md[end + 5:]


def find_template(name):
    """Return the template path for a slug, `/command` or a direct path."""
    p = Path(name)
    if p.suffix == ".md" and p.exists():
        return p
    slug = name.lstrip("/").lower()
    hits = sorted(TEMPLATES.glob(f"*/{slug}.md"))
    if not hits:
        raise SystemExit(f"No template named '{name}'. Try: fill_template.py list --search WORDS")
    return hits[0]


def load_template(name):
    path = find_template(name)
    meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
    return path, meta, body


# --------------------------------------------------------------------------- fields

def norm_name(name):
    return re.sub(r"\s+", " ", name.strip().strip("[]").strip()).casefold()


def context_of(line, start):
    """The word just before a bracket on its line ('' if none)."""
    before = line[:start]
    cut = before.rfind("]")
    if cut != -1:
        before = before[cut + 1:]
    tokens = before.split()
    if not tokens:
        return ""
    return tokens[-1].lstrip(LEFT_STRIP)


def find_fields(text):
    """Every bracket occurrence, in document order."""
    out, seen = [], {}
    for line_no, line in enumerate(text.split("\n"), 1):
        for m in FIELD_RE.finditer(line):
            name = m.group(1)
            key = norm_name(name)
            seen[key] = seen.get(key, 0) + 1
            out.append({
                "name": name,
                "occurrence": seen[key],
                "line": line_no,
                "start": m.start(),
                "end": m.end(),
                "context": context_of(line, m.start()),
                "whole_line": line.strip() == m.group(0),
                "line_text": line,
            })
    return out


def field_summary(text):
    """Distinct fields with counts and the context keys that tell repeated uses apart."""
    order, info = [], {}
    for occ in find_fields(text):
        key = norm_name(occ["name"])
        if key not in info:
            order.append(key)
            info[key] = {"name": occ["name"], "count": 0, "contexts": [], "lines": []}
        item = info[key]
        item["count"] += 1
        if occ["context"] not in item["contexts"]:
            item["contexts"].append(occ["context"])
        item["lines"].append(occ["line"])
    result = []
    for key in order:
        item = info[key]
        keys = [item["name"]]
        if len(item["contexts"]) > 1:
            keys += [f"{item['name']}@{c or '^'}" for c in item["contexts"]]
        item["keys"] = keys
        result.append(item)
    return result


def _parse_values(values):
    plain, ctx, nth = {}, {}, {}
    for raw_key, value in values.items():
        if value is None:
            continue
        value = str(value)
        if not value.strip():
            continue
        key = raw_key.strip()
        m = re.match(r"^(.*)#(\d+)$", key)
        if m:
            nth[(norm_name(m.group(1)), int(m.group(2)))] = value
            continue
        if "@" in key:
            name, _, c = key.rpartition("@")
            c = "" if c == "^" else c
            ctx[(norm_name(name), c.casefold())] = value
            continue
        plain[norm_name(key)] = value
    return plain, ctx, nth


def fill(text, values):
    """Replace bracketed fields with supplied values.

    Returns (filled_text, unresolved) where unresolved lists the fields still in brackets
    as [{"name": ..., "count": ...}] in document order.
    """
    plain, ctx, nth = _parse_values(values)
    lines = text.split("\n")
    occurrences = find_fields(text)
    by_line = {}
    for occ in occurrences:
        by_line.setdefault(occ["line"], []).append(occ)
    for line_no, occs in by_line.items():
        line = lines[line_no - 1]
        for occ in sorted(occs, key=lambda o: o["start"], reverse=True):
            key = norm_name(occ["name"])
            value = nth.get((key, occ["occurrence"]))
            if value is None:
                value = ctx.get((key, occ["context"].casefold()))
            if value is None:
                value = plain.get(key)
            if value is None:
                continue
            if not occ["whole_line"]:
                value = ", ".join(part.strip() for part in value.splitlines() if part.strip())
            line = line[:occ["start"]] + value + line[occ["end"]:]
        lines[line_no - 1] = line
    filled = "\n".join(lines)
    return filled, unresolved_fields(filled)


def unresolved_fields(text):
    counts, order = {}, []
    for occ in find_fields(text):
        if occ["name"] not in counts:
            order.append(occ["name"])
            counts[occ["name"]] = 0
        counts[occ["name"]] += 1
    return [{"name": n, "count": counts[n]} for n in order]


# --------------------------------------------------------------------------- checks

# Ported from the source app's fabrication detector. These patterns flag text that
# looks like a court-assigned number, a completed service date or a street address.
# Anything flagged that does not appear in the supplied values deserves a second look.
CASE_NUMBER_PATTERNS = [
    re.compile(r"\b(?:CL|HQ|JA|CR|FE|MI|GC)\s*-?\s*\d{2,4}[-\s]?\d{2,6}\b", re.I),
    re.compile(r"\b(?:CV|CA)\s*-?\s*\d{2,4}[-\s]?\d{2,6}\b", re.I),
    re.compile(r"\b\d{4}[-\s]?(?:CV|CA|CL)[-\s]?\d{2,6}\b", re.I),
    re.compile(r"\bCase\s+No\.\s*\d{2,4}[-\s]?\d{2,6}\b", re.I),
]
SERVICE_DATE = re.compile(r"this\s+\d+(?:st|nd|rd|th)?\s+day\s+of\s+[A-Z][a-z]+,?\s*\d{4}")
STREET_ADDRESS = re.compile(
    r"\b\d{3,5}\s+[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*\s+(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Drive|Dr\.?|"
    r"Pike|Boulevard|Blvd\.?|Lane|Ln\.?|Way|Court|Ct\.?|Place|Pl\.?|Highway|Hwy\.?|Parkway|Pkwy\.?)\b")


def check_draft(text, values):
    """Warn about case numbers, service dates and street addresses not found in the supplied values."""
    supplied = " ".join(str(v) for v in values.values() if v).casefold()
    squashed = re.sub(r"[-\s]", "", supplied)
    warnings, seen = [], set()

    def flag(kind, hit):
        if hit.casefold() in supplied or re.sub(r"[-\s]", "", hit.casefold()) in squashed:
            return
        msg = f"{kind} not in supplied facts: {hit}"
        if msg not in seen:
            seen.add(msg)
            warnings.append(msg)

    for rx in CASE_NUMBER_PATTERNS:
        for m in rx.finditer(text):
            flag("Possible case number", m.group(0))
    for m in SERVICE_DATE.finditer(text):
        flag("Completed service date", m.group(0))
    for m in STREET_ADDRESS.finditer(text):
        flag("Street address", m.group(0))
    return warnings


# --------------------------------------------------------------------------- docx

def render_docx(text, layout, target, title=""):
    """Render template-format text as a .docx using the template's layout profile.

    Returns False (and writes nothing) when python-docx is not installed.
    Ported from the reviewed library builder: Times New Roman, one-inch margins,
    COURT/APPELLATE double spacing, LETTER/DOCUMENT single spacing, borderless
    three-column captions, editable numbering, bottom-center page numbers and the
    APPELLATE cover / front matter (roman) / body (arabic) sections.
    """
    try:
        from docx import Document
        from docx.enum.section import WD_SECTION_START
        from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
        from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.shared import Inches, Pt, RGBColor
    except ImportError:
        return False

    def element(tag, **attrs):
        node = OxmlElement(f"w:{tag}")
        for key, value in attrs.items():
            node.set(qn(f"w:{key}"), str(value))
        return node

    def add_numbering(doc):
        numbering = doc.part.numbering_part.element
        abstract_id = max([int(x.get(qn("w:abstractNumId"))) for x in numbering.findall(qn("w:abstractNum"))] + [-1]) + 1
        num_id = max([int(x.get(qn("w:numId"))) for x in numbering.findall(qn("w:num"))] + [0]) + 1
        abstract = element("abstractNum", abstractNumId=abstract_id)
        abstract.append(element("multiLevelType", val="singleLevel"))
        level = element("lvl", ilvl=0)
        for child in [element("start", val=1), element("numFmt", val="decimal"),
                      element("lvlText", val="%1."), element("lvlJc", val="left")]:
            level.append(child)
        props = element("pPr")
        tabs = element("tabs")
        tabs.append(element("tab", val="num", pos=540))
        props.append(tabs)
        props.append(element("ind", left=540, hanging=540))
        level.append(props)
        abstract.append(level)
        numbering.append(abstract)
        num = element("num", numId=num_id)
        num.append(element("abstractNumId", val=abstract_id))
        numbering.append(num)
        return num_id

    doc = Document()
    appellate = layout == "APPELLATE"
    appellate_paper = layout == "APPELLATE_PAPER"
    court = layout in ("COURT", "APPELLATE", "APPELLATE_PAPER")
    letter = layout == "LETTER"
    leaf = "cover" if appellate else "body"
    section = doc.sections[0]
    section.page_width, section.page_height = Inches(8.5), Inches(11)
    section.top_margin = section.bottom_margin = section.left_margin = section.right_margin = Inches(1)
    section.header_distance = section.footer_distance = Inches(0.5)
    for name in ["Normal", "Title", "Heading 1", "Footer"]:
        style = doc.styles[name]
        style.font.name = "Times New Roman"
        style.font.size = Pt(14 if appellate or appellate_paper else 12)
        style.font.color.rgb = RGBColor(0, 0, 0)
        rpr = style.element.get_or_add_rPr()
        fonts = rpr.get_or_add_rFonts()
        for k in list(fonts.attrib):
            if "theme" in k.lower():
                del fonts.attrib[k]
        for k in ["ascii", "hAnsi", "eastAsia", "cs"]:
            fonts.set(qn("w:" + k), "Times New Roman")
        ppr = style.element.get_or_add_pPr()
        for border in ppr.findall(qn("w:pBdr")):
            ppr.remove(border)
        pf = style.paragraph_format
        pf.line_spacing = 2 if court else 1
        pf.space_before = pf.space_after = Pt(0)
        pf.widow_control = True
    for name in ["Title", "Heading 1"]:
        doc.styles[name].font.bold = True
        doc.styles[name].paragraph_format.keep_with_next = True
    number_id = add_numbering(doc)

    lines = text.splitlines()
    index = 0
    signature = page_break = assignments = letter_body = False
    while index < len(lines):
        line = lines[index]
        index += 1
        if not line.strip():
            continue
        stripped = line.strip()
        if appellate and stripped in ("<!-- frontmatter -->", "<!-- body -->"):
            leaf = "frontmatter" if "frontmatter" in stripped else "body"
            new_section = doc.add_section(WD_SECTION_START.NEW_PAGE)
            new_section.footer.is_linked_to_previous = False
            for inherited in new_section._sectPr.findall(qn("w:pgNumType")):
                new_section._sectPr.remove(inherited)
            new_section._sectPr.append(element("pgNumType", start=1, fmt="lowerRoman" if leaf == "frontmatter" else "decimal"))
            signature = page_break = False
            continue
        if stripped.startswith("<!--"):
            if stripped == "<!-- pagebreak -->":
                page_break = True
                signature = False
            continue
        if court and "|" in line:
            rows = [line]
            while index < len(lines) and "|" in lines[index]:
                rows.append(lines[index])
                index += 1
            table = doc.add_table(rows=len(rows), cols=3)
            table.autofit = False
            widths = [3.5, 0.3, 2.7]
            for col, width in zip(table.columns, widths):
                col.width = Inches(width)
            borders = element("tblBorders")
            for side in ["top", "left", "bottom", "right", "insideH", "insideV"]:
                borders.append(element(side, val="nil"))
            table._tbl.tblPr.append(borders)
            margins = element("tblCellMar")
            for side in ["top", "left", "bottom", "right"]:
                margins.append(element(side, w=0, type="dxa"))
            table._tbl.tblPr.append(margins)
            for tr, row_text in zip(table.rows, rows):
                tr._tr.get_or_add_trPr().append(element("cantSplit"))
                left, right = row_text.split("|", 1)
                for c, value in enumerate([left.strip(), ")", right.strip()]):
                    cell = tr.cells[c]
                    cell.width = Inches(widths[c])
                    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                    p = cell.paragraphs[0]
                    p.add_run(value)
                    p.paragraph_format.keep_with_next = True
                    if c == 1:
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            continue
        is_title = line.startswith("# ")
        is_heading = line.startswith("## ")
        if is_heading:
            assignments = line.strip() == "## Assignments of Error"
            signature = False
        if line.startswith(("Respectfully submitted", "Sincerely,")):
            signature = True
        numbered = re.match(r"^(\d+)\. (.+)$", line)
        body = re.sub(r"^#{1,2} ", "", line)
        if numbered:
            body = numbered.group(2)
        toc_entry = appellate and leaf == "frontmatter" and re.search(r"\.{3,}", body)
        if toc_entry:
            body = re.sub(r"\s*\.{3,}\s*", "\t", body)
        p = doc.add_paragraph(body, style="Title" if is_title else "Heading 1" if is_heading else "Normal")
        pf = p.paragraph_format
        if toc_entry:
            pf.tab_stops.add_tab_stop(Inches(6.5), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        if page_break:
            pf.page_break_before = True
            page_break = False
        pf.keep_together = True
        if (appellate or appellate_paper) and (is_title or is_heading or assignments):
            pf.line_spacing = 1
        if is_title:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pf.space_before, pf.space_after = Pt(8), Pt(4)
        elif is_heading:
            pf.space_before = Pt(6)
        if line.startswith("VIRGINIA:") and p.runs:
            p.runs[0].bold = True
            pf.keep_with_next = True
        if appellate and leaf == "cover":
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if numbered:
            num = element("numPr")
            num.append(element("ilvl", val=0))
            num.append(element("numId", val=number_id))
            p._p.get_or_add_pPr().append(num)
        if signature:
            pf.left_indent = Inches(3) if court and not appellate and not appellate_paper else Inches(0)
            pf.keep_with_next = True
            if line.startswith(("Respectfully submitted", "Sincerely,")):
                pf.space_before = Pt(8)
        if not court and not letter:
            pf.space_after = Pt(6)
        if letter:
            if line.startswith("Dear "):
                letter_body = True
            if letter_body and not signature:
                pf.space_after = Pt(8)
            if line.startswith("Re:"):
                pf.space_before = Pt(8)
                if p.runs:
                    p.runs[0].bold = True
            if not letter_body:
                pf.keep_with_next = True
    for i, sec in enumerate(doc.sections):
        footer = sec.footer.paragraphs[0]
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if not appellate or i > 0:
            footer._p.append(element("fldSimple", instr="PAGE"))
    props = doc.core_properties
    props.title = title
    props.author = ""
    props.last_modified_by = ""
    props.comments = "Draft for attorney review. Not legal advice."
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(target))
    return True


# --------------------------------------------------------------------------- index

def load_index():
    path = ROOT / "docs" / "templates.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))["templates"]
    rows = []
    for p in sorted(TEMPLATES.glob("*/*.md")):
        meta, _ = parse_front_matter(p.read_text(encoding="utf-8"))
        if meta:
            rows.append(meta)
    return rows


def cmd_list(args):
    words = (args.search or "").casefold().split()
    for row in load_index():
        if args.category and row["category"] != args.category:
            continue
        hay = " ".join(str(row.get(k, "")) for k in ("title", "command", "scope", "category_label")).casefold()
        if all(w in hay for w in words):
            print(f"{row['command']:<30} {row['layout']:<16} {row['category']:<20} {row['title']}")


def cmd_fields(args):
    path, meta, body = load_template(args.template)
    summary = field_summary(body)
    if args.json:
        print(json.dumps({"template": meta.get("command"), "layout": meta.get("layout"), "fields": summary}, indent=1, ensure_ascii=False))
        return
    print(f"{meta.get('title')} ({meta.get('command')}) - layout {meta.get('layout')}, {len(summary)} distinct fields")
    for item in summary:
        extra = ""
        if len(item["keys"]) > 1:
            extra = "   contexts: " + ", ".join(item["keys"][1:])
        print(f"  [{item['name']}] x{item['count']}{extra}")


def cmd_fill(args):
    path, meta, body = load_template(args.template)
    values = json.loads(Path(args.values).read_text(encoding="utf-8")) if args.values else {}
    filled, unresolved = fill(body, values)
    out = Path(args.out) if args.out else None
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(filled, encoding="utf-8")
    else:
        sys.stdout.write(filled)
    report = {
        "template": meta.get("command"),
        "title": meta.get("title"),
        "layout": meta.get("layout"),
        "unresolved": unresolved,
        "markdown": str(out) if out else None,
        "docx": None,
    }
    if args.docx:
        if render_docx(filled, meta.get("layout", "DOCUMENT"), args.docx, meta.get("title", "")):
            report["docx"] = args.docx
        else:
            print("python-docx is not installed; wrote Markdown only (pip install python-docx).", file=sys.stderr)
    report["warnings"] = check_draft(filled, values)
    for w in report["warnings"]:
        print("check:", w, file=sys.stderr)
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    if unresolved:
        print(f"{len(unresolved)} field(s) still bracketed:", file=sys.stderr)
        for u in unresolved:
            print(f"  [{u['name']}] x{u['count']}", file=sys.stderr)


def cmd_check(args):
    text = Path(args.draft).read_text(encoding="utf-8")
    values = json.loads(Path(args.values).read_text(encoding="utf-8")) if args.values else {}
    warnings = check_draft(text, values)
    for w in warnings:
        print(w)
    left = unresolved_fields(text)
    if left:
        print(f"{len(left)} field(s) still bracketed: " + ", ".join(f"[{u['name']}]" for u in left))
    if not warnings and not left:
        print("No flags. Still review every value against the case file.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list")
    p.add_argument("--category")
    p.add_argument("--search")
    p.set_defaults(func=cmd_list)
    p = sub.add_parser("fields")
    p.add_argument("template")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_fields)
    p = sub.add_parser("fill")
    p.add_argument("template")
    p.add_argument("--values")
    p.add_argument("--out")
    p.add_argument("--docx")
    p.add_argument("--report")
    p.set_defaults(func=cmd_fill)
    p = sub.add_parser("check")
    p.add_argument("draft")
    p.add_argument("--values")
    p.set_defaults(func=cmd_check)
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
