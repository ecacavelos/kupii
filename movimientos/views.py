from django.http import HttpResponse
from django.template import RequestContext, loader
from datos.models import Lote
from lotes.forms import LoteIdentifierForm
from django.core.context_processors import csrf

# Funcion principal del modulo de lotes.
def movimientos(request):
    t = loader.get_template('movimientos/index.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))

def ventas_de_lotes(request):
    t = loader.get_template('movimientos/ventas_lotes.html')
    
    if request.method == 'POST':
        data = request.POST
        identifier_form = LoteIdentifierForm(data)
        object_list = Lote.objects.all()        
        if data.get('buscar', ''):
            object_list = Lote.objects.all().filter(fraccion=data.get('buscar', ''))            
    else:
        object_list = Lote.objects.none()
        identifier_form = LoteIdentifierForm({})
        
    c = RequestContext(request, {
        'object_list': object_list,
        'identifier_form': identifier_form,
    })
    # c.update(csrf(request))
    return HttpResponse(t.render(c))
