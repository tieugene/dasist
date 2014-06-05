# -*- coding: utf-8 -*-
from django.contrib import admin
from models import *

# 1. inlines
class   BillEventInLine(admin.TabularInline):
        model           = BillEvent
        extra           = 1

class   ApproverInLine(admin.TabularInline):
        model           = Approver
        extra           = 1

# 2. odmins
class	FileAdmin(admin.ModelAdmin):
	ordering	= ('id',)
	list_display	= ('id', 'name', 'size', 'md5')

class	BillAdmin(admin.ModelAdmin):
	ordering	= ('id',)
	list_display	= ('id', 'project', 'depart', 'supplier', 'assign', 'approve', 'isalive', 'isgood')
	inlines		= [BillEventInLine,]

class	ApproverAdmin(admin.ModelAdmin):
	ordering	= ('last_name', 'first_name')
	list_display	= ('last_name', 'first_name', 'role', 'jobtit',)

class	RoleAdmin(admin.ModelAdmin):
	ordering	= ('id',)
	list_display	= ('id', 'name')
	inlines		= [ApproverInLine,]

admin.site.register(File,	FileAdmin)
admin.site.register(Bill,	BillAdmin)
admin.site.register(Approver,	ApproverAdmin)
admin.site.register(Role,	RoleAdmin)
