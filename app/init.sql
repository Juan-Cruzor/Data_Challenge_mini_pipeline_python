CREATE TABLE daily_user_stats (
    date DATE,
    user_id TEXT,
    searches INTEGER DEFAULT 0,
    purchases INTEGER DEFAULT 0,
    total_purchased_amount NUMERIC DEFAULT 0,
    PRIMARY KEY (date, user_id)
);

CREATE TABLE processed_events (
    event_hash TEXT PRIMARY KEY,
    processed_at TIMESTAMP DEFAULT NOW()
);