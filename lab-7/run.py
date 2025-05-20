from triangle_func import get_triangle_type, IncorrectTriangleSides
from triangle_class import Triangle

print("=== Демонстрация функции get_triangle_type ===")
a, b, c = 2, 4, 3

try:
    t_type = get_triangle_type(a, b, c)
    print(f"Треугольник со сторонами ({a}, {b}, {c}) — {t_type}")
except IncorrectTriangleSides as e:
    print("Ошибка:", e)

print("\n=== Демонстрация класса Triangle ===")
try:
    t = Triangle(a, b, c)
    print("Тип треугольника:", t.triangle_type())
    print("Периметр:", t.perimeter())
except ValueError as e:
    print("Ошибка:", e)

