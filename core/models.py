# -*- coding: utf-8 -*-
'''
core.models
'''

# 1. system
import hashlib
import os
import uuid

# 2. django
from django.conf import settings
# from django.core.files.base import ContentFile
from django.db import models, transaction
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver

# 2. 3rd parties

# 4. local
from rfm import RenameFilesModel


def my_upload_to(instance, filename):
    '''
    Generates upload path for FileField
    '''
    instance.name = filename
    # return u'temp/%s' % filename
    return u'temp/%s' % uuid.uuid4().hex.upper()


def file_md5(file, block_size=1024 * 14):
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


class File(RenameFilesModel):
    '''
    TODO:
    * delete
    '''
    # filename    = models.CharField(max_length=255, db_index=True, blank=False, verbose_name=u'Filename')
    # mimetype    = models.CharField(max_length=64, verbose_name=u'MIME')
    # size

    file = models.FileField(null=False, upload_to=my_upload_to, verbose_name=u'Файл')    # attrs: name, path, url, size
    name = models.CharField(null=False, db_index=True, blank=False, max_length=255, verbose_name=u'Имя файла')    # max=130
    mime = models.CharField(null=False, blank=False, db_index=True, max_length=16, verbose_name=u'Тип Mime')    # max=10
    ctime = models.DateTimeField(null=False, blank=False, db_index=True, auto_now_add=True, verbose_name=u'Записано')
    size = models.PositiveIntegerField(null=False, blank=False, db_index=True, verbose_name=u'Размер')
    md5 = models.CharField(null=False, blank=False, db_index=True, max_length=32, verbose_name=u'MD5')
    RENAME_FILES = {'file': {'dest': '', 'keep_ext': False}}

    def save(self):
        '''
        New: file = <InMemoryUploadedFile: 2.html (text/html)>
        django...file: _get_size
        '''
        # if (self.file._file):    # FIXME: костыль, надо not isinstance(FieldFile)
        self.mime = self.file._file.content_type
        self.size = self.file._file._size
        self.md5 = file_md5(self.file._file.file)
        super(File, self).save()    # unicode error
        # else:
        #    super(File, self).save()

    def raw_save(self):
        '''
        For import only
        '''
        super(File, self).save()

    def __unicode__(self):
        return self.name

    def get_filename(self):
        return '%08d' % self.pk

    def get_path(self):
        return os.path.join(settings.MEDIA_ROOT, '%08d' % self.pk)

    def update_meta(self):
        '''
        Update md5 and size to real values
        '''
        path = self.get_path()
        self.size = os.path.getsize(self.get_path())
        self.md5 = file_md5(path)
        super(File, self).save()

    def delete(self, *args, **kwargs):
        #print 'Start File.delete()'
        p = self.get_path()
        if (os.path.exists(p)):
            os.unlink(p)
        #print 'File Deleted'
        super(File, self).delete(*args, **kwargs)


    class Meta:
        verbose_name = u'Файл'
        verbose_name_plural = u'Файлы'


@receiver(post_delete, sender=File)
def _file_delete(sender, instance, **kwargs):
    #print 'Start post_delete'
    p = instance.get_path()
    if (os.path.exists(p)):
        os.unlink(p)
    #print 'End of post_delete'


class FileSeq(models.Model):
    '''
    File sequence
    TODO:
    - del file
    '''
    files = models.ManyToManyField(File, through='FileSeqItem', verbose_name=u'Файлы')

    def __unicode__(self):
        return str(self.pk)

    def clean_children(self):
        '''
        '''
        self.files.all().delete()

    def delete(self, *args, **kwargs):
        '''
        Delete self and all files in
        '''
        self.clean_children()
        super(FileSeq, self).delete(*args, **kwargs)

    def add_file(self, f):
        '''
        '''
        FileSeqItem(file=f, fileseq=self, order=self.files.count() + 1).save()

    @transaction.atomic
    def del_file(self, id):
        '''

        '''
        fsi = self.fileseqitem_set.get(file=id)
        ord = fsi.order
        fsi.file.delete()
        # self.fileseqitem_set.all().order_by('order').filter(order__gt=ord).update(order=order-1)
        for i in self.fileseqitem_set.all().order_by('order').filter(order__gt=ord):
            i.order = i.order - 1
            i.save()

    def list_items(self):
        return self.fileseqitem_set.all().order_by('order')

    class Meta:
        # unique_together        = (('scan', 'type', 'name'),)
        ordering = ('id',)
        verbose_name = u'Последовательность файлов'
        verbose_name_plural = u'Последовательности файлов'


@receiver(post_delete, sender=FileSeq)
def _fileseq_delete(sender, instance, **kwargs):
    sender.clean_children(instance)


class FileSeqItem(models.Model):
    file = models.OneToOneField(File, primary_key=True, verbose_name=u'Файл')
    fileseq = models.ForeignKey(FileSeq, null=False, blank=False, db_index=True, verbose_name=u'Последовательность файлов')
    order = models.PositiveSmallIntegerField(null=False, blank=False, db_index=True, verbose_name=u'#')

    # def    __unicode__(self):
    #    return '%s: %s' % (self.user, self.comment)

    def delete(self, *args, **kwargs):
        self.file.delete()
        super(FileSeqItem, self).delete(*args, **kwargs)

    @transaction.atomic
    def swap(self, sibling):
        new_fsi = self.fileseq.fileseqitem_set.get(order=sibling)
        old_order = self.order
        new_order = new_fsi.order
        new_fsi.order = old_order
        new_fsi.save()
        self.order = new_order
        self.save()

    def is_first(self):
        return self.order == 1

    def is_last(self):
        return self.order == self.fileseq.files.count()

    class Meta:
        ordering = ('file', 'order',)
        verbose_name = u'Файл последовательности'
        verbose_name_plural = u'Файлы последовательности'


class Org(models.Model):
    inn = models.CharField(unique=True, max_length=12, verbose_name=u'ИНН')
    name = models.CharField(unique=True, max_length=40, verbose_name=u'Краткое наименование')    # max=38
    fullname = models.CharField(null=False, blank=False, db_index=True, max_length=64, verbose_name=u'Полное наименование')    # max=63

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = u'Организация'
        verbose_name_plural = u'Организации'
