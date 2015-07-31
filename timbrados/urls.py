from django.conf.urls import patterns, url

urlpatterns = patterns('timbrados.views',        
    url(r'^timbrados/$', 'ver'),
)
