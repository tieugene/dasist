# -*- coding: utf-8 -*-

from django.contrib import admin

import models


# 1. inlines
class EventInLine(admin.TabularInline):
    model = models.Event
    extra = 1


# 2. odmins
class ScanAdmin(admin.ModelAdmin):
    ordering = ('fileseq',)
    list_display = ('fileseq', 'place', 'subject', 'depart', 'shipper', 'supplier', 'no', 'date', 'sum')
    inlines = (EventInLine,)


admin.site.register(models.Scan, ScanAdmin)
