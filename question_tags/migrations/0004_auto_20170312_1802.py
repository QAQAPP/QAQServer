# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-13 01:02
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('question_tags', '0003_auto_20170312_0112'),
    ]

    operations = [
        migrations.RenameField(
            model_name='word',
            old_name='t_fkey',
            new_name='tag',
        ),
    ]
