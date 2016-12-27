from django.conf.urls import patterns, url

# La barra despues 'urlpatterns = \' es para el salto de linea
urlpatterns = \
    patterns('api.views',
             # url(r'^consulta/(?P<cedula>\d+)/$', 'consulta'),
             url(r'^consulta/(?P<codigo_consulta>[-\w]+)/$', 'consulta'),
             url(r'^pago/$', 'pago', name='pago'),
             url(r'^reversion/$', 'reversion'),
             )
