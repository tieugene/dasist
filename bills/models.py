# -*- coding: utf-8 -*-

# 1. django
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile

# 2. 3rd parties
from sortedm2m.fields import SortedManyToManyField
from pyPdf import PdfFileReader
from pdfrw import PdfReader
from PIL import Image as PIL_Image
from wand.image import Image as Wand_Image

# 3. system
import os, datetime, hashlib
from StringIO import StringIO

# 4. local
from rfm import RenameFilesModel

states = {	# isalive, isgood
	(True,  False): 1,	# Draft
	(True,  True ): 2,	# OnWay
	(False, True ): 3,	# Accepted
	(False, False): 4,	# Rejected
}

class	Role(models.Model):
	'''
	Predefined role model
	TODO: m2m user [via Approver]
	'''
	id	= models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'ID')
	name	= models.CharField(max_length=16, verbose_name=u'Наименование')

	def	__unicode__(self):
		return self.name

	class   Meta:
		unique_together		= (('name',),)
		ordering                = ('id', )
		verbose_name            = u'Роль'
		verbose_name_plural     = u'Роли'

class	Approver(User):
	'''
	'''
	role	= models.ForeignKey(Role, verbose_name=u'Роль')
	jobtit	= models.CharField(max_length=32, verbose_name=u'Должность')

	class   Meta:
		ordering                = ('role', )
		verbose_name            = u'Подписант'
		verbose_name_plural     = u'Подписанты'

	def	__unicode__(self):
		return '%s %s (%s, %s)' % (self.first_name, self.last_name, self.jobtit, self.role.name)

