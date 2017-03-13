from django.conf.urls import url
from . import views
#import nltk

urlpatterns = [
    #url(r'^matthew/$', views.index2, name='index2'),
	url(r'^zhaowei/$', views.index, name='index'),
]

#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')