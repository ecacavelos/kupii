from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from datos.models import Cliente
from clientes.forms import ClienteForm

# vista principal del modulo de clientes
def clientes(request):
    t = loader.get_template('clientes/index.html')    
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))

#vista para consultar el listado de todos los clientes
def consultar_clientes(request):
    t = loader.get_template('clientes/consultar.html')
    object_list = Cliente.objects.all()
    c = RequestContext(request, {
        'object_list': object_list,                            
    })
    return HttpResponse(t.render(c))

#vista para consultar el detalle de un cliente
def detalle_cliente(request, cliente_id):
    t = loader.get_template('clientes/detalle.html')
    object_list = Cliente.objects.get(pk=cliente_id)
    form = ClienteForm(instance=object_list)
    #form.save()
    c = RequestContext(request, {
        'cliente': object_list,
        'form': form,
    })
    return HttpResponse(t.render(c))
#    try:
#        c = Cliente.objects.get(pk=cliente_id)
#    except Cliente.DoesNotExist:
#        raise Http404
#    return render_to_response('clientes/detalle.html', {'cliente': c})

# vista para agregar un nuevo cliente
def agregar_clientes(request):
    t = loader.get_template('clientes/agregar.html')
    if request.method == 'POST': # If the form has been submitted...    
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/clientes/listado')
    else:
        form = ClienteForm()        
        
    c = RequestContext(request, {
        'form': form,
    })
    return HttpResponse(t.render(c))

def borrar_cliente(request, cliente_id):
    c = Cliente.objects.get(pk=cliente_id)
    c.delete()
    return HttpResponseRedirect('/clientes/listado')
