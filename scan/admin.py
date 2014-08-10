# -*- coding: utf-8 -*-
from django.contrib import admin
from models import *

# 1. inlines

# 2. odmins
class	ScanAdmin(admin.ModelAdmin):
	ordering	= ('fileseq',)
	list_display	= ('fileseq', 'place', 'subject', 'depart', 'shipper', 'supplier', 'no', 'date', 'sum')

admin.site.register(Scan,	ScanAdmin)
