# -*- coding: utf-8 -*-

# 1. django
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile

# 2. 3rd parties
#from sortedm2m.fields import SortedManyToManyField

# 3. system
import os, datetime, hashlib, uuid
from StringIO import StringIO

# 4. local
from rfm import RenameFilesModel

def    my_upload_to(instance, filename):
	'''
	Generates upload path for FileField
	'''
	instance.name = filename
	#return u'temp/%s' % filename
	return u'temp/%s' % uuid.uuid4().hex.upper()

def file_md5(file, block_size=1024*14):
	'''
	file_md5(file, use_system = False) -> md5sum of "file" as hexdigest string.
	"file" may be a file name or file object, opened for read.
	If "use_system" is True, if possible use system specific program. This ignore, if file object given.
	"block_size" -- size in bytes buffer for calc md5. Used with "use_system=False".
	'''
	if isinstance(file, basestring):
		file = open(file, 'rb')
	h = hashlib.md5()
	block = file.read(block_size)
	while block:
		h.update(block)
		block = file.read(block_size)
	return h.hexdigest()

class	File(RenameFilesModel):
	'''
	TODO:
	* delete
	'''
	#filename	= models.CharField(max_length=255, db_index=True, blank=False, verbose_name=u'Filename')
	#mimetype	= models.CharField(max_length=64, verbose_name=u'MIME')
	#size

	#file	= models.FileField(null=False, upload_to=my_upload_to, verbose_name=u'Файл')    # attrs: name, path, url, size
	file	= models.FileField(null=False, upload_to=my_upload_to, verbose_name=u'Файл')    # attrs: name, path, url, size
	name	= models.CharField(null=False, db_index=True, blank=False, max_length=255, verbose_name=u'Имя файла')
	mime	= models.CharField(null=False, blank=False, max_length=255, verbose_name=u'Тип Mime')
	ctime	= models.DateTimeField(null=False, blank=False, auto_now_add=True, verbose_name=u'Записано')
	size	= models.PositiveIntegerField(null=False, blank=False, verbose_name=u'Размер')
	md5	= models.CharField(null=False, blank=False, max_length=32, verbose_name=u'MD5')
	#RENAME_FILES    = {'file': {'dest': settings.BILLS_ROOT, 'keep_ext': False}}
	RENAME_FILES    = {'file': {'dest': '', 'keep_ext': False}}

	def	save(self):
		'''
		New: file = <InMemoryUploadedFile: 2.html (text/html)>
		django...file: _get_size
		'''
		#if (self.file._file):	# FIXME: костыль, надо not isinstance(FieldFile)
		self.mime = self.file._file.content_type
		self.size = self.file._file._size
		self.md5 = file_md5(self.file._file.file)
		super(File, self).save()	# unicode error
		#else:
		#	super(File, self).save()

	#def	delete(self):
	#	os.unlink(self.get_path())
	#	super(File, self).delete()

	def	raw_save(self):
		'''
		For import only
		'''
		super(File, self).save()

	#def     __unicode__(self):
	#	return self.name

	def	get_filename(self):
		return '%08d' % self.pk

	def	get_path(self):
		return os.path.join(settings.MEDIA_ROOT, '%08d' % self.pk)

	class   Meta:
		verbose_name            = u'Файл'
		verbose_name_plural     = u'Файлы'

class	FileSeq(models.Model):
	'''
	File sequence
	TODO:
	- del file
	'''
	files	= models.ManyToManyField(File, null=True, blank=True, through='FileSeqItem', verbose_name=u'Файлы')

	def     __unicode__(self):
		return str(self.pk)

	def	clean_children(self):
		'''
		'''
		self.files.all().delete()

	def	purge(self):
		'''
		Delete self and all files in
		'''
		self.clean_children()
		super(FileSeq, self).delete()

	def	add_file(self, f):
		'''
		'''
		FileSeqItem(file=f, fileseq=self, order=self.files.count()+1).save()

	class   Meta:
		#unique_together		= (('scan', 'type', 'name'),)
		ordering                = ('id',)
		verbose_name            = u'Последовательность файлов'
		verbose_name_plural     = u'Последовательности файлов'

class	FileSeqItem(models.Model):
	file	= models.OneToOneField(File, primary_key=True, verbose_name=u'Файл')
	fileseq	= models.ForeignKey(FileSeq, null=False, blank=False, verbose_name=u'Последовательность файлов')
	order	= models.PositiveSmallIntegerField(null=False, blank=False, verbose_name=u'#')

	#def	__unicode__(self):
	#	return '%s: %s' % (self.user, self.comment)

	#def	delete(self):
	#	pass

	#def	swap(self, sibling):
	#	pass

	class   Meta:
		ordering                = ('file', 'order',)
		verbose_name            = u'Файл последовательности'
		verbose_name_plural     = u'Файлы последовательности'
