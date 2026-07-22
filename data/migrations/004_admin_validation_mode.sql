-- ==========================================
-- Admin validation mode option v0.1
-- ==========================================

ALTER TABLE family_config
ADD COLUMN admin_validation_mode TEXT DEFAULT 'admin_only';
