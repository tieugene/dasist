BEGIN;
ALTER TABLE "bills_bill" ADD COLUMN "shipper_id" integer REFERENCES "core_org" ("id");
ALTER TABLE "scan_scan"  ADD COLUMN "shipper_id" integer REFERENCES "core_org" ("id");
COMMIT;
