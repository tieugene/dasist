# -*- coding: UTF-8 -*-
__author__ = 'ti.eugene@gmail.com'

# 1. my
from dasist import db
import models, forms

# 2. flask, sqlalchemy
#import pdb
from pprint import pprint
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
# from flask.ext.classy import FlaskView, route
from flask_wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form
from sqlalchemy.orm import joinedload

# 3. 3rd paties

# 4. system
import sys
import datetime

reload(sys)
sys.setdefaultencoding('utf-8')

contact = Blueprint('contact', __name__, url_prefix='/contact')

@contact.route('/', methods=['GET'])
def index():
    #contacts = db.session.query(models.Contact).all()
    items = models.Contact.query.all()
    return  render_template('contact/list.html', items = items)

@contact.route('/add/', methods=['GET','POST'])
def add():
    form = forms.ContactForm(request.form)
    if request.method == 'POST' and form.validate():
    #if form.validate_on_submit():
        item = models.Contact(
            lastname=form.lastname.data,
            firstname=form.firstname.data,
            midname=form.midname.data,
            birthdate=form.birthdate.data,
	    #addresses=form.addresses.entries,	# - dict
            )
	#item.addresses.add('safg')
	#print form.addresses.data - [{'value': u'addressssss'}]
        db.session.add(item)	# item.id = None
        db.session.commit()	# => item.id = int
	for address in form.addresses.entries:
		db.session.add(models.ContactAddress(
			value=address.value.data,
			contact_id=item.id,
		))
	db.session.commit()
	return redirect(url_for('contact.view', id=item.id))
    return render_template('contact/form.html', form=form, id=None)


@contact.route('/<int:id>/', methods=['GET'])
def view(id):
	item = models.Contact.query.get_or_404(id)
	return render_template('contact/view.html', item = item)

@contact.route('/<int:id>/edit/', methods=['GET','POST'])
def edit(id):
    #  form = ContactForm(obj=Person)
    # person = db.session.query(models.Person).get_or_404(person_id)
    item = models.Contact.query.get_or_404(id)
    #form = forms.ContactForm(request.form, item)

    #if form.validate_on_submit():
    if request.method == 'POST':
	form = forms.ContactForm(request.form)	# , item
	if form.validate():
		# 1. what to del:
		todel = set()
		for address in form.addresses.entries:
			if (address.todel.data):
				todel.add(int(address.data['id']))
		# 2. what to add:
		while len(form.newaddresses.entries):
			address = form.newaddresses.pop_entry()
			db.session.add(models.ContactAddress(
					value=address.value.data,
					contact_id=item.id,
				))
		form.populate_obj(item)
		for id in todel:
			db.session.delete(models.ContactAddress.query.get(id))
		db.session.commit()
		return redirect(url_for('contact.view', id=item.id))
    else:
	form = forms.ContactForm(obj=item)
	#print form.addresses.data
    return render_template('contact/form.html', form=form, id=item.id)

@contact.route('/<int:id>/del/', methods=['GET'])
def delete(id):
	item = models.Contact.query.get_or_404(id)
	db.session.delete(item)
        db.session.commit()
	return redirect(url_for('contact.index'))