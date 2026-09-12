from io import BytesIO
from reportlab.pdfgen import canvas

def create_mock_pdf(text_lines):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    y = 700
    for line in text_lines:
        p.drawString(100, y, line)
        y -= 20
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
