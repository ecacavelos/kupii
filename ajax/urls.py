from django.conf.urls import patterns, include, url

urlpatterns = patterns('ajax.views',        
    url(r'^get_fracciones_by_name/$', 'get_fracciones_by_name', name='get_fracciones_by_name'),
)