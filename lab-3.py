from flask import Flask, request, jsonify
import random

app = Flask(__name__)

@app.route('/number/', methods=['GET'])
def get_number():
    # Получаем параметр 'param' из запроса
    param = request.args.get('param', type=float)
    
    # Если параметр не передан или не является числом - возвращаем ошибку
    if param is None:
        return jsonify({"error": "Parameter 'param' is required"}), 400
    
    # Генерируем случайное число и умножаем на param
    random_number = random.random() * param
    
    # Возвращаем результат в JSON формате
    return jsonify({
        "result": random_number,
        "multiplier": param,
        "random_value": random_number / param  # Исходное случайное число
    })

if __name__ == '__main__':
    app.run(debug=True)

