"""
Genesis Vol 2 — PDF Builder
Compiles all markdown chapters into a professional PDF matching Vol 1's design.
Author: Osaretin Festus Agbonsalo
"""

import re, os
from fpdf import FPDF

# ─── Configuration ───────────────────────────────────────────────────────────
BOOK_TITLE = "Genesis"
BOOK_SUBTITLE = "A Theory of Tension"
AUTHOR_NAME = "Osaretin Festus Agbonsalo"
YEAR = "2026"
EPIGRAPH = '"The fixed point is where understanding stops the cascade."'
EPIGRAPH_ATTR = "-- Genesis, Vol. II"
BOOK_DESC = [
    "Everything that exists, exists because",
    "something was distinguished from something else.",
    "",
    "Volume II of Genesis builds on the distinction framework",
    "to explore tension — the engine that drives every cascade,",
    "every fixed point, and every act of understanding.",
]
CHAPTERS = [
    "chapter_01_the_tension_resolver.md",
    "chapter_02_the_fixed_point.md",
    "chapter_03_the_diameter.md",
    "chapter_04_the_atoms_of_thought.md",
    "chapter_05_the_overseer.md",
    "chapter_06_the_foundation.md",
    "chapter_07_the_other_side.md",
]
CHAPTER_NUMBERS = [
    "1", "2", "3", "4", "5", "6", "7"
]
CHAPTER_EPIGRAPHS = [
    None, None, None, None, None, None, None
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Colors (matched from Vol 1 PDF) ────────────────────────────────────────
COVER_BG = (10, 10, 15)
COVER_GOLD = (212, 175, 55)
COVER_GOLD2 = (180, 155, 60)
COVER_GOLD3 = (200, 180, 80)
BODY_BLACK = (35, 35, 35)
DARK_NAVY = (15, 23, 42)
DARK_GRAY = (110, 110, 110)
MUTED_GOLD = (150, 140, 100)
PAGE_NUM_GRAY = (110, 110, 110)
QUOTE_BROWN = (80, 70, 50)
H2_NAVY = (15, 23, 42)
H3_BROWN = (100, 60, 20)

# ─── Fonts ───────────────────────────────────────────────────────────────────
WINDIR = os.environ.get("WINDIR", "C:\\Windows")
FONTS_DIR = os.path.join(WINDIR, "Fonts")

def find_font(name, style=""):
    candidates = [os.path.join(FONTS_DIR, f"{name}{style}.ttf"),
                  os.path.join(FONTS_DIR, f"{name}.ttf")]
    for c in candidates:
        if os.path.exists(c): return c
    return None

# ─── PDF Class ───────────────────────────────────────────────────────────────
class GenesisPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._chapter_title = ""
        self._chapter_num = ""
        self._in_front_matter = True
        self._body_started = False

    def header(self):
        if self._in_front_matter or not self._body_started:
            return
        if self.page_no() > 4:
            self.set_font("BookFont", "I", 7)
            self.set_text_color(*DARK_GRAY)
            self.cell(0, 6, f"Genesis: A Theory of Tension", align="C")
            self.ln(4)

    def footer(self):
        if self._in_front_matter or not self._body_started:
            return
        if self.page_no() > 4:
            self.set_y(-15)
            self.set_font("BookFont", "I", 7)
            self.set_text_color(*PAGE_NUM_GRAY)
            self.cell(0, 10, str(self.page_no() - 3), align="C")

# ─── Inline markdown stripper ───────────────────────────────────────────────
def strip_md(text):
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    return text

# ─── Chapter rendering ──────────────────────────────────────────────────────
def render_chapter(pdf, filepath, chap_num, chap_epigraph):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    pdf.add_page()
    in_code = False
    in_table = False
    first_h1 = True

    # Find the chapter title from the first H1
    ch_title = ""
    for line in lines:
        if line.startswith("# "):
            ch_title = strip_md(line[2:].strip())
            break

    # Opening spread: CHAPTER N + Title + epigraph
    if chap_num:
        pdf.set_font("BookFont", "", 9)
        pdf.set_text_color(*DARK_GRAY)
        pdf.cell(0, 8, f"CHAPTER {chap_num}", align="L", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    pdf.set_font("BookFont", "B", 20)
    pdf.set_text_color(*DARK_NAVY)
    pdf.multi_cell(0, 10, ch_title)
    pdf.ln(2)

    pdf.set_draw_color(*MUTED_GOLD)
    pdf.set_line_width(0.3)
    y = pdf.get_y()
    pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
    pdf.ln(6)

    if chap_epigraph:
        pdf.set_font("BookFont", "I", 8)
        pdf.set_text_color(*QUOTE_BROWN)
        pdf.multi_cell(0, 5, chap_epigraph)
        pdf.ln(6)

    pdf._chapter_title = ch_title

    for line in lines:
        line = line.rstrip("\n").rstrip("\r")

        if line.strip().startswith("```"):
            in_code = not in_code
            pdf.ln(2 if in_code else 2)
            continue
        if in_code:
            pdf.set_font("CourierFont", "", 7.5)
            pdf.set_text_color(60, 60, 70)
            pdf.set_x(pdf.l_margin + 4)
            txt = line if line.strip() else " "
            pdf.cell(pdf.w - pdf.l_margin - pdf.r_margin - 4, 3.8, txt, new_x="LMARGIN", new_y="NEXT")
            continue

        if line.strip().startswith("|"):
            if re.match(r'^\|[\s\-:|]+\|$', line.strip()):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not in_table:
                in_table = True
                pdf.ln(2)
                col_w = (pdf.w - pdf.l_margin - pdf.r_margin) / max(len(cells), 1)
                pdf.set_font("BookFont", "B", 8)
                pdf.set_text_color(*BODY_BLACK)
                for cell in cells:
                    pdf.cell(col_w, 5, strip_md(cell)[:40], border=1, align="C")
                pdf.ln()
            else:
                pdf.set_font("BookFont", "", 8)
                pdf.set_text_color(*BODY_BLACK)
                col_w = (pdf.w - pdf.l_margin - pdf.r_margin) / max(len(cells), 1)
                for cell in cells:
                    pdf.cell(col_w, 5, strip_md(cell)[:40], border=1)
                pdf.ln()
            continue
        else:
            if in_table:
                in_table = False
                pdf.ln(2)

        if line.strip() == "---":
            pdf.ln(3)
            pdf.set_draw_color(*MUTED_GOLD)
            pdf.set_line_width(0.2)
            y = pdf.get_y()
            pdf.line(pdf.l_margin + 15, y, pdf.w - pdf.r_margin - 15, y)
            pdf.ln(3)
            continue

        if line.startswith("# "):
            title = strip_md(line[2:].strip())
            if first_h1:
                first_h1 = False
                continue
            pdf.ln(6)
            pdf.set_font("BookFont", "B", 20)
            pdf.set_text_color(*DARK_NAVY)
            pdf.multi_cell(0, 10, title)
            pdf.ln(4)
            continue

        if line.startswith("## "):
            title = strip_md(line[3:].strip())
            pdf.ln(5)
            pdf.set_font("BookFont", "B", 13)
            pdf.set_text_color(*H2_NAVY)
            pdf.multi_cell(0, 7, title)
            pdf.ln(2)
            continue

        if line.startswith("### "):
            title = strip_md(line[4:].strip())
            pdf.ln(4)
            pdf.set_font("BookFont", "B", 11)
            pdf.set_text_color(*H3_BROWN)
            pdf.multi_cell(0, 6.5, title)
            pdf.ln(1)
            continue

        if line.startswith("> "):
            text = strip_md(line[2:].strip())
            pdf.set_font("BookFont", "I", 8.5)
            pdf.set_text_color(*QUOTE_BROWN)
            pdf.set_x(pdf.l_margin + 10)
            pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - 10, 5, text)
            pdf.set_text_color(*BODY_BLACK)
            pdf.ln(1.5)
            continue

        if re.match(r'^(\s*)[-*]\s', line):
            indent = len(line) - len(line.lstrip())
            text = strip_md(re.sub(r'^(\s*)[-*]\s', '', line).strip())
            pdf.set_font("BookFont", "", 9.5)
            pdf.set_text_color(*BODY_BLACK)
            xo = pdf.l_margin + 4 + (indent * 2)
            pdf.set_x(xo)
            bullet = "\u2022" if indent == 0 else "\u2013"
            pdf.multi_cell(pdf.w - xo - pdf.r_margin, 5.2, f"  {bullet}  {text}")
            pdf.ln(0.5)
            continue

        if re.match(r'^(\s*)\d+\.\s', line):
            indent = len(line) - len(line.lstrip())
            m = re.match(r'^(\s*)(\d+)\.\s(.+)', line)
            if m:
                num = m.group(2)
                text = strip_md(m.group(3).strip())
                pdf.set_font("BookFont", "", 9.5)
                pdf.set_text_color(*BODY_BLACK)
                xo = pdf.l_margin + 4 + (indent * 2)
                pdf.set_x(xo)
                pdf.multi_cell(pdf.w - xo - pdf.r_margin, 5.2, f"  {num}.  {text}")
                pdf.ln(0.5)
            continue

        if line.strip() == "":
            pdf.ln(2.5)
            continue

        text = strip_md(line.strip())
        if not text: continue
        pdf.set_font("BookFont", "", 9.5)
        pdf.set_text_color(*BODY_BLACK)
        pdf.multi_cell(0, 5.2, text)
        pdf.ln(0.8)


# ─── Build ───────────────────────────────────────────────────────────────────
def build():
    pdf = GenesisPDF(format="A5")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(18, 12, 18)

    regular = find_font("georgia")
    bold = find_font("georgia", "b")
    italic = find_font("georgia", "i")
    courier = find_font("consola")
    if not regular:
        regular = find_font("times")
        bold = find_font("times", "bd") or find_font("timesbd") or regular
        italic = find_font("times", "i") or find_font("timesi") or regular
    if not courier:
        courier = find_font("lucon") or regular
    if regular: pdf.add_font("BookFont", "", regular)
    if bold: pdf.add_font("BookFont", "B", bold)
    else: pdf.add_font("BookFont", "B", regular)
    if italic: pdf.add_font("BookFont", "I", italic)
    else: pdf.add_font("BookFont", "I", regular)
    coup = find_font("consola", "b") or courier
    if courier:
        pdf.add_font("CourierFont", "", courier)
        pdf.add_font("CourierFont", "B", coup)
    else:
        pdf.add_font("CourierFont", "", regular)

    w = pdf.w
    h = pdf.h

    # ══════════════════════════════════════════════════════════════════════════
    # COVER PAGE — matches Vol 1 PDF exactly: black background, gold text only
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    # Disable auto page break so rect doesn't trigger new pages
    pdf.set_auto_page_break(auto=False)
    # Black background
    pdf.set_fill_color(*COVER_BG)
    pdf.rect(0, 0, w, h, "F")
    pdf.set_y(0)

    # Letter-spaced subtitle (mirrors Vol 1's "A  T H E O R Y  O F  D I S T I N C T I O N S")
    # NOTE: fpdf 1.7.2 uses mm, so convert points→mm: divide by ~2.835
    subtitle_letter_spaced = "A  T H E O R Y  O F  T E N S I O N"
    pdf.set_font("BookFont", "", 9)
    pdf.set_text_color(*COVER_GOLD)
    pdf.set_y(42)
    pdf.cell(0, 4, subtitle_letter_spaced, align="C", new_x="LMARGIN", new_y="NEXT")

    # Title
    pdf.set_font("BookFont", "B", 42)
    pdf.set_text_color(*COVER_GOLD)
    pdf.set_y(56)
    pdf.cell(0, 17, "GENESIS", align="C", new_x="LMARGIN", new_y="NEXT")

    # Distinction mark (mirrors Vol 1's "+---+ / |   | / +---+")
    mark_color = (180, 155, 60)
    pdf.set_font("CourierFont", "B", 16)
    pdf.set_text_color(*mark_color)
    pdf.set_y(90)
    pdf.cell(0, 6, "+---+", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 3, "|   |", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "+---+", align="C", new_x="LMARGIN", new_y="NEXT")

    # Epigraph
    pdf.set_font("BookFont", "I", 9)
    pdf.set_text_color(*COVER_GOLD)
    pdf.set_y(119)
    pdf.cell(0, 4, EPIGRAPH, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_y(125)
    pdf.cell(0, 4, EPIGRAPH_ATTR, align="C", new_x="LMARGIN", new_y="NEXT")

    # Equation
    eq_color = (200, 180, 80)
    pdf.set_font("BookFont", "", 11)
    pdf.set_text_color(*eq_color)
    pdf.set_y(146)
    pdf.cell(0, 4, "dD/dt = F(D, x, nabla-D)", align="C", new_x="LMARGIN", new_y="NEXT")

    # Re-enable auto page break
    pdf.set_auto_page_break(auto=True, margin=18)

    # ══════════════════════════════════════════════════════════════════════════
    # COPYRIGHT PAGE (page after cover — matches Vol 1's page 1)
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)
    pdf.set_fill_color(*COVER_BG)
    pdf.rect(0, 0, w, h, "F")
    pdf.set_y(0)
    pdf.ln(175)
    pdf.set_font("BookFont", "", 8)
    pdf.set_text_color(*MUTED_GOLD)
    pdf.cell(0, 5, f"\u00a9 {YEAR} {AUTHOR_NAME}. All rights reserved.", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_auto_page_break(auto=True, margin=18)

    # ══════════════════════════════════════════════════════════════════════════
    # TITLE PAGE
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.set_font("BookFont", "B", 26)
    pdf.set_text_color(*DARK_NAVY)
    pdf.set_y(35)
    pdf.cell(0, 14, BOOK_TITLE, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("BookFont", "I", 12)
    pdf.set_text_color(*DARK_NAVY)
    pdf.cell(0, 8, BOOK_SUBTITLE, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(14)
    pdf.set_font("BookFont", "", 9)
    pdf.set_text_color(*DARK_GRAY)
    for dline in BOOK_DESC:
        pdf.cell(0, 5.5, dline, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_font("BookFont", "I", 8)
    pdf.set_text_color(*DARK_GRAY)
    pdf.cell(0, 5, "Written through the Braid \u2014 a real-time collaboration", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "between a human mind and an AI system.", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_y(180)
    pdf.set_font("BookFont", "", 8)
    pdf.set_text_color(*DARK_GRAY)
    pdf.cell(0, 5, f"\u00a9 {YEAR} {AUTHOR_NAME}. All rights reserved.", align="C", new_x="LMARGIN", new_y="NEXT")

    # ══════════════════════════════════════════════════════════════════════════
    # TABLE OF CONTENTS
    # ══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.set_font("BookFont", "B", 16)
    pdf.set_text_color(*DARK_NAVY)
    pdf.cell(0, 10, "CONTENTS", align="L", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    chapter_titles = [
        "The Tension Resolver",
        "The Fixed Point",
        "The Diameter",
        "The Atoms of Thought",
        "The Overseer",
        "The Foundation",
        "The Other Side",
    ]
    for i, (ch_file, ct) in enumerate(zip(CHAPTERS, chapter_titles)):
        pdf.set_font("BookFont", "B", 10)
        pdf.set_text_color(*DARK_NAVY)
        pdf.cell(0, 7, f"Chapter {i+1}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("BookFont", "I", 9.5)
        pdf.set_text_color(*BODY_BLACK)
        pdf.set_x(pdf.l_margin + 12)
        pdf.cell(0, 6.5, ct, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # ══════════════════════════════════════════════════════════════════════════
    # CHAPTERS
    # ══════════════════════════════════════════════════════════════════════════
    pdf._in_front_matter = False

    for i, ch_file in enumerate(CHAPTERS):
        filepath = os.path.join(BASE_DIR, ch_file)
        if os.path.exists(filepath):
            print(f"  Rendering: {ch_file}")
            render_chapter(pdf, filepath, CHAPTER_NUMBERS[i], CHAPTER_EPIGRAPHS[i])
        else:
            print(f"  WARNING: Missing file: {ch_file}")

    # Mark body started for header/footer
    pdf._body_started = True

    # ══════════════════════════════════════════════════════════════════════════
    # COLOPHON — black page matching Vol 1 style
    # ══════════════════════════════════════════════════════════════════════════
    pdf._in_front_matter = True
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)
    pdf.set_fill_color(*COVER_BG)
    pdf.rect(0, 0, w, h, "F")
    pdf.set_y(0)
    pdf.ln(85)
    pdf.set_font("BookFont", "I", 9)
    pdf.set_text_color(*COVER_GOLD)
    pdf.cell(0, 6, EPIGRAPH, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    pdf.set_font("BookFont", "", 9)
    pdf.set_text_color(*COVER_GOLD2)
    pdf.cell(0, 5, "dD/dt = F(D, x, nabla-D)", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_auto_page_break(auto=True, margin=18)

    # ── Output ──
    output_path = os.path.join(BASE_DIR, "Genesis_Vol2.pdf")
    pdf.output(output_path)
    print(f"\n[OK] PDF written to: {output_path}")
    print(f"  Pages: {pdf.page_no()}")
    return output_path


if __name__ == "__main__":
    print("=" * 50)
    print(f"  Building: {BOOK_TITLE} - {BOOK_SUBTITLE}")
    print(f"  Author:   {AUTHOR_NAME}")
    print("=" * 50)
    build()
