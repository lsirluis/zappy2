# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-28 17:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('edificios', '0017_auto_20161205_1626'),
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeNoticia',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'Detalle noticia',
                'verbose_name_plural': 'Detalles noticias',
            },
        ),
        migrations.CreateModel(
            name='Detalle',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('valor', models.BigIntegerField()),
                ('tipo', models.CharField(max_length=100)),
                ('descripcion', models.CharField(max_length=120)),
            ],
            options={
                'verbose_name': 'Detalle',
                'verbose_name_plural': 'Detalles',
            },
        ),
        migrations.CreateModel(
            name='Noticia',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('estado', models.PositiveIntegerField(choices=[(0, 'No visto'), (1, 'Visto'), (3, 'No visto 7 Dias')], default=0)),
                ('descripcion', models.CharField(blank=True, max_length=120, null=True)),
                ('fecha_generacion', models.DateTimeField(auto_now=True)),
                ('administrador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.Administrador')),
                ('propiedad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='edificios.Propiedad')),
            ],
            options={
                'verbose_name': 'Noticia',
                'verbose_name_plural': 'Noticias',
            },
        ),
        migrations.CreateModel(
            name='Recibo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('estado', models.PositiveIntegerField()),
                ('descripcion', models.CharField(blank=True, max_length=120, null=True)),
                ('numConsecutivo', models.IntegerField()),
                ('fecha_generacion', models.DateTimeField(auto_now=True)),
                ('fecha_cobrada', models.DateField()),
                ('fecha_vencimiento', models.DateField()),
                ('unidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='edificios.Unidad')),
            ],
            options={
                'verbose_name': 'Recibo',
                'verbose_name_plural': 'Recibos',
            },
        ),
        migrations.AddField(
            model_name='detalle',
            name='idRecibo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pagos.Recibo'),
        ),
        migrations.AddField(
            model_name='denoticia',
            name='idNoticia',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pagos.Noticia'),
        ),
        migrations.AddField(
            model_name='denoticia',
            name='idRecibo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pagos.Recibo'),
        ),
        migrations.AddField(
            model_name='denoticia',
            name='unidad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='edificios.Unidad'),
        ),
    ]
