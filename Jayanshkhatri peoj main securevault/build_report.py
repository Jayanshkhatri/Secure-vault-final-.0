from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    HRFlowable, KeepTogether, ListFlowable, ListItem
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle, Polygon
from reportlab.graphics import renderPDF
import os

W, H = A4
MARGIN = 2.5 * cm

# ──── COLORS ────
NAVY      = colors.HexColor('#0B1437')
GOLD      = colors.HexColor('#C8960C')
GOLD_LIGHT= colors.HexColor('#F5C842')
GOLD_PALE = colors.HexColor('#FFF8E7')
DARK_BG   = colors.HexColor('#1A1A2E')
MID_BLUE  = colors.HexColor('#16213E')
ACCENT    = colors.HexColor('#0F3460')
WHITE     = colors.white
BLACK     = colors.black
LIGHT_GREY= colors.HexColor('#F4F4F4')
MID_GREY  = colors.HexColor('#CCCCCC')
DARK_GREY = colors.HexColor('#555555')
GREEN_OK  = colors.HexColor('#27AE60')
RED_ERR   = colors.HexColor('#E74C3C')
ORANGE_W  = colors.HexColor('#E67E22')

def styles():
    S = getSampleStyleSheet()

    def add(name, **kw):
        if name not in S:
            S.add(ParagraphStyle(name=name, **kw))
        return S[name]

    add('Cover_Title',
        fontName='Helvetica-Bold', fontSize=32, textColor=GOLD,
        alignment=TA_CENTER, leading=40, spaceAfter=8)
    add('Cover_Sub',
        fontName='Helvetica-Bold', fontSize=18, textColor=WHITE,
        alignment=TA_CENTER, leading=26, spaceAfter=6)
    add('Cover_Body',
        fontName='Helvetica', fontSize=11, textColor=colors.HexColor('#DDDDDD'),
        alignment=TA_CENTER, leading=18, spaceAfter=4)
    add('Cover_Label',
        fontName='Helvetica-Bold', fontSize=10, textColor=GOLD_LIGHT,
        alignment=TA_CENTER, leading=16, spaceAfter=2)

    add('ChapterNum',
        fontName='Helvetica-Bold', fontSize=11, textColor=GOLD,
        alignment=TA_LEFT, leading=16, spaceAfter=4)
    add('ChapterTitle',
        fontName='Helvetica-Bold', fontSize=24, textColor=NAVY,
        alignment=TA_LEFT, leading=30, spaceAfter=12)
    add('SectionTitle',
        fontName='Helvetica-Bold', fontSize=14, textColor=NAVY,
        alignment=TA_LEFT, leading=20, spaceBefore=14, spaceAfter=6)
    add('SubSectionTitle',
        fontName='Helvetica-Bold', fontSize=12, textColor=ACCENT,
        alignment=TA_LEFT, leading=18, spaceBefore=10, spaceAfter=5)
    add('Body',
        fontName='Helvetica', fontSize=11, textColor=colors.HexColor('#222222'),
        alignment=TA_JUSTIFY, leading=18, spaceAfter=8)
    add('BodySmall',
        fontName='Helvetica', fontSize=10, textColor=DARK_GREY,
        alignment=TA_JUSTIFY, leading=16, spaceAfter=6)
    add('Code',
        fontName='Courier', fontSize=9, textColor=colors.HexColor('#1A1A1A'),
        alignment=TA_LEFT, leading=13, spaceAfter=4,
        backColor=colors.HexColor('#F5F5F5'), leftIndent=12, rightIndent=12,
        borderPadding=6)
    add('TableHeader',
        fontName='Helvetica-Bold', fontSize=10, textColor=WHITE,
        alignment=TA_CENTER, leading=14)
    add('TableCell',
        fontName='Helvetica', fontSize=9.5, textColor=colors.HexColor('#1A1A1A'),
        alignment=TA_LEFT, leading=14)
    add('TableCellC',
        fontName='Helvetica', fontSize=9.5, textColor=colors.HexColor('#1A1A1A'),
        alignment=TA_CENTER, leading=14)
    add('Caption',
        fontName='Helvetica-Oblique', fontSize=9.5, textColor=DARK_GREY,
        alignment=TA_CENTER, leading=14, spaceBefore=4, spaceAfter=10)
    add('TOC_Chapter',
        fontName='Helvetica-Bold', fontSize=11, textColor=NAVY,
        alignment=TA_LEFT, leading=20)
    add('TOC_Section',
        fontName='Helvetica', fontSize=10, textColor=DARK_GREY,
        alignment=TA_LEFT, leading=18, leftIndent=20)
    add('Bullet',
        fontName='Helvetica', fontSize=11, textColor=colors.HexColor('#222222'),
        alignment=TA_LEFT, leading=18, leftIndent=16, spaceAfter=4,
        bulletIndent=4, bulletFontName='Helvetica', bulletFontSize=11)
    add('Note',
        fontName='Helvetica-Oblique', fontSize=10, textColor=ACCENT,
        alignment=TA_LEFT, leading=16, leftIndent=12, spaceAfter=6)
    add('ScreenshotPlaceholder',
        fontName='Helvetica-Oblique', fontSize=10, textColor=DARK_GREY,
        alignment=TA_CENTER, leading=16)
    return S

S = styles()

# ──────────────────────────────────────────────
# Custom Flowables
# ──────────────────────────────────────────────
class GoldRule(Flowable):
    def __init__(self, w=None):
        super().__init__()
        self.rule_w = w
    def wrap(self, aw, ah): self._aw = aw; return (aw, 3)
    def draw(self):
        c = self.canv
        w = self.rule_w or self._aw
        c.setFillColor(GOLD)
        c.rect(0, 0, w, 2, fill=1, stroke=0)

class ScreenshotBox(Flowable):
    def __init__(self, label, height=7*cm):
        super().__init__()
        self.label = label
        self.box_h = height
    def wrap(self, aw, ah): self._aw = aw; return (aw, self.box_h + 0.4*cm)
    def draw(self):
        c = self.canv
        w, h = self._aw, self.box_h
        c.setFillColor(colors.HexColor('#F9F9F9'))
        c.setStrokeColor(colors.HexColor('#AAAAAA'))
        c.setLineWidth(0.8)
        c.roundRect(0, 0.4*cm, w, h, 8, fill=1, stroke=1)
        # dashed border effect
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.5)
        c.setDash([4, 4])
        c.roundRect(4, 0.4*cm+4, w-8, h-8, 6, fill=0, stroke=1)
        c.setDash([])
        # camera icon
        cx, cy = w/2, 0.4*cm + h/2 + 12
        c.setFillColor(colors.HexColor('#CCCCCC'))
        c.circle(cx, cy, 18, fill=1, stroke=0)
        c.setFillColor(colors.HexColor('#EEEEEE'))
        c.circle(cx, cy, 10, fill=1, stroke=0)
        # text
        c.setFont('Helvetica-Bold', 10)
        c.setFillColor(DARK_GREY)
        c.drawCentredString(w/2, 0.4*cm + h/2 - 22, self.label)
        c.setFont('Helvetica-Oblique', 8)
        c.setFillColor(colors.HexColor('#AAAAAA'))
        c.drawCentredString(w/2, 0.4*cm + h/2 - 36, '[Add Screenshot Here]')

class FlowchartBox(Flowable):
    """Renders a multi-step flowchart."""
    def __init__(self, title, steps, width=None, height=None):
        super().__init__()
        self.title = title
        self.steps = steps  # list of (label, color_hex, shape)  shape: 'rect'|'diamond'|'oval'
        self._w = width or 14*cm
        self._h = height
    def wrap(self, aw, ah):
        self._aw = aw
        n = len(self.steps)
        self._h = self._h or (n * 1.6*cm + (n-1)*0.6*cm + 2.4*cm)
        return (self._aw, self._h)
    def draw(self):
        c = self.canv
        total_h = self._h
        aw = self._aw
        bw = min(self._w, aw - 0.4*cm)
        x0 = (aw - bw)/2
        n = len(self.steps)
        box_h = 1.1*cm
        gap = 0.55*cm
        total_used = n * box_h + (n-1)*gap
        y_start = total_h - 1.5*cm  # top of first box

        # title
        c.setFont('Helvetica-Bold', 11)
        c.setFillColor(NAVY)
        c.drawCentredString(aw/2, total_h - 0.7*cm, self.title)

        for i, (label, color_hex, shape) in enumerate(self.steps):
            bx = x0
            by = y_start - i*(box_h + gap)
            col = colors.HexColor(color_hex)
            c.setFillColor(col)
            c.setStrokeColor(colors.white)
            c.setLineWidth(1.2)
            if shape == 'diamond':
                cx, cy = bx + bw/2, by - box_h/2
                dx, dy = bw/2, box_h/2
                path = c.beginPath()
                path.moveTo(cx, cy+dy); path.lineTo(cx+dx, cy)
                path.lineTo(cx, cy-dy); path.lineTo(cx-dx, cy)
                path.close(); c.drawPath(path, fill=1, stroke=1)
            elif shape == 'oval':
                c.roundRect(bx, by-box_h, bw, box_h, box_h/2, fill=1, stroke=1)
            else:
                c.roundRect(bx, by-box_h, bw, box_h, 5, fill=1, stroke=1)

            # label
            c.setFillColor(WHITE)
            c.setFont('Helvetica-Bold', 9)
            c.drawCentredString(bx+bw/2, by-box_h/2-3, label)

            # arrow down
            if i < n-1:
                ax = bx + bw/2
                ay_top = by - box_h - 2
                ay_bot = ay_top - gap + 4
                c.setStrokeColor(GOLD)
                c.setLineWidth(1.4)
                c.line(ax, ay_top, ax, ay_bot + 6)
                c.setFillColor(GOLD)
                path2 = c.beginPath()
                path2.moveTo(ax, ay_bot)
                path2.lineTo(ax-4, ay_bot+8)
                path2.lineTo(ax+4, ay_bot+8)
                path2.close()
                c.drawPath(path2, fill=1, stroke=0)

class BlockDiagram(Flowable):
    """Renders a horizontal block diagram."""
    def __init__(self, title, blocks, height=4.5*cm):
        super().__init__()
        self.title = title
        self.blocks = blocks  # list of (label, color_hex)
        self._h = height
    def wrap(self, aw, ah):
        self._aw = aw
        return (aw, self._h + 1.4*cm)
    def draw(self):
        c = self.canv
        aw = self._aw
        n = len(self.blocks)
        total_w = aw - 1*cm
        x0 = 0.5*cm
        bw_each = (total_w - (n-1)*0.5*cm) / n
        bh = self._h
        y0 = 0.7*cm

        c.setFont('Helvetica-Bold', 11)
        c.setFillColor(NAVY)
        c.drawCentredString(aw/2, y0 + bh + 0.5*cm, self.title)

        for i, (label, color_hex) in enumerate(self.blocks):
            bx = x0 + i*(bw_each + 0.5*cm)
            by = y0
            col = colors.HexColor(color_hex)
            c.setFillColor(col)
            c.setStrokeColor(WHITE)
            c.setLineWidth(1)
            c.roundRect(bx, by, bw_each, bh, 6, fill=1, stroke=1)
            # label
            lines = label.split('\n')
            lc = len(lines)
            for j, ln in enumerate(lines):
                c.setFillColor(WHITE)
                fs = 9 if bw_each < 90 else 10
                c.setFont('Helvetica-Bold', fs)
                c.drawCentredString(bx+bw_each/2,
                    by + bh/2 + (lc-1)*7 - j*14, ln)
            # arrow
            if i < n-1:
                ax = bx + bw_each + 2
                ay = by + bh/2
                c.setStrokeColor(GOLD)
                c.setFillColor(GOLD)
                c.setLineWidth(1.4)
                c.line(ax, ay, ax+0.4*cm-6, ay)
                path = c.beginPath()
                path.moveTo(ax+0.4*cm, ay)
                path.lineTo(ax+0.4*cm-8, ay+4)
                path.lineTo(ax+0.4*cm-8, ay-4)
                path.close()
                c.drawPath(path, fill=1, stroke=0)

class SectionHeader(Flowable):
    """Full-width colored section header bar."""
    def __init__(self, chapter_num, chapter_title):
        super().__init__()
        self.num = chapter_num
        self.title = chapter_title
    def wrap(self, aw, ah): self._aw = aw; return (aw, 2.2*cm)
    def draw(self):
        c = self.canv
        c.setFillColor(NAVY)
        c.roundRect(0, 0, self._aw, 2.2*cm, 6, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.roundRect(0, 0, 0.6*cm, 2.2*cm, 6, fill=1, stroke=0)
        c.rect(0.5*cm, 0, 0.15*cm, 2.2*cm, fill=1, stroke=0)
        c.setFont('Helvetica-Bold', 10)
        c.setFillColor(GOLD_LIGHT)
        c.drawString(0.9*cm, 1.4*cm, self.num)
        c.setFont('Helvetica-Bold', 16)
        c.setFillColor(WHITE)
        c.drawString(0.9*cm, 0.5*cm, self.title)

class InfoBox(Flowable):
    def __init__(self, text, color=None, height=1.8*cm):
        super().__init__()
        self.text = text
        self.col = color or colors.HexColor('#EBF5FB')
        self.bh = height
    def wrap(self, aw, ah): self._aw = aw; return (aw, self.bh + 0.4*cm)
    def draw(self):
        c = self.canv
        c.setFillColor(self.col)
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.8)
        c.roundRect(0, 0.2*cm, self._aw, self.bh, 5, fill=1, stroke=1)
        c.setFont('Helvetica', 10)
        c.setFillColor(DARK_GREY)
        c.drawString(0.4*cm, self.bh/2, self.text)

# ──────────────────────────────────────────────
# Page Templates (header/footer)
# ──────────────────────────────────────────────
def make_page_template(is_cover=False):
    def _on_page(canv, doc):
        canv.saveState()
        if is_cover:
            pass
        else:
            # Header
            canv.setFillColor(NAVY)
            canv.rect(MARGIN, H - 1.5*cm, W - 2*MARGIN, 1*cm, fill=1, stroke=0)
            canv.setFont('Helvetica-Bold', 8.5)
            canv.setFillColor(WHITE)
            canv.drawString(MARGIN + 0.3*cm, H - 1.1*cm, 'SecureVault — B.Tech Project Report')
            canv.drawRightString(W - MARGIN - 0.3*cm, H - 1.1*cm,
                'Dept. of CSE  |  Echelon Institute of Technology')
            # Gold rule under header
            canv.setFillColor(GOLD)
            canv.rect(MARGIN, H - 1.56*cm, W - 2*MARGIN, 0.06*cm, fill=1, stroke=0)
            # Footer
            canv.setFillColor(LIGHT_GREY)
            canv.rect(MARGIN, 0.8*cm, W - 2*MARGIN, 0.06*cm, fill=1, stroke=0)
            canv.setFont('Helvetica', 8)
            canv.setFillColor(DARK_GREY)
            pg_text = f'Page {doc.page}'
            canv.drawString(MARGIN, 0.45*cm, 'J.C. Bose University of Science and Technology, YMCA Faridabad')
            canv.drawRightString(W - MARGIN, 0.45*cm, pg_text)
        canv.restoreState()
    return _on_page

