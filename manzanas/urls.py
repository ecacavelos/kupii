from django.conf.urls import patterns, url

urlpatterns = patterns('manzanas.views',    
    url(r'^$', 'manzanas'),
    url(r'^listado/$', 'consultar_manzanas'),
    url(r'^listado/(?P<manzana_id>\d+)/$', 'detalle_manzana'),
    #url(r'^agregar/$', 'agregar_fracciones'),
)
