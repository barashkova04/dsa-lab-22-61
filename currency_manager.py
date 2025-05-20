from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
#Invoke-RestMethod -Uri http://localhost:5001/load -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"currency_name": "KRW", "rate": 0.058}'
#Invoke-RestMethod -Uri http://localhost:5001/delete -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"currency_name": "USD"}'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345678@localhost:5432/lab_6'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Currency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    currency_name = db.Column(db.String(50), unique=True, nullable=False)
    rate = db.Column(db.Numeric, nullable=False)

@app.route('/load', methods=['POST'])
def load_currency():
    data = request.json
    currency_name = data.get('currency_name')
    rate = data.get('rate')

    if Currency.query.filter_by(currency_name=currency_name).first():
        return jsonify({"message": "Currency already exists"}), 400

    new_currency = Currency(currency_name=currency_name, rate=rate)
    db.session.add(new_currency)
    db.session.commit()
    return jsonify({"message": "Currency added successfully"}), 200

@app.route('/update_currency', methods=['POST'])
def update_currency():
    data = request.json
    currency_name = data.get('currency_name')
    new_rate = data.get('rate')

    currency = Currency.query.filter_by(currency_name=currency_name).first()
    if not currency:
        return jsonify({"message": "Currency does not exist"}), 404

    currency.rate = new_rate
    db.session.commit()
    return jsonify({"message": "Currency updated successfully"}), 200

@app.route('/delete', methods=['POST'])
def delete_currency():
    data = request.json
    currency_name = data.get('currency_name')

    currency = Currency.query.filter_by(currency_name=currency_name).first()
    if not currency:
        return jsonify({"message": "Currency does not exist"}), 404

    db.session.delete(currency)
    db.session.commit()
    return jsonify({"message": "Currency deleted successfully"}), 200

if __name__ == '__main__':
    with app.app_context():  # Создание контекста приложения
        db.create_all()  # Создание таблиц
    app.run(port=5001)
