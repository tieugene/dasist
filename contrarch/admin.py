# -*- coding: utf-8 -*-

from django.contrib import admin

import models


# 1. inlines
class EventInLine(admin.TabularInline):
    model = models.Event
    extra = 1


# 2. odmins
class ContrarchAdmin(admin.ModelAdmin):
    ordering = ('fileseq',)
    list_display = ('fileseq', 'place', 'subject', 'depart', 'payer', 'shipper', 'docno', 'docdate', 'docsum')
    inlines = (EventInLine,)


admin.site.register(models.Contrarch, ContrarchAdmin)
