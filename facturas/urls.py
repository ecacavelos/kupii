from django.conf.urls import patterns, url

urlpatterns = patterns('facturas.views',        
    url(r'^facturar/$', 'facturar'),
    url(r'^listado/$', 'consultar_facturas'),
)
