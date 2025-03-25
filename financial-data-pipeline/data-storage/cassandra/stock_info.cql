CREATE TABLE IF NOT EXISTS stock_info (
    ticker TEXT PRIMARY KEY,
    name TEXT,
    description TEXT,
    country TEXT,
    industry TEXT,
    sector TEXT,
    employees BIGINT,
    market_cap BIGINT,
    website TEXT,
    created_at TIMESTAMP DEFAULT toTimestamp(now())
);
