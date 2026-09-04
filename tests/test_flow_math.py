import unittest
import sys
import os

# Ensure project root is in sys.path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from flowline_checker.models.data_types import ElevationPoint
from flowline_checker.core.flow_math import (
    compute_extrema_labels,
    format_delta_text,
    determine_flow_segment,
)


class TestFlowMath(unittest.TestCase):
    """Test suite for flow calculations, extrema identification, and delta formatting."""

    def _make_pt(self, value: float, x: float = 0.0, y: float = 0.0) -> ElevationPoint:
        return ElevationPoint(value=value, x=x, y=y)

    # -------------------------------------------------------------
    # 1. Extrema Identification (HP / LP)
    # -------------------------------------------------------------
    def test_extrema_short_sequence(self):
        """Sequences with fewer than 3 points cannot have intermediate extrema."""
        pts_empty = []
        compute_extrema_labels(pts_empty)

        pts_one = [self._make_pt(10.0)]
        compute_extrema_labels(pts_one)
        self.assertIsNone(pts_one[0].label)

        pts_two = [self._make_pt(10.0), self._make_pt(12.0)]
        compute_extrema_labels(pts_two)
        self.assertIsNone(pts_two[0].label)
        self.assertIsNone(pts_two[1].label)

    def test_extrema_v_valley_lp(self):
        """A valley point lower than both adjacent points must be marked LP."""
        pts = [self._make_pt(10.0), self._make_pt(8.0), self._make_pt(9.5)]
        compute_extrema_labels(pts)
        self.assertIsNone(pts[0].label)
        self.assertEqual(pts[1].label, "LP")
        self.assertIsNone(pts[2].label)

    def test_extrema_peak_hp(self):
        """A peak point higher than both adjacent points must be marked HP."""
        pts = [self._make_pt(10.0), self._make_pt(12.5), self._make_pt(11.0)]
        compute_extrema_labels(pts)
        self.assertIsNone(pts[0].label)
        self.assertEqual(pts[1].label, "HP")
        self.assertIsNone(pts[2].label)

    def test_extrema_multi_points_hp_and_lp(self):
        """Complex sequence with alternating peaks and valleys."""
        # Sequence: 10.0 -> 12.0 (HP) -> 9.0 -> 7.0 (LP) -> 8.5
        pts = [
            self._make_pt(10.0),
            self._make_pt(12.0),
            self._make_pt(9.0),
            self._make_pt(7.0),
            self._make_pt(8.5),
        ]
        compute_extrema_labels(pts)
        self.assertIsNone(pts[0].label)
        self.assertEqual(pts[1].label, "HP")
        self.assertIsNone(pts[2].label)
        self.assertEqual(pts[3].label, "LP")
        self.assertIsNone(pts[4].label)

    def test_extrema_monotonic_sequences(self):
        """Monotonic slopes should produce no extrema labels."""
        # Increasing
        inc = [self._make_pt(10.0), self._make_pt(11.0), self._make_pt(12.0)]
        compute_extrema_labels(inc)
        self.assertTrue(all(p.label is None for p in inc))

        # Decreasing
        dec = [self._make_pt(12.0), self._make_pt(11.0), self._make_pt(10.0)]
        compute_extrema_labels(dec)
        self.assertTrue(all(p.label is None for p in dec))

    def test_extrema_flat_and_plateaus(self):
        """Flat neighbors must not be mistakenly flagged as HP or LP."""
        flat = [self._make_pt(10.0), self._make_pt(10.0), self._make_pt(10.0)]
        compute_extrema_labels(flat)
        self.assertTrue(all(p.label is None for p in flat))

        plateau = [self._make_pt(10.0), self._make_pt(12.0), self._make_pt(12.0), self._make_pt(10.0)]
        compute_extrema_labels(plateau)
        self.assertTrue(all(p.label is None for p in plateau))

    # -------------------------------------------------------------
    # 2. Delta Formatting
    # -------------------------------------------------------------
    def test_format_delta_text_positive(self):
        self.assertEqual(format_delta_text(10.0, 8.5), "1.50")
        self.assertEqual(format_delta_text(8.5, 10.0), "1.50")
        self.assertEqual(format_delta_text(100.25, 100.0), "0.25")

    def test_format_delta_text_flat(self):
        self.assertEqual(format_delta_text(10.0, 10.0), "FLAT")
        self.assertEqual(format_delta_text(0.0, 0.0), "FLAT")

    # -------------------------------------------------------------
    # 3. Flow Segment Direction Determination
    # -------------------------------------------------------------
    def test_flow_direction_downhill(self):
        p1 = self._make_pt(10.0, x=10, y=10)
        p2 = self._make_pt(8.0, x=50, y=50)
        start, end, is_flat = determine_flow_segment(p1, p2)
        self.assertEqual(start, p1)
        self.assertEqual(end, p2)
        self.assertFalse(is_flat)

    def test_flow_direction_uphill_reversal(self):
        """Water flows downhill: if p2 is higher than p1, arrow must flow from p2 to p1."""
        p1 = self._make_pt(8.0, x=10, y=10)
        p2 = self._make_pt(10.0, x=50, y=50)
        start, end, is_flat = determine_flow_segment(p1, p2)
        self.assertEqual(start, p2)
        self.assertEqual(end, p1)
        self.assertFalse(is_flat)

    def test_flow_direction_flat(self):
        p1 = self._make_pt(10.0, x=10, y=10)
        p2 = self._make_pt(10.0, x=50, y=50)
        start, end, is_flat = determine_flow_segment(p1, p2)
        self.assertEqual(start, p1)
        self.assertEqual(end, p2)
        self.assertTrue(is_flat)


if __name__ == "__main__":
    unittest.main()
