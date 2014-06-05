#!/bin/sh
CODE=/mnt/shares/ftp/VCS/my/SVN/tipython
DATA=/mnt/shares/tmp
SRCCODE=$CODE/trunk/dasist
DSTCODE=$CODE/branches/dasist
SRCDATA=$DATA/dasist-0.0.3
DSTDATA=$DATA/dasist-0.1.0
$SRCCODE/manage.py dumpdata --format=json --indent=1 -a > 0.0.3.json && \
python ./003_010.py 0.0.3.json > 0.1.0.json && \
rm -f $DSTDATA/dasist.db && \
./manage.py syncdb --noinput && \
./manage.py loaddata 0.1.0.json
