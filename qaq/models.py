from django.db import models
#from django.contrib.postgres.fields import ArrayField
# Create your models here.
class Question(models.Model):
	#qDescription = models.CharField(max_length = 200, default = "no_name")
	#qOptions = ArrayField(models.CharField(max_length =200), size = 6)
	#10 tags
	qid = models.CharField(max_length = 200)
	qTags = models.CharField(max_length = 200,default = "no_tag")
	#qTime = models.IntegerField(default = 0)
	qTime = models.IntegerField(default = 0)
	qAnonymous = models.BooleanField(default = True)
	concluded = models.BooleanField(default = False)
	def __str__(self):
		return self.qDescription

class User(models.Model):
	uidd = models.CharField(max_length=200, default = 'not_valid')

class UsedQ(models.Model):
	qidd = models.CharField(max_length=200, default = 'no_q')
	user = models.ForeignKey(User, on_delete = models.CASCADE)

#class Option(models.Model):
#	oDescription = models.CharField(max_length = 200)
#	qQuestions = models.ForeignKey(Question, on_delete = models.CASCADE)
#	oOferBy = models.CharField(max_length = 200)
#	oVal = models.IntegerField(default = 0)

class Tag(models.Model):
	tName = models.CharField(max_length = 30, default = "no_tag")
	#qQuestions = ArrayField(models.ForeignKey(Question, on_delete=models.CASCADE))
	user = models.ForeignKey(User, on_delete = models.CASCADE, default=-1)
