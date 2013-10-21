from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from principal.models import Vendedor
from vendedores.forms import VendedorForm
from django.views.generic.list_detail import object_list

# Funcion principal del modulo de vendedores.
def vendedores(request):
    t = loader.get_template('vendedores/index.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))

# Funcion para consultar el listado de todas los vendedores.
def consultar_vendedores(request):
    t = loader.get_template('vendedores/listado.html')
    
    object_list = Vendedor.objects.all().order_by('id')
    
    c = RequestContext(request, {
        'object_list': object_list,
    })
    return HttpResponse(t.render(c))

# Funcion para el detalle de un vendedor: edita o borra un vendedor.
def detalle_vendedor(request, vendedor_id):
    t = loader.get_template('vendedores/detalle.html')    

    object_list = Vendedor.objects.get(pk=vendedor_id)
    message = ''

    if request.method == 'POST':
        data = request.POST
        if data.get('boton_guardar'):
            form = VendedorForm(data, instance=object_list)
            if form.is_valid():
                message = "Se actualizaron los datos."
                form.save(commit=False)
                object_list.save()
        elif data.get('boton_borrar'):
            f = Vendedor.objects.get(pk=vendedor_id)
            f.delete()
            return HttpResponseRedirect('/vendedores/listado')
    else:
        form = VendedorForm(instance=object_list)

    c = RequestContext(request, {
        'vendedor': object_list,
        'form': form,
        'message': message,
    })
    return HttpResponse(t.render(c))

# Funcion para agregar un nuevo vendedor.
def agregar_vendedores(request):
    t = loader.get_template('vendedores/agregar.html')

    if request.method == 'POST':
        form = VendedorForm(request.POST)
        if form.is_valid():
            form.save()
            # Redireccionamos al listado de lotes luego de agregar el nuevo lote.
            return HttpResponseRedirect('/vendedores/listado')
    else:
        form = VendedorForm()

    c = RequestContext(request, {
        'form': form,
    })
    return HttpResponse(t.render(c))
