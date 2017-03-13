from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Tag(models.Model):
	t_id = models.AutoField(primary_key = True)
	name = models.CharField(max_length = 200, default = "no_tag")

class Word(models.Model):
	w_id = models.AutoField(primary_key = True)
	name = models.CharField(max_length = 200, default = "no_word")
	hit = models.IntegerField(default = 0)
	total = models.IntegerField(default = 0)
	tag = models.ForeignKey(Tag, on_delete = models.CASCADE, default = -1)