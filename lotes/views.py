from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from datos.models import Lote

# Funcion principal del modulo de fracciones.
def lotes(request):
    t = loader.get_template('lotes/index.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))