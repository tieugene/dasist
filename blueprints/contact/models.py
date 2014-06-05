# -*- coding: UTF-8 -*-
'''
http://pythonhosted.org/Flask-SQLAlchemy/models.html
http://docs.sqlalchemy.org/en/latest/orm/relationships.html
http://docs.formalchemy.org
http://flask.pocoo.org/mailinglist/archive/2012/5/11/flask-wtf-problems-with-csrf-and-formfield/
http://stackoverflow.com/questions/18188428/dynamic-forms-formsets-in-flask-wtforms
http://stackoverflow.com/questions/9885693/how-i-do-to-update-data-on-many-to-many-with-wtforms-and-sqlalchemy
'''
__author__ = 'ti.eugene@gmail.com'

from dasist import db
from datetime import datetime

class Contact(db.Model):
    id		= db.Column(db.Integer, autoincrement=True, primary_key=True)
    firstname	= db.Column(db.String(length=64))
    lastname	= db.Column(db.String(length=64))
    midname	= db.Column(db.String(length=64))
    birthdate	= db.Column(db.DateTime())
    addresses	= db.relationship('ContactAddress', backref='contact', lazy='dynamic')

    def __unicode__(self):
        return '%s %s %s' % (self.lastname, self.firstname, self.midname)

class AddressType(db.Model):
    id		= db.Column(db.Integer, autoincrement=True, primary_key=True)
    name	= db.Column(db.String(length=16))

class ContactAddress(db.Model):
    id		= db.Column(db.Integer, autoincrement=True, primary_key=True)
    value	= db.Column(db.String(length=254))
    contact_id	= db.Column(db.Integer, db.ForeignKey('contact.id'))

class IMType(db.Model):
    id		= db.Column(db.Integer, autoincrement=True, primary_key=True)
    code	= db.Column(db.String(length=8))
    name	= db.Column(db.String(length=16))

class ContactIM(db.Model):
    id		= db.Column(db.Integer, autoincrement=True, primary_key=True)
    value	= db.Column(db.String(length=254))
    #type_id	= db.Column(db.Integer, db.ForeignKey('imtype.id'))
    contact_id	= db.Column(db.Integer, db.ForeignKey('contact.id'))
