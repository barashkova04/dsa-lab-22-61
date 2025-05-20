from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from decimal import Decimal
#Invoke-RestMethod -Uri "http://localhost:5002/convert?currency_name=USD&amount=100" -Method Get
#Invoke-RestMethod -Uri "http://localhost:5002/currencies" -Method Get

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345678@localhost:5432/lab_6'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Currency(db.Model):
    __tablename__ = 'currency'
    id = db.Column(db.Integer, primary_key=True)
    currency_name = db.Column(db.String(50), unique=True, nullable=False)
    rate = db.Column(db.Numeric, nullable=False)

@app.route('/convert', methods=['GET'])
def convert_currency():
    try:
        currency_name = request.args.get('currency_name')
        amount = request.args.get('amount', type=float)

        if not currency_name or amount is None:
            return jsonify({"message": "Currency name and amount are required"}), 400

        currency = Currency.query.filter_by(currency_name=currency_name).first()
        if not currency:
            return jsonify({"message": "Currency does not exist"}), 404

        # Преобразуем amount в Decimal
        converted_value = Decimal(str(amount)) * currency.rate

        return jsonify({"converted_value": float(converted_value)}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

@app.route('/currencies', methods=['GET'])
def get_currencies():
    try:
        currencies = Currency.query.all()
        currency_list = [
            {"currency_name": currency.currency_name, "rate": float(currency.rate)}
            for currency in currencies
        ]
        return jsonify(currency_list), 200
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5002)
