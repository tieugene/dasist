# -*- coding: utf-8 -*-
from django.contrib import admin
from models import *

# 1. inlines

# 2. odmins
class	ScanAdmin(admin.ModelAdmin):
	ordering	= ('date',)
	list_display	= ('place', 'subject', 'depart', 'supplier', 'no', 'date', 'sum')

admin.site.register(Scan,	ScanAdmin)
