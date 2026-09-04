import unittest
import sys
import os
import tempfile
import fitz

# Ensure project root is in sys.path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from flowline_checker.models.data_types import ElevationPoint
from flowline_checker.core.pdf_handler import PDFHandler, label_offset_distance


class TestPDFExport(unittest.TestCase):
    """Test suite for PDF vector annotation generation and headless export."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.sample_pdf_path = os.path.join(self.temp_dir.name, "sample.pdf")

        # Create a blank 1-page sample PDF (A4 size: 595 x 842 pt)
        doc = fitz.open()
        doc.new_page(width=595, height=842)
        doc.save(self.sample_pdf_path)
        doc.close()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_label_offset_distance(self):
        """Single line vs multiline clearance calculation."""
        offset_1line = label_offset_distance(text_size=10, label_text="1.50")
        offset_2lines = label_offset_distance(text_size=10, label_text="1.50\nL=50'")
        self.assertGreater(offset_2lines, offset_1line)

    def test_add_directional_arrow_and_labels(self):
        """Verify line arrow, delta text annotation, and HP/LP labels in exported PDF."""
        handler = PDFHandler(self.sample_pdf_path)
        p1 = ElevationPoint(value=10.0, x=100.0, y=100.0, label="HP")
        p2 = ElevationPoint(value=8.0, x=300.0, y=300.0, label="LP")

        drawn_labels = set()
        handler.add_arrow_annotation(
            page_number=0,
            p1=p1,
            p2=p2,
            visual_arrow_size=15,
            text_size=12,
            label_text="2.00",
            drawn_labels=drawn_labels,
        )

        out_pdf = os.path.join(self.temp_dir.name, "annotated.pdf")
        handler.save_copy(out_pdf)
        handler.close()

        # Reopen and inspect PDF annotations
        doc = fitz.open(out_pdf)
        page = doc[0]
        annots = list(page.annots())

        # Expect: 1 line annotation + 1 delta freetext + 2 extrema freetexts (HP, LP)
        types = [annot.type[0] for annot in annots]
        self.assertIn(fitz.PDF_ANNOT_LINE, types)
        self.assertIn(fitz.PDF_ANNOT_FREE_TEXT, types)

        line_annot = next(a for a in annots if a.type[0] == fitz.PDF_ANNOT_LINE)
        # Should have a closed arrow end because p1.value != p2.value
        self.assertEqual(line_annot.line_ends[1], fitz.PDF_ANNOT_LE_CLOSED_ARROW)

        freetext_contents = [a.info.get("content", "") for a in annots if a.type[0] == fitz.PDF_ANNOT_FREE_TEXT]
        self.assertTrue(any("2.00" in c for c in freetext_contents))
        self.assertTrue(any("HP" in c for c in freetext_contents))
        self.assertTrue(any("LP" in c for c in freetext_contents))

        doc.close()

    def test_add_flat_arrow_has_no_arrowhead(self):
        """Flat segment (delta == 0) should remain a plain line without arrowhead."""
        handler = PDFHandler(self.sample_pdf_path)
        p1 = ElevationPoint(value=10.0, x=100.0, y=100.0)
        p2 = ElevationPoint(value=10.0, x=300.0, y=100.0)

        handler.add_arrow_annotation(
            page_number=0,
            p1=p1,
            p2=p2,
            visual_arrow_size=15,
            text_size=12,
            label_text="FLAT",
        )

        out_pdf = os.path.join(self.temp_dir.name, "flat.pdf")
        handler.save_copy(out_pdf)
        handler.close()

        doc = fitz.open(out_pdf)
        page = doc[0]
        line_annot = next(a for a in page.annots() if a.type[0] == fitz.PDF_ANNOT_LINE)
        self.assertEqual(line_annot.line_ends[1], fitz.PDF_ANNOT_LE_NONE)
        doc.close()

    def test_rotated_page_export(self):
        """Verify export succeeds without exceptions when the PDF page is rotated 90 degrees."""
        rotated_pdf_path = os.path.join(self.temp_dir.name, "rotated.pdf")
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)
        page.set_rotation(90)
        doc.save(rotated_pdf_path)
        doc.close()

        handler = PDFHandler(rotated_pdf_path)
        p1 = ElevationPoint(value=12.0, x=150.0, y=150.0, label="HP")
        p2 = ElevationPoint(value=10.0, x=350.0, y=350.0)

        handler.add_arrow_annotation(
            page_number=0,
            p1=p1,
            p2=p2,
            visual_arrow_size=15,
            text_size=12,
            label_text="2.00",
        )

        out_pdf = os.path.join(self.temp_dir.name, "rotated_out.pdf")
        handler.save_copy(out_pdf)
        handler.close()

        # Check that the exported file is valid and contains annotations
        doc_out = fitz.open(out_pdf)
        self.assertEqual(len(list(doc_out[0].annots())), 3)  # 1 line + 1 delta + 1 HP
        doc_out.close()


if __name__ == "__main__":
    unittest.main()
