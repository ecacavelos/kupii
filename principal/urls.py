from django.conf.urls import patterns, url

urlpatterns = patterns('principal.views',
    url(r'^$', 'index'),
    url(r'^1/$', 'retrieve_lote'),
    url(r'^2/$', 'retrieve_cliente'),
    url(r'^3/$', 'retrieve_vendedor'),
    url(r'^5/$', 'retrieve_plan_pago'),
    url(r'^6/$', 'retrieve_venta'),
)