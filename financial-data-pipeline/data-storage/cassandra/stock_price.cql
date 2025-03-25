CREATE TABLE IF NOT EXISTS stock_price (
    ticker TEXT,
    price DECIMAL,
    change DECIMAL,
    change_percent DECIMAL,
    currency TEXT,
    timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT toTimestamp(now()),
    PRIMARY KEY (ticker, timestamp)
);
