

import yfinance as yf
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import pandas as pd
from analysis import analyze_positive_days

app = Flask(__name__)
DATABASE = "stocks.db"

def save_to_csv(ticker):
    conn = sqlite3.connect(DATABASE)
    query = "SELECT date, open, high, low, close, volume FROM stocks_data WHERE ticker = ?"
    df = pd.read_sql_query(query, conn, params=(ticker,))
    conn.close()

    csv_file_path = f"{ticker}.csv"
    df.to_csv(csv_file_path, index=False)

def fetch_data_for_stock(ticker, start_date, end_date):
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

def initialize_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stocks_data (
        ticker TEXT,
        date TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER
    )
    ''')
    conn.commit()
    conn.close()

def clear_data_for_ticker(ticker):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM stocks_data WHERE ticker = ?", (ticker,))
    conn.commit()
    conn.close()

def store_stock_data_in_db(stock_data, ticker):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    for index, row in stock_data.iterrows():
        cursor.execute("INSERT INTO stocks_data (ticker, date, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                       (ticker, str(index.date()), row['Open'], row['High'], row['Low'], row['Close'], row['Volume']))
    
    conn.commit()
    conn.close()

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ticker = request.form.get('ticker')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        stock_data = fetch_data_for_stock(ticker, start_date, end_date)
        print(stock_data.head())

        if stock_data is not None:
            clear_data_for_ticker(ticker)
            store_stock_data_in_db(stock_data, ticker)
            save_to_csv(ticker)
            
        return redirect(url_for('display_stock', ticker=ticker))
    
    return render_template('index.html')

@app.route('/<ticker>')
def display_stock(ticker):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT date, open, high, low, close, volume FROM stocks_data WHERE ticker = ?", (ticker,))
    data = cursor.fetchall()
    conn.close()
    
    structured_data = []
    for row in data:
        structured_data.append({
            "date": row[0],
            "open": row[1],
            "high": row[2],
            "low": row[3],
            "close": row[4],
            "volume": row[5]
        })
    
    return render_template('stock.html', data=structured_data, ticker=ticker)

@app.route('/analysis/<ticker>')
def display_analysis(ticker):
    analysis_data = analyze_positive_days(ticker)
    return render_template('analysis.html', data=analysis_data, ticker=ticker)

if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
