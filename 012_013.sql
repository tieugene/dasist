BEGIN;
ALTER TABLE bills_bill ADD COLUMN suppinn_id bool varchar(12) REFERENCES core_org (inn);
ALTER TABLE scan_scan  ADD COLUMN suppinn_id bool varchar(12) REFERENCES core_org (inn);
COMMIT;
