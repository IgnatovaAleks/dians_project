CREATE TABLE IF NOT EXISTS multiple_stock_prices (
    ticker TEXT,
    price DECIMAL,
    change DECIMAL,
    change_percent DECIMAL,
    currency TEXT,
    timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT toTimestamp(now()),
    PRIMARY KEY (ticker, timestamp)
);
