##Задание 1.1. Работа с математическими операциями в Python
# 2 задача
#Считать с клавиатуры три произвольных числа, вывести в консоль те числа, которые попадают в интервал [1, 50]
# Считываем три числа с клавиатуры
num1 = float(input("Введите первое число: "))
num2 = float(input("Введите второе число: "))
num3 = float(input("Введите третье число: "))

# Проверяем, попадают ли числа в интервал [1, 50]
numbers = [num1, num2, num3]
result = [num for num in numbers if 1 <= num <= 50]

# Выводим результат
print(f"Числа, попадающие в интервал [1, 50]: {result}")
