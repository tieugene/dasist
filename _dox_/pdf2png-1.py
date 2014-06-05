#!/bin/env python
# -*- coding: utf-8 -*-
'''
http://docs.wand-py.org
'''

from pyPdf import PdfFileReader
from wand.image import Image

myfile = PdfFileReader(file('test.pdf', 'rb'))
pages = myfile.getNumPages()

for page in range(pages):
	#print page+1
	#im = Image(myfile.getPage(page))
	img = Image(filename='test.pdf[%d]' % page)
	#img.type = 'truecolormatte'	# 'bilevel', 'grayscale', 'grayscalematte' (IMAGE_TYPES)
	#img.colorspace = 'gray'	# 'grey' as for bw as for grey (COLORSPACE_TYPES)
	img.colorspace = 'gray'		# 'grey' as for bw as for grey (COLORSPACE_TYPES)
	img.format = 'png'		#
	img.save(filename = 'test-%d.png' % page)
