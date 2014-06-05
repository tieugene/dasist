# -*- coding: utf-8 -*-
from django.contrib import admin
from models import *

# 1. inlines
class   RouteInLine(admin.TabularInline):
        model           = Route
        extra           = 1

class   EventInLine(admin.TabularInline):
        model           = Event
        extra           = 1

class   ApproverInLine(admin.TabularInline):
        model           = Approver
        extra           = 1

# 2. odmins
class	StateAdmin(admin.ModelAdmin):
	ordering	= ('id',)
	list_display	= ('id', 'name')

class	RoleAdmin(admin.ModelAdmin):
	ordering	= ('id',)
	list_display	= ('id', 'name')
	inlines		= (ApproverInLine,)

class	ApproverAdmin(admin.ModelAdmin):
	#ordering	= ('user.last_name', 'user.first_name')
	ordering	= ('user',)
	list_display	= ('pk', 'user', 'fio', 'role', 'jobtit', 'canadd')
	def fio(self, obj):
		return ('%s %s' % (obj.user.last_name, obj.user.first_name))
	fio.short_description = 'ФИО'

class	BillAdmin(admin.ModelAdmin):
	ordering	= ('id',)
	list_display	= ('id', 'project', 'depart', 'supplier', 'assign', 'rpoint', 'done',)
	inlines		= (RouteInLine, EventInLine,)

admin.site.register(State,	StateAdmin)
admin.site.register(Role,	RoleAdmin)
admin.site.register(Approver,	ApproverAdmin)
admin.site.register(Bill,	BillAdmin)
