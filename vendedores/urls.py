from django.conf.urls import patterns, include, url

urlpatterns = patterns('vendedores.views',    
    url(r'^$', 'vendedores'),
    url(r'^listado/$', 'consultar_vendedores'),
    url(r'^listado/(?P<vendedor_id>\d+)/$', 'detalle_vendedor'),
    url(r'^agregar/$', 'agregar_vendedores'),
)
