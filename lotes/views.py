from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from datos.models import Lote
from lotes.forms import LoteForm

# Funcion principal del modulo de lotes.
def lotes(request):
    t = loader.get_template('lotes/index.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))

# Funcion para consultar el listado de todas las lotes.
def consultar_lotes(request):
    t = loader.get_template('lotes/listado.html')
    
    object_list = Lote.objects.all().order_by('id')
    
    c = RequestContext(request, {
        'object_list': object_list,
    })
    return HttpResponse(t.render(c))

# Funcion para el detalle de una fraccion: edita o borra una fraccion.
def detalle_lote(request, lote_id):
    t = loader.get_template('lotes/detalle.html')    

    object_list = Lote.objects.get(pk=lote_id)
    message = ''

    if request.method == 'POST':
        data = request.POST
        if data.get('boton_guardar'):
            form = LoteForm(data, instance=object_list)
            if form.is_valid():
                message = "Se actualizaron los datos."
                form.save(commit=False)
                object_list.save()
        elif data.get('boton_borrar'):
            f = Lote.objects.get(pk=lote_id)
            f.delete()
            return HttpResponseRedirect('/lotes/listado')
    else:
        form = LoteForm(instance=object_list)
    
    c = RequestContext(request, {
        'lote': object_list,
        'form': form,
        'message': message,
    })
    return HttpResponse(t.render(c))

# Funcion para agregar una nueva fraccion.
def agregar_lotes(request):
    t = loader.get_template('lotes/agregar.html')

    if request.method == 'POST':
        form = LoteForm(request.POST)
        if form.is_valid():
            form.save()
            # Redireccionamos al listado de lotes luego de agregar el nuevo lote.
            return HttpResponseRedirect('/lotes/listado')
    else:
        form = LoteForm()

    c = RequestContext(request, {
        'form': form,
    })
    return HttpResponse(t.render(c))
