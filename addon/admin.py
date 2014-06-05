# -*- coding: utf-8 -*-
from django.contrib import admin
from models import *

# 1. inlines
class   SubjectInLine(admin.TabularInline):
        model           = Subject
        extra           = 1

# 2. odmins
class	PlaceAdmin(admin.ModelAdmin):
	ordering	= ('id',)
	list_display	= ('id', 'name')
	inlines		= (SubjectInLine,)

class	DepartmentAdmin(admin.ModelAdmin):
	ordering	= ('id',)
	list_display	= ('id', 'name')

class	PayerAdmin(admin.ModelAdmin):
	ordering	= ('id',)
	list_display	= ('id', 'name')

class	AddOnAdmin(admin.ModelAdmin):
	ordering	= ('bill',)
	list_display	= ('bill',)

admin.site.register(Place,	PlaceAdmin)
admin.site.register(Department,	DepartmentAdmin)
admin.site.register(Payer,	PayerAdmin)
admin.site.register(AddOn,	AddOnAdmin)
