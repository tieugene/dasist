# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-04-09 12:18
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0007_alter_validators_add_error_messages'),
        ('core', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Approver',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c')),
                ('jobtit', models.CharField(db_index=True, max_length=32, verbose_name='\u0414\u043e\u043b\u0436\u043d\u043e\u0441\u0442\u044c')),
                ('canadd', models.BooleanField(db_index=True, verbose_name='\u041c\u043e\u0436\u0435\u0442 \u0441\u043e\u0437\u0434\u0430\u0432\u0430\u0442\u044c')),
            ],
            options={
                'ordering': ('role',),
                'verbose_name': '\u041f\u043e\u0434\u043f\u0438\u0441\u0430\u043d\u0442',
                'verbose_name_plural': '\u041f\u043e\u0434\u043f\u0438\u0441\u0430\u043d\u0442\u044b',
            },
        ),
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('fileseq', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='core.FileSeq', verbose_name='\u0424\u0430\u0439\u043b\u044b')),
                ('billno', models.CharField(db_index=True, max_length=32, verbose_name='\u041d\u043e\u043c\u0435\u0440 \u0441\u0447\u0435\u0442\u0430')),
                ('billdate', models.DateField(db_index=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u0447\u0435\u0442\u0430')),
                ('billsum', models.DecimalField(db_index=True, decimal_places=2, max_digits=11, verbose_name='\u0421\u0443\u043c\u043c\u0430 \u0441\u0447\u0435\u0442\u0430')),
                ('payedsum', models.DecimalField(db_index=True, decimal_places=2, max_digits=11, verbose_name='\u041e\u043f\u043b\u0430\u0447\u0435\u043d\u043e')),
                ('topaysum', models.DecimalField(db_index=True, decimal_places=2, max_digits=11, verbose_name='\u0421\u0443\u043c\u043c\u0430 \u043a \u043e\u043f\u043b\u0430\u0442\u0435')),
                ('locked', models.BooleanField(db_index=True, default=False, verbose_name='\u0412 \u0440\u0430\u0431\u043e\u0442\u0435')),
                ('assign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_bills', to='bills.Approver', verbose_name='\u0418\u0441\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c')),
            ],
            options={
                'verbose_name': '\u0421\u0447\u0435\u0442',
                'verbose_name_plural': '\u0421\u0447\u0435\u0442\u0430',
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.PositiveSmallIntegerField(primary_key=True, serialize=False, verbose_name='#')),
                ('name', models.CharField(db_index=True, max_length=16, verbose_name='\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435')),
            ],
            options={
                'ordering': ('id',),
                'verbose_name': '\u041d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435',
                'verbose_name_plural': '\u041d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resume', models.BooleanField(db_index=True, verbose_name='\u0420\u0435\u0437\u043e\u043b\u044e\u0446\u0438\u044f')),
                ('ctime', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='\u0414\u0430\u0442\u0430\u0412\u0440\u0435\u043c\u044f')),
                ('comment', models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='\u041a\u0430\u043c\u043c\u0435\u043d\u0442\u044b')),
                ('approve', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bills.Approver', verbose_name='\u041f\u043e\u0434\u043f\u0438\u0441\u0430\u043d\u0442')),
                ('bill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bills.Bill', verbose_name='\u0421\u0447\u0435\u0442')),
            ],
            options={
                'ordering': ('ctime',),
                'verbose_name': '\u0420\u0435\u0437\u043e\u043b\u044e\u0446\u0438\u044f',
                'verbose_name_plural': '\u0420\u0435\u0437\u043e\u043b\u044e\u0446\u0438\u0438',
            },
        ),
        migrations.CreateModel(
            name='Payer',
            fields=[
                ('id', models.PositiveSmallIntegerField(primary_key=True, serialize=False, verbose_name='#')),
                ('name', models.CharField(db_index=True, max_length=16, verbose_name='\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435')),
            ],
            options={
                'ordering': ('id',),
                'verbose_name': '\u041f\u043b\u0430\u0442\u0435\u043b\u044c\u0449\u0438\u043a',
                'verbose_name_plural': '\u041f\u043b\u0430\u0442\u0435\u043b\u044c\u0449\u0438\u043a\u0438',
            },
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=24, verbose_name='\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435')),
            ],
            options={
                'ordering': ('id',),
                'verbose_name': '\u041e\u0431\u044a\u0435\u043a\u0442',
                'verbose_name_plural': '\u041e\u0431\u044a\u0435\u043a\u0442\u044b',
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.PositiveSmallIntegerField(primary_key=True, serialize=False, verbose_name='#')),
                ('name', models.CharField(db_index=True, max_length=32, verbose_name='\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435')),
            ],
            options={
                'ordering': ('id',),
                'verbose_name': '\u0420\u043e\u043b\u044c',
                'verbose_name_plural': '\u0420\u043e\u043b\u0438',
            },
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveSmallIntegerField(db_index=True, verbose_name='#')),
                ('approve', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bills.Approver', verbose_name='\u041f\u043e\u0434\u043f\u0438\u0441\u0430\u043d\u0442')),
                ('bill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bills.Bill', verbose_name='\u0421\u0447\u0435\u0442')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bills.Role', verbose_name='\u0420\u043e\u043b\u044c')),
            ],
            options={
                'ordering': ('bill', 'order'),
                'verbose_name': '\u0422\u043e\u0447\u043a\u0430 \u043c\u0430\u0440\u0448\u0440\u0443\u0442\u0430',
                'verbose_name_plural': '\u0422\u043e\u0447\u043a\u0438 \u043c\u0430\u0440\u0448\u0440\u0443\u0442\u0430',
            },
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.PositiveSmallIntegerField(primary_key=True, serialize=False, verbose_name='#')),
                ('name', models.CharField(db_index=True, max_length=16, verbose_name='\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435')),
                ('color', models.CharField(db_index=True, max_length=16, verbose_name='\u0426\u0432\u0435\u0442')),
            ],
            options={
                'ordering': ('id',),
                'verbose_name': '\u0421\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0435',
                'verbose_name_plural': '\u0421\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u044f',
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=32, verbose_name='\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435')),
                ('place', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='bills.Place', verbose_name='\u041e\u0431\u044a\u0435\u043a\u0442')),
            ],
            options={
                'ordering': ('place', 'id'),
                'verbose_name': '\u041f\u043e\u0434\u041e\u0431\u044a\u0435\u043a\u0442',
                'verbose_name_plural': '\u041f\u043e\u0434\u041e\u0431\u044a\u0435\u043a\u0442',
            },
        ),
        migrations.AlterUniqueTogether(
            name='state',
            unique_together=set([('name',)]),
        ),
        migrations.AlterUniqueTogether(
            name='role',
            unique_together=set([('name',)]),
        ),
        migrations.AlterUniqueTogether(
            name='place',
            unique_together=set([('name',)]),
        ),
        migrations.AlterUniqueTogether(
            name='payer',
            unique_together=set([('name',)]),
        ),
        migrations.AlterUniqueTogether(
            name='department',
            unique_together=set([('name',)]),
        ),
        migrations.AddField(
            model_name='bill',
            name='depart',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='department_bills', to='bills.Department', verbose_name='\u041d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435'),
        ),
        migrations.AddField(
            model_name='bill',
            name='payer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payer_bills', to='bills.Payer', verbose_name='\u041f\u043b\u0430\u0442\u0435\u043b\u044c\u0449\u0438\u043a'),
        ),
        migrations.AddField(
            model_name='bill',
            name='place',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='place_bills', to='bills.Place', verbose_name='\u041e\u0431\u044a\u0435\u043a\u0442'),
        ),
        migrations.AddField(
            model_name='bill',
            name='rpoint',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rbill', to='bills.Route', verbose_name='\u0422\u043e\u0447\u043a\u0430 \u043c\u0430\u0440\u0448\u0440\u0443\u0442\u0430'),
        ),
        migrations.AddField(
            model_name='bill',
            name='shipper',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shipper_bills', to='core.Org', verbose_name='\u041f\u043e\u0441\u0442\u0430\u0432\u0449\u0438\u043a'),
        ),
        migrations.AddField(
            model_name='bill',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='state_bills', to='bills.State', verbose_name='\u0421\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0435'),
        ),
        migrations.AddField(
            model_name='bill',
            name='subject',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subject_bills', to='bills.Subject', verbose_name='\u041f\u043e\u0434\u041e\u0431\u044a\u0435\u043a\u0442'),
        ),
        migrations.AddField(
            model_name='approver',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bills.Role', verbose_name='\u0420\u043e\u043b\u044c'),
        ),
        migrations.AlterUniqueTogether(
            name='subject',
            unique_together=set([('place', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='route',
            unique_together=set([('bill', 'role'), ('bill', 'order')]),
        ),
        migrations.AlterUniqueTogether(
            name='bill',
            unique_together=set([('shipper', 'billno', 'billdate')]),
        ),
    ]
