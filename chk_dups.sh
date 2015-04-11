#!/bin/sh
# Find duplicates Shipper/OrderNo/OrderDate in Bills, Scans and Scan<>Bill
DOSQL="./manage.py dbshell"
# 1. find bills dups
#echo "SELECT DISTINCT shipper_id, billno, billdate FROM bills_bill ORDER BY shipper_id, billdate, billno;" | $DOSQL > 1.lst
#echo "SELECT shipper_id, billno, billdate FROM bills_bill ORDER BY shipper_id, billdate, billno;" | $DOSQL > 2.lst
#echo "SELECT COUNT(*) AS cnt, shipper_id, billno, billdate FROM bills_bill GROUP BY shipper_id, billno, billdate WHERE cnt > 1;" | $DOSQL
#echo "SELECT COUNT(*) AS cnt, shipper_id, billno, billdate FROM bills_bill GROUP BY shipper_id, billno, billdate;" | $DOSQL
#echo "SELECT COUNT(*) AS cnt FROM bills_bill;" | $DOSQL
# ok
echo "SELECT * FROM (SELECT COUNT(*) AS cnt, shipper_id, billno, billdate FROM bills_bill GROUP BY shipper_id, billno, billdate) AS a WHERE a.cnt > 1;" | $DOSQL
# err
#echo "SELECT * FROM bills_bill AS c INNER JOIN (SELECT * FROM (SELECT * FROM (SELECT COUNT(*) AS cnt, shipper_id, billno, billdate FROM bills_bill GROUP BY shipper_id, billno, billdate) AS a WHERE a.cnt > 1)) AS b) ON c.shipper_id = b.shipper_id;" | $DOSQL
echo "SELECT * FROM (SELECT COUNT(*) AS cnt, shipper_id, no, date FROM scan_scan GROUP BY shipper_id, no, date) AS a WHERE a.cnt > 1;" | $DOSQL
