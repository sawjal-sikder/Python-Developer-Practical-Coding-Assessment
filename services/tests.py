import os
from io import BytesIO
from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from reportlab.pdfgen import canvas

from services.utils.services.translator import translate_pages
from services.utils.services.pdf_reader import extract_text
from services.utils.services.pdf_generator import generate_pdf


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


class TranslatorUnitTests(TestCase):
    """
    Unit tests for translation utility functions.
    """

    @patch("deep_translator.GoogleTranslator.translate")
    def test_translate_pages_success(self, mock_translate):
        # Setup mock behavior
        mock_translate.return_value = "হ্যালো, কেমন আছেন? ||| আশা করি ভালো আছেন।"
        
        pages = ["Hello, how are you?", "Hope you are doing well."]
        result = translate_pages(pages, "en", "bn")
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "হ্যালো, কেমন আছেন?")
        self.assertEqual(result[1], "আশা করি ভালো আছেন।")
        mock_translate.assert_called_once_with("Hello, how are you? ||| Hope you are doing well.")

    def test_translate_pages_same_languages(self):
        pages = ["Hello, how are you?", "Hope you are doing well."]
        # Should return original list without calling API
        result = translate_pages(pages, "en", "en")
        self.assertEqual(result, pages)

    @patch("deep_translator.GoogleTranslator.translate")
    def test_translate_pages_fallback_on_mismatch(self, mock_translate):
        # If the split counts don't match, it should fall back to page-by-page translation
        mock_translate.side_effect = [
            "Mismatched parts",  # Combined fails because it has only 1 part instead of 2
            "হ্যালো",            # First page page-by-page translation
            "ভালো"              # Second page page-by-page translation
        ]
        
        pages = ["Hello", "Good"]
        result = translate_pages(pages, "en", "bn")
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "হ্যালো")
        self.assertEqual(result[1], "ভালো")


class PDFProcessingUnitTests(TestCase):
    """
    Unit tests for PDF extraction and generation.
    """

    def test_pdf_extraction_and_generation(self):
        # Generate mock PDF with known text
        test_lines = ["Page Content 1", "Page Content 2"]
        pdf_file = create_mock_pdf(test_lines)
        
        # Extract text from the generated PDF
        extracted_pages = extract_text(pdf_file)
        self.assertTrue(len(extracted_pages) >= 1)
        self.assertIn("Page Content 1", extracted_pages[0])
        
        # Generate PDF from text
        generated_pdf_stream = generate_pdf(["translated line 1", "translated line 2"])
        self.assertIsNotNone(generated_pdf_stream)
        self.assertTrue(len(generated_pdf_stream.getvalue()) > 0)


class TranslatePDFAPITests(APITestCase):
    """
    Integration tests for POST /api/translate-pdf endpoint.
    """

    def setUp(self):
        self.url = "/api/translate-pdf/"

    @patch("services.utils.services.translator.translate_pages")
    def test_translate_pdf_api_success(self, mock_translate_pages):
        # Mock translation to return predefined list
        mock_translate_pages.return_value = ["অনূদিত পৃষ্ঠা ১"]
        
        from django.core.files.uploadedfile import SimpleUploadedFile
        pdf_content = create_mock_pdf(["Original English Text"]).read()
        pdf_file = SimpleUploadedFile("test.pdf", pdf_content, content_type="application/pdf")
        
        data = {
            "file": pdf_file,
            "source_language": "en",
            "target_language": "bn"
        }
        
        response = self.client.post(self.url, data, format="multipart")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.has_header("Content-Disposition"))
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertIn("translated.pdf", response["Content-Disposition"])

    def test_translate_pdf_missing_fields(self):
        # Missing file field
        data = {
            "source_language": "en",
            "target_language": "bn"
        }
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("file", response.json())
