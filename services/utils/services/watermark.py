import re
import fitz
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

from services.utils.services.pdf_generator import (
    register_bangla_font,
    register_korean_font,
    FONT_NAME as BANGLA_FONT_NAME,
    KOREAN_FONT_NAME,
)


def contains_bangla(text):
    """
    Check if a string contains any Bangla Unicode characters.
    """
    return bool(re.search(r"[\u0980-\u09FF]", text))


def contains_korean(text):
    """
    Check if a string contains any Korean Hangul characters.
    """
    return bool(re.search(r"[\uac00-\ud7a3\u1100-\u11ff\u3130-\u318f]", text))


def create_watermark_page(text, position, opacity, color_hex, width, height):
    """
    Generate a single-page PDF containing the transparent styled watermark text in memory.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(width, height))
    
    # Choose font: Use NotoSansBengali if Bangla text is detected,
    # NotoSansKorean if Korean text is detected, otherwise fallback to standard Helvetica
    font_name = "Helvetica"
    if contains_bangla(text):
        try:
            register_bangla_font()
            font_name = BANGLA_FONT_NAME
        except Exception:
            # Fallback to standard Helvetica if font registration fails
            font_name = "Helvetica"
    elif contains_korean(text):
        try:
            register_korean_font()
            font_name = KOREAN_FONT_NAME
        except Exception:
            # Fallback to standard Helvetica if font registration fails
            font_name = "Helvetica"
            
    # Set color and opacity/alpha transparency
    # Ensure color starts with '#'
    if not color_hex.startswith("#"):
        color_hex = f"#{color_hex}"
        
    try:
        color = HexColor(color_hex)
    except Exception:
        color = HexColor("#FF0000")  # Fallback to red if color format is invalid

    c.setFillColor(color, alpha=opacity)
    c.setFont(font_name, 36)
    
    margin = 50
    position = position.lower().strip()
    
    if position == "top-left":
        c.drawString(margin, height - margin - 20, text)
    elif position == "top-center":
        c.drawCentredString(width / 2, height - margin - 20, text)
    elif position == "top-right":
        c.drawRightString(width - margin, height - margin - 20, text)
    elif position == "center":
        c.saveState()
        c.translate(width / 2, height / 2)
        c.rotate(45)  # Diagonal watermark is standard for center positions
        c.drawCentredString(0, 0, text)
        c.restoreState()
    elif position == "bottom-left":
        c.drawString(margin, margin, text)
    elif position == "bottom-center":
        c.drawCentredString(width / 2, margin, text)
    elif position == "bottom-right":
        c.drawRightString(width - margin, margin, text)
    else:
        # Fallback to center if an invalid position is provided
        c.saveState()
        c.translate(width / 2, height / 2)
        c.rotate(45)
        c.drawCentredString(0, 0, text)
        c.restoreState()
        
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def apply_watermark(pdf_file, text, position, opacity, color_hex):
    """
    Extract original PDF, overlay watermark text page-by-page, and return the watermarked PDF.
    """
    pdf_file.seek(0)
    pdf_bytes = pdf_file.read()
    
    # Open original PDF
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    for page in doc:
        rect = page.rect
        width, height = rect.width, rect.height
        
        # Create watermark for this page size
        wm_buffer = create_watermark_page(text, position, opacity, color_hex, width, height)
        wm_doc = fitz.open(stream=wm_buffer.read(), filetype="pdf")
        
        # Overlay the watermark onto the page
        page.show_pdf_page(rect, wm_doc, 0)
        wm_doc.close()
        
    output = BytesIO()
    doc.save(output)
    doc.close()
    output.seek(0)
    return output
