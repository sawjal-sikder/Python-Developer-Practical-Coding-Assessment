from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle


FONT_NAME = "NotoSansBengali"

FONT_PATH = (
    Path(__file__).resolve().parent.parent
    / "fonts"
    / "NotoSansBengali-Regular.ttf"
)


def register_bangla_font():

    if FONT_NAME not in pdfmetrics.getRegisteredFontNames():

        if not FONT_PATH.exists():
            raise FileNotFoundError(
                f"Font not found: {FONT_PATH}"
            )

        pdfmetrics.registerFont(
            TTFont(
                FONT_NAME,
                str(FONT_PATH)
            )
        )


def generate_pdf(pages, target_language="bn"):

    target_language = target_language.lower()
    if target_language in ("bn", "bengali"):
        register_bangla_font()
        font_name = FONT_NAME
        shaping = True
    else:
        font_name = "Helvetica"
        shaping = False

    output = BytesIO()

    pdf = canvas.Canvas(
        output,
        pagesize=A4
    )

    width, height = A4

    style = ParagraphStyle(
        "PDFLineStyle",
        fontName=font_name,
        fontSize=12,
        leading=14,
        shaping=shaping
    )

    for page_text in pages:

        y = height - 20 * mm

        lines = page_text.splitlines()

        for line in lines:

            if not line.strip():
                y -= 15
                continue

            escaped_line = escape(line)
            p = Paragraph(escaped_line, style)
            w, h = p.wrap(width - 40 * mm, height)

            # Check if we need a new page BEFORE drawing
            if y - h < 20 * mm:
                pdf.showPage()
                y = height - 20 * mm

            p.drawOn(pdf, 20 * mm, y - h)

            y -= h + 4

        pdf.showPage()

    pdf.save()

    output.seek(0)

    return output