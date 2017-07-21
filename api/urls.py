from django.conf.urls import patterns, url

# La barra despues 'urlpatterns = \' es para el salto de linea
urlpatterns = \
    patterns('api.views',
             #API Practi Pagos
             # url(r'^consulta/(?P<cedula>\d+)/$', 'consulta'),
             url(r'^consulta/(?P<codigo_consulta>[-\w]+)/$', 'consulta'),
             url(r'^pago/$', 'pago', name='pago'),
             url(r'^reversion/$', 'reversion'),

             #API Aqui Pagos
             url(r'^aqui_pagos/consulta/', 'aqui_pagos_consulta', name='aqui_pagos_consulta'),
             url(r'^aqui_pagos/pago/$', 'aqui_pagos_pago', name='aqui_pagos_pago'),
             url(r'^aqui_pagos/reversion/$', 'aqui_pagos_reversion', name='aqui_pagos_reversion'),
             )