def    my_upload_to(instance, filename):
    '''
    Generates upload path for FileField
    '''
    instance.name = filename
    return u'temp/%s' % filename

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
	* cache
	* delete
	'''
	#filename	= models.CharField(max_length=255, db_index=True, blank=False, verbose_name=u'Filename')
	#mimetype	= models.CharField(max_length=64, verbose_name=u'MIME')
	#size

	file        = models.FileField(null=False, upload_to=my_upload_to, verbose_name=u'Файл')    # attrs: name, path, url, size
	name        = models.CharField(null=False, db_index=True, blank=False, max_length=255, verbose_name=u'Имя файла')
	mime        = models.CharField(null=False, blank=False, max_length=255, verbose_name=u'Тип Mime')
	saved       = models.DateTimeField(null=False, blank=False, auto_now_add=True, verbose_name=u'Записано')
	size        = models.PositiveIntegerField(null=False, blank=False, verbose_name=u'Размер')
	md5         = models.CharField(null=False, blank=False, max_length=32, verbose_name=u'MD5')
	pages       = models.PositiveSmallIntegerField(null=False, blank=False, verbose_name=u'Страниц')
	#RENAME_FILES    = {'file': {'dest': settings.BILLS_ROOT, 'keep_ext': False}}
	RENAME_FILES    = {'file': {'dest': '', 'keep_ext': False}}

	def	__rm_cache(self):
		'''
		Delete cached thumbnails
		'''
		src_path = os.path.join(settings.MEDIA_ROOT, '%08d' % self.pk)
		thumb_template = os.path.join(settings.PROJECT_DIR, 'static', 'cache', '%08d-%%d.png' % self.pk)
		for i in range(10):
			thumb = thumb_template % i
			if os.path.exists(thumb):
				os.remove(thumb)

	def	__pdf2png(self, src_path, thumb_template, pages):
		for page in range(pages, 10):
			img = Wand_Image(filename = src_path + '[%d]' % page, resolution=(150,150))
			#print img.size
			if (img.colorspace != 'gray'):
				img.colorspace = 'gray'		# 'grey' as for bw as for grey (COLORSPACE_TYPES)
			img.format = 'png'
			#img.resolution = (300, 300)
			img.save(filename = thumb_template % page)

	def	__pdf2png2(self, src_path, thumb_template, pages):
		import subprocess
		arglist = ["gs",
			"-dBATCH",
			"-dNOPAUSE",
			"-sOutputFile=%s" % thumb_template,
			"-sDEVICE=pnggray",
			"-r150",
			src_path]
		sp = subprocess.Popen(args=arglist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		sp.communicate()

	def	__mk_cache(self):
		'''
		Created cached thumbnails
		'''
		# make thumbnails
		src_path = os.path.join(settings.MEDIA_ROOT, '%08d' % self.pk)
		thumb_template = os.path.join(settings.PROJECT_DIR, 'static', 'cache', '%08d-%%d.png' % self.pk)
		if (self.mime == 'image/png'):
			img = PIL_Image.open(src_path)
			if (img.mode not in set(['P', '1', 'L'])):	# paletted, bw, grey
				thumb = img.convert('L')
			else:
				thumb = img
			thumb.save(thumb_template % 1, 'PNG')
			self.pages = 1
		elif (self.mime == 'image/tiff'):
			img = PIL_Image.open(src_path)
			for i in range(9):
				try:
					img.seek(i)
					if (img.mode in set(['1','L'])):
						thumb = img
					else:
						thumb = img.convert('L')
					thumb.save(thumb_template % (i+1), 'PNG')
					self.pages += 1
				except EOFError:
					break
		elif (self.mime == 'application/pdf'):
			#pages = PdfFileReader(file(src_path, 'rb')).getNumPages()
			pages = min(9, len(PdfReader(file(src_path, 'rb')).pages))
			self.__pdf2png2(src_path, thumb_template, pages)
			self.pages = pages
		super(File, self).save()	# for pages

	def	save(self):
		'''
		New: file = <InMemoryUploadedFile: 2.html (text/html)>
		django...file: _get_size
		'''
		if (self.file._file):	# FIXME: костыль, надо not isinstance(FieldFile)
			self.mime = self.file._file.content_type
			self.size = self.file._file._size
			self.md5 = file_md5(self.file._file.file)
			self.pages = 0
			super(File, self).save()
			# Now self.pk != None
			self.__rm_cache()
			self.__mk_cache()
		else:
			super(File, self).save()

	def	delete(self):
		self.__rm_cache()
		super(File, self).delete()

	def	raw_save(self):
		'''
		For import only
		'''
		super(File, self).save()

	def     __unicode__(self):
		return self.name

	def	get_filename(self):
		return '%08d' % self.pk

	def	get_path(self):
		return os.path.join(settings.BILLS_ROOT, '%08d' % self.pk)

	class   Meta:
		verbose_name            = u'Файл'
		verbose_name_plural     = u'Файлы'

class	Bill(File):
	'''
	Fields:
	?desc:txt
	?ctime:datetime - время создания
	?etime:datetime - время окончания

	??Поставщик
	??Номер счета
	??Дата счета
	??Сумма счета
	TODO:
	* route = ManyToMany(User)
	* history = ManyToMany(User)
	* Object = FK
	* Depart = FK
	#created	= models.DateTimeField(auto_now_add=True, verbose_name=u'Создан')	# editable-False
	#updated	= models.DateTimeField(auto_now=True, verbose_name=u'Изменен')		# editable-False
	TODO: get_route_ok(user):
	* user not in route
	* route ends w/ accounter
	* route len > 0
	'''
	project		= models.CharField(max_length=64, null=True, blank=True, verbose_name=u'Объект')
	depart		= models.CharField(max_length=64, null=True, blank=True, verbose_name=u'Направление')
	supplier	= models.CharField(max_length=64, verbose_name=u'Поставщик')
	assign		= models.ForeignKey(Approver, related_name='assigned', verbose_name=u'Исполнитель')
	approve		= models.ForeignKey(Approver, related_name='inbox',    verbose_name=u'Согласующий')
	isalive		= models.BooleanField(verbose_name=u'Живой')
	isgood		= models.BooleanField(verbose_name=u'Хороший')
	#route		= SortedManyToManyField(User, null=True, blank=True, through='BillRoute', verbose_name=u'Маршрут', sort_value_field_name='orderno')
	route		= SortedManyToManyField(Approver, null=True, blank=True, related_name='route', verbose_name=u'Маршрут')
	history		= models.ManyToManyField(Approver, null=True, blank=True, related_name='history', through='BillEvent', verbose_name=u'История')

	def     __unicode__(self):
		return self.name

	def	get_state(self):
		return states[(self.isalive, self.isgood)]

	class   Meta:
		#unique_together		= (('scan', 'type', 'name'),)
		#ordering                = ('id',)
		verbose_name            = u'Счет'
		verbose_name_plural     = u'Счета'

class	BillEvent(models.Model):
	bill	= models.ForeignKey(Bill, verbose_name=u'Счет')
	user	= models.ForeignKey(Approver, verbose_name=u'Подписант')
	ctime	= models.DateTimeField(auto_now_add=True, verbose_name=u'ДатаВремя')
	comment	= models.TextField(null=True, blank=True, verbose_name=u'Камменты')

	def	__unicode__(self):
		return '%s: %s' % (self.user, self.comment)

	class   Meta:
		ordering                = ('ctime',)
		verbose_name            = u'Резолюция'
		verbose_name_plural     = u'Резолюции'
