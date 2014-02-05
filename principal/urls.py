from django.conf.urls import patterns, url

urlpatterns = patterns('principal.views',
    url(r'^$', 'index'),
    url(r'^$autenticar', 'index'),
    url(r'^1/$', 'retrieve_lote'),
    url(r'^2/$', 'retrieve_cliente'),
    url(r'^3/$', 'retrieve_vendedor'),
    url(r'^5/$', 'retrieve_plan_pago'),
    url(r'^6/$', 'retrieve_venta'),
    url(r'^7/$', 'get_all_planes'),
    url(r'^8/$', 'get_id_propietario'),
    url(r'^$login/', 'django.contrib.auth.views.login', {'template_name': '/login.html'}, name='login'),
    url(r'^$logout/', 'django.contrib.auth.views.logout', {'template_name': '/logout.html'}, name='logout'),
)

