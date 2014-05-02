from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from principal.models import Lote
from lotes.forms import LoteForm

# Funcion principal del modulo de lotes.
def informes(request):
    
    if request.user.is_authenticated():
        t = loader.get_template('informes/index.html')
        c = RequestContext(request, {})
        return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login") 

def lotes_libres(request):
    
    
    if request.user.is_authenticated():
        t = loader.get_template('informes/lotes_libres.html')
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login") 
    
    object_list = Lote.objects.filter(estado="1").order_by('fraccion', 'manzana', 'nro_lote')
    
    c = RequestContext(request, {
        'object_list': object_list,
    })
    return HttpResponse(t.render(c))
