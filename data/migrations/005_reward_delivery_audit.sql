-- Migration 005: Reward Audit & Icons
ALTER TABLE rewards ADD COLUMN icon TEXT DEFAULT '🎁';
ALTER TABLE reward_history ADD COLUMN delivered_by INTEGER;
ALTER TABLE reward_history ADD COLUMN delivered_at DATETIME;
ALTER TABLE reward_history ADD COLUMN comment TEXT;
