#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Converts data from 0.0.3 to 0.1.0
Src:
* ./manage.py dumpdata --format=json --indent=1 -a > 0.0.3.json
Dst:
* ./03_10.py 0.0.3.json > 0.1.0.json
* ./manage.py syncdb
* ./manage.py loaddata 0.1.0.json
* ./manage.py syncdb

Handle:
-- del record
-- modify record:
--- del attr
--- rename attr
-- add record
'''

import sys, json, pprint, decimal

'''
18/23:
MODIFY:
	bills.state
		+color
	bills.route:
		-state
		-action
	bills.bill:
		-project
		-done
		+place = addon.place
		+subject = addon.subject
		+depart = addon.depart
		+payer		= null
		+billdate	= 01.01.1970
		+billno		= '-'
		+billsum	= 0
		+payedsum	= 0
		+topaysum	= 0
	scan.scan:
CP:
	?auth.group
	?auth.permission
	auth.user
	core.file
	core.fileseq
	core.fileseqitem
	bills.approver
	bills.role
	bills.event (.comment: text => char)
	bills.state
	scan.event
RENAME:
	bills.place = addon.place
	bills.subject = addon.subject
	bills.depart = addon.depart
	bills.payer = addon.payer
TODEL:
	admin.logentry
	contenttypes.contenttype
	sessions.session
	sites.site
	addon.addon
'''

NULL = decimal.Decimal('0.00')
ADDON = dict()	# bill.pk: place, subject, depart
BILL = dict()	# bill.pk: fileseq_id

MODELS = set()
TORENAME = {
	'addon.department':	'bills.department',
	'addon.payer':		'bills.payer',
	'addon.place':		'bills.place',
	'addon.subject':	'bills.subject',
}
TOSKIP = set([
	'admin.logentry',
	'contenttypes.contenttype',
	'sessions.session',
	'sites.site',
	'addon.addon',
	# tmp
	#'bills.event',
	#'bills.route',
])

STATE_ID = {	# rpoint==None, done
	(True,	None):	1,	# Draft
	(False,	None):	2,	# OnWay
	(True,	False):	3,	# Rejected
	(False,	True):	4,	# OnPay
	(True,	True):	5,	# Done
	#(False,False):	6,	# <impossible>
}

STATE_COLOR = {
	1: 'white',
	2: 'FFFF99',
	3: 'silver',
	4: 'aqua',
	5: 'chartreuse',
	6: 'white',
	7: 'FFFF99',
	8: 'silver',
	9: 'chartreuse',
}

def	bills_state(rec):
	return {
		'pk': rec['pk'],
		'model': rec['model'],
		'fields': {
			'name':		rec['fields']['name'],
			'color':	STATE_COLOR[rec['pk']],
		}
	}

def	bills_route(rec):
	return {
		'pk': rec['pk'],
		'model': rec['model'],
		'fields': {
			'bill':		BILL[rec['fields']['bill']],
			#'state':	rec['fields']['state'],
			'role':		rec['fields']['role'],
			#'action':	rec['fields']['action'],
			'approve':	rec['fields']['approve'],
			'order':	rec['fields']['order'],
		}
	}

def	bills_event(rec):
	return {
		'pk': rec['pk'],
		'model': rec['model'],
		'fields': {
			'bill':		BILL[rec['fields']['bill']],
			'comment':	rec['fields']['comment'],
			'approve':	rec['fields']['approve'],
			'ctime':	rec['fields']['ctime'],
			'resume':	rec['fields']['resume'],
		}
	}

def	bills_bill(rec):
	pk = rec['pk']
	addon = ADDON[pk]
	return {
		'pk': rec['pk'],
		'model': rec['model'],
		'fields': {
			'fileseq':	rec['fields']['fileseq'],
			#'project': rec['fields'][''],
			'supplier':	rec['fields']['supplier'],
			'assign':	rec['fields']['assign'],
			'place':	addon['place'],
			'subject':	addon['subject'],
			'depart':	addon['depart'],
			'payer':	None,
			'billdate':	'1970-01-01',
			'billno':	'-',
			'billsum':	'0.00',
			'payedsum':	'0.00',
			'topaysum':	'0.00',
			'rpoint':	rec['fields']['rpoint'],
			#'done':		rec['fields']['done'],
			'state':	STATE_ID[(rec['fields']['rpoint']==None, rec['fields']['done'])],
		}
	}

def	scan_scan(rec):
	pk = rec['pk']
	return {
		'pk': rec['pk'],
		'model': rec['model'],
		'fields': {
			'place':	rec['fields']['project'],
			'depart':	rec['fields']['depart'],
			'supplier':	rec['fields']['supplier'],
			'no':		rec['fields']['no'],
			'date':		rec['fields']['date'],
		}
	}

TOMODIFY = {
	'bills.state':	bills_state,
	'bills.event':	bills_event,
	'bills.route':	bills_route,
	'bills.bill':	bills_bill,
	'scan.scan':	scan_scan,
}

def	main(infile):
	result = list()
	data = json.load(open(infile))
	# 1. preload some data
	for rec in data:
		model = rec['model']
		#if not model in MODELS:
		#	MODELS.add(model)
		# 1.1. rename
		if model in TORENAME:
			rec['model'] = TORENAME[model]
		# 1.2. preload
		elif model == u'addon.addon':
			ADDON[rec['pk']] = rec['fields']
		elif model == u'bills.bill':
			BILL[rec['pk']] = rec['fields']['fileseq']
	# 2. go
	for rec in data:
		model = rec['model']
		if model in TOSKIP:
			continue
		elif model in TOMODIFY:
			newrec = TOMODIFY[model](rec)
			if newrec:
				result.append(newrec)
		else:
			result.append(rec)
	#pprint.pprint(MODELS)
	print json.dumps(result, indent=1, encoding='utf-8')

if __name__ == '__main__':
	main(sys.argv[1])
