#!/bin/sh
# Refresh DB (sqlite spec)
echo "1. dump data (30'')"
time ./manage.py dumpdata --format=json --indent=1 | gzip -c > data.json.gz
echo "2. drop tables"
time for i in `echo ".tables" | ./manage.py dbshell`; do echo "DROP TABLE IF EXISTS $i;" | ./manage.py dbshell; done
echo "3. recreate db"
time echo "no" | ./manage.py syncdb
echo "4. clean tables"
time for i in `echo ".tables" | ./manage.py dbshell`; do echo "DELETE FROM $i;" | ./manage.py dbshell; done
echo "5. load data"
time ./manage.py loaddata data.json
