# -*- coding: utf-8 -*-

from django.contrib import admin

import models


# 1. inlines
class FileSeqItemInLine(admin.TabularInline):
    model = models.FileSeqItem
    extra = 1
    fields = ('order', 'file')


# 2. odmins
class FileAdmin(admin.ModelAdmin):
    ordering = ('id',)
    list_display = ('id', 'name', 'size', 'md5')
    exclude = ('name', 'size', 'md5', 'mime')
    inlines = (FileSeqItemInLine,)


class FileSeqAdmin(admin.ModelAdmin):
    ordering = ('id',)
    inlines = (FileSeqItemInLine,)


class OrgAdmin(admin.ModelAdmin):
    list_display = ('id', 'inn', 'name', 'fullname')
    ordering = ('name',)


admin.site.register(models.File,       FileAdmin)
admin.site.register(models.FileSeq,    FileSeqAdmin)
admin.site.register(models.Org,        OrgAdmin)
