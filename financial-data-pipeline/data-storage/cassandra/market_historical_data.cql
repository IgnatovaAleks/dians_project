CREATE TABLE IF NOT EXISTS market_historical_data (
    ticker TEXT,
    date DATE,
    open DECIMAL,
    high DECIMAL,
    low DECIMAL,
    close DECIMAL,
    volume BIGINT,
    stock_splits DECIMAL DEFAULT 0.0,
    dividends DECIMAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT toTimestamp(now()),
    PRIMARY KEY (ticker, date)
);
