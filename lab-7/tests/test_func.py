import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from triangle_func import get_triangle_type, IncorrectTriangleSides

class TestTriangleFunction(unittest.TestCase):
    def test_equilateral(self):
        self.assertEqual(get_triangle_type(3, 3, 3), "equilateral")

    def test_isosceles(self):
        self.assertEqual(get_triangle_type(3, 3, 2), "isosceles")

    def test_nonequilateral(self):
        self.assertEqual(get_triangle_type(3, 4, 5), "nonequilateral")

    def test_invalid_sides(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(0, 1, 2)
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(1, 2, 10)
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(-1, 2, 3)

if __name__ == '__main__':
    unittest.main()
