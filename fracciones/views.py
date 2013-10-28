from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from principal.models import Fraccion, Manzana
from fracciones.forms import FraccionForm

# Funcion principal del modulo de fracciones.
def fracciones(request):
    t = loader.get_template('fracciones/index.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))

# Funcion para consultar el listado de todas las fracciones.
def consultar_fracciones(request):
    t = loader.get_template('fracciones/listado.html')
    
    object_list = Fraccion.objects.all().order_by('id')
    
    c = RequestContext(request, {
        'object_list': object_list,
    })
    return HttpResponse(t.render(c))

# Funcion para el detalle de una fraccion: edita o borra una fraccion.
def detalle_fraccion(request, fraccion_id):
    t = loader.get_template('fracciones/detalle.html')    

    object_list = Fraccion.objects.get(pk=fraccion_id)
    message = ''

    if request.method == 'POST':
        data = request.POST
        if data.get('boton_guardar'):
            form = FraccionForm(data, instance=object_list)
            if form.is_valid():
                message = "Se actualizaron los datos."
                form.save(commit=False)
                object_list.save()
        elif data.get('boton_borrar'):
            f = Fraccion.objects.get(pk=fraccion_id)
            f.delete()
            return HttpResponseRedirect('/fracciones/listado')
    else:        
        form = FraccionForm(instance=object_list)
                
    c = RequestContext(request, {
        'fraccion': object_list,
        'form': form,
        'message': message,
    })
    return HttpResponse(t.render(c))

# Funcion para agregar una nueva fraccion.
def agregar_fracciones(request):
    t = loader.get_template('fracciones/agregar2.html')

    if request.method == 'POST':
        form = FraccionForm(request.POST)
        if form.is_valid():
            fraccion = form.save()
            cantidad_manzanas = fraccion.cantidad_manzanas
            for i in range(1, cantidad_manzanas + 1):
                manzana = Manzana()
                manzana.fraccion = fraccion
                manzana.nro_manzana = i
                manzana.save()
            # Agregar las cantidad_manzanas que correspondan
            # total_manzanas = form.
            # while 
            # Redireccionamos al listado de clientes luego de agregar el nuevo cliente.
            return HttpResponseRedirect('/fracciones/listado')
    else:
        form = FraccionForm()

    c = RequestContext(request, {
        'form': form,
    })
    return HttpResponse(t.render(c))
