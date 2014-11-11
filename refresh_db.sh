#!/bin/sh
# Refresh DB (mysql spec)
#echo "1. dump data"
#./manage.py dumpdata --format=json --indent=1 | gzip -c > data.json.gz
echo "2. drop tables"
TMP=`mktemp --suffix=.sql`
echo "BEGIN;" > $TMP
echo "SET FOREIGN_KEY_CHECKS = 0;" >> $TMP
for i in `echo "SHOW TABLES;" | ./manage.py dbshell`; do echo "DROP TABLE IF EXISTS $i;" >> $TMP; done
echo "COMMIT;" >> $TMP
cat $TMP | ./manage.py dbshell
echo "3. recreate db"
echo "no" | ./manage.py syncdb > /dev/null
echo "4. clean tables"
echo "BEGIN;" > $TMP
for i in `echo "SHOW TABLES;" | ./manage.py dbshell | grep -v ^Tables_in_dasist`; do echo "DELETE FROM $i;" >> $TMP; done
echo "COMMIT;" >> $TMP
cat $TMP | ./manage.py dbshell
echo "5. load data"
./manage.py loaddata data.json.gz
# the end
rm -f $TMP
