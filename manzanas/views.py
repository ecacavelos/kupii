from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from principal.models import Manzana
from manzanas.forms import ManzanaForm

# Funcion principal del modulo de manzanas.
def manzanas(request):
    t = loader.get_template('manzanas/index.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))

# Funcion para consultar el listado de todas las manzanas.
def consultar_manzanas(request):
    t = loader.get_template('manzanas/listado.html')
    
    object_list = Manzana.objects.all().order_by('id')
    
    c = RequestContext(request, {
        'object_list': object_list,
    })
    return HttpResponse(t.render(c))

# Funcion para el detalle de una fraccion: edita o borra una fraccion.
def detalle_manzana(request, manzana_id):
    t = loader.get_template('manzanas/detalle.html')    
 
    object_list = Manzana.objects.get(pk=manzana_id)
    message = ''
 
    if request.method == 'POST':
        data = request.POST
        if data.get('boton_guardar'):
            form = ManzanaForm(data, instance=object_list)
            if form.is_valid():
                message = "Se actualizaron los datos."
                form.save(commit=False)
                object_list.save()
        elif data.get('boton_borrar'):
            f = Manzana.objects.get(pk=manzana_id)
            f.delete()
            return HttpResponseRedirect('/manzanas/listado')
    else:        
        form = ManzanaForm(instance=object_list)
                 
    c = RequestContext(request, {
        'manzana': object_list,
        'form': form,
        'message': message,
    })
    return HttpResponse(t.render(c))