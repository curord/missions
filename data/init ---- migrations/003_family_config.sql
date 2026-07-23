-- ==========================================
-- Family Config Schema v0.1
-- ==========================================

CREATE TABLE IF NOT EXISTS family_config (
    family_id INTEGER PRIMARY KEY,
    auto_approve_admin_missions INTEGER DEFAULT 0,
    rewards_require_delivery INTEGER DEFAULT 1,
    count_weekends_streaks INTEGER DEFAULT 1,
    admin_validation_mode TEXT DEFAULT 'admin_only',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id)
);

