from django.conf.urls import patterns, url

urlpatterns = patterns('fracciones.views',    
    url(r'^$', 'fracciones'),
    url(r'^listado/$', 'consultar_fracciones'),
    url(r'^listado/(?P<fraccion_id>\d+)/$', 'detalle_fraccion'),
    url(r'^agregar/$', 'agregar_fracciones'),
    url(r'^listado_busqueda_fracciones/$', 'listar_busqueda_fracciones'),
)
