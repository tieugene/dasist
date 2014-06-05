#!/bin/sh
OUT="`basename $1 .pdf`-%d.png"
echo $OUT
gs -dBATCH -dNOPAUSE -sDEVICE=pnggray -r150 -sOutputFile=$OUT $1
