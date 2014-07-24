# -*- coding: utf-8 -*-

from django.db import models
from django import forms
from django.utils.encoding import force_unicode

import sys, os.path

reload(sys)
sys.setdefaultencoding('utf-8')

class RenameFilesModel(models.Model):
	"""
	http://www.djangosnippets.org/snippets/1129/
	Abstract model implementing a two-phase save in order to rename
	`FileField` and `ImageField` filenames after saving.  This allows the
	final filenames to contain information like the primary key of the model.

	Example:

		class Photo(RenameFilesModel):
			file = models.ImageField(upload_to='uploads/temp')

			RENAME_FILES = {
				'file': {'dest': 'uploads/photos', 'keep_ext': True}
			}

		>>> photo = Photo(file='uploads/temp/photo.jpg')
		>>> photo.pk

		>>> photo.save()
		>>> photo.pk
		1
		>>> photo.file
		<ImageFieldFile: uploads/photos/1.jpg>

	If the 'dest' option is a callable, it will be called with the model
	instance (guaranteed to be saved) and the currently saved filename, and
	must return the new filename.  Otherwise, the filename is determined by
	'dest' and the model's primary key.

	If a file already exists at the resulting path, it is deleted.	This is
	desirable if the filename should always be the primary key, for instance.
	To avoid this behavior, write a 'dest' handler that results in a unique
	filename.

	If 'keep_ext' is True (the default), the extension of the previously saved
	filename will be appended to the primary key to construct the filename.
	The value of 'keep_ext' is not considered if 'dest' is a callable.
	"""
	RENAME_FILES = {}

	class Meta:
		abstract = True

	def save(self, force_insert=False, force_update=False):
		rename_files = getattr(self, 'RENAME_FILES', None)
		if rename_files:
			#print dir(self)
			super(RenameFilesModel, self).save(force_insert, force_update)	# unicode error
			force_insert, force_update = False, True
			for field_name, options in rename_files.iteritems():
				field = getattr(self, field_name)
				#print "Field:"
				#print field
				file_name = force_unicode(field)
				#file_name = file_name.encode('utf-8')
				name, ext = os.path.splitext(file_name)
				keep_ext = options.get('keep_ext', True)
				final_dest = options['dest']
				if callable(final_dest):
					final_name = final_dest(self, file_name)
				else:
					final_name = os.path.join(final_dest, self.getfilename())
					if keep_ext:
						final_name += ext
				if file_name != final_name:
					#if (os.path.exists(final_name)):	# костыль
					field.storage.delete(final_name)
					field.storage.save(final_name, field)
					field.storage.delete(file_name)
					setattr(self, field_name, final_name)
		super(RenameFilesModel, self).save(force_insert, force_update)
	def	getfilename(self):
		return '%08d' % (int(self.pk),)

class	ReadOnlyWidget(forms.Widget):
	def __init__(self, original_value, display_value):
		self.original_value = original_value
		self.display_value = display_value
		super(ReadOnlyWidget, self).__init__()

	def render(self, name, value, attrs=None):
		if self.display_value is not None:
			return unicode(self.display_value)
		return unicode(self.original_value)

	def value_from_datadict(self, data, files, name):
		return self.original_value

class	ReadOnlyAdminFields(object):
	'''
	http://www.djangosnippets.org/snippets/937/
	'''
	def	get_form(self, request, obj=None):
		form = super(ReadOnlyAdminFields, self).get_form(request, obj)
		if hasattr(self, 'readonly'):
			for field_name in self.readonly:
				if field_name in form.base_fields:

					if hasattr(obj, 'get_%s_display' % field_name):
						display_value = getattr(obj, 'get_%s_display' % field_name)()
					else:
						display_value = None
					form.base_fields[field_name].widget = ReadOnlyWidget(getattr(obj, field_name, ''), display_value)
					form.base_fields[field_name].required = False
		return form
