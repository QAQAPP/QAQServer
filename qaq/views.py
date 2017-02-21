from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
# Create your views here
from googleapiclient import discovery
import httplib2
import json
import os
from oauth2client.client import GoogleCredentials
import sqlite3
import operator
import time
from .models import Question, Option, Tag, User, UsedQ
from django.db.models.query import EmptyQuerySet
#from models import Question

DISCOVERY_URL = ('https://{api}.googleapis.com/'
                 '$discovery/rest?version={apiVersion}')

def googleEntityAnalysis(sentence):
	http = httplib2.Http()
	
	os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "qaq/test.json"

	credentials = GoogleCredentials.get_application_default().create_scoped(
	  ['https://www.googleapis.com/auth/cloud-platform'])
	http=httplib2.Http()
	
	credentials.authorize(http)

	service = discovery.build('language', 'v1beta1',
							http=http, discoveryServiceUrl=DISCOVERY_URL)

	service_request = service.documents().analyzeEntities(
	body={
	  'document': {
		 'type': 'PLAIN_TEXT',
		 'content': sentence,
	  }
	})

	response = service_request.execute()
	entities = response['entities'];
	
	wordList = []
	for i in range(0, len(entities)):
		name = entities[i]['name']
		salience = entities[i]['salience']
		dict = {}
		dict['name'] = name
		dict['salience'] = salience
		#print name
		wordList.append(dict)
	return wordList

				 
def handleQuery(request):
	emptyArr = []
	if request.method != 'GET':
		return emptyArr
	if not request.GET.__contains__('q'):
		return emptyArr
		
	question = request.GET.get('q')
	wordList = googleEntityAnalysis(question)
	
	#wordListString = request.GET.get('q')
	
	#wordList = nltk.word_tokenize(wordListString);
	#wordList = wordListString.split(',',5)
	
	conn = sqlite3.connect('test1.db')
	c = conn.cursor()
	
	maxnumtag = 8;
	tagDict = {}
	for word in wordList:
		wordName = word['name']
		wordName = wordName.lower()
		salience = word['salience']
		c.execute("SELECT tags.name, hit, total FROM words join tags on words.t_id = tags.id where words.name='%s' order by hit / total limit %d" % (wordName, maxnumtag))
		tags = c.fetchall()
		if not tags is []:
			for j in range (0, len(tags)):
				tagName = tags[j][0]
				hit = tags[j][1]
				total = tags[j][2]
				hitRatio = float(hit) / total
				if not tagName in tagDict:
					tagDict[tagName] = float(hitRatio) * salience
				else:
					tagDict[tagName] += float(hitRatio) * salience
	conn.commit()
	conn.close()
	
	sortedTags = sorted(tagDict.items(), key = operator.itemgetter(1), reverse=True)
	
	numberOfTags = min(maxnumtag, len(sortedTags))
	
	return sortedTags[:numberOfTags]
	
def handleUpdate(request):
	emptyArr = []
	if request.method != 'GET':
		return emptyArr
	if not request.GET.__contains__('q'):
		return emptyArr
	if not request.GET.__contains__('t'):
		return emptyArr
	
	question = request.GET.get('q')
	#TODO
	#wordList = wordListString.split(',',5)
	tagstring = request.GET.get('t')
	tagstring = tagstring.lower()
	tags = tagstring.split(',', 11)
	for tag in tags:
		tag = tag.strip()
	
	wordDictList = googleEntityAnalysis(question)
	
	conn = sqlite3.connect('test1.db')
	c = conn.cursor()
	
	wordList = []
	for wordDict in wordDictList:
		word = wordDict['name']
		word = word.lower()
		wordList.append(word)
	t_idList = []
	for tag in tags:
		c.execute("select id from tags where name = '%s' limit 1" % (tag))
		tagrow = c.fetchone()
		if tagrow is None:
			c.execute("insert into tags(name) values('%s')" % (tag))
			c.execute("select id from tags where name = '%s' limit 1" % (tag))
			newtagrow = c.fetchone()
			t_id = newtagrow[0]
			t_idList.append(t_id)
			for word in wordList:
				c.execute("insert into words(name, t_id, hit,total) values('%s',%d,1,2)" % (word, t_id))
		else:
			t_id = tagrow[0]
			t_idList.append(t_id)
			for word in wordList:
				c.execute("select w_id from words where name = '%s' and t_id = %d limit 1" % (word, t_id))
				wordrow = c.fetchone()
				if wordrow is None:
					c.execute("insert into words(name, t_id, hit,total) values('%s',%d,1,2)" % (word, t_id))
				else:
					w_id = wordrow[0]
					c.execute("update words set hit = hit+1,total=total+1 where w_id = %d" %(w_id))
		
	for word in wordList:
		addtotalsql = "update words set total = total + 1 where name = '%s' and t_id not in ({seq})".format(seq=','.join(['?']*len(t_idList)))
		c.execute(addtotalsql, t_idList)	
		
	conn.commit()
	conn.close()
	
	return

	
