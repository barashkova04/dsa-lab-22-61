import sys

def main():
    # Считываем массив из параметров командной строки
    try:
        array = list(map(int, sys.argv[1:]))
    except ValueError:
        print("Пожалуйста, введите целочисленные значения.")
        return

    if not array:
        print("Массив пуст.")
        return

    # Находим минимальный элемент и его индекс
    min_value = min(array)
    min_index = array.index(min_value)

    # Выводим индекс минимального элемента
    print(f"Индекс минимального элемента: {min_index}")

    # Выводим положительные числа
    positive_numbers = [str(num) for num in array if num > 0]
    print("Положительные числа:", " ".join(positive_numbers))

    # Выводим отрицательные числа
    negative_numbers = [str(num) for num in array if num < 0]
    print("Отрицательные числа:", " ".join(negative_numbers))

if __name__ == "__main__":
    main()