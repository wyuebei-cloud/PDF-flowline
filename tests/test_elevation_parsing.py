import unittest
import sys
import os

# Ensure project root is in sys.path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from flowline_checker.core.flow_math import extract_elevation_value


class TestElevationParsing(unittest.TestCase):
    """Test suite for engineering elevation text parsing and numerical extraction."""

    def test_standard_numbers(self):
        self.assertEqual(extract_elevation_value("31.95"), 31.95)
        self.assertEqual(extract_elevation_value("102"), 102.0)
        self.assertEqual(extract_elevation_value("0.5"), 0.5)
        self.assertEqual(extract_elevation_value("0"), 0.0)
        self.assertEqual(extract_elevation_value("100.00"), 100.0)

    def test_engineering_suffixes(self):
        self.assertEqual(extract_elevation_value("31.95 FS"), 31.95)
        self.assertEqual(extract_elevation_value("31.95FS"), 31.95)
        self.assertEqual(extract_elevation_value("31.95  FS"), 31.95)
        self.assertEqual(extract_elevation_value("42.30 EL"), 42.30)
        self.assertEqual(extract_elevation_value("42.30 EL."), 42.30)
        self.assertEqual(extract_elevation_value("105.0 ELEV"), 105.0)
        self.assertEqual(extract_elevation_value("50.2 TOP"), 50.2)
        self.assertEqual(extract_elevation_value("48.1 BOT"), 48.1)

    def test_engineering_prefixes(self):
        self.assertEqual(extract_elevation_value("EL 42.30"), 42.30)
        self.assertEqual(extract_elevation_value("EL. 42.30"), 42.30)
        self.assertEqual(extract_elevation_value("ELEV 105.50"), 105.50)
        self.assertEqual(extract_elevation_value("TOP 45.0"), 45.0)
        self.assertEqual(extract_elevation_value("BOT 22.1"), 22.1)

    def test_negative_values(self):
        self.assertEqual(extract_elevation_value("-1.50"), -1.50)
        self.assertEqual(extract_elevation_value("-0.25 FS"), -0.25)
        self.assertEqual(extract_elevation_value("-10.05"), -10.05)

    def test_wrapped_and_embedded_numbers(self):
        self.assertEqual(extract_elevation_value("(31.95)"), 31.95)
        self.assertEqual(extract_elevation_value("[105.20]"), 105.2)
        self.assertEqual(extract_elevation_value("FL: 31.95"), 31.95)

    def test_invalid_or_noisy_strings(self):
        self.assertIsNone(extract_elevation_value(""))
        self.assertIsNone(extract_elevation_value("   "))
        self.assertIsNone(extract_elevation_value(None))
        self.assertIsNone(extract_elevation_value("NULL"))
        self.assertIsNone(extract_elevation_value("???"))
        self.assertIsNone(extract_elevation_value("..."))
        self.assertIsNone(extract_elevation_value("FS"))
        self.assertIsNone(extract_elevation_value("EL."))
        self.assertIsNone(extract_elevation_value("ABC"))


if __name__ == "__main__":
    unittest.main()
