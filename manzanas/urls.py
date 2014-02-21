from django.conf.urls import patterns, url

urlpatterns = patterns('manzanas.views',    
    url(r'^$', 'manzanas'),
    url(r'^agregar_lotes_por_manzana/$', 'agregar_lotes_por_manzana'),
    url(r'^listado/$', 'consultar_manzanas'),
    url(r'^listado/(?P<manzana_id>\d+)/$', 'detalle_manzana'),
    # url(r'^agregar/$', 'agregar_manzanas'),
)
