-- 0001_init.sql

CREATE TABLE IF NOT EXISTS wallets (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    balance NUMERIC NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS wallets_events (
    id SERIAL PRIMARY KEY,
    wallet_id INTEGER REFERENCES wallets(id),
    event_type TEXT NOT NULL,
    amount NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
