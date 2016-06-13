from django.conf.urls import patterns, url

urlpatterns = patterns('manzanas.views',    
    url(r'^$', 'manzanas'),
    url(r'^agregar_lotes_por_manzana/$', 'agregar_lotes_por_manzana'),
    url(r'^listado/$', 'consultar_manzanas', name='frontend_listado_manzanas'),
    url(r'^listado/(?P<manzana_id>\d+)/$', 'detalle_manzana'),
    url(r'^listado_busqueda_manzanas/$', 'listar_busqueda_manzanas'),
    # url(r'^agregar/$', 'agregar_manzanas'),
)
