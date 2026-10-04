import unittest
from config import LANDMARKS
from graph import GRAPH
from main import calculate_route
from matrix_map import (BASE_MASK, BASE_PIXELS, NODE_PIXELS, edge_pixels,
                        mask_for_path, pack_pixels, unpack_pixels)


class MatrixMap(unittest.TestCase):
    def test_all_routes_highlight_the_edges_of_each_instruction(self):
        self.assertEqual(set(NODE_PIXELS), set(GRAPH))
        self.assertEqual(unpack_pixels(BASE_MASK), BASE_PIXELS)
        for start in LANDMARKS:
            for destination in LANDMARKS - {start}:
                route = calculate_route(start, destination)
                path = route["full_path"]
                offset = 0
                for step in route["steps"]:
                    with self.subTest(start=start, destination=destination, step=step["to"]):
                        end = path.index(step["to"], offset + 1)
                        segment = path[offset:end + 1]
                        expected = {NODE_PIXELS[n] for n in segment}
                        for a, b in zip(segment, segment[1:]):
                            expected.update(edge_pixels(a, b))
                        actual = unpack_pixels(step["matrix_mask"])
                        self.assertEqual(actual, expected)
                        self.assertTrue(actual <= BASE_PIXELS)
                        self.assertEqual(mask_for_path(segment), mask_for_path(segment[::-1]))
                        offset = end
                self.assertEqual(offset, len(path) - 1)

    def test_asb_to_aq_blinks_the_entire_hidden_junction_path(self):
        route = calculate_route("ASB", "AQ")
        self.assertEqual(len(route["steps"]), 1)
        pixels = unpack_pixels(route["steps"][0]["matrix_mask"])
        for node in route["full_path"]:
            self.assertIn(NODE_PIXELS[node], pixels)
        self.assertNotEqual(route["steps"][0]["matrix_mask"],
                            calculate_route("Library", "AQ")["steps"][0]["matrix_mask"])

    def test_pack_boundaries(self):
        self.assertEqual(pack_pixels({(0, 0), (7, 11)}), "800000000000000000000001")
        with self.assertRaises(ValueError):
            pack_pixels({(8, 0)})


if __name__ == "__main__":
    unittest.main()
