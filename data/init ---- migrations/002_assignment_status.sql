-- ===========================
-- Assignment improvements
-- ===========================

ALTER TABLE mission_assignments
ADD COLUMN coins INTEGER DEFAULT 0;

ALTER TABLE mission_assignments
ADD COLUMN completed_points INTEGER;

ALTER TABLE mission_assignments
ADD COLUMN validated_at DATETIME;

ALTER TABLE mission_assignments
ADD COLUMN validated_by INTEGER;