from django.conf.urls import patterns, url

urlpatterns = patterns('contactos.contactos_views',
                       #url(r'^$', 'contactos', name='frontend_contactos_index'),
                       url(r'^listado/$', 'listado_contactos', name='frontend_listado_contactos'),
                       url(r'^listado/(?P<contacto_id>\d+)/$', 'detalle_contacto', name='frontend_detalle_contacto'),
                       url(r'^agregar/$', 'agregar_contacto'),
                       )
