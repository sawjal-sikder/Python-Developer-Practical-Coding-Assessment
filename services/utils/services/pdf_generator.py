from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


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


def generate_pdf(pages):

    register_bangla_font()

    output = BytesIO()

    pdf = canvas.Canvas(
        output,
        pagesize=A4
    )

    width, height = A4

    pdf.setFont(
        FONT_NAME,
        12
    )

    for page_text in pages:

        y = height - 20 * mm

        lines = page_text.splitlines()

        for line in lines:

            if not line.strip():
                y -= 15
                continue

            pdf.drawString(
                20 * mm,
                y,
                line
            )

            y -= 18

            # Create another page if content reaches bottom
            if y < 20 * mm:
                pdf.showPage()

                pdf.setFont(
                    FONT_NAME,
                    12
                )

                y = height - 20 * mm

        pdf.showPage()

    pdf.save()

    output.seek(0)

    return output