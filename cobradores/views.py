from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from datos.models import Cobrador
from cobradores.forms import CobradorForm
from django.views.generic.list_detail import object_list

# Funcion principal del modulo de cobradores.
def cobradores(request):
    t = loader.get_template('cobradores/index.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))

# Funcion para consultar el listado de todas los cobradores.
def consultar_cobradores(request):
    t = loader.get_template('cobradores/listado.html')
    
    object_list = Cobrador.objects.all().order_by('id')
    
    c = RequestContext(request, {
        'object_list': object_list,
    })
    return HttpResponse(t.render(c))

# Funcion para el detalle de un cobrador: edita o borra un cobrador.
def detalle_cobrador(request, cobrador_id):
    t = loader.get_template('cobradores/detalle.html')    

    object_list = Cobrador.objects.get(pk=cobrador_id)
    message = ''

    if request.method == 'POST':
        data = request.POST
        if data.get('boton_guardar'):
            form = CobradorForm(data, instance=object_list)
            if form.is_valid():
                message = "Se actualizaron los datos."
                form.save(commit=False)
                object_list.save()
        elif data.get('boton_borrar'):
            f = Cobrador.objects.get(pk=cobrador_id)
            f.delete()
            return HttpResponseRedirect('/cobradores/listado')
    else:
        form = CobradorForm(instance=object_list)
    
    c = RequestContext(request, {
        'cobrador': object_list,
        'form': form,
        'message': message,
    })
    return HttpResponse(t.render(c))

# Funcion para agregar un nuevo cobrador.
def agregar_cobradores(request):
    t = loader.get_template('cobradores/agregar.html')

    if request.method == 'POST':
        form = CobradorForm(request.POST)
        if form.is_valid():
            form.save()
            # Redireccionamos al listado de cobradores luego de agregar el nuevo cobrador.
            return HttpResponseRedirect('/cobradores/listado')
    else:
        form = CobradorForm()

    c = RequestContext(request, {
        'form': form,
    })
    return HttpResponse(t.render(c))
