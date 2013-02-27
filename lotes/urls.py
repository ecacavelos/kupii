from django.conf.urls import patterns, url

urlpatterns = patterns('lotes.views',    
    url(r'^$', 'lotes'),
    url(r'^listado/$', 'consultar_lotes'),
    url(r'^listado/(?P<lote_id>\d+)/$', 'detalle_lote'),
    url(r'^agregar/$', 'agregar_lotes'),
)
