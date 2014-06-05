#!/bin/env python
# -*- coding: utf-8 -*-
'''
No docs.
Try help(something),
http://docs.wand-py.org
'''

from pyPdf import PdfFileReader
from PythonMagick import Image

myfile = PdfFileReader(file('test.pdf', 'rb'))
pages = myfile.getNumPages()

for page in range(pages):
	#print page+1
	#im = Image(myfile.getPage(page))
	img = Image('test.pdf[%d]' % page)
	#img.type = GrayscaleType
	#img.colorSpace
	img.write('test-%d.png' % page)
