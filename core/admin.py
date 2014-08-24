# -*- coding: utf-8 -*-
from django.contrib import admin
from models import *

# 1. inlines
class   FileSeqItemInLine(admin.TabularInline):
        model           = FileSeqItem
        extra           = 1

# 2. odmins
class	FileAdmin(admin.ModelAdmin):
	ordering	= ('id',)
	list_display	= ('id', 'name', 'size', 'md5')
	exclude		= ('name', 'size', 'md5', 'mime')
	inlines		= (FileSeqItemInLine,)

class	FileSeqAdmin(admin.ModelAdmin):
	ordering	= ('id',)
	inlines		= (FileSeqItemInLine,)

admin.site.register(File,	FileAdmin)
admin.site.register(FileSeq,	FileSeqAdmin)
