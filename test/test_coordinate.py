import unittest
from board import Coordinate


class TestCoordinate(unittest.TestCase):

    def test_from_string(self):
        self.assertEqual(Coordinate.from_string("a1"), Coordinate(0, 0))
        self.assertEqual(Coordinate.from_string("a2"), Coordinate(0, 1))
        self.assertEqual(Coordinate.from_string("h8"), Coordinate(7, 7))
        self.assertEqual(Coordinate.from_string("c3"), Coordinate(2, 2))
        self.assertEqual(Coordinate.from_string("f6"), Coordinate(5, 5))
        self.assertEqual(Coordinate.from_string("d4"), Coordinate(3, 3))

    def test_to_string(self):
        self.assertEqual(Coordinate.to_string(Coordinate(0, 0)), "a1")
        self.assertEqual(Coordinate.to_string(Coordinate(0, 1)), "a2")
        self.assertEqual(Coordinate.to_string(Coordinate(7, 7)), "h8")
        self.assertEqual(Coordinate.to_string(Coordinate(2, 2)), "c3")
        self.assertEqual(Coordinate.to_string(Coordinate(5, 5)), "f6")
        self.assertEqual(Coordinate.to_string(Coordinate(3, 3)), "d4")


if __name__ == "__main__":
    unittest.main()
