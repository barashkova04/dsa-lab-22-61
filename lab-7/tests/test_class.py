import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from triangle_class import Triangle
from triangle_func import IncorrectTriangleSides

@pytest.mark.parametrize("a, b, c, expected", [
    (3, 3, 3, "equilateral"),
    (3, 3, 2, "isosceles"),
    (3, 4, 5, "nonequilateral")
])
def test_triangle_type(a, b, c, expected):
    t = Triangle(a, b, c)
    assert t.triangle_type() == expected

@pytest.mark.parametrize("a, b, c, expected", [
    (3, 3, 3, 9),
    (3, 4, 5, 12)
])
def test_perimeter(a, b, c, expected):
    t = Triangle(a, b, c)
    assert t.perimeter() == expected

@pytest.mark.parametrize("a, b, c", [
    (0, 2, 2),
    (-1, 3, 3),
    (1, 2, 10)
])
def test_invalid_triangle(a, b, c):
    with pytest.raises(IncorrectTriangleSides):
        Triangle(a, b, c)
