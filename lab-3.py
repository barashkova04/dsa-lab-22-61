from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# Список операций для генерации
OPERATIONS = ['+', '-', '*', '/']

# 1. GET /number/
@app.route('/number/', methods=['GET'])
def get_number():
    param = request.args.get('param', type=float)
    if param is None:
        return jsonify({"error": "Parameter 'param' is required"}), 400
    
    random_num = random.random() * param
    return jsonify({
        "result": random_num,
        "multiplier": param,
        "random_value": random_num / param
    })

# 2. POST /number/
@app.route('/number/', methods=['POST'])
def post_number():
    data = request.get_json()
    
    if not data or 'jsonParam' not in data:
        return jsonify({"error": "JSON with 'jsonParam' field is required"}), 400
    
    try:
        json_param = float(data['jsonParam'])
    except (TypeError, ValueError):
        return jsonify({"error": "'jsonParam' must be a number"}), 400
    
    random_num = random.random() * json_param
    operation = random.choice(OPERATIONS)
    
    return jsonify({
        "result": random_num,
        "value_from_request": json_param,
        "operation": operation
    })

# 3. DELETE /number/
@app.route('/number/', methods=['DELETE'])
def delete_number():
    random_num = random.random()
    operation = random.choice(OPERATIONS)
    
    return jsonify({
        "generated_number": random_num,
        "operation": operation
    })

if __name__ == '__main__':
    app.run(debug=True)

