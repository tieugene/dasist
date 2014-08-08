BEGIN;
ALTER TABLE bills_bill ADD COLUMN locked bool NOT NULL DEFAULT 0;
UPDATE bills_bill SET state_id=1, locked=1 WHERE state_id=6;
UPDATE bills_bill SET state_id=2, locked=1 WHERE state_id=7;
UPDATE bills_bill SET state_id=3, locked=1 WHERE state_id=8;
UPDATE bills_bill SET state_id=5, locked=1 WHERE state_id=9;
DELETE FROM bills_state WHERE id>5;
COMMIT;