def index2(request):

	if request.method != 'GET':
		return JsonResponse({'Error':'Please use get request'})
	
	if not request.GET.__contains__('q'):
		return JsonResponse({'Error':'Please add key wclea to get request'})
	
	if request.GET.__contains__('t'):
		handleUpdate(request)
		return JsonResponse({})
	else:
		sortedTags = handleQuery(request)
		return JsonResponse(
		{
			'tags':sortedTags
		});
		
def add_ques(request):
	question = request.POST.get('qDescription')
	#print(question)
	opts = request.POST.get('qOptions')
	tags = request.POST.get('qTags')
	ano = request.POST.get('qAnonymous')
	uid = request.POST.get('uid')
	user = User.objects.filter(uidd=uid)
	if user.count() is 0:
		curruser = User(uidd=uid)
		curruser.save()
	else:
		curruser = user[0]
	curruser.usedq_set.create(qidd = question)
	tagstr = ''
	for tag in tags:
		tagset = curruser.tag_set.filter(tName = tag)
		if tagset.count() is 0:
			curruser.tag_set.create(tName = tag)
		tagstr += tag + ','
	q = Question(
	qDescription = question,
	qTags = tagstr,	#store all tags in one CharArray and search 
					#by ...__contains = tag
	qTime = int(round(time.time() * 10)),
	qAnonymous = ano)
	q.save()
	#print(opts)
	# add options and tags to the question
	for op in opts:
		q.option_set.create(Description = op)
	
	# for tag in tags:
	# 	q.tag_set.create(qName = tag)
	return JsonResponse(
		{
		'qid':q.pk,
		'success':True,
		'error':None
		})

#@csrf_exempt
def get_ques(request):
	qids = request.POST.get('qids')
	if not qids is None:
		res = []
		for qid in qids:
			q = Question.objects.get(pk=qid)
			temp = []
			temp.append(qid)
			temp.append(q.qDescription)
			options = []
			for op in q.option_set.all():
				options.append(op.Description)
			temp.append(options)
			temp.append(q.qAnonymous)
			res.append(temp)
		return JsonResponse(
			{
			'success':True,
			'error':None,
			'questions':res
			})

	uid = request.POST.get('uid')
	user = User.objects.filter(uidd=uid)
	#num = request.GET.get('num')
	#assume the json package contains user tags(we can change later)
	#tags = request.GET.get('tags')
	qset = Question.objects.none()
	if not user.count() is 0 and not user[0].tag_set.all().count() is 0:
		for tag in user[0].tag_set.all():
			print(tag.tName)
			qset = qset | Question.objects.filter(qTags__contains=tag.tName)
		qset.distinct()
		if not user[0].usedq_set.all().count() is 0:
			for uq in user[0].usedq_set.all():
				qset = qset.exclude(qDescription = uq.qidd)
		qset = qset.exclude(concluded = True).order_by('-qTime')
		
	if qset.count() is 0:
		qset = Question.objects.filter(concluded = False).order_by('-qTime')
		
	if not user.count() is 0:
		if not user[0].usedq_set.all().count() is 0:
			for uq in user[0].usedq_set.all():
				qset = qset.exclude(qDescription = uq.qidd)
		qset = qset.exclude(concluded = True).order_by('-qTime')	#multiple by [0:5]
	if qset.count() is 0:
		return JsonResponse(
		{
		'success':False,
		'error':"No question found",
		'qids': None,
		'qDescription': None,
		'qOptions':None,
		'qAnonymous': None
		})
	q = qset[0]
	if not user:
		curruser = User(uidd=uid)
		curruser.save()
	else:
		curruser = user[0]
	curruser.usedq_set.create(qidd=q.qDescription)
	curruser.save()
	# for each in q:
	# 	print(each.qDescription)
	# print(q.qDescription)
	# print(q.pk)
	options = []
	for op in q.option_set.all():
		options.append(op.Description)
	return JsonResponse(
		{
		'success':True,
		'error':None,
		'qids': q.pk,
		'qDescription': q.qDescription,
		'qOptions':options,
		'qAnonymous': q.qAnonymous
		#test before adding other components
		})
def add_op(request):
	q = Question.objects.get(pk = request.POST.get('qid'))
	q.option_set.create(Description = request.POST.get('oDescription'))
	q.save()
def choose_op(request):
	q = Question.objects.get(pk = request.POST.get('qid'))
	op = q.option_set.get(Description=request.POST.get('oid'))
	op.counter +=1
	op.save()
	q.save()
def conclude(request):
	q = Question.objects.get(pk = request.POST.get('qid'))
	q.concluded = True
	q.save()

def index(request):
	# if request.method != 'POST':
	# 	return JsonResponse({'Error':'Please use POST request'})
	
	# if not request.POST.__contains__('q'):
	# 	return JsonResponse({'Error':'Please add key q to get request'})
	action = request.POST.get('action')
	if action == 'get_questions':
		return get_ques(request)
	elif action == 'add_questions':
		return add_ques(request)
	elif action == 'add_option':
		add_op(request)
	elif action == 'choose_option':
		choose_op(request)
	elif action == 'conclude_ques':
		conclude(request)
	return JsonResponse(
		{
			'success':True,
			'error':None,
		})
