import psycopg2
import os
import time
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

def init_postgres():
    postgres_params = {
        'host': os.environ.get('POSTGRES_HOST', 'postgres'),
        'dbname': os.environ.get('POSTGRES_DB', 'financedb'),
        'user': os.environ.get('POSTGRES_USER', 'financeuser'),
        'password': os.environ.get('POSTGRES_PASSWORD', 'password'),
        'port': os.environ.get('POSTGRES_PORT', '5432')
    }
    
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(**postgres_params)
            break
        except psycopg2.OperationalError:
            retries -= 1
            print(f"Waiting for PostgreSQL to be ready... (retries left: {retries})")
            time.sleep(5)
    
    if retries == 0:
        print("Failed to connect to PostgreSQL")
        return
    
    cursor = conn.cursor()
    
    try:
        create_tables = [
            """
            CREATE TABLE IF NOT EXISTS market_historical_data (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(10) NOT NULL,
                date DATE NOT NULL,
                open NUMERIC NOT NULL,
                high NUMERIC NOT NULL,
                low NUMERIC NOT NULL,
                close NUMERIC NOT NULL,
                volume BIGINT NOT NULL,
                stock_splits NUMERIC DEFAULT 0.0,
                dividends NUMERIC DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_ticker_date ON market_historical_data(ticker, date);
            """,
            """
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
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_ticker_multiple ON multiple_stock_prices(ticker);
            """,
            """
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
            """,
            """
            CREATE TABLE IF NOT EXISTS stock_price (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(10) NOT NULL,
                price NUMERIC NOT NULL,
                change NUMERIC NOT NULL,
                change_percent NUMERIC NOT NULL,
                currency VARCHAR(3) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_ticker_price ON stock_price(ticker);
            """
        ]
        
        for statement in create_tables:
            cursor.execute(statement)
        
        conn.commit()
        print("PostgreSQL tables created successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error creating PostgreSQL tables: {e}")
    finally:
        cursor.close()
        conn.close()

def init_cassandra():
    cassandra_host = os.environ.get('CASSANDRA_HOST', 'cassandra')
    cassandra_user = os.environ.get('CASSANDRA_USER', 'cassandra')
    cassandra_password = os.environ.get('CASSANDRA_PASSWORD', 'cassandra')
    cassandra_keyspace = os.environ.get('CASSANDRA_KEYSPACE', 'finance')
    
    retries = 10
    while retries > 0:
        try:
            auth_provider = PlainTextAuthProvider(username=cassandra_user, password=cassandra_password)
            cluster = Cluster([cassandra_host], auth_provider=auth_provider)
            session = cluster.connect()
            break
        except Exception:
            retries -= 1
            print(f"Waiting for Cassandra to be ready... (retries left: {retries})")
            time.sleep(5)
    
    if retries == 0:
        print("Failed to connect to Cassandra")
        return
    
    try:
        session.execute(f"""
            CREATE KEYSPACE IF NOT EXISTS {cassandra_keyspace}
            WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}
        """)
        
        session.execute(f"USE {cassandra_keyspace}")
        
        create_tables = [
            """
            CREATE TABLE IF NOT EXISTS market_historical_data (
                ticker text,
                date timestamp,
                open double,
                high double,
                low double,
                close double,
                volume bigint,
                PRIMARY KEY (ticker, date)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS stock_price (
                ticker text,
                price double,
                change double,
                change_percent double,
                currency text,
                timestamp timestamp,
                PRIMARY KEY (ticker, timestamp)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS multiple_stock_prices (
                ticker text,
                price double,
                change double,
                change_percent double,
                currency text,
                timestamp timestamp,
                PRIMARY KEY (ticker, timestamp)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS stock_info (
                ticker text PRIMARY KEY,
                company_name text,
                sector text,
                industry text,
                market_cap bigint,
                ceo text
            );
            """
        ]
        
        for statement in create_tables:
            session.execute(statement)
        
        print("Cassandra tables created successfully!")
        
    except Exception as e:
        print(f"Error creating Cassandra tables: {e}")
    finally:
        cluster.shutdown()

if __name__ == "__main__":
    init_postgres()
    init_cassandra()