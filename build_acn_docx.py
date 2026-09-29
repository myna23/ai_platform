"""
Convert ACN_Zambia_GeoHub_AI_Solution_Architecture.md → Word .docx
Run: python build_acn_docx.py
"""

import re
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

# ── Colours ──────────────────────────────────────────────────────────────────
WB_BLUE       = RGBColor(0x1D, 0x35, 0x57)   # dark navy
WB_MID        = RGBColor(0x2A, 0x64, 0x96)   # medium blue
WB_LIGHT      = RGBColor(0xE8, 0xF4, 0xFD)   # light blue (table header bg)
WHITE         = RGBColor(0xFF, 0xFF, 0xFF)
GREY_TEXT     = RGBColor(0x44, 0x44, 0x44)
TABLE_STRIPE  = RGBColor(0xF5, 0xF8, 0xFC)


def set_cell_bg(cell, hex_colour: str):
    """Set cell background colour via XML."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_colour)
    tcPr.append(shd)


def set_cell_border(cell, **kwargs):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        tag = OxmlElement(f'w:{edge}')
        tag.set(qn('w:val'),   kwargs.get('val',   'single'))
        tag.set(qn('w:sz'),    kwargs.get('sz',    '4'))
        tag.set(qn('w:space'), '0')
        tag.set(qn('w:color'), kwargs.get('color', 'BFCFDF'))
        tcBorders.append(tag)
    tcPr.append(tcBorders)


def add_run_with_inline(para, text: str, bold=False, italic=False,
                        font_size=None, color=None):
    """Add a run, processing **bold** and *italic* inline markers."""
    # Split on ** markers
    parts = re.split(r'(\*\*[^*]+\*\*)', text)
    for part in parts:
        m_bold = re.match(r'\*\*([^*]+)\*\*', part)
        if m_bold:
            r = para.add_run(m_bold.group(1))
            r.bold = True
        else:
            r = para.add_run(part)
            r.bold = bold
        r.italic = italic
        if font_size:
            r.font.size = Pt(font_size)
        if color:
            r.font.color.rgb = color


def build_docx(md_path: str, out_path: str):
    doc = Document()

    # ── Page margins ─────────────────────────────────────────────────────────
    for section in doc.sections:
        section.top_margin    = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin   = Cm(2.8)
        section.right_margin  = Cm(2.8)

    # ── Default paragraph style ───────────────────────────────────────────────
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(10.5)
    style.font.color.rgb = GREY_TEXT

    # ── Read markdown ─────────────────────────────────────────────────────────
    with open(md_path, encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    in_code_block = False
    code_lines    = []

    def flush_code():
        nonlocal code_lines
        if not code_lines:
            return
        para = doc.add_paragraph()
        para.paragraph_format.left_indent = Cm(0.8)
        para.paragraph_format.space_before = Pt(4)
        para.paragraph_format.space_after  = Pt(4)
        run = para.add_run('\n'.join(code_lines))
        run.font.name = 'Courier New'
        run.font.size = Pt(8.5)
        run.font.color.rgb = RGBColor(0x1D, 0x35, 0x57)
        # light grey shading via XML
        pPr = para._p.get_or_add_pPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'),   'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'),  'F0F4F9')
        pPr.append(shd)
        code_lines = []

    while i < len(lines):
        raw = lines[i].rstrip('\n')
        i  += 1

        # ── Code block fence ─────────────────────────────────────────────────
        if raw.strip().startswith('```'):
            if in_code_block:
                flush_code()
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(raw)
            continue

        # ── Horizontal rule ──────────────────────────────────────────────────
        if re.match(r'^-{3,}$', raw.strip()):
            para = doc.add_paragraph()
            pPr  = para._p.get_or_add_pPr()
            pBdr = OxmlElement('w:pBdr')
            bot  = OxmlElement('w:bottom')
            bot.set(qn('w:val'),   'single')
            bot.set(qn('w:sz'),    '6')
            bot.set(qn('w:space'), '1')
            bot.set(qn('w:color'), '1D3557')
            pBdr.append(bot)
            pPr.append(pBdr)
            para.paragraph_format.space_after = Pt(6)
            continue

        # ── Markdown tables ───────────────────────────────────────────────────
        if raw.strip().startswith('|'):
            # Collect all table rows
            tbl_rows = [raw]
            while i < len(lines) and lines[i].strip().startswith('|'):
                tbl_rows.append(lines[i].rstrip('\n'))
                i += 1

            # Parse rows (skip separator rows: |---|---|)
            parsed = []
            for row in tbl_rows:
                if re.match(r'^\s*\|[-| :]+\|\s*$', row):
                    continue
                cells = [c.strip() for c in row.strip().strip('|').split('|')]
                parsed.append(cells)

            if not parsed:
                continue

            n_cols = max(len(r) for r in parsed)
            # Pad short rows
            parsed = [r + [''] * (n_cols - len(r)) for r in parsed]

            tbl = doc.add_table(rows=len(parsed), cols=n_cols)
            tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
            tbl.style     = 'Table Grid'

            for ri, row in enumerate(parsed):
                for ci, cell_text in enumerate(row):
                    cell = tbl.cell(ri, ci)
                    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

                    # Background
                    if ri == 0:
                        set_cell_bg(cell, '1D3557')
                    elif ri % 2 == 0:
                        set_cell_bg(cell, 'F0F5FA')
                    else:
                        set_cell_bg(cell, 'FFFFFF')

                    set_cell_border(cell)

                    para = cell.paragraphs[0]
                    para.paragraph_format.space_before = Pt(3)
                    para.paragraph_format.space_after  = Pt(3)
                    run  = para.add_run(cell_text)
                    run.font.size = Pt(9.5)
                    if ri == 0:
                        run.bold = True
                        run.font.color.rgb = WHITE
                    else:
                        run.font.color.rgb = GREY_TEXT

            doc.add_paragraph()  # spacing after table
            continue

        # ── Headings ─────────────────────────────────────────────────────────
        m = re.match(r'^(#{1,4})\s+(.*)', raw)
        if m:
            level = len(m.group(1))
            text  = m.group(2).strip()

            if level == 1:
                # Big title / cover
                para = doc.add_paragraph()
                para.paragraph_format.space_before = Pt(18)
                para.paragraph_format.space_after  = Pt(6)
                run  = para.add_run(text)
                run.bold             = True
                run.font.size        = Pt(22)
                run.font.color.rgb   = WB_BLUE
                run.font.name        = 'Calibri'
                para.alignment       = WD_ALIGN_PARAGRAPH.LEFT

            elif level == 2:
                # Section heading — with coloured left border effect (shaded para)
                para = doc.add_paragraph()
                para.paragraph_format.space_before = Pt(14)
                para.paragraph_format.space_after  = Pt(4)
                run  = para.add_run(text)
                run.bold           = True
                run.font.size      = Pt(14)
                run.font.color.rgb = WB_BLUE
                run.font.name      = 'Calibri'
                # Add bottom border
                pPr  = para._p.get_or_add_pPr()
                pBdr = OxmlElement('w:pBdr')
                bot  = OxmlElement('w:bottom')
                bot.set(qn('w:val'),   'single')
                bot.set(qn('w:sz'),    '8')
                bot.set(qn('w:space'), '1')
                bot.set(qn('w:color'), '2A6496')
                pBdr.append(bot)
                pPr.append(pBdr)

            elif level == 3:
                para = doc.add_paragraph()
                para.paragraph_format.space_before = Pt(10)
                para.paragraph_format.space_after  = Pt(3)
                run  = para.add_run(text)
                run.bold           = True
                run.font.size      = Pt(12)
                run.font.color.rgb = WB_MID
                run.font.name      = 'Calibri'

            else:  # level 4
                para = doc.add_paragraph()
                para.paragraph_format.space_before = Pt(8)
                para.paragraph_format.space_after  = Pt(2)
                run  = para.add_run(text)
                run.bold           = True
                run.font.size      = Pt(10.5)
                run.font.color.rgb = GREY_TEXT
                run.font.name      = 'Calibri'

            continue

        # ── Bullet list ───────────────────────────────────────────────────────
        m_bullet = re.match(r'^(\s*)[-*]\s+(.*)', raw)
        if m_bullet:
            indent = len(m_bullet.group(1)) // 2
            text   = m_bullet.group(2)
            para   = doc.add_paragraph(style='List Bullet')
            para.paragraph_format.left_indent  = Cm(0.5 + indent * 0.5)
            para.paragraph_format.space_before = Pt(1)
            para.paragraph_format.space_after  = Pt(1)
            add_run_with_inline(para, text, font_size=10.5, color=GREY_TEXT)
            continue

        # ── Numbered list ─────────────────────────────────────────────────────
        m_num = re.match(r'^(\s*)\d+\.\s+(.*)', raw)
        if m_num:
            text = m_num.group(2)
            para = doc.add_paragraph(style='List Number')
            para.paragraph_format.space_before = Pt(1)
            para.paragraph_format.space_after  = Pt(1)
            add_run_with_inline(para, text, font_size=10.5, color=GREY_TEXT)
            continue

        # ── Blank line ────────────────────────────────────────────────────────
        if raw.strip() == '':
            continue

        # ── Blockquote (>) ────────────────────────────────────────────────────
        m_bq = re.match(r'^>\s*(.*)', raw)
        if m_bq:
            para = doc.add_paragraph()
            para.paragraph_format.left_indent  = Cm(0.8)
            para.paragraph_format.space_before = Pt(2)
            para.paragraph_format.space_after  = Pt(2)
            pPr  = para._p.get_or_add_pPr()
            pBdr = OxmlElement('w:pBdr')
            left = OxmlElement('w:left')
            left.set(qn('w:val'),   'single')
            left.set(qn('w:sz'),    '12')
            left.set(qn('w:space'), '4')
            left.set(qn('w:color'), '2A6496')
            pBdr.append(left)
            pPr.append(pBdr)
            add_run_with_inline(para, m_bq.group(1), font_size=10, color=WB_MID)
            continue

        # ── Normal paragraph ──────────────────────────────────────────────────
        para = doc.add_paragraph()
        para.paragraph_format.space_before = Pt(2)
        para.paragraph_format.space_after  = Pt(4)
        add_run_with_inline(para, raw, font_size=10.5, color=GREY_TEXT)

    # ── Architecture diagram placeholder pages ────────────────────────────────
    doc.add_page_break()

    # Figure 1 placeholder
    p1 = doc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p1.add_run('Figure 1: Deployment Architecture Diagram')
    r1.bold = True; r1.font.size = Pt(13); r1.font.color.rgb = WB_BLUE

    box1 = doc.add_paragraph()
    box1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    box1.paragraph_format.space_before = Pt(12)
    box1.paragraph_format.space_after  = Pt(6)
    br1 = box1.add_run(
        '\n\n\n'
        '[ INSERT FIGURE 1 HERE ]\n'
        'Screenshot from ACN_Architecture_Diagrams.html — Figure 1\n'
        '\n\n\n'
    )
    br1.font.size      = Pt(11)
    br1.font.color.rgb = RGBColor(0x99, 0xAA, 0xBB)
    br1.italic         = True
    pPr  = box1._p.get_or_add_pPr()
    shd  = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  'F0F5FA')
    pPr.append(shd)

    cap1 = doc.add_paragraph(
        'The diagram above shows the full deployment architecture: '
        'user browser → WBG Posit Connect (Streamlit app) → '
        'Zambia GeoHub (ArcGIS FeatureServer, public datasets) + '
        'WBG mAI Factory via Azure APIM Gateway (GPT-5 / Claude Sonnet). '
        'All connections use HTTPS with certificate validation enforced. '
        'Authentication detail: Posit Connect OAuth token exchange (RFC 8693) for '
        'mAI Factory. Zambia GeoHub public datasets require no credential — '
        'private/token-based dataset access was removed from scope under '
        'ACN-2026-31023.'
    )
    cap1.paragraph_format.space_before = Pt(4)
    cap1.paragraph_format.space_after  = Pt(18)
    cap1.runs[0].font.size      = Pt(9.5)
    cap1.runs[0].font.color.rgb = RGBColor(0x55, 0x66, 0x77)
    cap1.runs[0].italic         = True

    doc.add_page_break()

    # Figure 2 placeholder
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run('Figure 2: Question-to-Answer Process Flow')
    r2.bold = True; r2.font.size = Pt(13); r2.font.color.rgb = WB_BLUE

    box2 = doc.add_paragraph()
    box2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    box2.paragraph_format.space_before = Pt(12)
    box2.paragraph_format.space_after  = Pt(6)
    br2 = box2.add_run(
        '\n\n\n'
        '[ INSERT FIGURE 2 HERE ]\n'
        'Screenshot from ACN_Architecture_Diagrams.html — Figure 2\n'
        '\n\n\n'
    )
    br2.font.size      = Pt(11)
    br2.font.color.rgb = RGBColor(0x99, 0xAA, 0xBB)
    br2.italic         = True
    pPr2  = box2._p.get_or_add_pPr()
    shd2  = OxmlElement('w:shd')
    shd2.set(qn('w:val'),   'clear')
    shd2.set(qn('w:color'), 'auto')
    shd2.set(qn('w:fill'),  'F0F5FA')
    pPr2.append(shd2)

    cap2 = doc.add_paragraph(
        'The diagram above shows the 8-step data flow: '
        '(1) User query → (2) Intent detection → (3) Location/topic extraction → '
        '(4) Dataset catalog search → (5) Live ArcGIS data fetch → '
        '(6) AI prompt construction → (7) mAI Factory inference (OAuth Bearer) → '
        '(8) Display: text answer + interactive map + data table + report download.'
    )
    cap2.paragraph_format.space_before = Pt(4)
    cap2.paragraph_format.space_after  = Pt(18)
    cap2.runs[0].font.size      = Pt(9.5)
    cap2.runs[0].font.color.rgb = RGBColor(0x55, 0x66, 0x77)
    cap2.runs[0].italic         = True

    # ── Save ─────────────────────────────────────────────────────────────────
    doc.save(out_path)
    print(f"Saved: {out_path}")


if __name__ == '__main__':
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    build_docx(
        md_path  = os.path.join(base, 'ACN_Zambia_GeoHub_AI_Solution_Architecture.md'),
        out_path = os.path.join(base, 'ACN_Zambia_GeoHub_AI.docx'),
    )
