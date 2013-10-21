from django.conf.urls import patterns, url

urlpatterns = patterns('parametros.views',
    url(r'^$', 'parametros'),
    url(r'^plan_pago/$', 'plan_de_pago'),
    url(r'^plan_pago/listado/$', 'consultar_plan_de_pago'),
    url(r'^plan_pago/listado/(?P<plandepago_id>\d+)/$', 'detalle_plan_de_pago'),
    url(r'^plan_pago/agregar/$', 'agregar_plan_de_pago'),
    url(r'^generales/$', 'parametros_generales'),
)