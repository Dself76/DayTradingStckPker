import sqlite3

DATABASE = "stocks.db"

def analyze_positive_days(ticker):
    conn = sqlite3.connect(DATABASE)
    query = "SELECT date, open, close FROM stocks_data WHERE ticker = ?"
    data = conn.execute(query, (ticker,)).fetchall()
    conn.close()

    # Dictionary to store results: {year: {month: count of positive days}}
    results = {}

    for row in data:
        date = row[0]
        open_price = row[1]
        close_price = row[2]

        year, month, _ = date.split('-')

        if year not in results:
            results[year] = {}
        if month not in results[year]:
            results[year][month] = 0

        if close_price > open_price:
            results[year][month] += 1

    # Prepare output
    output = []
    for year, months in results.items():
        yearly_data = {"year": year, "months": []}
        for month, count in months.items():
            yearly_data["months"].append({"month": month, "positive_days": count})

        best_month = max(months, key=months.get)
        yearly_data["best_month"] = best_month

        output.append(yearly_data)

    return output
