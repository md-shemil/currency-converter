from flask import Flask, render_template, request, redirect, url_for
import requests
import sqlite3

app = Flask(__name__)

def create_table():
    conn = sqlite3.connect('transactions.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            from_currency TEXT NOT NULL,
            to_currency TEXT NOT NULL,
            result REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

create_table()

def convert_currency(amount, from_currency, to_currency):
    api_key = 'YOUR_OPENEXCHANGERATES_API_KEY'
    url = f'https://open.er-api.com/v6/latest'
    params = {'api_key': api_key}
    response = requests.get(url, params=params)
    data = response.json()

    rate = data['rates'][to_currency] / data['rates'][from_currency]
    result = round(amount * rate, 2)
    return result

@app.route('/')
def index():
    currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'INR', 'MXN', 'BRL', 'ZAR']
    return render_template('index.html', currencies=currencies)

@app.route('/convert', methods=['POST'])
def convert():
    amount = float(request.form['amount'])
    from_currency = request.form['from_currency']
    to_currency = request.form['to_currency']

    result = convert_currency(amount, from_currency, to_currency)

    conn = sqlite3.connect('transactions.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (amount, from_currency, to_currency, result)
        VALUES (?, ?, ?, ?)
    ''', (amount, from_currency, to_currency, result))
    conn.commit()
    conn.close()

    currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'INR', 'MXN', 'BRL', 'ZAR']
    
    return render_template('index.html', currencies=currencies, result=result, amount=amount, from_currency=from_currency, to_currency=to_currency)
@app.route('/history')
def history():
    conn = sqlite3.connect('transactions.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transactions')
    transactions = cursor.fetchall()
    conn.close()

    return render_template('history.html', transactions=transactions)

@app.route('/delete/<int:transaction_id>')
def delete(transaction_id):
    conn = sqlite3.connect('transactions.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('history'))

if __name__ == '__main__':
    app.run(debug=True)
