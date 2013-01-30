from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from datos.models import Cliente
from clientes.forms import ClienteForm

# vista principal del modulo de clientes
def clientes(request):
    t = loader.get_template('clientes/index.html')    
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))

#vista para listar todos los clientes
def consultar_clientes(request):
    t = loader.get_template('clientes/consultar.html')
    object_list = Cliente.objects.all()
    c = RequestContext(request, {
        'object_list': object_list,                            
    })
    return HttpResponse(t.render(c))

# vista para agregar un nuevo cliente
def agregar_clientes(request):
    t = loader.get_template('clientes/agregar.html')
    if request.method == 'POST': # If the form has been submitted...    
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/clientes/consultar')
    else:
        form = ClienteForm()        
        
    c = RequestContext(request, {
        'form': form,
    })
    return HttpResponse(t.render(c))
