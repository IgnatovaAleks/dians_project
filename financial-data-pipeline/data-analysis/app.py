from flask import Flask, jsonify, request
from flask_cors import CORS
from yahoo_finance_fetcher import YahooFinanceDataFetcher
import psycopg2
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd

app = Flask(__name__)
CORS(app)

fetcher = YahooFinanceDataFetcher()

postgres_conn = psycopg2.connect(
    host="postgres",
    dbname="financedb",
    user="financeuser",
    password="password"
)
postgres_cursor = postgres_conn.cursor()

cassandra_auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
cluster = Cluster(['cassandra'], auth_provider=cassandra_auth_provider)
session = cluster.connect('finance')  # Use the 'finance' keyspace

@app.route('/api/historical', methods=['GET'])
def get_historical_data():
    ticker = request.args.get('ticker', 'AAPL')
    period = request.args.get('period', '1mo')
    interval = request.args.get('interval', '1d')
    
    data = fetcher.get_historical_data(ticker, period, interval)
    
    print(f"Retrieved data for {ticker}: {data}")

    save_to_postgres(ticker, data['data'], 'historical')  
    
    save_to_cassandra(ticker, data['data'], 'historical')

    return jsonify(data)

@app.route('/api/price', methods=['GET'])
def get_price():
    ticker = request.args.get('ticker', 'AAPL')
    
    data = fetcher.get_real_time_price(ticker)
    
    save_to_postgres(ticker, data, 'price')
    
    save_to_cassandra(ticker, data, 'price')

    return jsonify(data)

@app.route('/api/multiple', methods=['GET'])
def get_multiple():
    tickers = request.args.get('tickers', 'AAPL,MSFT,GOOGL').split(',')
    
    data = fetcher.get_multiple_tickers(tickers)
    
    for ticker in tickers:
        if ticker in data and 'error' not in data[ticker]:
            save_to_postgres(ticker, data[ticker], 'multiple')
            save_to_cassandra(ticker, data[ticker], 'multiple')
    
    return jsonify(data)

@app.route('/api/info', methods=['GET'])
def get_company_info():
    ticker = request.args.get('ticker', 'AAPL')
    
    data = fetcher.get_company_info(ticker)
    
    save_to_postgres(ticker, data, 'info')
    
    save_to_cassandra(ticker, data, 'info')

    return jsonify(data)

@app.route('/api/predict', methods=['GET'])
def predict_future():
    ticker = request.args.get('ticker', 'AAPL')
    days = int(request.args.get('days', 5))

    historical_data = fetcher.get_historical_data(ticker, period="1mo", interval="1d")

    if historical_data is None or 'data' not in historical_data:
        return jsonify({'error': 'No historical data available'}), 400

    df = pd.DataFrame(historical_data['data'])
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by='Date')

    df['Days'] = np.arange(len(df))

    X = df[['Days']]
    y = df['Close']

    model = LinearRegression()
    model.fit(X, y)

    future_days = np.arange(len(df), len(df) + days).reshape(-1, 1)
    predictions = model.predict(future_days)

    future_dates = pd.date_range(df['Date'].iloc[-1], periods=days + 1)[1:]
    prediction_results = [
        {"date": str(future_dates[i].date()), "predicted_close": float(predictions[i])}
        for i in range(days)
    ]

    return jsonify({"ticker": ticker, "predictions": prediction_results})

@app.route('/api/test-db', methods=['GET'])
def test_db():
    try:
        postgres_cursor.execute(
            "INSERT INTO stock_price (ticker, price, change, change_percent, currency, timestamp) VALUES (%s, %s, %s, %s, %s, %s)",
            ('TEST', 100.0, 1.0, 1.0, 'USD', "20242025")
        )
        postgres_conn.commit()
        return jsonify({"status": "success", "message": "Test data inserted"})
    except Exception as e:
        postgres_conn.rollback()
        return jsonify({"status": "error", "message": str(e)})

def save_to_postgres(ticker, data, route):
    try:
        if route == 'historical':
            for item in data:
                query = """INSERT INTO market_historical_data (ticker, date, open, high, low, close, volume, stock_splits, dividends) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                postgres_cursor.execute(query, (
                    ticker, 
                    item['Date'], 
                    float(item['Open']), 
                    float(item['High']), 
                    float(item['Low']), 
                    float(item['Close']), 
                    float(item['Volume']), 
                    float(item.get('Stock Splits', 0)), 
                    float(item.get('Dividends', 0))
                ))
        
        elif route == 'price':
            query = """INSERT INTO stock_price (ticker, price, change, change_percent, currency, timestamp) 
                       VALUES (%s, %s, %s, %s, %s, %s)"""
            postgres_cursor.execute(query, (
                ticker, 
                float(data['price']), 
                float(data['change']), 
                float(data['change_percent']), 
                data['currency'], 
                data['timestamp']
            ))
            
        elif route == 'multiple':
            query = """INSERT INTO multiple_stock_prices (ticker, price, change, change_percent, currency, timestamp) 
                       VALUES (%s, %s, %s, %s, %s, %s)"""
            postgres_cursor.execute(query, (
                ticker, 
                float(data['price']), 
                float(data['change']), 
                float(data['change_percent']), 
                data['currency'], 
                data['timestamp']
            ))
                
        elif route == 'info':
            query = """INSERT INTO stock_info (ticker, name, description, country, industry, sector, employees, market_cap, website) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            postgres_cursor.execute(query, (
                ticker,
                data.get('name', None),
                data.get('description', None),
                data.get('country', None),
                data.get('industry', None),
                data.get('sector', None),
                data.get('employees', None),
                data.get('market_cap', None),
                data.get('website', None)
            ))
        
        postgres_conn.commit()
    except Exception as e:
        postgres_conn.rollback()
        print(f"Error saving to PostgreSQL for {ticker} (route: {route}): {e}")
        print(f"Data attempted to save: {data}")


def save_to_cassandra(ticker, data, route):
    try:
        if route == 'historical':
            for item in data:
                query = """INSERT INTO market_historical_data (ticker, date, open, high, low, close, volume) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                session.execute(query, (ticker, item['Date'], item['Open'], item['High'], 
                                        item['Low'], item['Close'], item['Volume']))
        
        elif route == 'price':
            query = """INSERT INTO stock_price (ticker, price, change, change_percent, currency, timestamp) 
                       VALUES (%s, %s, %s, %s, %s, %s)"""
            session.execute(query, (ticker, data['price'], data['change'], 
                                    data['change_percent'], data['currency'], data['timestamp']))
        
        elif route == 'multiple':
            for item in data:
                query = """INSERT INTO multiple_stock_prices (ticker, price, change, change_percent, currency, timestamp) 
                           VALUES (%s, %s, %s, %s, %s, %s)"""
                session.execute(query, (ticker, item['price'], item['change'], 
                                        item['change_percent'], item['currency'], item['timestamp']))
        
        elif route == 'info':
            query = """INSERT INTO stock_info (ticker, company_name, sector, industry, market_cap, ceo) 
                       VALUES (%s, %s, %s, %s, %s, %s)"""
            session.execute(query, (ticker, data['company_name'], data['sector'], 
                                    data['industry'], data['market_cap'], data['ceo']))

    except Exception as e:
        print(f"Error saving to Cassandra: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
