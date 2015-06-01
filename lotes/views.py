from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template import RequestContext, loader
from principal.models import Lote, Venta, Manzana, Fraccion, Propietario, Cliente
from lotes.forms import LoteForm, FraccionManzana
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.core.urlresolvers import reverse, resolve
# Funcion principal del modulo de lotes.
def lotes(request):
    
    if request.user.is_authenticated():
        t = loader.get_template('lotes/index.html')
        c = RequestContext(request, {})
        return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login')) 

# Funcion para consultar el listado de todas las lotes.
def consultar_lotes(request):
    
    if request.user.is_authenticated():
        t = loader.get_template('lotes/listado.html')
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login')) 
    
    object_list = Lote.objects.all().order_by( 'id','manzana')
    
    paginator=Paginator(object_list,15)
    page=request.GET.get('page')
    try:
        lista=paginator.page(page)
    except PageNotAnInteger:
        lista=paginator.page(1)
    except EmptyPage:
        lista=paginator.page(paginator.num_pages)
    
        
    c = RequestContext(request, {
        'object_list': lista,
    })
    return HttpResponse(t.render(c))

# Funcion para el detalle de una fraccion: edita o borra una fraccion.
def detalle_lote(request, lote_id):
    
    
    if request.user.is_authenticated():
        t = loader.get_template('lotes/detalle.html')
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))     

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
    if request.user.is_authenticated():
        t = loader.get_template('lotes/detalle_ventas.html')
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))  
    
    try:
        venta = Venta.objects.get(pk=venta_id)
        venta.fecha_de_venta=venta.fecha_de_venta.strftime("%d/%m/%Y")
        venta.precio_final_de_venta=unicode('{:,}'.format(venta.precio_final_de_venta)).replace(",", ".")
        c = RequestContext(request, {
            'venta': venta,
            })
        return HttpResponse(t.render(c))
    except:    
        return HttpResponseServerError("No se pudo obtener el Detalle de Venta del Lote.") 

# Funcion para agregar un nuevo lote.
def agregar_lotes(request):
    
    
    if request.user.is_authenticated():
        t = loader.get_template('lotes/agregar2.html')
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login')) 
    
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

def listar_busqueda_lotes(request):
       
    if request.user.is_authenticated():
        t = loader.get_template('lotes/listado.html')
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login')) 
    
    
    busqueda = request.POST['busqueda']
    tipo_busqueda=request.POST['tipo_busqueda']
    #se busca un lote
    if busqueda:        
        x=unicode(busqueda)
        fraccion_int = int(x[0:3])
        manzana_int =int(x[4:7])
        lote_int = int(x[8:])
        manzana= Manzana.objects.get(fraccion_id= fraccion_int, nro_manzana= manzana_int)
        object_list = Lote.objects.filter(manzana=manzana.id, nro_lote=lote_int)
    elif tipo_busqueda:
        #se buscan los lotes de un determinado cliente
        busqueda = request.POST['busqueda_cliente']                
        lista_lotes=[]        
        if(tipo_busqueda=='cedula'):            
            cliente=Cliente.objects.get(Q(cedula=busqueda)| Q(ruc=busqueda))
            ventas=Venta.objects.filter(cliente_id=cliente.id).order_by('cliente')
            for venta in ventas:
                lote=Lote.objects.get(pk=venta.lote_id)
                lista_lotes.append(lote)
    
        if(tipo_busqueda=='nombre'):
            clientes=Cliente.objects.filter(nombres__icontains=busqueda).order_by('id')            
            for cliente in clientes:
                ventas=Venta.objects.filter(cliente_id=cliente)
                for venta in ventas:
                    lote=Lote.objects.get(pk=venta.lote_id)
                    lista_lotes.append(lote)
        
        if(tipo_busqueda=='id'):
            ventas=Venta.objects.filter(cliente_id=busqueda).order_by('cliente')
            for venta in ventas:
                lote=Lote.objects.get(pk=venta.lote_id)
                lista_lotes.append(lote)
        object_list=lista_lotes
            
    paginator=Paginator(object_list,15)
    page=request.GET.get('page')
    try:
        lista=paginator.page(page)
    except PageNotAnInteger:
        lista=paginator.page(1)
    except EmptyPage:
        lista=paginator.page(paginator.num_pages)
    
        
    c = RequestContext(request, {
        'object_list': lista,
    })
    return HttpResponse(t.render(c))


   
        
         
    
    
    
    
    