from django.conf.urls import patterns, url

urlpatterns = patterns('movimientos.views',    
    url(r'^$', 'movimientos'),
    url(r'^ventas_lotes/$', 'ventas_de_lotes'),
)
