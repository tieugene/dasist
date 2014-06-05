# -*- coding: UTF-8 -*-
__author__ = 'ti.eugene@gmail.com'

from models import Contact

#from flask_wtf import Form
from flask.ext.wtf import Form
#from wtforms.ext.sqlalchemy.orm import model_form, QuerySelectField, QuerySelectMultipleField
import wtforms
from wtforms.validators import Required, EqualTo, Email
from wtforms import validators
# from wtforms.fields.html5 import DateField

#ContactForm = model_form(Contact, base_class=Form)

class ContactAddressForm(Form):
	id = wtforms.IntegerField(u'ID')
	value = wtforms.StringField(u'Адрес',validators=[Required(), validators.Length(max=254)])
	todel = wtforms.BooleanField(u'X')

	def __init__(self, csrf_enabled=False, *args, **kwargs):
		super(ContactAddressForm, self).__init__(csrf_enabled=csrf_enabled, *args, **kwargs)

class NewContactAddressForm(Form):
	value = wtforms.StringField(u'Адрес',validators=[Required(), validators.Length(max=254)])

	def __init__(self, csrf_enabled=False, *args, **kwargs):
		super(NewContactAddressForm, self).__init__(csrf_enabled=csrf_enabled, *args, **kwargs)

class ContactForm(Form):
	lastname = wtforms.StringField(u'Фамилия',validators=[validators.Length(max=64)])
	firstname = wtforms.StringField(u'Имя',validators=[Required(),validators.Length(max=64)])
	midname = wtforms.StringField(u'Отчество',validators=[validators.Length(max=64)])
	birthdate = wtforms.DateField(u'Дата рождения')
	addresses = wtforms.FieldList(wtforms.FormField(ContactAddressForm))
	newaddresses = wtforms.FieldList(wtforms.FormField(NewContactAddressForm))
	#newaddress = wtforms.FormField(NewContactAddressForm)
	#addresses = wtforms.FieldList(wtforms.FormField(ContactAddressForm, default=None), min_entries=1)
