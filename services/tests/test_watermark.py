from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from services.utils.services.watermark import apply_watermark
from services.tests.helpers import create_mock_pdf


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

    def test_watermark_korean_support(self):
        # Create a mock source PDF
        pdf_file = create_mock_pdf(["Original English Text"])
        
        # Apply Korean watermark
        watermarked = apply_watermark(
            pdf_file=pdf_file,
            text="안녕",  # Korean text
            position="top-right",
            opacity=0.5,
            color_hex="00FF00"  # Without #
        )
        self.assertIsNotNone(watermarked)
        self.assertTrue(len(watermarked.getvalue()) > 0)

    def test_watermark_japanese_support(self):
        # Create a mock source PDF
        pdf_file = create_mock_pdf(["Original English Text"])
        
        # Apply Japanese watermark
        watermarked = apply_watermark(
            pdf_file=pdf_file,
            text="こんにちは",  # Japanese text
            position="top-right",
            opacity=0.5,
            color_hex="00FF00"  # Without #
        )
        self.assertIsNotNone(watermarked)
        self.assertTrue(len(watermarked.getvalue()) > 0)

    def test_watermark_hindi_support(self):
        # Create a mock source PDF
        pdf_file = create_mock_pdf(["Original English Text"])
        
        # Apply Hindi watermark
        watermarked = apply_watermark(
            pdf_file=pdf_file,
            text="नमस्ते",  # Hindi text
            position="top-right",
            opacity=0.5,
            color_hex="00FF00"  # Without #
        )
        self.assertIsNotNone(watermarked)
        self.assertTrue(len(watermarked.getvalue()) > 0)

    def test_watermark_arabic_support(self):
        # Create a mock source PDF
        pdf_file = create_mock_pdf(["Original English Text"])
        
        # Apply Arabic watermark
        watermarked = apply_watermark(
            pdf_file=pdf_file,
            text="مرحبا",  # Arabic text
            position="top-right",
            opacity=0.5,
            color_hex="00FF00"  # Without #
        )
        self.assertIsNotNone(watermarked)
        self.assertTrue(len(watermarked.getvalue()) > 0)

    def test_watermark_urdu_support(self):
        # Create a mock source PDF
        pdf_file = create_mock_pdf(["Original English Text"])
        
        # Apply Urdu watermark
        watermarked = apply_watermark(
            pdf_file=pdf_file,
            text="خوش",  # Urdu text
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
        self.url = reverse("watermark_pdf")

    def test_watermark_pdf_api_success(self):
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
