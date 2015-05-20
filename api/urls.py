from django.conf.urls import patterns, include, url

urlpatterns = patterns('api.views',        
    url(r'^consulta/(?P<cedula>\d+)/$', 'consulta'),
    url(r'^pago/$', 'pago', name='pago'),       
)
