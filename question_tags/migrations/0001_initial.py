# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-03-12 07:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('t_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='no_tag', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('w_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='no_word', max_length=200)),
                ('hit', models.IntegerField(default=0)),
                ('total', models.IntegerField(default=0)),
                ('t_id', models.ForeignKey(default=-1, on_delete=django.db.models.deletion.CASCADE, to='question_tags.Tag')),
            ],
        ),
    ]
