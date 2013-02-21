from django.conf.urls import patterns, include, url

urlpatterns = patterns('clientes.views',    
    url(r'^$', 'clientes'),    
    url(r'^listado/$', 'consultar_clientes'),
    url(r'^listado/(?P<cliente_id>\d+)/$', 'detalle_cliente'),
    url(r'^agregar/$', 'agregar_clientes'),    
)
