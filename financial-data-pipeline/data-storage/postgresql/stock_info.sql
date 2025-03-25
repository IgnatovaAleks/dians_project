CREATE TABLE IF NOT EXISTS stock_info (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    name VARCHAR(100),
    description TEXT,
    country VARCHAR(100),
    industry VARCHAR(100),
    sector VARCHAR(100),
    employees BIGINT,
    market_cap BIGINT,
    website VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
