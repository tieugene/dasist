# -*- coding: utf-8 -*-
from django.contrib import admin
from models import *

# 1. inlines
class   EventInLine(admin.TabularInline):
        model           = Event
        extra           = 1

# 2. odmins
class	ScanAdmin(admin.ModelAdmin):
	ordering	= ('date',)
	list_display	= ('project', 'depart', 'supplier', 'no', 'date')
	inlines		= (EventInLine,)

admin.site.register(Scan,	ScanAdmin)
