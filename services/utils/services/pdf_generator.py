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
KOREAN_FONT_NAME = "NotoSansKorean"
JAPANESE_FONT_NAME = "NotoSansJapanese"
ARABIC_FONT_NAME = "NotoSansArabic"
URDU_FONT_NAME = "NotoNastaliqUrdu"
HINDI_FONT_NAME = "NotoSansDevanagari"

FONTS_DIR = Path(__file__).resolve().parent.parent / "fonts"


def register_custom_font(font_name, filename):
    if font_name not in pdfmetrics.getRegisteredFontNames():
        font_path = FONTS_DIR / filename
        if not font_path.exists():
            raise FileNotFoundError(f"Font not found: {font_path}")
        pdfmetrics.registerFont(TTFont(font_name, str(font_path)))


def register_bangla_font():
    register_custom_font(FONT_NAME, "NotoSansBengali-Regular.ttf")


def register_korean_font():
    register_custom_font(KOREAN_FONT_NAME, "NotoSansKR-Regular.ttf")


def register_japanese_font():
    register_custom_font(JAPANESE_FONT_NAME, "NotoSansJP-Regular.ttf")


def register_arabic_font():
    register_custom_font(ARABIC_FONT_NAME, "NotoSansArabic-Regular.ttf")


def register_urdu_font():
    register_custom_font(URDU_FONT_NAME, "NotoNastaliqUrdu-Regular.ttf")


def register_hindi_font():
    register_custom_font(HINDI_FONT_NAME, "NotoSansDevanagari-Regular.ttf")


def generate_pdf(pages, target_language="bn"):

    target_language = target_language.lower()
    if target_language in ("bn", "bengali"):
        register_bangla_font()
        font_name = FONT_NAME
        shaping = True
    elif target_language in ("ko", "korean", "ko-kr"):
        register_korean_font()
        font_name = KOREAN_FONT_NAME
        shaping = True
    elif target_language in ("ja", "japanese"):
        register_japanese_font()
        font_name = JAPANESE_FONT_NAME
        shaping = True
    elif target_language in ("ar", "arabic"):
        register_arabic_font()
        font_name = ARABIC_FONT_NAME
        shaping = True
    elif target_language in ("ur", "urdu"):
        register_urdu_font()
        font_name = URDU_FONT_NAME
        shaping = True
    elif target_language in ("hi", "hindi"):
        register_hindi_font()
        font_name = HINDI_FONT_NAME
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