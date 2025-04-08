CREATE TABLE IF NOT EXISTS anomalies (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    time TIME NOT NULL,
    pid TEXT,
    level TEXT NOT NULL ,
    component TEXT,
    event_id TEXT,
    event_template TEXT,
    template_params JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
