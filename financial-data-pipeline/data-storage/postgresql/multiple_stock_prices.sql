CREATE TABLE IF NOT EXISTS multiple_stock_prices (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    price NUMERIC NOT NULL,
    change NUMERIC NOT NULL,
    change_percent NUMERIC NOT NULL,
    currency VARCHAR(3) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ticker_multiple ON multiple_stock_prices(ticker);
