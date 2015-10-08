#!/bin/sh
# Dump database (MySQL)
mysqldump -u dasist -pdasist dasist | gzip -c > data.sql.gz
