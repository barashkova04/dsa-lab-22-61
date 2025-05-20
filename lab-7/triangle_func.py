class IncorrectTriangleSides(Exception):
    pass

def get_triangle_type(a, b, c):
    sides = sorted([a, b, c])
    if any(s <= 0 for s in sides) or sides[0] + sides[1] <= sides[2]:
        raise IncorrectTriangleSides("Некорректные стороны треугольника")

    if a == b == c:
        return "equilateral"
    elif a == b or b == c or a == c:
        return "isosceles"
    else:
        return "nonequilateral"
