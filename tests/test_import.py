import os
import unittest

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET = os.path.join(ROOT, "assets", "teapot")
PARTS = ("body", "handle", "spout", "lid", "bottom")


def read_geo(part):
    arrays = {}
    with open(os.path.join(ASSET, "geo", part + ".rib")) as f:
        for line in f:
            for name in ('"P"', '"N"', '"st"'):
                if line.lstrip().startswith(name + " ["):
                    body = line.split("[", 1)[1].rsplit("]", 1)[0]
                    arrays[name.strip('"')] = np.array(body.split(), dtype=float)
    return arrays


class GeometryTest(unittest.TestCase):
    def test_normals_are_finite_and_unit_length(self):
        for part in PARTS:
            normals = read_geo(part)["N"].reshape(-1, 3)
            self.assertTrue(np.isfinite(normals).all(), part)
            lengths = np.linalg.norm(normals, axis=1)
            self.assertLess(np.abs(lengths - 1).max(), 1e-6, part)

    def test_attributes_agree_on_vertex_count(self):
        for part in PARTS:
            geo = read_geo(part)
            self.assertEqual(len(geo["P"]) // 3, len(geo["N"]) // 3, part)
            self.assertEqual(len(geo["P"]) // 3, len(geo["st"]) // 2, part)

    def test_asset_spans_y_zero_to_three_point_one_five(self):
        heights = np.concatenate([read_geo(part)["P"].reshape(-1, 3)[:, 1] for part in PARTS])
        self.assertAlmostEqual(heights.min(), 0.0, places=6)
        self.assertAlmostEqual(heights.max(), 3.15, places=6)


if __name__ == "__main__":
    unittest.main()
