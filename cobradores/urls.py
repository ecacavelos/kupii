from django.conf.urls import patterns, include, url

urlpatterns = patterns('cobradores.views',    
    url(r'^$', 'cobradores'),    
    url(r'^listado/$', 'consultar_cobradores'),
    url(r'^listado/(?P<cobrador_id>\d+)/$', 'detalle_cobrador'),
    url(r'^agregar/$', 'agregar_cobradores'),
)
