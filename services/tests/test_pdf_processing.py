from django.test import TestCase
from services.utils.services.pdf_reader import extract_text
from services.utils.services.pdf_generator import generate_pdf
from services.tests.helpers import create_mock_pdf


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
        bengali_pages = ["হ্যালো ওয়ার্ল্ড", "এটি বাংলা টেক্সट।"]
        generated_pdf = generate_pdf(bengali_pages, target_language="bn")
        extracted_pages = extract_text(generated_pdf)
        self.assertEqual(len(extracted_pages), 2)
        self.assertIn("হ", extracted_pages[0])
        self.assertIn("বাংলা", extracted_pages[1])

    def test_pdf_generation_target_language_korean(self):
        # Generate PDF in Korean and extract text to verify
        korean_pages = ["안녕하세요", "이것은 한국어 텍스트입니다."]
        generated_pdf = generate_pdf(korean_pages, target_language="ko")
        extracted_pages = extract_text(generated_pdf)
        self.assertEqual(len(extracted_pages), 2)
        self.assertIn("안녕하세요", extracted_pages[0])
        self.assertIn("한국어", extracted_pages[1])

    def test_pdf_generation_target_language_japanese(self):
        # Generate PDF in Japanese and extract text to verify
        japanese_pages = ["こんにちは", "これは日本語のテキストです。"]
        generated_pdf = generate_pdf(japanese_pages, target_language="ja")
        extracted_pages = extract_text(generated_pdf)
        self.assertEqual(len(extracted_pages), 2)
        self.assertIn("こんにちは", extracted_pages[0])
        self.assertIn("これは", extracted_pages[1])

    def test_pdf_generation_target_language_hindi(self):
        # Generate PDF in Hindi and extract text to verify
        hindi_pages = ["नमस्ते", "यह हिंदी टेक्स्ट है।"]
        generated_pdf = generate_pdf(hindi_pages, target_language="hi")
        extracted_pages = extract_text(generated_pdf)
        self.assertEqual(len(extracted_pages), 2)
        self.assertIn("नम", extracted_pages[0])
        self.assertIn("यह", extracted_pages[1])
        self.assertIn("है", extracted_pages[1])

    def test_pdf_generation_target_language_arabic(self):
        # Generate PDF in Arabic and extract text to verify
        arabic_pages = ["مرحبا بك", "هذا نص باللغة العربية."]
        generated_pdf = generate_pdf(arabic_pages, target_language="ar")
        extracted_pages = extract_text(generated_pdf)
        self.assertEqual(len(extracted_pages), 2)
        self.assertTrue(len(extracted_pages[0].strip()) > 0)
        self.assertTrue(len(extracted_pages[1].strip()) > 0)

    def test_pdf_generation_target_language_urdu(self):
        # Generate PDF in Urdu and extract text to verify
        urdu_pages = ["خوش آمدید", "یہ اردو ٹیکسٹ ہے۔"]
        generated_pdf = generate_pdf(urdu_pages, target_language="ur")
        extracted_pages = extract_text(generated_pdf)
        self.assertEqual(len(extracted_pages), 2)
        self.assertTrue(len(extracted_pages[0].strip()) > 0)
        self.assertTrue(len(extracted_pages[1].strip()) > 0)

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
