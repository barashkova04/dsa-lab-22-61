import requests
import random
import time

def main():
    # Даем серверу время на запуск
    time.sleep(2)
    
    # 1. GET запрос
    get_num = random.randint(1, 10)
    print(f"\n1. Отправляем GET с param={get_num}")
    get_response = requests.get(f"http://localhost:5000/number/?param={get_num}")
    get_data = get_response.json()
    print("Ответ:", get_data)

    # 2. POST запрос
    post_num = random.randint(1, 10)
    print(f"\n2. Отправляем POST с jsonParam={post_num}")
    post_response = requests.post(
        "http://localhost:5000/number/",
        json={"jsonParam": post_num},
        headers={"Content-Type": "application/json"}
    )
    post_data = post_response.json()
    print("Ответ:", post_data)

    # 3. DELETE запрос
    print("\n3. Отправляем DELETE")
    delete_response = requests.delete("http://localhost:5000/number/")
    delete_data = delete_response.json()
    print("Ответ:", delete_data)

    # 4. Вычисление
    print("\n4. Вычисляем результат:")
    expression = f"{get_data['result']} {post_data['operation']} {post_data['result']} {delete_data['operation']} {delete_data['generated_number']}"
    result = int(eval(expression))
    print(f"Выражение: {expression}")
    print(f"Результат: {result}")

if __name__ == '__main__':
    main()

    