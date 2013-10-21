from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'principal.views.index'),
    url(r'^datos/', include('principal.urls')),
    url(r'^clientes/', include('clientes.urls')),
    url(r'^propietarios/', include('propietarios.urls')),
    url(r'^fracciones/', include('fracciones.urls')),
    url(r'^lotes/', include('lotes.urls')),
    url(r'^vendedores/', include('vendedores.urls')),
    url(r'^manzanas/', include('manzanas.urls')),
    url(r'^cobradores/', include('cobradores.urls')),
    url(r'^informes/', include('informes.urls')),
    url(r'^movimientos/', include('movimientos.urls')),
    url(r'^parametros/', include('parametros.urls')),
    url(r'^ajax/', include('ajax.urls')),
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),    
    url(r'^admin/', include(admin.site.urls)),
)
