# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-02-28 11:20
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0002_auto_20170515_1717'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=8, unique=True, verbose_name='\u0417\u0430\u043a\u0430\u0437\u0447\u0438\u043a')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': '\u0417\u0430\u043a\u0430\u0437\u0447\u0438\u043a',
                'verbose_name_plural': '\u0417\u0430\u043a\u0430\u0437\u0447\u0438\u043a\u0438',
            },
        ),
        migrations.AlterField(
            model_name='contract',
            name='payer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payer_contracts', to='bills.Payer', verbose_name='\u041d\u0430\u0448\u0430 \u0444\u0438\u0440\u043c\u0430'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='shipper',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shipper_contracts', to='core.Org', verbose_name='\u041a\u043e\u043d\u0442\u0440\u0430\u0433\u0435\u043d\u0442'),
        ),
        migrations.AddField(
            model_name='contract',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer_contracts', to='contract.Customer', verbose_name='\u0417\u0430\u043a\u0430\u0437\u0447\u0438\u043a'),
        ),
    ]
