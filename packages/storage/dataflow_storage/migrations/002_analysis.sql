CREATE TABLE IF NOT EXISTS datasets (
    id TEXT PRIMARY KEY,
    owner_id TEXT NOT NULL,
    name TEXT NOT NULL,
    source TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_datasets_owner ON datasets(owner_id);

CREATE TABLE IF NOT EXISTS analyses (
    id TEXT PRIMARY KEY,
    owner_id TEXT NOT NULL,
    dataset_id TEXT NOT NULL,
    name TEXT NOT NULL,
    definition_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_analyses_owner_updated ON analyses(owner_id, updated_at);