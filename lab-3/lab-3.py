from flask import Flask, request, jsonify
import random
import operator

app = Flask(__name__)

# Словарь операций для удобного выбора
OPERATIONS = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv
}

@app.route('/number/', methods=['GET'])
def get_number():
    # Получаем параметр из запроса
    param = request.args.get('param', type=float)
    
    if param is None:
        return jsonify({'error': 'Parameter "param" is required'}), 400
    
    # Генерируем случайное число
    random_num = random.uniform(1, 100)
    result = random_num * param
    
    return jsonify({
        'random_number': random_num,
        'param': param,
        'result': result
    })

@app.route('/number/', methods=['POST'])
def post_number():
    # Получаем JSON из тела запроса
    data = request.get_json()
    
    if not data or 'jsonParam' not in data:
        return jsonify({'error': 'JSON with "jsonParam" field is required'}), 400
    
    json_param = data['jsonParam']
    
    # Генерируем случайное число
    random_num = random.uniform(1, 100)
    
    # Выбираем случайную операцию
    op_symbol, op_func = random.choice(list(OPERATIONS.items()))
    result = op_func(random_num, json_param)
    
    return jsonify({
        'random_number': random_num,
        'jsonParam': json_param,
        'operation': op_symbol,
        'result': result
    })

@app.route('/number/', methods=['DELETE'])
def delete_number():
    # Генерируем два случайных числа
    num1 = random.uniform(1, 100)
    num2 = random.uniform(1, 100)
    
    # Выбираем случайную операцию
    op_symbol, op_func = random.choice(list(OPERATIONS.items()))
    result = op_func(num1, num2)
    
    return jsonify({
        'number1': num1,
        'number2': num2,
        'operation': op_symbol,
        'result': result
    })

if __name__ == '__main__':
    app.run(debug=True)