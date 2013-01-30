from django.conf.urls import patterns, include, url

urlpatterns = patterns('clientes.views',    
    url(r'^$', 'clientes'),
    url(r'^consultar/$', 'consultar_clientes'),
    url(r'^agregar/$', 'agregar_clientes'),
)
