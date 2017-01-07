# -*- coding: utf-8 -*-

from django.contrib import admin

import models


# 1. inlines
class RouteInLine(admin.TabularInline):
    model = models.Route
    extra = 1


class EventInLine(admin.TabularInline):
    model = models.Event
    extra = 1


class ApproverInLine(admin.TabularInline):
    model = models.Approver
    extra = 1


class SubjectInLine(admin.TabularInline):
    model = models.Subject
    extra = 1


# 2. odmins
class RoleAdmin(admin.ModelAdmin):
    ordering = ('id',)
    list_display = ('id', 'name')
    inlines = (ApproverInLine,)


class ApproverAdmin(admin.ModelAdmin):
    # ordering    = ('user.last_name', 'user.first_name')
    ordering = ('user',)
    list_display = ('pk', 'user', 'fio', 'role', 'jobtit', 'canadd')

    def fio(self, obj):
        return ('%s %s' % (obj.user.last_name, obj.user.first_name))
    fio.short_description = 'ФИО'


class PlaceAdmin(admin.ModelAdmin):
    ordering = ('id',)
    list_display = ('id', 'name')
    inlines = (SubjectInLine,)


class DepartmentAdmin(admin.ModelAdmin):
    ordering = ('id',)
    list_display = ('id', 'name')


class PayerAdmin(admin.ModelAdmin):
    ordering = ('id',)
    list_display = ('id', 'name')


class BillAdmin(admin.ModelAdmin):
    ordering = ('fileseq',)
    list_display = ('fileseq', 'place', 'subject', 'depart', 'shipper', 'assign', 'rpoint', 'state',)
    inlines = (RouteInLine, EventInLine,)


class StateAdmin(admin.ModelAdmin):
    ordering = ('id',)
    list_display = ('id', 'name', 'color')


admin.site.register(models.Role,       RoleAdmin)
admin.site.register(models.Approver,   ApproverAdmin)
admin.site.register(models.Place,      PlaceAdmin)
admin.site.register(models.Department, DepartmentAdmin)
admin.site.register(models.Payer,      PayerAdmin)
admin.site.register(models.Bill,       BillAdmin)
admin.site.register(models.State,      StateAdmin)
