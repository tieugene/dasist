https://github.com/ifanrx/django-dajaxice
https://www.djangopackages.com/grids/g/ajax/

http://robots.thoughtbot.com/class-based-generic-views-in-django
http://habrahabr.ru/post/137168/

[post => ]get_context_data
get_queryset => get_context_data[ => get]

Итого:
	* если POST - снять реквизиты фильтра в self.filter (???)
	или
	- заслать в другую view
	- записать в session
	- передать в get
	* get_queryset: обработать session (не нравится, ппц просто)
	* get_context_data: подобрать локальные переменные
	* get: do nothing

	#@method_decorator(login_required())
	#def	dispatch(self, request, *args, **kwargs):
	#	print 'ScanList dispatch'
	#	return super(ScanList, self).dispatch(request, *args, **kwargs)

	#def	post(self, request, *args, **kwargs):
	#	'''
	#	'ScanList' object has no attribute 'object_list'
	#	'''
	#	print 'ScanList post'
	#	return self.render_to_response(self.get_context_data(), **kwargs)

	#def	get(self, request, **kwargs):
	#	'''
	#	'ScanList' object has no attribute 'object_list'
	#	'''
	#	print 'ScanList get'
	#	return self.render_to_response(self.get_context_data(), **kwargs)
