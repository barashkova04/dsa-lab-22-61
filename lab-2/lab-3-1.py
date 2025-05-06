#Считать из параметров командной строки одномерный массив, состоящий из N целочисленных элементов.
#2. Найти минимальный элемент.
#3. Вывести индекс минимального элемента на экран.
#4. Вывести в одну строку все положительные числа массива.
#5. Вывести в одну строку все отрицательные числа массива

import sys #для доступа к аргументам командной строки
def main():
    # Считываем массив из параметров командной строки
    try:
        array = list(map(int, sys.argv[1:])) #sys.argv — это список аргументов командной строки

    except ValueError:
        print("Пожалуйста, введите целочисленные значения.")
        return

    if not array:
        print("Массив пуст.")
        return

    min_value = min(array) #находит минимальное значение в массиве.
    min_index = array.index(min_value) #находит индекс первого вхождения минимального значения в массиве

    print(f"Индекс минимального элемента: {min_index}")

    positive_numbers = [str(num) for num in array if num > 0]
    print("Положительные числа:", " ".join(positive_numbers))

    negative_numbers = [str(num) for num in array if num < 0]
    print("Отрицательные числа:", " ".join(negative_numbers))

if __name__ == "__main__":
    main()