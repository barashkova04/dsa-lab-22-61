from triangle_func import IncorrectTriangleSides

class Triangle:
    def __init__(self, a, b, c):
        if any(side <= 0 for side in (a, b, c)) or a + b <= c or a + c <= b or b + c <= a:
            raise IncorrectTriangleSides("Некорректные стороны треугольника")
        self.a, self.b, self.c = a, b, c

    def triangle_type(self):
        if self.a == self.b == self.c:
            return "equilateral"
        elif self.a == self.b or self.b == self.c or self.a == self.c:
            return "isosceles"
        return "nonequilateral"

    def perimeter(self):
        return self.a + self.b + self.c
