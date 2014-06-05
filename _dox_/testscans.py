#!/bin/env python
# -*- coding: utf-8 -*-
# Tool to check scans on std:
# <YY.MM.DD> №<номер> <Поставщик>.jpg/png
# Result:
# files: 10725
# - folders: 202
# - dates: 10.02.08+ =>
# - suppliers:

import os, sys, re

# re.compile('\(([0-9\.]*),([0-9\.]*),([0-9\.]*)\)')
regex = re.compile('([0-9]2)\.')

def	main(path):
	for (path, dirs, files) in os.walk(path):
		for filename in files:
			res = regex.search(filename, 0)
			if res:
				print res.group(0), filename

if (__name__ == '__main__'):
        if (len(sys.argv) != 2):
                print 'Usage: %s <folder>' % sys.argv[0]
                sys.exit(0)
	else:
		main(sys.argv[1])
