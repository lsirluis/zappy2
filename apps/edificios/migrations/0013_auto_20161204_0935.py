# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-04 14:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edificios', '0012_auto_20161204_0921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unidad',
            name='dia_cobro',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='unidad',
            name='numero',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='unidad',
            name='saldo_favor',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='unidad',
            name='valor_mora',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='unidad',
            name='valor_pago',
            field=models.PositiveIntegerField(),
        ),
    ]