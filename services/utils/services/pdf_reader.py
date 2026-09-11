import fitz


def extract_text(pdf_file):
    """
    Extract text from every page of a PDF.
    Returns a list where each item represents one page.
    """

    pdf_file.seek(0)

    document = fitz.open(
        stream=pdf_file.read(),
        filetype="pdf"
    )

    pages = []

    try:
        for page in document:
            text = page.get_text("text")
            pages.append(text)

    finally:
        document.close()

    return pages