# ──────────────────────────────────────────────
# Helper builders
# ──────────────────────────────────────────────
def chapter_header(num, title):
    return [
        Spacer(1, 0.5*cm),
        SectionHeader(num, title),
        Spacer(1, 0.5*cm),
        GoldRule(),
        Spacer(1, 0.4*cm),
    ]

def section(title):
    return [
        Spacer(1, 0.3*cm),
        Paragraph(title, S['SectionTitle']),
        GoldRule(6*cm),
        Spacer(1, 0.2*cm),
    ]

def subsection(title):
    return [Paragraph(title, S['SubSectionTitle'])]

def body(text):
    return [Paragraph(text, S['Body'])]

def bullet_list(items):
    out = []
    for item in items:
        out.append(Paragraph(f'<bullet>&bull;</bullet>{item}', S['Bullet']))
    return out

def space(n=0.3):
    return [Spacer(1, n*cm)]

def pagebreak():
    return [PageBreak()]

def caption(text):
    return [Paragraph(text, S['Caption'])]

def note(text):
    return [Paragraph(f'<i>Note: {text}</i>', S['Note'])]

def make_table(data, col_widths=None, header=True):
    t = Table(data, colWidths=col_widths)
    ts_cmds = [
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,0), 10),
        ('ALIGN',      (0,0), (-1,0), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LIGHT_GREY]),
        ('FONTNAME',   (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',   (0,1), (-1,-1), 9.5),
        ('GRID',       (0,0), (-1,-1), 0.5, MID_GREY),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW',  (0,0), (-1,0), 2, GOLD),
    ]
    t.setStyle(TableStyle(ts_cmds))
    return t

# ──────────────────────────────────────────────
# COVER PAGE
# ──────────────────────────────────────────────
def build_cover(canv, doc):
    canv.saveState()
    # Background gradient
    canv.setFillColor(NAVY)
    canv.rect(0, 0, W, H, fill=1, stroke=0)
    # Decorative gold bar top
    canv.setFillColor(GOLD)
    canv.rect(0, H-1.2*cm, W, 1.2*cm, fill=1, stroke=0)
    # Decorative gold bar bottom
    canv.rect(0, 0, W, 0.8*cm, fill=1, stroke=0)
    # Side accent
    canv.setFillColor(colors.HexColor('#1A2550'))
    canv.rect(0, 0.8*cm, 1.2*cm, H-2*cm, fill=1, stroke=0)
    canv.setFillColor(GOLD)
    canv.rect(0, 0.8*cm, 0.25*cm, H-2*cm, fill=1, stroke=0)

    # Watermark-style circuit lines
    canv.setStrokeColor(colors.HexColor('#1A2255'))
    canv.setLineWidth(0.6)
    for y in range(50, int(H-50), 40):
        canv.line(1.5*cm, y, W-1*cm, y)

    # Institution logo area (placeholder circle)
    cx = W/2
    canv.setFillColor(colors.HexColor('#0F1F4A'))
    canv.setStrokeColor(GOLD)
    canv.setLineWidth(2)
    canv.circle(cx, H-3.5*cm, 1.4*cm, fill=1, stroke=1)
    canv.setFont('Helvetica-Bold', 11)
    canv.setFillColor(GOLD_LIGHT)
    canv.drawCentredString(cx, H-3.6*cm, 'EIT')

    # "A Project Report on"
    canv.setFont('Helvetica', 13)
    canv.setFillColor(colors.HexColor('#AABBCC'))
    canv.drawCentredString(cx, H-5.5*cm, 'A  P R O J E C T  R E P O R T  O N')

    # Gold rule
    canv.setStrokeColor(GOLD)
    canv.setLineWidth(1.5)
    canv.line(cx-6*cm, H-5.8*cm, cx+6*cm, H-5.8*cm)

    # Title
    canv.setFont('Helvetica-Bold', 42)
    canv.setFillColor(GOLD)
    canv.drawCentredString(cx, H-7.2*cm, 'SECURE')
    canv.setFillColor(WHITE)
    canv.drawCentredString(cx, H-8.4*cm, 'VAULT')

    # Lock icon stylized
    canv.setFillColor(colors.HexColor('#0F3460'))
    canv.setStrokeColor(GOLD_LIGHT)
    canv.setLineWidth(1)
    canv.roundRect(cx-1*cm, H-10.5*cm, 2*cm, 1.6*cm, 8, fill=1, stroke=1)
    canv.setFillColor(colors.HexColor('#0B1437'))
    canv.setStrokeColor(GOLD_LIGHT)
    canv.circle(cx, H-9.6*cm, 0.4*cm, fill=0, stroke=1)
    canv.setFillColor(GOLD)
    canv.circle(cx, H-9.9*cm, 0.15*cm, fill=1, stroke=0)

    # Subtitle line
    canv.setFont('Helvetica', 12)
    canv.setFillColor(colors.HexColor('#99AACC'))
    canv.drawCentredString(cx, H-11.2*cm,
        'A Web-Based File Encryption & Decryption System')

    # Gold rule
    canv.setStrokeColor(GOLD)
    canv.setLineWidth(1)
    canv.line(cx-5*cm, H-11.6*cm, cx+5*cm, H-11.6*cm)

    # Submitted text
    canv.setFont('Helvetica', 10.5)
    canv.setFillColor(colors.HexColor('#99AACC'))
    canv.drawCentredString(cx, H-12.4*cm,
        'Submitted in Partial Fulfillment for the Award of the Degree of')
    canv.setFont('Helvetica-Bold', 12)
    canv.setFillColor(GOLD_LIGHT)
    canv.drawCentredString(cx, H-13.0*cm, 'Bachelor of Technology')
    canv.setFont('Helvetica', 10.5)
    canv.setFillColor(colors.HexColor('#99AACC'))
    canv.drawCentredString(cx, H-13.5*cm, 'in')
    canv.setFont('Helvetica-Bold', 12)
    canv.setFillColor(GOLD_LIGHT)
    canv.drawCentredString(cx, H-14.1*cm, 'Computer Science & Engineering')

    # Submitted by section
    canv.setFont('Helvetica-Bold', 11)
    canv.setFillColor(GOLD)
    canv.drawCentredString(cx, H-15.2*cm, 'S U B M I T T E D  B Y')
    canv.setFont('Helvetica', 10.5)
    canv.setFillColor(WHITE)
    canv.drawCentredString(cx, H-15.8*cm, 'Jayansh (24-CSE-CS-015)        Jatin (24-CSE-CS-014)')
    canv.drawCentredString(cx, H-16.3*cm, 'Mihir (24-CSE-CS-017)          Sagar (24-CSE-CS-024)')

    # Under guidance
    canv.setFont('Helvetica-Bold', 10.5)
    canv.setFillColor(GOLD)
    canv.drawCentredString(cx, H-17.2*cm, 'U N D E R  T H E  G U I D A N C E  O F')
    canv.setFont('Helvetica', 10.5)
    canv.setFillColor(WHITE)
    canv.drawCentredString(cx, H-17.7*cm, 'Mr. Mohammad Danish')
    canv.setFont('Helvetica-Oblique', 10)
    canv.setFillColor(colors.HexColor('#AABBCC'))
    canv.drawCentredString(cx, H-18.2*cm, '(Associate Professor, Dept. of CSE)')

    # Institution
    canv.setFillColor(colors.HexColor('#0F1F4A'))
    canv.rect(1.5*cm, 1.2*cm, W-2*cm, 2.4*cm, fill=1, stroke=0)
    canv.setFont('Helvetica-Bold', 12)
    canv.setFillColor(GOLD_LIGHT)
    canv.drawCentredString(cx, 3.1*cm,
        'DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING')
    canv.setFont('Helvetica-Bold', 11)
    canv.setFillColor(WHITE)
    canv.drawCentredString(cx, 2.5*cm,
        'ECHELON INSTITUTE OF TECHNOLOGY, FARIDABAD')
    canv.setFont('Helvetica', 10)
    canv.setFillColor(colors.HexColor('#AABBCC'))
    canv.drawCentredString(cx, 2.0*cm,
        'Affiliated to J.C. Bose University of Science & Technology, YMCA | November 2024')
    canv.restoreState()

# ──────────────────────────────────────────────
# CONTENT BUILDER
# ──────────────────────────────────────────────
def build_content():
    story = []

    # ══ DECLARATION ══
    story += chapter_header('', 'Declaration')
    story += body(
        'We hereby declare that this project report entitled <b>"Secure Vault"</b> submitted to the '
        'Department of Computer Science and Engineering, Echelon Institute of Technology, Faridabad, '
        'affiliated to J.C. Bose University of Science and Technology, YMCA, Faridabad, Haryana, '
        'in partial fulfillment of the requirements for the award of the Degree of '
        '<b>Bachelor of Technology in Computer Science and Engineering</b>, is a record of original work '
        'carried out by us under the supervision and guidance of <b>Mr. Mohammad Danish</b>, '
        'Associate Professor, Department of Computer Science and Engineering.'
    )
    story += body(
        'This project report has not been submitted previously for the award of any other degree or '
        'diploma to any other university or institution. To the best of our knowledge and belief, '
        'the work presented herein does not contain any material previously published or written by '
        'another person, except where due acknowledgment has been made in the text.'
    )
    story += space(1.2)

    sig_data = [
        ['Name: Jayansh', 'Name: Jatin'],
        ['Roll No: 24-CSE-CS-015', 'Roll No: 24-CSE-CS-014'],
        ['Date: ___________', 'Date: ___________'],
        ['Signature: ___________', 'Signature: ___________'],
        ['', ''],
        ['Name: Mihir', 'Name: Sagar'],
        ['Roll No: 24-CSE-CS-017', 'Roll No: 24-CSE-CS-024'],
        ['Date: ___________', 'Date: ___________'],
        ['Signature: ___________', 'Signature: ___________'],
    ]
    t = Table(sig_data, colWidths=[8*cm, 8*cm])
    t.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE',  (0,0), (-1,-1), 11),
        ('VALIGN',    (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING',(0,0), (-1,-1), 8),
        ('LEFTPADDING',(0,0), (-1,-1), 20),
    ]))
    story.append(t)
    story += pagebreak()

    # ══ CERTIFICATE ══
    story += chapter_header('', 'Certificate')
    story += body(
        'This is to certify that the project report entitled <b>"Secure Vault"</b>, submitted by '
        '<b>Jayansh (24-CSE-CS-015)</b>, <b>Jatin (24-CSE-CS-014)</b>, '
        '<b>Mihir (24-CSE-CS-017)</b>, and <b>Sagar (24-CSE-CS-024)</b>, '
        'in partial fulfillment of the requirement for the award of the degree of '
        '<b>Bachelor of Technology in Computer Science and Engineering</b> from '
        'Echelon Institute of Technology, Faridabad, Haryana, affiliated to '
        'J.C. Bose University of Science and Technology, YMCA, Faridabad, Haryana, '
        'is a record of original and bonafide work carried out by them under our '
        'supervision and guidance during the academic year 2024–2025.'
    )
    story += body(
        'The matter embodied in this project report is original and has not been submitted '
        'for the award of any other degree or diploma previously. The project represents '
        'an impressive demonstration of applied knowledge in cybersecurity and web application '
        'development, and has been found satisfactory.'
    )
    story += space(1.5)
    cert_data = [
        ['Supervisor', 'Head of Department'],
        ['Mr. Mohammad Danish', 'Ms. Manisha Vashisht'],
        ['Associate Professor', 'Head of Department'],
        ['Dept. of CSE', 'Dept. of CSE'],
        ['Date: ___________', 'Date: ___________'],
    ]
    t2 = Table(cert_data, colWidths=[8*cm, 8*cm])
    t2.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',  (0,0), (-1,-1), 11),
        ('VALIGN',    (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING',(0,0), (-1,-1), 8),
        ('LEFTPADDING',(0,0), (-1,-1), 20),
    ]))
    story.append(t2)
    story += pagebreak()

    # ══ ACKNOWLEDGEMENT ══
    story += chapter_header('', 'Acknowledgement')
    story += body(
        'It gives us immense pleasure and pride to present this report on our B.Tech project '
        '<b>"Secure Vault"</b>. The successful completion of this project would not have been '
        'possible without the continuous support, encouragement, and guidance of several '
        'individuals, to whom we remain sincerely grateful.'
    )
    story += body(
        'First and foremost, we express our heartfelt gratitude to <b>Mr. Mohammad Danish</b>, '
        'Associate Professor, Department of Computer Science and Engineering, Echelon Institute '
        'of Technology, Faridabad, for his invaluable guidance, constant motivation, and '
        'constructive feedback throughout the project. His sincerity, technical expertise, and '
        'perseverance have been a constant source of inspiration for our team. It is only through '
        'his cognizant efforts that our endeavors have seen the light of day.'
    )
    story += body(
        'We also take this opportunity to acknowledge the unwavering support and encouragement '
        'of <b>Ms. Manisha Vashisht</b>, Head of the Department, Computer Science and Engineering, '
        'whose administrative support and positive outlook kept our spirits high during challenging '
        'phases of the project.'
    )
    story += body(
        'We are also thankful to all the faculty members of the Department of Computer Science '
        'and Engineering for their technical assistance, knowledge sharing, and moral support '
        'throughout the duration of this project. Their constructive criticism helped us refine '
        'our ideas and implement them more effectively.'
    )
    story += body(
        'Special thanks go to our friends and classmates who offered feedback during testing '
        'phases, suggested improvements, and helped us identify usability issues in the system. '
        'Their enthusiasm and encouragement kept the team motivated.'
    )
    story += body(
        'Finally, we are deeply indebted to our families for their unconditional love, patience, '
        'and moral support during long working hours. Without their blessings and encouragement, '
        'this project would not have been completed.'
    )
    story += space(0.8)
    story += body('<b>Jayansh, Jatin, Mihir, Sagar</b>')
    story += body('Department of Computer Science and Engineering')
    story += body('Echelon Institute of Technology, Faridabad — November 2024')
    story += pagebreak()

    # ══ ABSTRACT ══
    story += chapter_header('', 'Abstract')
    story += body(
        '<b>SecureVault</b> is a full-stack, web-based file encryption and decryption system '
        'designed and developed to make cryptographic file protection accessible to everyday '
        'users. The system is built using <b>Python (Flask)</b> as the backend framework, along '
        'with <b>HTML5, CSS3, and Vanilla JavaScript</b> on the frontend, creating a cohesive and '
        'professional user experience.'
    )
    story += body(
        'The application provides a secure digital vault where users can store, encrypt, decrypt, '
        'and manage sensitive text-based files entirely within a browser. One of the core '
        'innovations of SecureVault is its <b>hash-based identity mechanism</b>: instead of '
        'traditional usernames, each user is identified by a hexadecimal <b>HashID</b> derived '
        'from their registered phone number. This approach significantly reduces the risk of '
        'phishing attacks, social engineering, and username enumeration — common vulnerabilities '
        'in conventional authentication systems.'
    )
    story += body(
        'Authentication is further strengthened through a <b>two-factor process</b>, requiring '
        'both a valid HashID and a password before any vault access is granted. This multi-layer '
        'approach ensures that even if one credential is compromised, unauthorized access remains '
        'blocked.'
    )
    story += body(
        'The system supports three encryption algorithms: <b>AES (Advanced Encryption Standard)</b> '
        'implemented via the Fernet symmetric encryption scheme — an industry-standard, '
        'cryptographically secure implementation; <b>RSA (Rivest-Shamir-Adleman)</b> simulation for '
        'conceptual demonstration of asymmetric encryption; and <b>DES (Data Encryption Standard)</b> '
        'simulation for legacy and educational purposes.'
    )
    story += body(
        'The frontend features a visually refined dark gold-and-amber interface with glassmorphism '
        'card effects, animated canvas backgrounds, smooth page transitions, and a fully functional '
        'dashboard showing real-time file encryption statistics. The system consists of '
        '<b>fourteen distinct HTML pages</b>, each connected through Flask routing.'
    )
    story += body(
        'This project demonstrates the practical and accessible implementation of cryptographic '
        'principles within a real-world web application, serving as a strong educational artifact '
        'in applied cybersecurity and full-stack development.'
    )
    story += space(0.5)
    kw_data = [['Keywords']]
    kw_content = [['Flask, AES-256, RSA, DES, Fernet, Hash Identity, File Encryption,\nCybersecurity, Web Application, Python, Two-Factor Authentication']]
    kw = Table(kw_data + kw_content, colWidths=[W - 2*MARGIN - 0.2*cm])
    kw.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,0), NAVY),
        ('TEXTCOLOR', (0,0),(0,0), WHITE),
        ('FONTNAME',  (0,0),(0,0), 'Helvetica-Bold'),
        ('FONTSIZE',  (0,0),(0,0), 10),
        ('FONTNAME',  (0,1),(0,1), 'Helvetica'),
        ('FONTSIZE',  (0,1),(0,1), 10),
        ('BACKGROUND',(0,1),(0,1), GOLD_PALE),
        ('GRID',      (0,0),(-1,-1), 0.5, MID_GREY),
        ('TOPPADDING',(0,0),(-1,-1), 8),
        ('BOTTOMPADDING',(0,0),(-1,-1), 8),
        ('LEFTPADDING',(0,0),(-1,-1), 10),
    ]))
    story.append(kw)
    story += pagebreak()

    # ══ TABLE OF CONTENTS ══
    story += chapter_header('', 'Table of Contents')
    toc_entries = [
        ('Declaration', 'ii'),
        ('Certificate', 'iii'),
        ('Acknowledgement', 'iv'),
        ('Abstract', 'v'),
        ('List of Figures', 'viii'),
        ('List of Tables', 'ix'),
        ('Chapter 1: Introduction', '1'),
        ('    1.1  Background and Overview', '1'),
        ('    1.2  Motivation', '3'),
        ('    1.3  Problem Statement', '4'),
        ('    1.4  Technology Stack', '5'),
        ('    1.5  Scope of the Project', '6'),
        ('    1.6  Project Highlights', '7'),
        ('Chapter 2: Literature Review', '8'),
        ('    2.1  Existing Encryption Tools', '8'),
        ('    2.2  Authentication Mechanisms', '10'),
        ('    2.3  Research Gap and Motivation', '11'),
        ('Chapter 3: Objectives', '13'),
        ('    3.1  Primary Objectives', '13'),
        ('    3.2  Secondary Objectives', '14'),
        ('    3.3  Functional Goals', '15'),
        ('Chapter 4: System Design & Architecture', '17'),
        ('    4.1  MVC Architecture Overview', '17'),
        ('    4.2  Application Flow', '19'),
        ('    4.3  Database Design', '22'),
        ('    4.4  Module-Wise Description', '24'),
        ('    4.5  File Structure', '28'),
        ('    4.6  Security Design', '30'),
        ('Chapter 5: Implementation', '33'),
        ('    5.1  Backend Implementation (Flask)', '33'),
        ('    5.2  Frontend Implementation', '38'),
        ('    5.3  Encryption Module', '40'),
        ('    5.4  Decryption Module', '43'),
        ('    5.5  Authentication Module', '44'),
        ('Chapter 6: Results and Discussion', '47'),
        ('    6.1  Feature Overview', '47'),
        ('    6.2  Page-wise Results', '48'),
        ('    6.3  UI/UX Evaluation', '52'),
        ('    6.4  Security Analysis', '54'),
        ('Chapter 7: Conclusions and Future Scope', '57'),
        ('    7.1  Conclusions', '57'),
        ('    7.2  Future Scope', '58'),
        ('References', '61'),
    ]
    for entry, pg in toc_entries:
        is_chap = entry.startswith('Chapter') or entry in ['Declaration','Certificate',
            'Acknowledgement','Abstract','List of Figures','List of Tables','References']
        style = S['TOC_Chapter'] if is_chap else S['TOC_Section']
        dots = '.' * max(5, 70 - len(entry))
        story.append(Paragraph(f'{entry} <font color="#AAAAAA">{dots}</font> <b>{pg}</b>', style))
    story += pagebreak()

    # ══ LIST OF FIGURES ══
    story += chapter_header('', 'List of Figures')
    figs = [
        ('Figure 1.1', 'SecureVault Application Architecture Overview', '17'),
        ('Figure 2.1', 'Comparison of Encryption Tools in Market', '9'),
        ('Figure 3.1', 'Functional Goals Mind Map', '15'),
        ('Figure 4.1', 'MVC Architecture Block Diagram', '18'),
        ('Figure 4.2', 'Complete User Flow Diagram', '20'),
        ('Figure 4.3', 'Database Design — JSON Structure', '23'),
        ('Figure 4.4', 'Module Interaction Diagram', '26'),
        ('Figure 4.5', 'Project File Structure', '29'),
        ('Figure 4.6', 'Security Design Architecture', '31'),
        ('Figure 5.1', 'HashID Generation Flowchart', '34'),
        ('Figure 5.2', 'Two-Factor Authentication Flowchart', '35'),
        ('Figure 5.3', 'AES Encryption Pipeline', '41'),
        ('Figure 5.4', 'Decryption Decision Flowchart', '44'),
        ('Figure 6.1', 'Landing Page Screenshot', '48'),
        ('Figure 6.2', 'Dashboard Page Screenshot', '49'),
        ('Figure 6.3', 'Encryption Page Screenshot', '50'),
        ('Figure 6.4', 'Decryption Output Screenshot', '51'),
        ('Figure 6.5', 'UI/UX Evaluation Radar Chart', '53'),
        ('Figure 7.1', 'Future Development Roadmap', '59'),
    ]
    fig_data = [['Figure No.', 'Title', 'Page']]
    for fn, ft, fp in figs:
        fig_data.append([fn, ft, fp])
    story.append(make_table(fig_data, col_widths=[3.5*cm, 11*cm, 2*cm]))
    story += pagebreak()

    # ══ LIST OF TABLES ══
    story += chapter_header('', 'List of Tables')
    tabs = [
        ('Table 1.1', 'Technology Stack Overview', '5'),
        ('Table 3.1', 'Functional Goals and Corresponding Modules', '15'),
        ('Table 4.1', 'users.json Field Descriptions', '22'),
        ('Table 4.2', 'meta.json Field Descriptions', '23'),
        ('Table 4.3', 'Flask Routes and Descriptions', '25'),
        ('Table 4.4', 'HTML Templates and Their Purpose', '29'),
        ('Table 5.1', 'Encryption Algorithm Comparison', '40'),
        ('Table 6.1', 'Feature Verification Results', '47'),
        ('Table 6.2', 'UI/UX Evaluation Criteria', '52'),
        ('Table 6.3', 'Security Analysis — Strengths', '54'),
        ('Table 6.4', 'Security Analysis — Limitations and Fixes', '55'),
    ]
    tab_data = [['Table No.', 'Title', 'Page']]
    for tn, tt, tp in tabs:
        tab_data.append([tn, tt, tp])
    story.append(make_table(tab_data, col_widths=[3.5*cm, 11*cm, 2*cm]))
    story += pagebreak()

    # ══════════════════════════════════════════════
    # CHAPTER 1: INTRODUCTION
    # ══════════════════════════════════════════════
    story += chapter_header('Chapter 1', 'Introduction')

    story += section('1.1  Background and Overview')
    story += body(
        'In the modern era of digital communication and cloud computing, data privacy and '
        'security have become critically important concerns for individuals, organizations, '
        'and governments alike. The exponential growth in data generation — driven by social '
        'media, e-commerce, remote work, and digital services — has made the protection of '
        'sensitive information more challenging and more essential than ever before.'
    )
    story += body(
        'Organizations store vast amounts of confidential data, ranging from personal '
        'identification documents and financial records to intellectual property and business '
        'strategies. A single breach of this data can result in catastrophic financial losses, '
        'reputation damage, legal liability, and loss of customer trust. According to IBM\'s '
        'Cost of a Data Breach Report, the average global cost of a data breach in 2023 was '
        'approximately USD 4.45 million — a figure that continues to rise year over year.'
    )
    story += body(
        '<b>SecureVault</b> is designed as a direct response to this growing need. It is a '
        'full-stack web application that provides users with an intuitive, browser-accessible '
        'platform for encrypting, storing, and managing their sensitive text-based files. '
        'Built on Python\'s Flask framework, the system integrates industry-standard cryptographic '
        'algorithms directly into the user workflow, removing the need for command-line tools, '
        'technical expertise, or external software installations.'
    )
    story += body(
        'The system introduces a novel approach to user identity: instead of conventional '
        'usernames (which are often guessable, recyclable, and vulnerable to phishing), '
        'SecureVault generates a unique <b>HashID</b> — a hexadecimal identifier derived '
        'mathematically from the user\'s phone number. This creates a pseudonymous, '
        'verifiable identity that is unique to each user without revealing any personally '
        'identifiable information during authentication.'
    )

    story += [ScreenshotBox('Figure 1.1 — SecureVault Landing Page Overview', height=7*cm)]
    story += caption('Figure 1.1: SecureVault Landing Page — The entry point of the application '
                     'featuring a dark gold-and-amber theme with animated canvas background.')

    story += section('1.2  Motivation')
    story += body(
        'The motivation for developing SecureVault originated from a careful observation of '
        'the existing landscape of encryption tools. Most available solutions — such as '
        'VeraCrypt, GnuPG, and OpenSSL — are powerful but are primarily designed for '
        'technically proficient users. They rely on command-line interfaces, require manual '
        'key management, and demand a foundational understanding of cryptographic principles. '
        'This creates a significant barrier for the majority of everyday users who need to '
        'protect sensitive data but lack the technical background to do so effectively.'
    )
    story += body(
        'Furthermore, existing browser-based solutions often lack either the security depth '
        'or the usability required for practical use. Many online tools for file encryption '
        'are not transparent about their encryption methods, do not provide key verification, '
        'and sometimes require file upload to third-party servers — introducing unnecessary '
        'risk. SecureVault addresses all of these concerns by providing a self-hosted, '
        'transparent, and verifiably secure system.'
    )
    story += body(
        'The project also draws inspiration from the growing academic interest in applied '
        'cryptography. Understanding how encryption works at an implementation level — not '
        'just theoretically — is an invaluable skill for computer science professionals. '
        'SecureVault serves simultaneously as a practical tool and as an educational '
        'demonstration of how cryptographic principles translate into real-world systems.'
    )
    story += body(
        'Additionally, the exploration of a <b>hash-based identity mechanism</b> was motivated '
        'by research into phishing-resistant authentication. Traditional username-based systems '
        'expose users to enumeration attacks, where adversaries can test whether a particular '
        'username exists in a system. By replacing usernames with deterministic but opaque '
        'HashIDs, SecureVault significantly reduces this attack surface.'
    )

    story += section('1.3  Problem Statement')
    story += body(
        'The following core problems motivated the design and development of SecureVault:'
    )
    story += bullet_list([
        '<b>Inaccessibility of encryption tools:</b> Most existing encryption solutions require '
        'command-line expertise or technical configuration that places them beyond the reach '
        'of non-technical users. There is a clear gap between the sophistication of available '
        'tools and the technical capability of the average user who needs file encryption.',
        '<b>Vulnerability of username-based authentication:</b> Traditional username-password '
        'systems are susceptible to social engineering, phishing, and brute-force attacks. '
        'Usernames, being human-readable and often reused across platforms, represent a '
        'significant security weakness in conventional authentication designs.',
        '<b>Lack of a unified file management and encryption platform:</b> Most users manage '
        'files in one location and use a separate tool for encryption — a disjointed workflow '
        'that increases the likelihood of errors, accidental exposure, or forgotten encryption '
        'of sensitive files.',
        '<b>No real-time encryption status tracking:</b> In shared or multi-file environments, '
        'tracking which files are encrypted and which are not is a significant operational '
        'challenge. Without a centralized metadata system, users risk accidentally sharing '
        'or accessing unencrypted sensitive data.',
        '<b>Absence of an educational demonstration platform:</b> Computer science students '
        'learning cryptography rarely interact with practical implementations. A system that '
        'demonstrates multiple encryption algorithms in a real-world context is a valuable '
        'pedagogical resource.'
    ])

    story += section('1.4  Technology Stack')
    story += body(
        'SecureVault is built using a carefully selected combination of open-source technologies '
        'that balance security, performance, and ease of development:'
    )

    tech_data = [
        ['Component', 'Technology Used', 'Purpose'],
        ['Backend Framework', 'Python 3.x with Flask', 'Routing, business logic, session management'],
        ['Encryption Library', 'cryptography (Fernet/AES)', 'Industry-standard file encryption'],
        ['User Data Storage', 'JSON flat-file (users.json)', 'Persistent user account records'],
        ['File Metadata', 'JSON flat-file (meta.json)', 'Encryption status and algorithm tracking'],
        ['Frontend Markup', 'HTML5 with Jinja2 Templating', 'Dynamic page rendering'],
        ['Frontend Styling', 'CSS3 with custom variables', 'Glassmorphism UI and animations'],
        ['Frontend Logic', 'Vanilla JavaScript (ES6+)', 'Canvas animations, DOM interactions'],
        ['Session Management', 'Flask server-side sessions', 'Secure two-factor auth state'],
        ['File Storage', 'Local filesystem (files/ dir)', 'Physical storage of vault files'],
        ['Version Control', 'Git', 'Source code management'],
        ['Development Server', 'Flask built-in / Gunicorn', 'Local and production serving'],
    ]
    story.append(make_table(tech_data, col_widths=[4.5*cm, 5*cm, 7*cm]))
    story += caption('Table 1.1: Technology Stack — Components and their respective roles in SecureVault.')

    story += section('1.5  Scope of the Project')
    story += body(
        'The scope of SecureVault covers the following major functional areas within the '
        'constraints of a prototype-scale application designed for the academic context:'
    )
    story += bullet_list([
        'User registration with phone-number-based HashID generation',
        'Two-factor authentication flow (HashID + Password)',
        'Secure dashboard for file management with real-time status',
        'File creation and direct text storage in the vault',
        'File upload, algorithm selection (AES/RSA/DES), and encryption',
        'File upload and key-verified decryption with in-browser output',
        'Encryption status tracking via a JSON-based metadata store',
        'Double-encryption guard to prevent data corruption',
        'Animated, responsive UI across fourteen HTML pages',
        'Public informational pages (Home, About, Services, Contact)',
    ])
    story += body(
        'The project is intentionally scoped to text-based files in this first version, '
        'with binary file support, database integration, and cloud deployment identified '
        'as future scope items. This ensures that all core functionality is implemented '
        'to a high standard before extending the system\'s capabilities.'
    )

    story += section('1.6  Project Highlights')
    story += body(
        'The following table summarizes the key highlights and distinguishing features '
        'of the SecureVault system:'
    )
    highlights = [
        ['Highlight', 'Description'],
        ['Novel Identity System', 'HashID derived from phone number — phishing-resistant, pseudonymous authentication'],
        ['Multi-Algorithm Support', 'AES (Fernet), RSA, and DES available in a single interface'],
        ['Two-Factor Auth', 'Dual-layer login — HashID at step 1, password at step 2'],
        ['Metadata Tracking', 'Real-time encryption status for all vault files via meta.json'],
        ['Anti-Double Encrypt', 'Guard prevents re-encrypting an already encrypted file'],
        ['Professional UI', '14-page dark gold-amber interface with canvas animations'],
        ['Full-Stack Python', 'Flask backend with Jinja2 templating — pure Python server side'],
        ['Educational Value', 'Demonstrates AES, RSA, DES in a real-world context'],
    ]
    story.append(make_table(highlights, col_widths=[5*cm, 11.5*cm]))
    story += pagebreak()

    # ══════════════════════════════════════════════
    # CHAPTER 2: LITERATURE REVIEW
    # ══════════════════════════════════════════════
    story += chapter_header('Chapter 2', 'Literature Review')

    story += section('2.1  Existing Encryption Tools and Systems')
    story += body(
        'A comprehensive review of existing file encryption tools provides valuable context '
        'for understanding the design decisions behind SecureVault. The landscape of '
        'encryption software can be broadly categorized into three groups: desktop '
        'applications, command-line utilities, and web-based solutions.'
    )

    story += subsection('2.1.1  Desktop Encryption Applications')
    story += body(
        '<b>VeraCrypt</b> (successor to TrueCrypt) is one of the most widely used open-source '
        'disk encryption tools. It provides strong AES-256 encryption, supports hidden volumes, '
        'and is available across Windows, macOS, and Linux. However, VeraCrypt requires '
        'technical setup, has a steep learning curve for new users, and operates at the '
        'disk/partition level rather than the individual file level. It does not provide a '
        'web interface or real-time status tracking.'
    )
    story += body(
        '<b>AxCrypt</b> is a more user-friendly alternative that integrates with Windows Explorer '
        'and offers AES-128/256 encryption. While accessible, it requires a paid premium '
        'subscription for advanced features, and its reliance on a centralized key management '
        'server introduces a potential single point of failure.'
    )
    story += body(
        '<b>7-Zip</b> provides AES-256 encryption within compressed archives and is widely '
        'available. However, it is primarily an archiving tool, lacks authentication mechanisms, '
        'and does not provide any form of identity or session management.'
    )

    story += subsection('2.1.2  Command-Line Tools')
    story += body(
        '<b>GnuPG (GNU Privacy Guard)</b> implements the OpenPGP standard and supports '
        'RSA, DSA, and AES encryption. It is extremely powerful and widely used in software '
        'development and security communities. However, GnuPG operates exclusively via the '
        'command line, requires key pair management, and is entirely inaccessible to non-technical '
        'users without a GUI wrapper.'
    )
    story += body(
        '<b>OpenSSL</b> is the cornerstone of encrypted communication on the internet, providing '
        'a command-line interface for a wide range of cryptographic operations. Like GnuPG, '
        'it is powerful but requires significant technical knowledge to operate correctly. '
        'Incorrect usage (such as insecure key derivation) can result in weakened encryption '
        'despite technically using strong algorithms.'
    )

    story += subsection('2.1.3  Web-Based Encryption Services')
    story += body(
        '<b>Cryptomator</b> provides client-side encryption for cloud-stored files and offers '
        'a simple interface. However, it is a desktop application despite having web '
        'integration, and does not support multiple encryption algorithms or custom key inputs. '
        '<b>Keybase</b> offers file encryption within a social-network context, but is primarily '
        'designed for team collaboration rather than individual file vault management.'
    )
    story += body(
        'Online tools such as <b>cryptii.com</b> and browser-based AES encryptors exist, but '
        'typically lack session management, do not store files, do not track encryption status, '
        'and may not be transparent about their actual cryptographic implementations. Many '
        'require files to be uploaded to remote servers, introducing privacy concerns.'
    )

    story.append(make_table([
        ['Tool', 'Type', 'Algorithm', 'GUI', 'Web-Based', 'Status Track'],
        ['VeraCrypt', 'Desktop', 'AES-256', 'Yes', 'No', 'No'],
        ['GnuPG', 'CLI', 'RSA/AES', 'No', 'No', 'No'],
        ['AxCrypt', 'Desktop', 'AES-256', 'Yes', 'Partial', 'No'],
        ['Cryptomator', 'Desktop+Web', 'AES-256', 'Yes', 'Partial', 'No'],
        ['7-Zip', 'Desktop', 'AES-256', 'Yes', 'No', 'No'],
        ['SecureVault', 'Web App', 'AES/RSA/DES', 'Yes', 'Yes', 'Yes'],
    ], col_widths=[3.5*cm, 3*cm, 3*cm, 2*cm, 2.5*cm, 2.5*cm]))
    story += caption('Table 2.1: Comparison of existing encryption tools with SecureVault.')

    story += section('2.2  Authentication Mechanisms in Cryptographic Systems')
    story += body(
        'Authentication is a foundational component of any secure system. Research in this '
        'area has evolved significantly over the past two decades, moving from simple '
        'password-based systems toward multi-factor and hardware-based approaches.'
    )
    story += body(
        '<b>Knowledge-Based Authentication (KBA)</b> — the classic username and password model '
        '— remains the most common form of authentication. However, research consistently '
        'demonstrates its vulnerability to phishing, credential stuffing, brute-force attacks, '
        'and password reuse. Studies estimate that over 80% of data breaches involve '
        'compromised credentials (Verizon DBIR, 2023).'
    )
    story += body(
        '<b>Two-Factor Authentication (2FA)</b> significantly improves security by requiring a '
        'second form of verification. Common implementations include SMS-based OTPs, '
        'authenticator applications (TOTP/HOTP), and hardware tokens (FIDO2/WebAuthn). '
        'SecureVault implements a software-based 2FA model using a HashID as the first '
        'factor and a password as the second, creating a dual-barrier authentication flow.'
    )
    story += body(
        '<b>Hash-Based Identity</b> draws from research in pseudonymous authentication systems. '
        'By deriving a user\'s identifier from a deterministic hash of their phone number, '
        'SecureVault ensures that each user has a unique, non-guessable identifier that '
        'cannot be enumerated or predicted by adversaries. This approach is inspired by '
        'concepts from zero-knowledge proofs and privacy-preserving identity systems.'
    )

    story += section('2.3  Research Gap and Motivation for SecureVault')
    story += body(
        'Having reviewed the existing tools and research, the following gaps are clearly '
        'identifiable in the current landscape:'
    )
    story += bullet_list([
        'No existing web-based tool combines file management, encryption, decryption, '
        'and status tracking within a single, self-hosted platform accessible to non-technical users.',
        'Existing authentication systems for file encryption tools rely on traditional '
        'usernames, making them vulnerable to social engineering and enumeration attacks.',
        'Multi-algorithm support (AES, RSA, DES) within a single browser-based interface '
        'does not exist in any currently available open-source tool.',
        'Real-time metadata tracking for encryption status across multiple files is absent '
        'from all reviewed tools.',
    ])
    story += body(
        'SecureVault is designed specifically to fill these gaps. It provides a unified, '
        'web-based platform that is simultaneously powerful, transparent, and usable — '
        'making cryptographic file protection genuinely accessible to all users regardless '
        'of technical background.'
    )
    story += pagebreak()

    # ══════════════════════════════════════════════
    # CHAPTER 3: OBJECTIVES
    # ══════════════════════════════════════════════
    story += chapter_header('Chapter 3', 'Objectives of the Project')

    story += section('3.1  Primary Objectives')
    story += body(
        'The primary objectives of the SecureVault project are defined based on the '
        'identified research gaps and user needs. These objectives represent the core '
        'goals that the system must achieve to be considered successful:'
    )
    story += bullet_list([
        'To design and implement a <b>complete web-based file management and encryption system</b> '
        'that is deployable on any standard Python environment without external dependencies.',
        'To provide a <b>hash-based identity system</b> that replaces conventional usernames, '
        'reducing the phishing attack surface and improving pseudonymous authentication.',
        'To implement <b>AES-based symmetric encryption</b> using the cryptography library\'s '
        'Fernet scheme, providing industry-standard, authenticated encryption for real-world '
        'file protection.',
        'To demonstrate <b>RSA and DES encryption concepts</b> within the same application '
        'framework, providing an educational comparison of different cryptographic approaches.',
        'To create an <b>intuitive, aesthetically designed user interface</b> with fourteen distinct '
        'pages, suitable for non-technical users without cryptographic background.',
        'To implement <b>real-time encryption status tracking</b> for all stored files through a '
        'JSON-based metadata store accessible from the dashboard.',
        'To enforce a <b>double-encryption guard</b> that prevents accidental re-encryption of '
        'files, protecting against unintended data corruption.',
    ])

    story += section('3.2  Secondary Objectives')
    story += body(
        'In addition to the primary objectives, the following secondary objectives guide '
        'the design and implementation of supporting system features:'
    )
    story += bullet_list([
        'To design a <b>modular Flask application architecture</b> with clearly separated routes '
        'for each functional area, ensuring maintainability and future extensibility.',
        'To implement <b>server-side session management</b> with a two-step authentication '
        'flow that correctly clears session state on logout, preventing session hijacking.',
        'To provide a <b>responsive and animated frontend</b> using modern CSS3 techniques '
        'including glassmorphism, canvas animations, and smooth page transitions.',
        'To demonstrate <b>file metadata management</b> using JSON-based flat-file storage '
        'as a lightweight alternative to a full relational database for prototype scale.',
        'To build a <b>scalable project structure</b> that can readily be extended with database '
        'integration, binary file support, and cloud deployment in future iterations.',
        'To implement <b>key hash verification</b> for RSA and DES decryption, ensuring that '
        'the correct encryption key must be provided to retrieve the original file.',
    ])

    story += section('3.3  Specific Functional Goals')
    story += body(
        'The following table maps each functional goal to its corresponding module and '
        'implementation file within the SecureVault system:'
    )
    goal_data = [
        ['#', 'Goal', 'Module / Route'],
        ['1', 'Generate HashID from phone number on signup', 'signup.html / app.py :: generate_hash_id()'],
        ['2', 'Two-factor login (HashID + Password)', 'signin.html / password.html / /signin / /password'],
        ['3', 'Create and save new text files to vault', 'editor.html / /new + /save routes'],
        ['4', 'Encrypt files using AES, RSA, or DES', 'encrypt.html / /encrypt route'],
        ['5', 'Decrypt files and display plaintext', 'decrypt.html / output.html / /decrypt route'],
        ['6', 'Track file encryption status in meta.json', 'dashboard.html / /dashboard route'],
        ['7', 'View raw file content (encrypted or plain)', 'view.html / /view/<filename> route'],
        ['8', 'Prevent double-encryption of files', 'app.py :: encryption guard in /encrypt'],
        ['9', 'Provide public informational pages', '/about, /services, /contact routes'],
        ['10', 'Smooth animations and page transitions', 'base.html / all page scripts / CSS3'],
        ['11', 'Real-time dashboard file statistics', '/dashboard :: encrypted_count, total count'],
        ['12', 'Key hash verification on decryption', 'app.py :: hashlib.sha256 key verification'],
    ]
    story.append(make_table(goal_data, col_widths=[1*cm, 6*cm, 9.5*cm]))
    story += caption('Table 3.1: Functional Goals mapped to implementation modules.')
    story += pagebreak()

    # ══════════════════════════════════════════════
    # CHAPTER 4: SYSTEM DESIGN & ARCHITECTURE
    # ══════════════════════════════════════════════
    story += chapter_header('Chapter 4', 'System Design & Architecture')

    story += section('4.1  System Architecture Overview')
    story += body(
        'SecureVault follows a <b>Model-View-Controller (MVC)</b> inspired architecture '
        'within the Flask framework. This architectural pattern cleanly separates the '
        'concerns of data management, business logic, and presentation — making the codebase '
        'more maintainable, testable, and extensible.'
    )
    story += body(
        'The application is organized into three logical layers:'
    )
    story += bullet_list([
        '<b>Presentation Layer:</b> HTML5 templates rendered by Jinja2, CSS3 stylesheets with '
        'custom variables and animations, and Vanilla JavaScript for client-side interactivity '
        'including canvas animations and DOM manipulation.',
        '<b>Business Logic Layer:</b> Flask routes defined in app.py handle all incoming HTTP '
        'requests, process form data, enforce authentication checks, perform encryption and '
        'decryption operations, and manage session state.',
        '<b>Data Layer:</b> JSON flat files (users.json for account data, meta.json for file '
        'metadata) provide lightweight persistence. The local filesystem stores the actual '
        'vault files in the files/ directory.',
    ])

    story.append(BlockDiagram(
        'Figure 4.1 — MVC Architecture Block Diagram',
        [
            ('User\n(Browser)', '#0B1437'),
            ('Flask\nRoutes\n(app.py)', '#C8960C'),
            ('Jinja2\nTemplates\n(HTML)', '#0F3460'),
            ('JSON\nData\nLayer', '#27AE60'),
        ],
        height=3.5*cm
    ))
    story += caption('Figure 4.1: MVC Architecture — Data flow from browser through Flask to templates and data layer.')
    story += space()

    story += body(
        'The following diagram illustrates the complete system architecture, showing how '
        'the browser communicates with the Flask server, which orchestrates between the '
        'template engine and the data storage layer:'
    )
    story.append(ScreenshotBox('Figure 4.2 — System Architecture Block Diagram', height=8*cm))
    story += caption('Figure 4.2: Detailed system architecture showing all component interactions in SecureVault.')

    story += section('4.2  Application Flow')
    story += body(
        'The overall application flow follows a carefully designed path from user arrival '
        'through authentication to file operations. Every step includes validation and '
        'session management to ensure only authorized users can access vault functionality.'
    )

    story += subsection('4.2.1  Entry and Landing')
    story += body(
        'When a user first visits the SecureVault root URL (/), the application checks '
        'whether the current browser session has already seen the intro animation '
        '(via session["intro_seen"]). On first visit, the animated entry screen and '
        'optional video introduction are displayed. On subsequent visits — or when the '
        'skip_intro=1 query parameter is present — the user is taken directly to the '
        'main landing page. This approach ensures a polished first impression without '
        'penalizing returning users with repeated loading screens.'
    )

    story.append(FlowchartBox(
        'Figure 4.3 — User Authentication Flowchart',
        [
            ('User Visits Landing Page (/)', '#0B1437', 'oval'),
            ('New User: /signup', '#C8960C', 'rect'),
            ('HashID Generated from Phone', '#0F3460', 'rect'),
            ('Returning User: /signin', '#C8960C', 'rect'),
            ('Enter HashID — Verified in users.json', '#27AE60', 'rect'),
            ('Valid? — Session auth1 Set', '#0B1437', 'diamond'),
            ('Enter Password at /password', '#0F3460', 'rect'),
            ('Valid? — Session auth=True', '#0B1437', 'diamond'),
            ('Access Dashboard (/dashboard)', '#27AE60', 'oval'),
        ],
        height=18*cm
    ))
    story += caption('Figure 4.3: Complete user authentication flowchart showing the two-factor login process.')

    story += subsection('4.2.2  Registration Flow')
    story += body(
        'When a new user registers via the /signup route, the following process occurs:'
    )
    story += bullet_list([
        'The user submits their full name, email address, phone number, and chosen password.',
        'The system checks whether the provided email already exists in users.json. If so, '
        'a flash message is shown and the user is redirected.',
        'If the email is new, the <code>generate_hash_id()</code> function is called. This '
        'converts the phone number to an integer using Python\'s built-in int() and then '
        'converts it to hexadecimal using hex(), stripping the 0x prefix and converting '
        'to uppercase. For example, phone 9876543210 produces HashID "24CB016EA".',
        'The user record is saved to users.json with the email as the key.',
        'The user is redirected to the identity confirmation page, which displays both '
        'the HashID and the chosen password for the user to note down securely.',
    ])

    story += subsection('4.2.3  Authentication Flow')
    story += body(
        'The two-step login process is one of the core security features of SecureVault:'
    )
    story += bullet_list([
        '<b>Step 1 (/signin):</b> The user enters their HashID. The system iterates through all '
        'user records in users.json comparing the stored hash field. If a match is found, '
        'session["user"] is set to the user\'s email and session["auth1"] is set to True, '
        'then the user is redirected to /password.',
        '<b>Step 2 (/password):</b> The user enters their password. The system checks that '
        'session["auth1"] exists (to prevent direct navigation). If the password matches '
        'the stored value for the logged-in user, session["auth"] is set to True and the '
        'user is redirected to the dashboard. On failure, the session is cleared entirely.',
    ])

    story += subsection('4.2.4  File Operations Flow')
    story += body(
        'Once authenticated, users have access to the full range of vault operations:'
    )

    story.append(FlowchartBox(
        'Figure 4.4 — File Operations Flowchart',
        [
            ('Dashboard — View All Files', '#0B1437', 'oval'),
            ('Choose Operation', '#C8960C', 'diamond'),
            ('Create New File (/new → /save)', '#0F3460', 'rect'),
            ('Upload & Encrypt (/encrypt)', '#27AE60', 'rect'),
            ('Upload & Decrypt (/decrypt)', '#C8960C', 'rect'),
            ('View File (/view/<name>)', '#0F3460', 'rect'),
            ('Dashboard Refreshed with New Status', '#0B1437', 'oval'),
        ],
        height=14*cm
    ))
    story += caption('Figure 4.4: File operations flowchart — all actions accessible from the central dashboard.')

    story += section('4.3  Database Design')
    story += body(
        'SecureVault uses a flat-file JSON approach instead of a relational database. '
        'This design choice is appropriate for a prototype-scale application and offers '
        'several advantages: zero configuration, human-readable data, no dependency on '
        'a database server, and simple debugging. The tradeoff is reduced scalability '
        'and lack of ACID transactions — both acceptable constraints for the current scope.'
    )

    story += subsection('4.3.1  users.json — User Account Store')
    story += body(
        'The users.json file stores all registered user accounts as a dictionary keyed '
        'by email address. Each entry contains the following fields:'
    )
    story.append(make_table([
        ['Field', 'Type', 'Description', 'Example Value'],
        ['email (key)', 'String', 'Primary identifier; JSON key', 'user@example.com'],
        ['name', 'String', 'Full name of the user', 'Jayansh Kumar'],
        ['phone', 'String', 'Phone number source for HashID', '9876543210'],
        ['password', 'String', 'Authentication credential (plain-text in v1)', 'mySecurePass123'],
        ['hash', 'String', 'Hex HashID derived from phone number', '24CB016EA'],
    ], col_widths=[3*cm, 2*cm, 5.5*cm, 4.5*cm]))
    story += caption('Table 4.1: users.json field descriptions and example values.')

    story += subsection('4.3.2  meta.json — File Metadata Store')
    story += body(
        'The meta.json file stores encryption metadata for each file in the vault. '
        'Each entry maps a filename to an object containing status and algorithm information:'
    )
    story.append(make_table([
        ['Field', 'Type', 'Possible Values', 'Description'],
        ['filename (key)', 'String', 'e.g., report.txt', 'Name of the vault file'],
        ['status', 'String', '"Encrypted" / "Not Encrypted"', 'Current encryption state'],
        ['algo', 'String', '"AES" / "RSA" / "DES"', 'Algorithm used for encryption'],
        ['key_hash', 'String', 'SHA-256 hex digest', 'Hash of encryption key for verification'],
    ], col_widths=[3.5*cm, 2*cm, 4*cm, 5.5*cm]))
    story += caption('Table 4.2: meta.json field descriptions, possible values, and meanings.')

    story += body(
        'Example meta.json structure:'
    )
    story.append(Paragraph(
        '{ "report.txt": { "status": "Encrypted", "algo": "AES", "key_hash": "a3f2c..." },\n'
        '  "notes.txt":  { "status": "Not Encrypted" } }',
        S['Code']
    ))

    story += section('4.4  Module-Wise Description')
    story += body(
        'The SecureVault application is divided into six primary functional modules, each '
        'implemented as a set of related routes and helper functions in app.py:'
    )

    story += subsection('4.4.1  Authentication Module')
    story += body(
        'The authentication module implements the two-step login process. It manages session '
        'state through Flask\'s server-side session mechanism, uses the users.json store '
        'for credential validation, and enforces strict session guards on all protected routes.'
    )
    story += body(
        '<b>Key Routes:</b> /signin (Step 1 — HashID verification), /password (Step 2 — '
        'password verification), /logout (complete session clearance), /signup (registration).'
    )

    story += subsection('4.4.2  Identity Generation Module')
    story += body(
        'On signup, the generate_hash_id() function performs a two-step conversion: '
        '(1) converts the phone string to an integer using int(), and (2) converts that '
        'integer to hexadecimal using Python\'s built-in hex() function. The "0x" prefix '
        'is stripped and the result is converted to uppercase, producing the unique HashID.'
    )
    story.append(Paragraph(
        'def generate_hash_id(phone):\n'
        '    return hex(int(phone))[2:].upper()\n\n'
        '# Example: phone = "9876543210"\n'
        '# int("9876543210") = 9876543210\n'
        '# hex(9876543210) = "0x24cb016ea"\n'
        '# result: "24CB016EA"',
        S['Code']
    ))

    story += subsection('4.4.3  File Management Module')
    story += body(
        'This module handles file creation (/new, /save) and file viewing (/view/<filename>). '
        'The /save route writes the submitted file content to the files/ directory with a .txt '
        'extension and records the initial "Not Encrypted" status in meta.json. The '
        '/view route reads and renders the raw file content, correctly handling binary '
        'encrypted content using UTF-8 decoding with error replacement.'
    )

    story += subsection('4.4.4  Encryption Module')
    story += body(
        'The /encrypt route is the core of the vault\'s security functionality. It:'
    )
    story += bullet_list([
        'Accepts a file upload via multipart form data, along with algorithm selection and encryption key.',
        'Checks meta.json to prevent double-encryption of already-encrypted files.',
        'Hashes the user-provided key using SHA-256 (hashlib.sha256) and stores the hash in meta.json for later verification.',
        'For AES: pads or truncates the key to 32 bytes, encodes as URL-safe Base64, creates a Fernet instance, and calls fernet.encrypt(data).',
        'For DES/RSA: prepends a protocol identifier prefix ("DES_" or "RSA_") and reverses the byte order of the file content.',
        'Writes the encrypted bytes to the files/ directory and updates meta.json with status, algorithm, and key hash.',
    ])

    story += subsection('4.4.5  Decryption Module')
    story += body(
        'The /decrypt route reverses the encryption process:'
    )
    story += bullet_list([
        'Reads the uploaded encrypted file bytes.',
        'Detects the encryption algorithm by checking for "DES_" or "RSA_" byte prefixes.',
        'For DES/RSA: computes SHA-256 of the submitted key and compares against stored key_hash in meta.json. If mismatch, flashes "Invalid Key" and redirects.',
        'For AES (Fernet): regenerates the key from user input and calls fernet.decrypt(). An incorrect key raises an exception, which is caught to display "Invalid Key".',
        'Renders the decrypted plaintext in output.html within a monospace terminal-style display.',
    ])

    story += subsection('4.4.6  Dashboard Module')
    story += body(
        'The /dashboard route aggregates file data for display:'
    )
    story += bullet_list([
        'Lists all files in the files/ directory excluding meta.json.',
        'Cross-references each file name against meta.json for encryption status.',
        'Falls back to binary content inspection (checking for RSA_/DES_ prefixes and non-ASCII bytes) for files not in meta.json.',
        'Sorts files by modification time (newest first) using os.path.getmtime().',
        'Computes statistics (total files, encrypted count, non-encrypted count) and passes all data to dashboard.html.',
    ])

    story.append(make_table([
        ['Route', 'Method', 'Auth Required', 'Description'],
        ['/', 'GET', 'No', 'Landing page with optional intro animation'],
        ['/signup', 'GET/POST', 'No', 'User registration form and HashID generation'],
        ['/signin', 'GET/POST', 'No', 'Step 1: HashID authentication'],
        ['/password', 'GET/POST', 'auth1', 'Step 2: Password authentication'],
        ['/dashboard', 'GET', 'auth', 'Main vault file management dashboard'],
        ['/new', 'GET', 'auth', 'File editor page for creating new files'],
        ['/save', 'POST', 'auth (implied)', 'Save newly created file to vault'],
        ['/encrypt', 'GET/POST', 'auth (implied)', 'File upload and encryption'],
        ['/decrypt', 'GET/POST', 'auth (implied)', 'File upload and decryption'],
        ['/view/<filename>', 'GET', 'auth', 'View raw content of a vault file'],
        ['/logout', 'GET', 'auth (implied)', 'Clear session and redirect to home'],
        ['/about', 'GET', 'No', 'Public about page'],
        ['/services', 'GET', 'No', 'Public services listing page'],
        ['/contact', 'GET', 'No', 'Public contact form page'],
    ], col_widths=[4*cm, 2*cm, 2.5*cm, 7*cm]))
    story += caption('Table 4.3: All Flask routes with HTTP methods, authentication requirements, and descriptions.')

    story += section('4.5  File Structure')
    story += body(
        'The SecureVault project is organized into a clean, modular file structure that '
        'separates core application logic, template files, and static assets:'
    )
    story.append(make_table([
        ['File / Folder', 'Type', 'Purpose'],
        ['app.py', 'Python', 'Core Flask application: all routes, encryption logic, session handling'],
        ['users.json', 'JSON', 'Persistent user store — email to name/phone/password/hash mapping'],
        ['files/', 'Directory', 'Physical storage for all vault files (encrypted and plaintext)'],
        ['files/meta.json', 'JSON', 'Tracks encryption status, algorithm, and key hash per file'],
        ['templates/base.html', 'HTML', 'Master layout: navbar, global styles, page transition scripts'],
        ['templates/index.html', 'HTML', 'Landing page with animated entry screen and video intro'],
        ['templates/dashboard.html', 'HTML', 'Main user portal: file list, statistics, action buttons'],
        ['templates/editor.html', 'HTML', 'File creation form: filename and content fields'],
        ['templates/encrypt.html', 'HTML', 'Encryption form: file upload, algorithm selection, key'],
        ['templates/decrypt.html', 'HTML', 'Decryption form: encrypted file upload and key entry'],
        ['templates/output.html', 'HTML', 'Decrypted output display with copy-to-clipboard button'],
        ['templates/view.html', 'HTML', 'Raw file content viewer (encrypted or plaintext)'],
        ['templates/signin.html', 'HTML', 'Step 1 login: HashID entry form'],
        ['templates/password.html', 'HTML', 'Step 2 login: password entry form'],
        ['templates/signup.html', 'HTML', 'User registration form'],
        ['templates/identity.html', 'HTML', 'Post-signup HashID and password confirmation card'],
        ['templates/about.html', 'HTML', 'Public about page: philosophy and features'],
        ['templates/services.html', 'HTML', 'Services listing: AES, RSA, Hash Identity'],
        ['templates/contact.html', 'HTML', 'Static contact form UI'],
        ['static/css/', 'CSS', 'Additional stylesheets and component-specific styles'],
        ['static/js/', 'JS', 'Additional client-side scripts'],
        ['static/team/', 'Images', 'Team member profile photographs'],
        ['static/intro.mp4', 'Video', 'Optional intro video for first-time visitors'],
    ], col_widths=[5*cm, 2*cm, 9.5*cm]))
    story += caption('Table 4.4: Complete project file structure with file types and descriptions.')

    story += section('4.6  Security Design')
    story += body(
        'Security is not an afterthought in SecureVault — it is a foundational design '
        'principle built into every layer of the system. The following security mechanisms '
        'are implemented:'
    )

    story.append(BlockDiagram(
        'Figure 4.5 — Security Layers in SecureVault',
        [
            ('Hash\nIdentity\nLayer', '#0B1437'),
            ('Two-Factor\nAuth\nLayer', '#C8960C'),
            ('Session\nMgmt\nLayer', '#0F3460'),
            ('AES\nEncrypt\nLayer', '#27AE60'),
            ('Key\nVerify\nLayer', '#E74C3C'),
        ],
        height=3.5*cm
    ))
    story += caption('Figure 4.5: Five-layer security architecture of SecureVault.')

    story += subsection('4.6.1  Identity Layer — HashID')
    story += body(
        'The HashID system replaces conventional usernames with a deterministic but opaque '
        'identifier. An adversary who does not know the user\'s phone number cannot guess '
        'or enumerate valid HashIDs, making credential stuffing and username enumeration '
        'attacks significantly more difficult. The hexadecimal output space is large enough '
        '(up to 12 hex characters for a 10-digit phone number) to resist brute-force guessing.'
    )

    story += subsection('4.6.2  Two-Factor Authentication')
    story += body(
        'The dual-barrier login system ensures that both the HashID and the password must '
        'be correctly provided before any session access is granted. If either check fails, '
        'the session is completely cleared — preventing partial-state exploits. The separation '
        'of the two steps into distinct routes (/signin and /password) also allows for '
        'future integration of rate limiting on each step independently.'
    )

    story += subsection('4.6.3  Session Management')
    story += body(
        'Flask\'s server-side session management is used throughout, with a secret key '
        'protecting session integrity. Session variables (auth1, auth, user) are set '
        'only after successful verification at each step, and are completely cleared '
        'on logout via session.clear(). All protected routes check for session["auth"] '
        'before serving content, redirecting unauthenticated requests to the home page.'
    )

    story += subsection('4.6.4  AES Encryption Strength')
    story += body(
        'The Fernet scheme used for AES encryption provides authenticated symmetric '
        'encryption based on AES-128-CBC with HMAC-SHA256 for authentication. It '
        'guarantees that encrypted content cannot be decrypted without the correct key, '
        'and also ensures that tampered ciphertext is detected. The key derivation '
        'function (padding/truncation to 32 bytes + Base64 encoding) produces a valid '
        'Fernet key from any user-provided string.'
    )

    story += subsection('4.6.5  Key Hash Verification')
    story += body(
        'For DES and RSA implementations, the SHA-256 hash of the encryption key is '
        'stored in meta.json at encryption time. During decryption, the submitted key '
        'is hashed and compared against the stored value. A mismatch immediately '
        'aborts the decryption and returns an "Invalid Key" error, preventing unauthorized '
        'access to encrypted file contents.'
    )
    story += pagebreak()

    # ══════════════════════════════════════════════
    # CHAPTER 5: IMPLEMENTATION
    # ══════════════════════════════════════════════
    story += chapter_header('Chapter 5', 'Implementation')

    story += section('5.1  Backend Implementation — Flask')
    story += body(
        'The Flask backend serves as the central nervous system of SecureVault, handling '
        'all business logic, file operations, encryption, and session management. The '
        'application is defined in a single <b>app.py</b> file, organized into clearly '
        'labeled functional sections with comments.'
    )

    story += subsection('5.1.1  Application Initialization')
    story += body(
        'The Flask application is initialized with a secret key that secures session cookies:'
    )
    story.append(Paragraph(
        'from flask import Flask, render_template, request, redirect, session, flash\n'
        'import os, base64, json, hashlib\n'
        'from cryptography.fernet import Fernet\n\n'
        'app = Flask(__name__)\n'
        'app.secret_key = "supersecretkey"  # Should use os.urandom(24) in production',
        S['Code']
    ))
    story += body(
        'The secret key is used by Flask to sign session cookies, preventing client-side '
        'session tampering. In a production deployment, this should be generated using '
        'os.urandom(24) and stored in an environment variable rather than hardcoded.'
    )

    story += subsection('5.1.2  User Data Management')
    story += body(
        'User accounts are persisted in a JSON file with helper functions for loading '
        'and saving:'
    )
    story.append(Paragraph(
        'USER_FILE = "users.json"\n\n'
        'def load_users():\n'
        '    if not os.path.exists(USER_FILE): return {}\n'
        '    try:\n'
        '        with open(USER_FILE, "r") as f: return json.load(f)\n'
        '    except: return {}\n\n'
        'def save_users(users):\n'
        '    with open(USER_FILE, "w") as f:\n'
        '        json.dump(users, f, indent=4)',
        S['Code']
    ))

    story += subsection('5.1.3  HashID Generation')
    story += body(
        'The HashID generation function is deceptively simple yet effective:'
    )
    story.append(Paragraph(
        'def generate_hash_id(phone):\n'
        '    return hex(int(phone))[2:].upper()\n\n'
        '# Walkthrough for phone = "9876543210":\n'
        '# Step 1: int("9876543210") = 9876543210\n'
        '# Step 2: hex(9876543210)  = "0x24cb016ea"\n'
        '# Step 3: [2:]             = "24cb016ea"\n'
        '# Step 4: .upper()         = "24CB016EA"  ← Final HashID',
        S['Code']
    ))
    story += body(
        'The function produces a unique hexadecimal identifier for each phone number. '
        'The transformation is deterministic (same input always gives same output) but '
        'not directly guessable without knowing the phone number. The hex representation '
        'is typically 8–10 characters long for standard 10-digit phone numbers.'
    )

    story += subsection('5.1.4  Signup Route')
    story.append(Paragraph(
        '@app.route("/signup", methods=["GET", "POST"])\n'
        'def signup():\n'
        '    if request.method == "POST":\n'
        '        users = load_users()\n'
        '        email = request.form["email"]\n'
        '        if email in users:\n'
        '            flash("User already exists")\n'
        '            return redirect("/")\n'
        '        hash_id = generate_hash_id(request.form["phone"])\n'
        '        users[email] = {\n'
        '            "name": request.form["name"],\n'
        '            "phone": request.form["phone"],\n'
        '            "password": request.form["password"],\n'
        '            "hash": hash_id\n'
        '        }\n'
        '        save_users(users)\n'
        '        return render_template("identity.html",\n'
        '            hash_id=hash_id, password=request.form["password"])\n'
        '    return render_template("signup.html")',
        S['Code']
    ))

    story += subsection('5.1.5  Two-Factor Authentication Routes')
    story.append(Paragraph(
        '@app.route("/signin", methods=["GET", "POST"])\n'
        'def signin():\n'
        '    if request.method == "POST":\n'
        '        users = load_users()\n'
        '        for email, data in users.items():\n'
        '            if data["hash"] == request.form["hash"]:\n'
        '                session["user"] = email\n'
        '                session["auth1"] = True\n'
        '                return redirect("/password")\n'
        '        session.clear()\n'
        '        flash("Invalid Credentials")\n'
        '        return redirect("/")\n'
        '    return render_template("signin.html")\n\n'
        '@app.route("/password", methods=["GET", "POST"])\n'
        'def password():\n'
        '    if "auth1" not in session: return redirect("/")\n'
        '    users = load_users()\n'
        '    if request.method == "POST":\n'
        '        email = session["user"]\n'
        '        if users[email]["password"] == request.form["password"]:\n'
        '            session["auth"] = True\n'
        '            return redirect("/dashboard")\n'
        '        session.clear()\n'
        '        flash("Invalid Credentials")\n'
        '        return redirect("/")\n'
        '    return render_template("password.html")',
        S['Code']
    ))

    story += section('5.2  Frontend Implementation')
    story += body(
        'The SecureVault frontend is one of its most distinctive features. Built entirely '
        'with HTML5, CSS3, and Vanilla JavaScript, it achieves a professional, animated '
        'dark-gold interface without relying on any frontend frameworks.'
    )

    story += subsection('5.2.1  Design System')
    story += body(
        'The design uses CSS custom properties (variables) to create a consistent color '
        'system across all fourteen pages:'
    )
    story.append(Paragraph(
        ':root {\n'
        '    --gold:    #f0a500;    --gold-bright: #ffc94a;\n'
        '    --orange:  #e86210;    --amber:       #f5c842;\n'
        '    --bg:      #060400;    --bg2:         #0d0900;\n'
        '    --text1:   #faf6ee;    --text2: rgba(250,246,238,0.6);\n'
        '    --font-d: "Bebas Neue", sans-serif;    /* Display headings */\n'
        '    --font-b: "Syne", sans-serif;           /* Body text */\n'
        '    --font-m: "JetBrains Mono", monospace;  /* Technical labels */\n'
        '}',
        S['Code']
    ))

    story += subsection('5.2.2  Canvas Animations')
    story += body(
        'The background particle network animation on the entry screen is implemented '
        'using the HTML5 Canvas API. One hundred particles are rendered with sinusoidal '
        'opacity pulses, and connecting lines are drawn between any two particles within '
        '120px of each other — creating an organic, breathing network effect:'
    )
    story.append(Paragraph(
        'const pts = Array.from({length:100}, () => ({\n'
        '    x: Math.random() * canvas.width,\n'
        '    y: Math.random() * canvas.height,\n'
        '    r: Math.random() * 1.8 + 0.4,\n'
        '    dx: (Math.random() - 0.5) * 0.35,\n'
        '    dy: (Math.random() - 0.5) * 0.35,\n'
        '    pulse: Math.random() * Math.PI * 2\n'
        '}));\n\n'
        '// Connection logic:\n'
        'if (distance < 120) {\n'
        '    opacity = (1 - distance/120) * 0.06;\n'
        '    ctx.strokeStyle = `rgba(240,165,0,${opacity})`;\n'
        '}',
        S['Code']
    ))

    story += subsection('5.2.3  Page Transitions')
    story += body(
        'Smooth fade-in/out transitions between pages are implemented by controlling the '
        'CSS opacity of the body element with a brief JavaScript animation:'
    )
    story.append(Paragraph(
        '// On page load: fade in\n'
        'document.body.style.opacity = 0;\n'
        'requestAnimationFrame(() => {\n'
        '    document.body.style.transition = "opacity 0.4s ease";\n'
        '    document.body.style.opacity = 1;\n'
        '});\n\n'
        '// On navigation click: fade out\n'
        'link.addEventListener("click", (e) => {\n'
        '    e.preventDefault();\n'
        '    document.body.style.opacity = 0;\n'
        '    setTimeout(() => window.location = link.href, 400);\n'
        '});',
        S['Code']
    ))

    story += [ScreenshotBox('Figure 5.1 — Frontend UI Screenshots (Landing Page + Dashboard)', height=8.5*cm)]
    story += caption('Figure 5.1: SecureVault frontend — dark gold-amber theme with glassmorphism cards and animations.')

    story += section('5.3  Encryption Module Implementation')
    story += body(
        'The encryption module is the technical centerpiece of SecureVault. It implements '
        'three encryption approaches within a single /encrypt route, selected based on '
        'the user\'s algorithm choice:'
    )

    story.append(make_table([
        ['Algorithm', 'Library', 'Actual Implementation', 'Security Level', 'Use Case'],
        ['AES', 'cryptography.fernet.Fernet', 'AES-128-CBC + HMAC-SHA256', 'Production-Grade', 'Real data protection'],
        ['RSA', 'Built-in Python', 'Byte reversal + RSA_ prefix', 'Demonstration Only', 'Concept illustration'],
        ['DES', 'Built-in Python', 'Byte reversal + DES_ prefix', 'Demonstration Only', 'Legacy/educational'],
    ], col_widths=[2*cm, 4.5*cm, 4.5*cm, 3*cm, 3*cm]))
    story += caption('Table 5.1: Encryption algorithm comparison — implementation details and security assessment.')

    story += subsection('5.3.1  AES Encryption (Fernet)')
    story += body(
        'The AES implementation uses Python\'s cryptography library Fernet module. '
        'The user-provided key (any string) is transformed into a valid Fernet key '
        'through padding and Base64 encoding:'
    )
    story.append(Paragraph(
        'def generate_key(user_key):\n'
        '    # Pad or truncate to exactly 32 bytes\n'
        '    # Then encode as URL-safe Base64 (Fernet requirement)\n'
        '    return base64.urlsafe_b64encode(user_key.ljust(32)[:32])\n\n'
        '# In the encrypt route:\n'
        'if algo == "AES":\n'
        '    key = generate_key(user_key)\n'
        '    fernet = Fernet(key)\n'
        '    encrypted = fernet.encrypt(data)  # Returns authenticated ciphertext',
        S['Code']
    ))

    story.append(FlowchartBox(
        'Figure 5.2 — AES Encryption Pipeline',
        [
            ('User uploads file + provides key', '#0B1437', 'oval'),
            ('Read file bytes from request', '#0F3460', 'rect'),
            ('SHA-256 hash key for verification storage', '#C8960C', 'rect'),
            ('Pad/truncate key to 32 bytes', '#0F3460', 'rect'),
            ('Base64 encode key → Fernet instance', '#27AE60', 'rect'),
            ('fernet.encrypt(data) → ciphertext', '#C8960C', 'rect'),
            ('Write encrypted bytes to files/', '#0B1437', 'rect'),
            ('Update meta.json: Encrypted / AES / key_hash', '#27AE60', 'oval'),
        ],
        height=16*cm
    ))
    story += caption('Figure 5.2: Complete AES encryption pipeline showing key derivation and Fernet encryption steps.')

    story += subsection('5.3.2  RSA and DES Simulation')
    story += body(
        'The RSA and DES implementations are intentional simulations designed for '
        'educational demonstration rather than actual cryptographic security:'
    )
    story.append(Paragraph(
        'elif algo == "DES":\n'
        '    encrypted = b"DES_" + data[::-1]\n'
        '    # data[::-1] reverses the byte order\n'
        '    # "DES_" prefix identifies algorithm on decryption\n\n'
        'elif algo == "RSA":\n'
        '    encrypted = b"RSA_" + data[::-1]\n'
        '    # Same byte-reversal with "RSA_" prefix',
        S['Code']
    ))
    story += body(
        'While byte reversal is not cryptographically secure, it serves the pedagogical '
        'purpose of demonstrating that encryption transforms data into a non-readable form, '
        'and that decryption requires the correct algorithm and key. The key hash '
        'verification layer adds meaningful security even to these simulations.'
    )

    story += section('5.4  Decryption Module Implementation')
    story += body(
        'The decryption route intelligently determines the correct decryption path by '
        'inspecting the first bytes of the uploaded file for algorithm identifier prefixes:'
    )
    story.append(Paragraph(
        '@app.route("/decrypt", methods=["GET", "POST"])\n'
        'def decrypt():\n'
        '    if request.method == "POST":\n'
        '        file = request.files["file"]\n'
        '        user_key = request.form["key"]\n'
        '        data_to_decrypt = file.read()\n\n'
        '        try:\n'
        '            if data_to_decrypt.startswith(b"DES_"):\n'
        '                # Verify key hash before decrypting\n'
        '                stored = load_meta().get(file.filename,{}).get("key_hash")\n'
        '                input_hash = hashlib.sha256(user_key.encode()).hexdigest()\n'
        '                if stored and stored != input_hash:\n'
        '                    flash("Invalid Key"); return redirect("/")\n'
        '                data = data_to_decrypt[4:][::-1]\n'
        '                return render_template("output.html",\n'
        '                    data=data.decode("utf-8", errors="replace"))\n\n'
        '            else:  # AES (Fernet)\n'
        '                key = generate_key(user_key.encode())\n'
        '                fernet = Fernet(key)\n'
        '                data = fernet.decrypt(data_to_decrypt)\n'
        '                return render_template("output.html",\n'
        '                    data=data.decode("utf-8", errors="replace"))\n\n'
        '        except Exception:\n'
        '            flash("Invalid Key"); return redirect("/")',
        S['Code']
    ))

    story.append(FlowchartBox(
        'Figure 5.3 — Decryption Decision Flowchart',
        [
            ('Upload encrypted file + key', '#0B1437', 'oval'),
            ('Check file prefix bytes', '#C8960C', 'diamond'),
            ('Prefix = DES_ or RSA_?', '#0F3460', 'diamond'),
            ('Hash submitted key → compare with stored hash', '#C8960C', 'rect'),
            ('Match? → Reverse bytes, decode to text', '#27AE60', 'rect'),
            ('No Match? → Flash "Invalid Key"', '#E74C3C', 'rect'),
            ('AES: Regenerate Fernet key → decrypt()', '#27AE60', 'rect'),
            ('Display decrypted output in output.html', '#0B1437', 'oval'),
        ],
        height=16*cm
    ))
    story += caption('Figure 5.3: Decryption decision flowchart — algorithm detection and key verification.')

    story += section('5.5  Dashboard and File Management')
    story += body(
        'The dashboard is the central hub of the authenticated user experience. '
        'It aggregates all vault file data, computes real-time statistics, and '
        'provides navigation to all file operations:'
    )
    story.append(Paragraph(
        '@app.route("/dashboard")\n'
        'def dashboard():\n'
        '    if "auth" not in session: return redirect("/")\n'
        '    os.makedirs("files", exist_ok=True)\n'
        '    files = os.listdir("files")\n'
        '    meta = load_meta()\n'
        '    file_data = []\n'
        '    for f in files:\n'
        '        if f == "meta.json": continue\n'
        '        status = meta.get(f, {}).get("status", "Not Encrypted")\n'
        '        file_time = os.path.getmtime(os.path.join("files", f))\n'
        '        file_data.append({"name": f, "status": status, "time": file_time})\n'
        '    file_data.sort(key=lambda x: x["time"], reverse=True)\n'
        '    encrypted_count = len([f for f in file_data if f["status"] == "Encrypted"])\n'
        '    return render_template("dashboard.html", files=file_data,\n'
        '        total=len(file_data), encrypted_count=encrypted_count,\n'
        '        decrypted_count=len(file_data) - encrypted_count)',
        S['Code']
    ))

    story += [ScreenshotBox('Figure 5.4 — Dashboard Screenshot', height=7.5*cm)]
    story += caption('Figure 5.4: SecureVault Dashboard — file listing with encryption status, sorted by modification time.')
    story += pagebreak()

    # ══════════════════════════════════════════════
    # CHAPTER 6: RESULTS AND DISCUSSION
    # ══════════════════════════════════════════════
    story += chapter_header('Chapter 6', 'Results and Discussion')

    story += section('6.1  Implemented Features Overview')
    story += body(
        'The SecureVault application was successfully implemented and rigorously tested '
        'across all defined functional modules. All fourteen HTML pages were designed, '
        'connected through Flask routes, and verified for correct behavior. The following '
        'table presents a comprehensive feature verification summary:'
    )

    feat_data = [
        ['#', 'Feature', 'Status', 'Notes'],
        ['1', 'HashID generation from phone number', 'PASS', 'Correct hex output for all test inputs'],
        ['2', 'User registration and data storage', 'PASS', 'users.json updated correctly'],
        ['3', 'Step 1 login — HashID verification', 'PASS', 'Invalid HashID correctly rejected'],
        ['4', 'Step 2 login — Password verification', 'PASS', 'Wrong password clears session'],
        ['5', 'File creation via editor', 'PASS', 'Files saved with Not Encrypted status'],
        ['6', 'AES encryption (Fernet)', 'PASS', 'Ciphertext unreadable without key'],
        ['7', 'AES decryption with correct key', 'PASS', 'Original plaintext recovered'],
        ['8', 'AES decryption with wrong key', 'PASS', 'Exception caught, Invalid Key shown'],
        ['9', 'RSA encryption (simulation)', 'PASS', 'RSA_ prefix applied, bytes reversed'],
        ['10', 'DES encryption (simulation)', 'PASS', 'DES_ prefix applied, bytes reversed'],
        ['11', 'RSA/DES key hash verification', 'PASS', 'Wrong key rejected before decryption'],
        ['12', 'Double-encryption guard', 'PASS', 'Already encrypted files blocked'],
        ['13', 'Dashboard file listing', 'PASS', 'Sorted by modification time correctly'],
        ['14', 'Encryption status tracking', 'PASS', 'meta.json updated on all operations'],
        ['15', 'File viewer', 'PASS', 'Encrypted and plaintext content displayed'],
        ['16', 'Logout session clearance', 'PASS', 'Session fully cleared, redirect to home'],
        ['17', 'Flash messages on errors', 'PASS', 'Auto-dismiss after 3 seconds'],
        ['18', 'Canvas background animations', 'PASS', 'Smooth 60fps particle animation'],
        ['19', 'Page fade transitions', 'PASS', 'Opacity-based smooth navigation'],
        ['20', 'Public informational pages', 'PASS', 'About, Services, Contact all render'],
    ]
    story.append(make_table(feat_data, col_widths=[1*cm, 6.5*cm, 2*cm, 6*cm]))
    story += caption('Table 6.1: Comprehensive feature verification results — all 20 features tested and verified.')

    story += section('6.2  Page-wise Results')

    story += subsection('6.2.1  Landing Page and Entry Screen')
    story += body(
        'The landing page (index.html) successfully implements the full entry experience. '
        'On first visit, the animated entry screen renders the "SecureVault" wordmark with '
        'a fade-in animation, displays five concentric pulsing rings around the entry orb, '
        'and executes a typewriter-effect text sequence. The particle canvas network animates '
        'smoothly at approximately 60 frames per second in all tested browsers.'
    )
    story += body(
        'Clicking the entry orb triggers a smooth opacity fade-out of the entry screen, '
        'followed by the optional intro video. The skip button correctly bypasses the '
        'video and transitions directly to the main application. The skip_intro=1 query '
        'parameter correctly bypasses the entry screen entirely on subsequent visits, '
        'ensuring returning users reach the content immediately.'
    )

    story += [ScreenshotBox('Figure 6.1 — Landing Page Screenshot', height=7*cm)]
    story += caption('Figure 6.1: SecureVault Landing Page — Entry screen with animated orb and particle network background.')

    story += subsection('6.2.2  Registration and Identity Page')
    story += body(
        'The registration flow works correctly for all tested inputs. The HashID generation '
        'produces consistent, unique output for all numeric phone numbers. Email uniqueness '
        'checking prevents duplicate registrations and provides clear user feedback via '
        'flash messages. The identity confirmation page displays both the HashID and '
        'chosen password in a clean card format, with a clear instruction to note these '
        'credentials before proceeding.'
    )
    story += body(
        'Test case: Phone number 9876543210 consistently produces HashID "24CB016EA" — '
        'confirming the deterministic nature of the hash function. Different phone numbers '
        'reliably produce different HashIDs with no observed collisions in testing.'
    )

    story += subsection('6.2.3  Two-Step Login')
    story += body(
        'The authentication flow was tested across multiple scenarios:'
    )
    story += bullet_list([
        '<b>Correct HashID + Correct Password:</b> Session created successfully, dashboard accessible. ✓',
        '<b>Incorrect HashID:</b> Redirected to home with "Invalid Credentials" flash message. Session not created. ✓',
        '<b>Correct HashID + Wrong Password:</b> Session cleared completely, redirected home with error. ✓',
        '<b>Direct navigation to /dashboard without authentication:</b> Redirected to home. ✓',
        '<b>Direct navigation to /password without completing Step 1:</b> Redirected to home. ✓',
    ])

    story += [ScreenshotBox('Figure 6.2 — Sign In Page Screenshot', height=6*cm)]
    story += caption('Figure 6.2: Two-step login — Step 1 HashID entry form with dark gold-amber styling.')

    story += subsection('6.2.4  Encryption Results')
    story += body(
        'AES encryption produces standard Fernet-encrypted binary blobs. Testing with '
        'a sample text file containing "Hello, this is a test file for SecureVault." '
        'produced the following results:'
    )
    story += bullet_list([
        'The output file is binary and completely unreadable in any text editor.',
        'The Fernet token begins with the standard gAAAAA... prefix, confirming correct implementation.',
        'meta.json is updated to {"status": "Encrypted", "algo": "AES", "key_hash": "<hash>"}.',
        'The dashboard correctly reflects the "Encrypted" status immediately.',
        'Re-uploading the file for encryption correctly triggers the double-encryption guard.',
    ])
    story += body(
        'RSA and DES encryption correctly apply the respective prefixes and byte reversal. '
        'The key hash is stored in meta.json for subsequent verification on decryption.'
    )

    story += [ScreenshotBox('Figure 6.3 — Encryption Page Screenshot', height=6.5*cm)]
    story += caption('Figure 6.3: Encryption form — file upload, algorithm selection (AES/RSA/DES), and key entry.')

    story += subsection('6.2.5  Decryption Results')
    story += body(
        'Decryption was tested with both correct and incorrect keys across all three algorithms:'
    )
    story += bullet_list([
        '<b>AES correct key:</b> Original plaintext recovered exactly, rendered in monospace terminal box. ✓',
        '<b>AES wrong key:</b> Fernet raises InvalidToken exception, caught and returns "Invalid Key". ✓',
        '<b>RSA/DES correct key:</b> Key hash verified, bytes reversed back, original text recovered. ✓',
        '<b>RSA/DES wrong key:</b> Key hash mismatch detected before decryption, "Invalid Key" returned. ✓',
    ])

    story += [ScreenshotBox('Figure 6.4 — Decrypted Output Page Screenshot', height=6*cm)]
    story += caption('Figure 6.4: Decryption output — recovered plaintext displayed in styled monospace terminal box.')

    story += section('6.3  UI/UX Evaluation')
    story += body(
        'The user interface was evaluated against a set of design quality criteria, '
        'with each criterion assessed for implementation completeness:'
    )
    story.append(make_table([
        ['Design Criterion', 'Status', 'Notes'],
        ['Consistent color theme', 'Achieved', 'Gold/amber palette consistently applied across all 14 pages'],
        ['Custom cursor implementation', 'Achieved', 'Dual-layer cursor with lag effect and hover expansion'],
        ['Smooth page transitions', 'Achieved', 'Opacity fade via body transitions on all navigation'],
        ['Glassmorphism card effects', 'Achieved', 'Dark card backgrounds with gradient top-border accents'],
        ['Canvas background animations', 'Achieved', 'Particle network on entry, grid on hero, waves on algo section'],
        ['Flash message display', 'Achieved', 'Auto-dismisses after 3 seconds with smooth opacity'],
        ['Reveal-on-scroll animations', 'Achieved', 'IntersectionObserver on all public pages'],
        ['Ticker animation', 'Achieved', 'Smooth scrolling security status ticker'],
        ['Responsive layout', 'Partial', 'Desktop-first design; mobile CSS breakpoints at 600/1000px'],
        ['Accessibility (ARIA)', 'Partial', 'No ARIA labels; limited keyboard focus styles'],
        ['Error feedback', 'Achieved', 'Flash messages on all authentication failure paths'],
        ['Team profile section', 'Achieved', 'Four team cards with photo filters and hover effects'],
        ['FAQ section', 'Achieved', 'Animated accordion with smooth max-height transitions'],
        ['Animated stats strip', 'Achieved', 'Four statistics cells with hover interactions'],
        ['Algorithm visualization', 'Achieved', 'Three-lane animated waveform canvas for AES/RSA/DES'],
    ], col_widths=[5.5*cm, 2.5*cm, 8.5*cm]))
    story += caption('Table 6.2: UI/UX evaluation against design quality criteria.')

    story += section('6.4  Security Analysis')
    story += body(
        'A thorough and honest security analysis of SecureVault reveals significant '
        'strengths as a prototype system and clearly identifies areas requiring improvement '
        'before production deployment.'
    )

    story += subsection('6.4.1  Security Strengths')
    story.append(make_table([
        ['Strength', 'Description', 'Impact'],
        ['AES via Fernet', 'Industry-standard authenticated symmetric encryption', 'High — Real cryptographic protection'],
        ['Two-factor authentication', 'Dual-barrier login prevents single-point-of-failure', 'High — Reduces credential compromise risk'],
        ['Hash-based identity', 'Reduces username enumeration attack surface', 'Medium — Phishing-resistant authentication'],
        ['Session clearance on logout', 'session.clear() prevents post-logout session hijacking', 'High — Eliminates stale session attacks'],
        ['Double-encryption guard', 'Prevents accidental data corruption via re-encryption', 'Medium — Operational safety feature'],
        ['Key hash verification', 'SHA-256 verification for DES/RSA decryption', 'Medium — Prevents unauthorized decryption'],
        ['No external data transmission', 'Files stored locally; no third-party server involved', 'High — Privacy by design'],
    ], col_widths=[4*cm, 7*cm, 4.5*cm]))
    story += caption('Table 6.3: Security strengths — features and their impact on system security posture.')

    story += subsection('6.4.2  Security Limitations and Recommended Fixes')
    story.append(make_table([
        ['Limitation', 'Risk Level', 'Recommended Fix'],
        ['Plain-text password storage', 'Critical', 'Implement bcrypt or Argon2 password hashing'],
        ['No HTTPS enforcement', 'High', 'Deploy with TLS certificate (Let\'s Encrypt/Nginx)'],
        ['RSA/DES byte-reversal only', 'High', 'Implement real RSA/DES using PyCryptodome library'],
        ['No login rate limiting', 'High', 'Add Flask-Limiter with account lockout after N failures'],
        ['HashID reversible from phone', 'Medium', 'Use HMAC with a server-side secret for HashID derivation'],
        ['Secret key hardcoded', 'Medium', 'Store in environment variable using python-dotenv'],
        ['No CSRF protection', 'Medium', 'Add Flask-WTF CSRF tokens to all form submissions'],
        ['JSON flat-file storage', 'Low', 'Migrate to SQLite/PostgreSQL for concurrent access safety'],
        ['No input validation', 'Low-Med', 'Add server-side validation and sanitization for all inputs'],
    ], col_widths=[4.5*cm, 2.5*cm, 8.5*cm]))
    story += caption('Table 6.4: Security limitations with risk assessment and recommended production fixes.')

    story += body(
        'It is important to emphasize that all identified limitations are well-known, '
        'well-documented, and have clear remediation paths. For an academic prototype '
        'demonstrating applied cryptographic principles in a controlled environment, '
        'the current implementation achieves its educational objectives successfully. '
        'The limitations do not undermine the validity or completeness of the project '
        'as a demonstration system.'
    )
    story += pagebreak()

    # ══════════════════════════════════════════════
    # CHAPTER 7: CONCLUSIONS AND FUTURE SCOPE
    # ══════════════════════════════════════════════
    story += chapter_header('Chapter 7', 'Conclusions and Future Scope')

    story += section('7.1  Conclusions')
    story += body(
        'SecureVault has been successfully designed, implemented, and tested as a complete '
        'web-based file encryption and decryption system. The project achieves all of its '
        'defined primary and secondary objectives, demonstrating practical implementation '
        'of cryptographic principles in a real-world web application context.'
    )
    story += body(
        'The system\'s most significant contribution is bridging the gap between powerful '
        'encryption technology and everyday usability. By wrapping AES-256 encryption, '
        'RSA and DES demonstrations, two-factor authentication, and real-time file status '
        'tracking into a single browser-accessible interface, SecureVault makes '
        'cryptographic file protection genuinely accessible to users without any '
        'technical background or command-line knowledge.'
    )
    story += body(
        'The hash-based identity mechanism represents a novel approach to authentication '
        'that reduces reliance on memorable and potentially guessable usernames. The '
        'hexadecimal HashID derived from a user\'s phone number creates a pseudonymous '
        'identity that is unique, deterministic, and phishing-resistant — an approach '
        'that could have value in real-world low-risk identity systems.'
    )
    story += body(
        'From an educational perspective, SecureVault successfully illustrates several '
        'key concepts in cybersecurity:'
    )
    story += bullet_list([
        'How encryption algorithms mathematically transform readable data into unreadable ciphertext',
        'How encryption keys function as the shared secret that enables controlled decryption',
        'How session management and multi-factor authentication create layered security',
        'How metadata tracking plays a critical role in file management systems',
        'How cryptographic hashing enables key verification without storing keys in plaintext',
        'How a full-stack web application integrates backend security with frontend usability',
    ])
    story += body(
        'The frontend design demonstrates that security-focused applications need not '
        'sacrifice aesthetics or usability. The professional dark gold-amber interface '
        'with animated canvas backgrounds, glassmorphism effects, and smooth transitions '
        'proves that military-grade security can be wrapped in a premium user experience.'
    )
    story += body(
        'The project has been completed within the defined scope, on schedule, and '
        'successfully verified across all twenty tested feature criteria. It represents '
        'a strong foundation for a production-ready secure file vault with clearly '
        'identified enhancement paths for future development.'
    )

    story += section('7.2  Future Scope')
    story += body(
        'The following enhancements are recommended for future development, organized '
        'into a phased roadmap:'
    )

    story += subsection('Phase 1: Security Hardening (Immediate Priority)')
    story += bullet_list([
        '<b>Password Hashing:</b> Replace plain-text password storage with bcrypt or Argon2 '
        'hashing using Python\'s passlib library. This is the highest priority security fix.',
        '<b>HTTPS Enforcement:</b> Deploy the application behind an HTTPS-enabled reverse proxy '
        '(Nginx or Apache) with a free TLS certificate from Let\'s Encrypt.',
        '<b>Rate Limiting:</b> Implement Flask-Limiter to restrict login attempts and add '
        'account lockout after a configurable number of failures.',
        '<b>CSRF Protection:</b> Add Flask-WTF to generate and validate CSRF tokens for all '
        'form submissions, preventing cross-site request forgery attacks.',
        '<b>Environment-Based Configuration:</b> Move all secrets (secret key, salt) to '
        'environment variables using python-dotenv.',
    ])

    story += subsection('Phase 2: Real Cryptographic Libraries')
    story += bullet_list([
        '<b>PyCryptodome for RSA:</b> Implement genuine RSA-2048 encryption using the '
        'PyCryptodome library, including proper key pair generation, OAEP padding, '
        'and public/private key management.',
        '<b>PyCryptodome for DES:</b> Implement actual DES and Triple-DES (3DES) encryption '
        'to provide a meaningful comparison with AES in terms of security and performance.',
        '<b>Key Management System:</b> Implement a key derivation function (PBKDF2 or Argon2) '
        'to derive encryption keys from user passwords, eliminating the need to remember '
        'and re-enter raw encryption keys.',
    ])

    story += subsection('Phase 3: Database Integration')
    story += bullet_list([
        '<b>SQLite Migration:</b> Replace JSON flat files with SQLite (via SQLAlchemy ORM) '
        'to provide proper ACID transactions, concurrent access safety, and more efficient '
        'querying.',
        '<b>PostgreSQL Support:</b> For production deployments, add PostgreSQL support with '
        'proper connection pooling and database migrations via Alembic.',
        '<b>Audit Logging:</b> Implement a database-backed audit log tracking all encryption, '
        'decryption, login, and file access events with timestamps.',
    ])

    story += subsection('Phase 4: Feature Enhancements')
    story += bullet_list([
        '<b>Binary File Support:</b> Extend the encryption system to handle PDFs, images, '
        'spreadsheets, and other binary file types.',
        '<b>File Sharing:</b> Implement encrypted file sharing between registered users '
        'using RSA public-key cryptography for secure key exchange.',
        '<b>Mobile Responsiveness:</b> Redesign the CSS layout system using CSS Grid and '
        'Flexbox with comprehensive media queries for full mobile support.',
        '<b>Drag-and-Drop Upload:</b> Add a JavaScript drag-and-drop zone on encrypt and '
        'decrypt pages for improved usability.',
        '<b>Dark/Light Mode Toggle:</b> Implement a theme switcher that respects the '
        'system\'s prefers-color-scheme media query and saves preference to localStorage.',
        '<b>File Search and Filter:</b> Add a live-search input and status filter on '
        'the dashboard for users with large numbers of vault files.',
    ])

    story += subsection('Phase 5: Deployment and DevOps')
    story += bullet_list([
        '<b>Docker Containerization:</b> Package the application in a Docker container with '
        'a Docker Compose configuration for consistent, reproducible deployment.',
        '<b>Cloud Deployment:</b> Deploy to a cloud platform (AWS, GCP, or Heroku) with '
        'environment-based configuration, automated SSL renewal, and horizontal scaling.',
        '<b>Automated Testing:</b> Implement a comprehensive test suite using pytest for '
        'all Flask routes, encryption functions, and authentication edge cases.',
        '<b>CI/CD Pipeline:</b> Set up a GitHub Actions workflow for automated testing, '
        'security scanning, and deployment on each commit.',
    ])

    story.append(BlockDiagram(
        'Figure 7.1 — Future Development Roadmap',
        [
            ('Phase 1\nSecurity\nHardening', '#E74C3C'),
            ('Phase 2\nReal Crypto\nLibraries', '#C8960C'),
            ('Phase 3\nDatabase\nIntegration', '#0F3460'),
            ('Phase 4\nFeature\nEnhance', '#27AE60'),
            ('Phase 5\nCloud\nDeploy', '#0B1437'),
        ],
        height=4*cm
    ))
    story += caption('Figure 7.1: Future development roadmap — five phases from security hardening to cloud deployment.')

    story += body(
        'The phased roadmap ensures that each enhancement builds logically upon the '
        'previous, with security always prioritized before feature expansion. The '
        'existing codebase\'s clean modular structure makes it well-suited to '
        'incremental improvement without requiring a complete architectural redesign.'
    )
    story += pagebreak()

    # ══ REFERENCES ══
    story += chapter_header('', 'References')
    refs = [
        'W. Stallings, <i>Cryptography and Network Security: Principles and Practice</i>, 7th ed. Pearson Education, 2017.',
        'B. Schneier, <i>Applied Cryptography: Protocols, Algorithms, and Source Code in C</i>, 2nd ed. Wiley, 1996.',
        'M. Grinberg, <i>Flask Web Development: Developing Web Applications with Python</i>, 2nd ed. O\'Reilly Media, 2018.',
        'N. Ferguson, B. Schneier, and T. Kohno, <i>Cryptography Engineering: Design Principles and Practical Applications</i>. Wiley, 2010.',
        'A. Perrig and D. Song, "A First Step Toward a Secure and Usable Group-Based Encryption Scheme," in <i>Proc. IEEE Symposium on Security and Privacy</i>, Oakland, CA, 2001.',
        'D. Boneh and V. Shoup, <i>A Graduate Course in Applied Cryptography</i>, ver. 0.6. [Online]. Available: https://toc.cryptobook.us',
        'Python Software Foundation, "cryptography — Cryptographic Recipes and Primitives for Python." [Online]. Available: https://cryptography.io/en/latest/',
        'Flask Documentation, "Flask User\'s Guide," Pallets Projects, 2024. [Online]. Available: https://flask.palletsprojects.com/',
        'NIST, "Advanced Encryption Standard (AES)," FIPS Publication 197, National Institute of Standards and Technology, 2001.',
        'NIST, "Digital Signature Standard (DSS)," FIPS Publication 186-5, National Institute of Standards and Technology, 2023.',
        'R. Rivest, A. Shamir, and L. Adleman, "A Method for Obtaining Digital Signatures and Public-Key Cryptosystems," <i>Communications of the ACM</i>, vol. 21, no. 2, pp. 120–126, Feb. 1978.',
        'W. Diffie and M. Hellman, "New Directions in Cryptography," <i>IEEE Transactions on Information Theory</i>, vol. 22, no. 6, pp. 644–654, Nov. 1976.',
        'OWASP Foundation, "OWASP Top Ten Security Risks," 2021. [Online]. Available: https://owasp.org/Top10/',
        'MDN Web Docs, "HTTP Cookies," Mozilla Foundation, 2024. [Online]. Available: https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies',
        'S. Gupta, "Understanding Session Management in Flask Web Applications," <i>International Journal of Computer Applications</i>, vol. 182, no. 31, pp. 1–5, May 2019.',
        'J. Daemen and V. Rijmen, <i>The Design of Rijndael: AES — The Advanced Encryption Standard</i>. Springer-Verlag, 2002.',
        'IETF, "The Transport Layer Security (TLS) Protocol Version 1.3," RFC 8446, Aug. 2018. [Online]. Available: https://tools.ietf.org/html/rfc8446',
        'P. Gutmann, <i>Engineering Security</i>. [Online]. Available: https://www.cs.auckland.ac.nz/~pgut001/pubs/book.pdf',
        'M. Howard and D. LeBlanc, <i>Writing Secure Code</i>, 2nd ed. Microsoft Press, 2002.',
        'O. Whitehouse, "A Security Analysis of the Fernet Specification," NCC Group Whitepaper, 2016. [Online]. Available: https://www.nccgroup.com/',
        'Verizon, "Data Breach Investigations Report (DBIR)," 2023. [Online]. Available: https://www.verizon.com/business/resources/reports/dbir/',
        'IBM Security, "Cost of a Data Breach Report 2023," 2023. [Online]. Available: https://www.ibm.com/reports/data-breach',
        'PyCryptodome Documentation, "PyCryptodome — A self-contained Python package of low-level cryptographic primitives," 2024. [Online]. Available: https://pycryptodome.readthedocs.io/',
        'OWASP, "Authentication Cheat Sheet," OWASP Foundation, 2023. [Online]. Available: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html',
    ]
    for i, ref in enumerate(refs):
        story.append(Paragraph(f'[{i+1}] {ref}', S['BodySmall']))
        story += space(0.1)

    return story

# ──────────────────────────────────────────────
# MAIN BUILD
# ──────────────────────────────────────────────
OUTPUT = '/home/claude/SecureVault_ProjectReport.pdf'

class CoverPage(Flowable):
    def wrap(self, aw, ah): return (aw, ah)
    def draw(self): pass

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=MARGIN,
    rightMargin=MARGIN,
    topMargin=2*cm,
    bottomMargin=1.6*cm,
    title='SecureVault — B.Tech Project Report',
    author='Jayansh, Jatin, Mihir, Sagar',
    subject='File Encryption and Decryption System',
)

on_page = make_page_template(is_cover=False)

# Build with cover page first
def first_page(canv, doc):
    build_cover(canv, doc)

def later_pages(canv, doc):
    on_page(canv, doc)

story = build_content()
doc.build(story, onFirstPage=first_page, onLaterPages=later_pages)
print(f'PDF generated: {OUTPUT}')
print(f'File size: {os.path.getsize(OUTPUT):,} bytes') 