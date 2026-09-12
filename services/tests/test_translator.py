from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from services.utils.services.translator import translate_pages, translate_text
from services.tests.helpers import create_mock_pdf


class TranslatorUnitTests(TestCase):
    """
    Unit tests for translation utility functions.
    """

    @patch("services.utils.services.translator.GoogleTranslator.translate")
    def test_translate_pages_success(self, mock_translate):
        from contextlib import redirect_stdout
        from io import StringIO

        # Setup mock behavior
        mock_translate.return_value = "হ্যালো, কেমন আছেন? ||| আশা করি ভালো আছেন।"
        
        pages = ["Hello, how are you?", "Hope you are doing well."]
        
        f = StringIO()
        with redirect_stdout(f):
            result = translate_pages(pages, "en", "bn")
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "হ্যালো, কেমন আছেন?")
        self.assertEqual(result[1], "আশা করি ভালো আছেন।")
        mock_translate.assert_called_once_with("Hello, how are you? ||| Hope you are doing well.")
        
        output = f.getvalue()
        self.assertIn("হ্যালো, কেমন আছেন?", output)
        self.assertIn("আশা করি ভালো আছেন।", output)

    def test_translate_pages_same_languages(self):
        pages = ["Hello, how are you?", "Hope you are doing well."]
        # Should return original list without calling API
        result = translate_pages(pages, "en", "en")
        self.assertEqual(result, pages)

    @patch("services.utils.services.translator.GoogleTranslator.translate")
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

    @patch("services.utils.services.translator.GoogleTranslator.translate")
    def test_translate_text_success(self, mock_translate):
        from contextlib import redirect_stdout
        from io import StringIO

        mock_translate.return_value = "হ্যালো"
        
        f = StringIO()
        with redirect_stdout(f):
            result = translate_text("Hello", "en", "bn")
            
        self.assertEqual(result, "হ্যালো")
        self.assertEqual(f.getvalue().strip(), "হ্যালো")
        mock_translate.assert_called_once_with("Hello")

    def test_translate_text_empty(self):
        result = translate_text("", "en", "bn")
        self.assertEqual(result, "")

    def test_translate_text_same_languages(self):
        result = translate_text("Hello", "en", "en")
        self.assertEqual(result, "Hello")


class TranslatePDFAPITests(APITestCase):
    """
    Integration tests for POST /api/translate-pdf endpoint.
    """

    def setUp(self):
        self.url = reverse("translate_pdf")

    @patch("services.utils.services.translator.translate_pages")
    def test_translate_pdf_api_success(self, mock_translate_pages):
        # Mock translation to return predefined list
        mock_translate_pages.return_value = ["অনূদিত পৃষ্ঠা ১"]
        
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
