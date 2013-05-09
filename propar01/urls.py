from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'principal.views.index'),
    url(r'^datos/', include('principal.urls')),
    url(r'^clientes/', include('clientes.urls')),
    url(r'^fracciones/', include('fracciones.urls')),
    url(r'^lotes/', include('lotes.urls')),
    url(r'^vendedores/', include('vendedores.urls')),
    url(r'^cobradores/', include('cobradores.urls')),
    url(r'^informes/', include('informes.urls')),
    url(r'^movimientos/', include('movimientos.urls')),
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),    
    url(r'^admin/', include(admin.site.urls)),
)
