import os
import unittest
from fastapi.testclient import TestClient
from main import app
from utils.text_sanitizer import sanitize_text
from utils.formatters import format_docx, format_pdf, format_html_preview
from ai_core.gemini_generator import GeminiDocumentGenerator

class TestLegalEase(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.sample_text = """# NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement (“Agreement”) is entered into by Party A & Party B.

ARTICLE I: CONFIDENTIALITY
- Proprietary information must be protected.
- Data retention period is 3 years.

ARTICLE II: GOVERNING LAW
This agreement is governed by the laws of California.
"""
        self.sample_terms = "Proprietary information protection; 3 year retention period; California governing law"
        self.logo_path = os.path.join(os.path.dirname(__file__), "assets", "legalease_logo.png")

    def test_text_sanitizer(self):
        dirty = "Test “smart quotes” and ‘single quotes’ & zero-width\u200bspace"
        clean = sanitize_text(dirty)
        self.assertIn('"smart quotes"', clean)
        self.assertIn("'single quotes'", clean)
        self.assertNotIn('\u200b', clean)

    def test_docx_formatter(self):
        docx_bytes = format_docx(
            text=self.sample_text,
            doc_type="Non-Disclosure Agreement",
            logo_path=self.logo_path if os.path.exists(self.logo_path) else None,
            terms_str=self.sample_terms
        )
        self.assertIsInstance(docx_bytes, bytes)
        self.assertGreater(len(docx_bytes), 1000)

    def test_pdf_formatter(self):
        pdf_bytes = format_pdf(
            text=self.sample_text,
            doc_type="Non-Disclosure Agreement",
            logo_path=self.logo_path if os.path.exists(self.logo_path) else None,
            terms_str=self.sample_terms
        )
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 500)

    def test_html_preview_formatter(self):
        html = format_html_preview(self.sample_text, doc_type="Non-Disclosure Agreement")
        self.assertIn("<h3", html)
        self.assertIn("Non-Disclosure Agreement", html)

    def test_gemini_generator(self):
        generator = GeminiDocumentGenerator()
        doc = generator.generate_document(
            document_type="Employment Contract",
            parties="ABC Corp & Jane Doe",
            terms="Salary $100k; 15 days PTO",
            dates="October 01, 2026"
        )
        self.assertIsNotNone(doc)
        self.assertIn("EMPLOYMENT CONTRACT", doc.upper())

    def test_fastapi_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "online")

    def test_fastapi_generate_endpoint(self):
        payload = {
            "document_type": "Freelance Work Contract",
            "parties": "John Doe & Client Corp",
            "terms": "Payment $50/hr; Deadline Nov 1, 2026",
            "dates": "October 01, 2026",
            "custom_instructions": "Include IP assignment"
        }
        response = self.client.post("/generate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("sanitized_content", data)
        self.assertIn("html_preview", data)

if __name__ == "__main__":
    unittest.main()
