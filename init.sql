-- Schema for the events pipeline.
-- Automatically executed by PostgreSQL on first container start.

CREATE TABLE IF NOT EXISTS daily_user_stats (
    date                   DATE    NOT NULL,
    user_id                TEXT    NOT NULL,
    searches               INTEGER NOT NULL DEFAULT 0,
    purchases              INTEGER NOT NULL DEFAULT 0,
    total_purchased_amount NUMERIC NOT NULL DEFAULT 0,
    PRIMARY KEY (date, user_id)
);

-- Tracks every processed event to prevent duplicates on re-runs.
-- Keyed on (event_type, user_id, ts) — a natural composite key since
-- the source data has no explicit event ID field.
CREATE TABLE IF NOT EXISTS processed_events (
    event_type  TEXT        NOT NULL,
    user_id     TEXT        NOT NULL,
    ts          TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (event_type, user_id, ts)
);

-- Single-row table holding the high-water mark timestamp.
-- CHECK (id = 1) enforces the single-row invariant at the DB level.
CREATE TABLE IF NOT EXISTS pipeline_watermark (
    id      INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    last_ts TIMESTAMPTZ NOT NULL
);