# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-22 23:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qaq', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='qTag1',
        ),
        migrations.AddField(
            model_name='question',
            name='qTags',
            field=models.CharField(default='no_tag', max_length=200),
        ),
    ]
