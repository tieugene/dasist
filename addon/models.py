# -*- coding: utf-8 -*-

# 1. django
from django.db import models

# 2. 3rd parties

# 3. system

# 4. local
from bills.models import Bill

class	Place(models.Model):
	#id	= models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'#')
	name	= models.CharField(max_length=32, verbose_name=u'Наименование')

	def	__unicode__(self):
		return self.name

	class   Meta:
		unique_together		= (('name',),)
		ordering                = ('name', )
		verbose_name            = u'Объект'
		verbose_name_plural     = u'Объекты'

class	Subject(models.Model):
	#id	= models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'#')
	place	= models.ForeignKey(Place, related_name='subjects', verbose_name=u'Объект')
	name	= models.CharField(max_length=32, verbose_name=u'Наименование')

	def	__unicode__(self):
		return u'%s, %s' % (self.place.name, self.name)

	class   Meta:
		unique_together		= (('place', 'name',),)
		ordering                = ('place', 'name', )
		verbose_name            = u'ПодОбъект'
		verbose_name_plural     = u'ПодОбъект'

class	Department(models.Model):
	id	= models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'#')
	name	= models.CharField(max_length=32, verbose_name=u'Наименование')

	def	__unicode__(self):
		return self.name

	class   Meta:
		unique_together		= (('name',),)
		ordering                = ('name', )
		verbose_name            = u'Направление'
		verbose_name_plural     = u'Направления'

class	Payer(models.Model):
	id	= models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'#')
	name	= models.CharField(max_length=32, verbose_name=u'Наименование')

	def	__unicode__(self):
		return self.name

	class   Meta:
		unique_together		= (('name',),)
		ordering                = ('name', )
		verbose_name            = u'Плательщик'
		verbose_name_plural     = u'Плательщики'

# Working
class	AddOn(models.Model):
	bill		= models.OneToOneField(Bill, primary_key=True, verbose_name=u'Счет')
	place		= models.ForeignKey(Place, verbose_name=u'Объект')
	subject		= models.ForeignKey(Subject, null=True, blank=True, verbose_name=u'ПодОбъект')
	depart		= models.ForeignKey(Department, verbose_name=u'Направление')
	#payer		= models.ForeignKey(Payer, null=False, blank=False, verbose_name=u'Плательщик')
	##billno		= models.CharField(max_length=64, verbose_name=u'Номер счета')
	##billdate	= models.DateField(verbose_name=u'Дата счета')
	##billsum		= models.PositiveIntegerField(default=0, verbose_name=u'Сумма счета')
	#payedsum	= models.PositiveIntegerField(default=0, verbose_name=u'Оплачено')
	#topaysum	= models.PositiveIntegerField(default=0, verbose_name=u'Сумма к оплате')

	def     __unicode__(self):
		return str(self.pk)

	class   Meta:
		#unique_together		= (('scan', 'type', 'name'),)
		#ordering                = ('id',)
		verbose_name            = u'Новый Счет'
		verbose_name_plural     = u'Новые Счета'
