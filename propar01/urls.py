from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import settings

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'},
                           name='login'),
                       url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'login.html'},
                           name='logout'),
                       url(r'^$', 'principal.views.index', name='frontend_home'),
                       url(r'^clientes/', include('clientes.urls')),
                       url(r'^propietarios/', include('propietarios.urls')),
                       url(r'^fracciones/', include('fracciones.urls')),
                       url(r'^informes/', include('informes.urls')),
                       url(r'^movimientos/', include('movimientos.urls')),
                       url(r'^parametros/', include('parametros.urls')),
                       url(r'^vendedores/', include('vendedores.urls')),
                       url(r'^manzanas/', include('manzanas.urls')),
                       url(r'^cobradores/', include('cobradores.urls')),
                       url(r'^facturacion/', include('facturas.urls')),
                       # url(r'^configuraciones/', include('configuraciones.urls')),
                       url(r'^lotes/', include('lotes.urls')),
                       url(r'^ajax/', include('ajax.urls')),
                       url(r'^datos/', include('principal.urls')),
                       url(r'^api/', include('api.urls')),
                       url(r'^logo/', 'parametros.views.cambio_logo', name='cambio_logo'),
                       url(r'^contactos/', include('contactos.contactos_urls')),
                       )
urlpatterns += patterns('',
                        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                            'document_root': settings.MEDIA_ROOT}))
