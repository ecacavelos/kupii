from django.conf.urls import patterns, include, url

urlpatterns = patterns('lotes.views',    
    url(r'^$', 'lotes'),
)
