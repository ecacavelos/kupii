from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from principal.models import Lote, Venta, Manzana, Fraccion
from lotes.forms import LoteForm, FraccionManzana

# Funcion principal del modulo de lotes.
def lotes(request):
    t = loader.get_template('lotes/index.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))

# Funcion para consultar el listado de todas las lotes.
def consultar_lotes(request):
    t = loader.get_template('lotes/listado.html')
    
    object_list = Lote.objects.all().order_by( 'id','manzana')
    total_lotes = object_list.count()
    m=[]
    f=[]
    
    for i in range(0, total_lotes): 
        manzana_id = object_list[i].manzana_id
        m.append( Manzana.objects.get(pk = manzana_id))
        
        #setattr(object_list[i], 'nro_manzana', m.nro_manzana)
        fraccion_id = m[i].fraccion_id
        f.append(Fraccion.objects.get(pk = fraccion_id))
        #setattr(object_list[i], 'fraccion', fraccion_id)
        
        
    c = RequestContext(request, {
        'object_list': object_list,
        'manzana': m,
        'fraccion': f,
        
    })
    return HttpResponse(t.render(c))

# Funcion para el detalle de una fraccion: edita o borra una fraccion.
def detalle_lote(request, lote_id):
    t = loader.get_template('lotes/detalle.html')    

    object_list = Lote.objects.get(pk=lote_id)
    message = ''
    message_id = "message"
    
    ventas_relacionadas = Venta.objects.filter(lote=lote_id)

    if request.method == 'POST':
        data = request.POST
        if data.get('boton_guardar'):
            form = LoteForm(data, instance=object_list)
            if form.is_valid():
                message = "Se actualizaron los datos."
                message_id = "message-success"
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
        'ventas_relacionadas': ventas_relacionadas,
        'form': form,
        'message_id': message_id,
        'message': message,
    })
    return HttpResponse(t.render(c))

# Funcion que detalla las ventas relacionadas a un lote determinado.
def detalle_ventas_lote(request, venta_id):
    t = loader.get_template('lotes/detalle_ventas.html')
    venta = Venta.objects.get(pk=venta_id)
    c = RequestContext(request, {
        'venta': venta,
    })
    return HttpResponse(t.render(c))

# Funcion para agregar un nuevo lote.
def agregar_lotes(request):
    t = loader.get_template('lotes/agregar2.html')
    message = ""    

    if request.method == 'POST':
        form = LoteForm(request.POST)
        if form.is_valid():
            form.save()
            # Redireccionamos al listado de lotes luego de agregar el nuevo lote.
            return HttpResponseRedirect('/lotes/listado')
        else:
            form = LoteForm()
            form2 = FraccionManzana()
            message = "Debe Completar los campos requeridos"
            
    else:
        form = LoteForm()
        form2 = FraccionManzana()

    c = RequestContext(request, {
        'form': form,
        'form2': form2,
        'message': message,
    })
    return HttpResponse(t.render(c))


        
         
    
    
    
    
    