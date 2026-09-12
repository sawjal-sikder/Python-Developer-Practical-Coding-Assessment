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
from services.utils.services.watermark import apply_watermark


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

    def test_pdf_generation_target_language_bengali(self):
        # Generate PDF in Bengali and extract text to verify
        bengali_pages = ["হ্যালো ওয়ার্ল্ড", "এটি বাংলা টেক্সট।"]
        generated_pdf = generate_pdf(bengali_pages, target_language="bn")
        extracted_pages = extract_text(generated_pdf)
        self.assertEqual(len(extracted_pages), 2)
        self.assertIn("হ", extracted_pages[0])
        self.assertIn("বাংলা", extracted_pages[1])

    def test_pdf_generation_target_language_english(self):
        # Generate PDF in English and extract text to verify
        english_pages = ["Hello World", "This is English text."]
        generated_pdf = generate_pdf(english_pages, target_language="en")
        extracted_pages = extract_text(generated_pdf)
        self.assertEqual(len(extracted_pages), 2)
        self.assertIn("Hello World", extracted_pages[0])
        self.assertIn("This is English text.", extracted_pages[1])

    def test_pdf_generation_boundary_overflow(self):
        # Test boundary overflow to make sure we don't get an extra blank page
        # 40 lines fit on 1 page with Paragraph style and spacing
        pages_content = ["\n".join(f"Line {i+1}" for i in range(40))]
        generated_pdf = generate_pdf(pages_content, target_language="en")
        extracted_pages = extract_text(generated_pdf)
        self.assertEqual(len(extracted_pages), 1)
        
        # 41 lines overflow to Page 2
        pages_content_overflow = ["\n".join(f"Line {i+1}" for i in range(41))]
        generated_pdf_overflow = generate_pdf(pages_content_overflow, target_language="en")
        extracted_pages_overflow = extract_text(generated_pdf_overflow)
        self.assertEqual(len(extracted_pages_overflow), 2)


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


class WatermarkPDFUnitTests(TestCase):
    """
    Unit tests for PDF watermarking utility functions.
    """

    def test_watermark_generation_and_overlay(self):
        # Create a mock source PDF
        pdf_file = create_mock_pdf(["Page 1 Content", "Page 2 Content"])
        
        # Apply center watermark
        watermarked = apply_watermark(
            pdf_file=pdf_file,
            text="TOP SECRET",
            position="center",
            opacity=0.3,
            color_hex="#0000FF"
        )
        
        self.assertIsNotNone(watermarked)
        self.assertTrue(len(watermarked.getvalue()) > 0)

    def test_watermark_bangla_support(self):
        # Create a mock source PDF
        pdf_file = create_mock_pdf(["Original English Text"])
        
        # Apply Bangla watermark
        watermarked = apply_watermark(
            pdf_file=pdf_file,
            text="গোপনীয়",  # Bangla text
            position="top-right",
            opacity=0.5,
            color_hex="00FF00"  # Without #
        )
        self.assertIsNotNone(watermarked)
        self.assertTrue(len(watermarked.getvalue()) > 0)


class WatermarkPDFAPITests(APITestCase):
    """
    Integration tests for POST /editor/pdf/watermark/ endpoint.
    """

    def setUp(self):
        self.url = "/editor/pdf/watermark/"

    def test_watermark_pdf_api_success(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        pdf_content = create_mock_pdf(["Hello, test this PDF file."]).read()
        pdf_file = SimpleUploadedFile("sample.pdf", pdf_content, content_type="application/pdf")
        
        data = {
            "file": pdf_file,
            "text": "DRAFT",
            "position": "bottom-center",
            "opacity": 0.5,
            "color": "#FF5500"
        }
        
        response = self.client.post(self.url, data, format="multipart")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.has_header("Content-Disposition"))
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertIn("watermarked.pdf", response["Content-Disposition"])

    def test_watermark_pdf_api_validation_errors(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        pdf_content = create_mock_pdf(["Test content."]).read()
        pdf_file = SimpleUploadedFile("sample.pdf", pdf_content, content_type="application/pdf")
        
        # 1. Test invalid position
        data = {
            "file": pdf_file,
            "text": "DRAFT",
            "position": "somewhere-invalid",
            "opacity": 0.5,
            "color": "#FF5500"
        }
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("position", response.json())
        
        # 2. Test invalid opacity
        data = {
            "file": pdf_file,
            "text": "DRAFT",
            "position": "center",
            "opacity": 1.5,  # Out of range (0.0 to 1.0)
            "color": "#FF5500"
        }
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("opacity", response.json())
        
        # 3. Test invalid color
        data = {
            "file": pdf_file,
            "text": "DRAFT",
            "position": "center",
            "opacity": 0.5,
            "color": "NOT-A-COLOR"
        }
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("color", response.json())
