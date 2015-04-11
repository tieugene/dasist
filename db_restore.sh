#!/bin/sh
# Restore database (MySQL)
gunzip < $1 | mysql -u dasist -pdasist dasist
