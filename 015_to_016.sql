ALTER TABLE bills_bill
	MODIFY `shipper_id` int(11) NOT NULL,
	ADD UNIQUE `shipper_id` (`shipper_id`,`billno`,`billdate`),
	DROP INDEX `bills_bill_272520ac`,
	DROP COLUMN `supplier`
;