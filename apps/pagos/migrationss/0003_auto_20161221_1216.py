# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-21 17:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagos', '0002_auto_20161221_1009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recibo',
            name='fecha_cobrada',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='recibo',
            name='fecha_vencimiento',
            field=models.DateField(),
        ),
    ]
