from django.shortcuts import render
from .models import Tag, Word
from django.http import JsonResponse
from googleapiclient import discovery
import httplib2
import os
from oauth2client.client import GoogleCredentials
from django.db.models import F, FloatField
from django.db import connections
from django.db.models.functions import Cast
import operator

# Create your views here.
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
	
	maxnumtag = 8;
	tagDict = {}
	for word in wordList:
		wordName = word['name']
		wordName = wordName.lower()
		salience = word['salience']
		#c.execute("SELECT tags.name, hit, total FROM words join tags on words.t_id = tags.id where words.name='%s' order by hit / total limit %d" % (wordName, maxnumtag))
		#tags = c.fetchall()
		words = Word.objects.filter(name = wordName).order_by(Cast(F('hit') / F('total'), FloatField())).all()[:maxnumtag]
		if not words.count() is 0:
			for j in range (0, len(words)):
				#tagName = tags[j][0]
				hit = words[j].hit
				total = words[j].total
				hitRatio = float(hit) / total

				tag = Tag.objects.get(t_id = words[j].tag_id)
				tagName = tag.name

				if not tagName in tagDict:
					tagDict[tagName] = float(hitRatio) * salience
				else:
					tagDict[tagName] += float(hitRatio) * salience

	sortedTags = sorted(tagDict.items(), key = operator.itemgetter(1), reverse=True)
	
	numberOfTags = min(maxnumtag, len(sortedTags))
	
	result = []
	for i in range (0, numberOfTags):
		result.append(sortedTags[i][0])

	return result
	
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
	for index, tag in enumerate(tags):
		tags[index] = tag.strip()
	
	wordDictList = googleEntityAnalysis(question)
	
	
	wordList = []
	for wordDict in wordDictList:
		word = wordDict['name']
		word = word.lower()
		wordList.append(word)
	t_idList = []
	for tag in tags:
		#c.execute("select id from tags where name = '%s' limit 1" % (tag))
		tags = Tag.objects.filter(name = tag).all()[:1]
		
		if tags.count() is 0:
			#c.execute("insert into tags(name) values('%s')" % (tag))
			newTag = Tag(name = tag)
			newTag.save()
			retrievedTag = Tag.objects.get(name = tag)
			t_id = retrievedTag.t_id
			t_idList.append(t_id)
			for word in wordList:
				#c.execute("insert into words(name, t_id, hit,total) values('%s',%d,1,2)" % (word, t_id))
				newWord = Word(name = word, hit = 1, total = 2, tag = retrievedTag)
				newWord.save()
		else:
			t_id = tags[0].t_id
			t_idList.append(t_id)
			for word in wordList:
				#c.execute("select w_id from words where name = '%s' and t_id = %d limit 1" % (word, t_id))
				#wordrow = c.fetchone()
				wordrow = Word.objects.filter(name = word, tag = t_id).all()[:1]
				if wordrow.count() is 0:
					#c.execute("insert into words(name, t_id, hit,total) values('%s',%d,1,2)" % (word, t_id))
					newWord = Word(name = word, hit = 1, total = 2 , tag = tags[0])
					newWord.save()
				else:
					retrievedWord = wordrow[0]
					retrievedWord.hit += 1
					retrievedWord.total += 1
					retrievedWord.save()
					#c.execute("update words set hit = hit+1,total=total+1 where w_id = %d" %(w_id))
	cursor = connections['default'].cursor()
	format_strings = ','.join(['%s'] * len(t_idList))
	for word in wordList:
		addtotalsql = "update question_tags_word set total = total + 1 where name = '%s' and tag_id not in (%s)" % (word, format_strings)
		cursor.execute(addtotalsql, tuple(t_idList))	
		
	return

	
def handleTagQuery(request):
	arr = []
	if request.method != 'GET':
		return arr
	if not request.GET.__contains__('t'):
		return arr
		
	query = request.GET.get('t')
	
	query = query.strip()
	query = query.lower()
	
	maxnumberoftags = 3
	tagdict = {}

	count = 1
	startwithtags = Tag.objects.filter(name__istartswith=query)[:maxnumberoftags]
	if (len(startwithtags) >= maxnumberoftags):
		for tag in startwithtags:
			arr.append(tag.name)
		return arr

	for tag in startwithtags:
		if(tagdict.has_key(tag.name) == False):
			tagdict[tag.name] = count
			count = count + 1
	
	containtags = Tag.objects.filter(name__icontains=query)[:maxnumberoftags]
	for tag in containtags:
		if(tagdict.has_key(tag.name) == False):
			tagdict[tag.name] = count
			count = count + 1

	sortedTags = sorted(tagdict.items(), key = operator.itemgetter(1), reverse=False)
	for tag in sortedTags:
		arr.append(tag[0])
	
	return arr[:maxnumberoftags]
		
	
	
	
	
	
	
	
def index(request):

	if request.method != 'GET':
		return JsonResponse({'Error':'Please use get request'})
	
	#if not request.GET.__contains__('q'):
	#	return JsonResponse({'Error':'Please add key wclea to get request'})
	
	if request.GET.__contains__('t') and request.GET.__contains__('q'):
		handleUpdate(request)
		return JsonResponse({})
	elif request.GET.__contains__('q'):
		sortedTags = handleQuery(request)
		return JsonResponse(
		{
			'tags':sortedTags
		});
		
	elif request.GET.__contains__('t'):
		tags = handleTagQuery(request)
		return JsonResponse({
			'tags':tags
		})
		