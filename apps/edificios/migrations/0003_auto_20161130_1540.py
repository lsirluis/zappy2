# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-30 20:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edificios', '0002_auto_20161130_1538'),
    ]

    operations = [
        migrations.AlterField(
            model_name='persona',
            name='celular',
            field=models.BigIntegerField(blank=True),
        ),
    ]
