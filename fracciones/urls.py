from django.conf.urls import patterns, include, url

urlpatterns = patterns('fracciones.views',    
    url(r'^$', 'fracciones'),
    url(r'^listado/$', 'consultar_fracciones'),
    url(r'^listado/(?P<fraccion_id>\d+)/$', 'detalle_fraccion'),
    url(r'^agregar/$', 'agregar_fracciones'),
)
