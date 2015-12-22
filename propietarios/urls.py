from django.conf.urls import patterns, include, url

urlpatterns = patterns('propietarios.views',    
    url(r'^$', 'index'),    
    url(r'^listado/$', 'consultar_propietarios', name='frontend_listado_propietarios'),
    url(r'^listado/(?P<propietario_id>\d+)/$', 'detalle_propietario'),
    url(r'^agregar/$', 'agregar_propietarios'),    
)
