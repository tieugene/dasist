# -*- coding: utf-8 -*-
'''
contract.forms
'''

import decimal

# import models
from bills.models import Approver, Department, Payer, Place, Subject
from bills.views_extras import \
    ROLE_ACCOUNTER, ROLE_CHIEF


from core.forms import InnField, chk_new_org, chk_org_names
from core.models import Org

from django import forms
from django.db.models.fields.files import FieldFile

from models import Contract

mime_available = set((
    'application/pdf',
))


class ApproverModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_fio()


class ResumeForm(forms.Form):
    note = forms.CharField(max_length=255, label='Замечание', required=False, widget=forms.TextInput(attrs={'size': 80}))


class FilterContractListForm(forms.Form):
    draft = forms.BooleanField(label='Черновики', required=False)
    onway = forms.BooleanField(label='На подписи', required=False)
    onpay = forms.BooleanField(label='У юриста', required=False)
    done = forms.BooleanField(label='Одобрены', required=False)
    dead = forms.BooleanField(label='Завернуты', required=False)
    place = forms.ModelChoiceField(queryset=Place.objects.all().order_by('name'), label=u'Объект', required=False)
    subject = forms.ModelChoiceField(queryset=Subject.objects.none().order_by('name'), label=u'Подобъект', required=False)
    depart = forms.ModelChoiceField(queryset=Department.objects.all().order_by('name'), label=u'Направление', required=False)
    shipper = forms.ModelChoiceField(queryset=Org.objects.all().order_by('name'), label=u'Поставщик', required=False)
    payer = forms.ModelChoiceField(queryset=Payer.objects.all().order_by('name'), label=u'Поставщик', required=False)

    def __init__(self, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        place = self.fields['place'].initial or self.initial.get('place')
        if place:
            self.fields['subject'].queryset = Subject.objects.filter(place__pk=int(place)).order_by('name')


class ContractAddFileForm(forms.Form):
    file = forms.FileField(label=u'Файл')

    def clean_file(self):
        file = self.cleaned_data['file']
        if (not isinstance(file, FieldFile)) and (file.content_type not in mime_available):
            raise forms.ValidationError('File must be PDF only!')
        return None


class ContractForm(forms.Form):
    '''
    Parent form; abstract only.
    '''
    file = forms.FileField(label=u'Скан')
    place = forms.ModelChoiceField(queryset=Place.objects.all().order_by('name'), empty_label=None, label=u'Объект')
    subject = forms.ModelChoiceField(queryset=Subject.objects.all().order_by('name'), label=u'Подобъект', required=False)
    depart = forms.ModelChoiceField(queryset=Department.objects.all().order_by('name'), label=u'Направление', required=False)
    payer = forms.ModelChoiceField(queryset=Payer.objects.all().order_by('name'), empty_label='---', label=u'Наша фирма')
    suppinn = InnField(min_length=10, max_length=12, label=u'ИНН Контрагента', required=True)
    suppname = forms.CharField(max_length=64, label=u'Контрагент (кратко)', required=True)
    suppfull = forms.CharField(max_length=64, label=u'Контрагент (полностью)', required=True)
    docno = forms.CharField(max_length=64, label=u'Номер договора')
    docdate = forms.DateField(label=u'Дата договора')
    docsum = forms.DecimalField(max_digits=11, decimal_places=2, min_value=decimal.Decimal('0.01'), localize=True, label=u'Сумма договора')
    mgr = ApproverModelChoiceField(queryset=Approver.objects.filter(role__pk=ROLE_CHIEF), empty_label=None, label=u'Руководитель', widget=forms.RadioSelect)
    booker = ApproverModelChoiceField(queryset=Approver.objects.filter(role__pk=ROLE_ACCOUNTER), empty_label=None, label=u'Бухгалтер', widget=forms.RadioSelect)

    def clean(self):
        cleaned_data = super(ContractForm, self).clean()
        # 1. chk inn<>suppname
        suppinn = cleaned_data.get('suppinn')
        suppname = cleaned_data.get('suppname')
        suppfull = cleaned_data.get('suppfull')
        if (suppinn and suppname):
            chk_new_org(suppinn, suppname)
        # 2. chk supp names
        if (suppname and suppfull):
            chk_org_names(suppname, suppfull)
        # 3. chk summs
        docsum = cleaned_data.get('docsum')
        if (docsum is None):
            raise forms.ValidationError('Заполните сумму договора.')
        # X. that's all, folks
        return cleaned_data


class ContractAddForm(ContractForm):
    '''
    Add new contract
    '''
    def clean_file(self):
        file = self.cleaned_data['file']
        if (not isinstance(file, FieldFile)) and (file.content_type not in mime_available):
            raise forms.ValidationError('File must be PDF only!')
        return None

    def clean(self):
        cleaned_data = super(ContractAddForm, self).clean()
        # 4. chk unqueness
        shipper__inn = cleaned_data.get('suppinn')
        docno = cleaned_data.get('docno')
        docdate = cleaned_data.get('docdate')
        if (shipper__inn and docno and docdate):
            if Contract.objects.filter(
                shipper__inn=shipper__inn,
                docno=docno,
                docdate=docdate
            ).exists():
                raise forms.ValidationError('Такой договор уже есть.')
        return cleaned_data


class ContractEditForm(ContractForm):
    '''
    Edit existance bill (not locked)
    '''
    id = forms.IntegerField(label=u'ID', widget=forms.HiddenInput())
    file = forms.FileField(label=u'Скан', required=False, help_text=u'(Выберите файл, если хотите заменить скан)')

    def clean_file(self):
        file = self.cleaned_data['file']
        if (file):
            if (not isinstance(file, FieldFile)) and (file.content_type not in mime_available):
                raise forms.ValidationError('File must be PDF only!')
        return None

    def clean(self):
        cleaned_data = super(ContractEditForm, self).clean()
        # 4. chk unqueness
        if Contract.objects.filter(
            shipper__inn=cleaned_data['suppinn'],
            docno=cleaned_data['docno'],
            docdate=cleaned_data['docdate']
        ).exclude(fileseq_id=int(cleaned_data['id'])).exists():
            raise forms.ValidationError('Такой договор уже есть.')
        return cleaned_data
