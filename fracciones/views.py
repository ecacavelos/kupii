from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from principal.models import Propietario,Fraccion, Manzana, Lote, Factura, PagoDeCuotas, RecuperacionDeLotes, CambioDeLotes, TransferenciaDeLotes, Reserva
from fracciones.forms import FraccionForm, FraccionFormAdd
from django.db import reset_queries, close_connection
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse, resolve
from principal.common_functions import *
from principal import permisos
from django.views.generic.edit import DeleteView
from django.core.urlresolvers import reverse_lazy

class FraccionDelete(DeleteView):
    model = Fraccion
    success_url = reverse_lazy('frontend_listado_fracciones')

# Funcion principal del modulo de fracciones.
def fracciones(request):
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_OPCIONES_FRACCION):
            t = loader.get_template('fracciones/index.html')
            c = RequestContext(request, {})
            return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo  
                })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))

# Funcion para consultar el listado de todas las fracciones.
def consultar_fracciones(request):
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_FRACCIONES):
            t = loader.get_template('fracciones/listado.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo  
                })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
    object_list = Fraccion.objects.all().order_by('id')
    
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
def detalle_fraccion(request, fraccion_id):
    close_connection()
    reset_queries()   
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_FRACCIONES):            
            t = loader.get_template('fracciones/detalle.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo  
            })
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo  
                })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))    
    
    object_list = Fraccion.objects.get(pk=fraccion_id)
    message = ''

    if request.method == 'POST':
        request.POST = request.POST.copy()
        data = request.POST
        if data.get('boton_guardar'):
            form = FraccionFormAdd(data, instance=object_list)
            if form.is_valid():
                message = "Se actualizaron los datos."
                data['fecha_aprobacion'] = datetime.datetime.strptime(data['fecha_aprobacion'], "%d/%m/%Y")
                form.save(commit=False)
                
                #Se loggea la accion del usuario
                id_objeto = form.instance.id
                codigo_lote = ''
                loggear_accion(request.user, "Actualizar", "Fraccion", id_objeto, codigo_lote)
                
                object_list.save()
                #return HttpResponseRedirect('/fracciones/listado')
            else:
                message = "No se pudo actualizar los datos."
                    
        elif data.get('boton_borrar'):
            fraccion = Fraccion.objects.get(pk=fraccion_id)
            manzanas = Manzana.objects.filter(fraccion = fraccion)
            for manzana in manzanas:
                lotes = Lote.objects.filter(manzana = manzana)
                for lote in lotes:
                    ventas = Venta.objects.filter(lote = lote)
                    for venta in ventas:
                        pagos = PagoDeCuotas.objects.filter(venta = venta)
                        for pago in pagos:
                            pago.delete()
                        recuperaciones = RecuperacionDeLotes.objects.filter(venta = venta)
                        for recuperacion in recuperaciones:
                            recuperacion.delete()
                        venta.delete()
                    cambios = CambioDeLotes.objects.filter(lote_a_cambiar = lote)
                    for cambio in cambios:
                        cambio.delete()
                    cambios = CambioDeLotes.objects.filter(lote_nuevo = lote)
                    for cambio in cambios:
                        cambio.delete()
                    facturas = Factura.objects.filter(lote = lote)
                    for factura in facturas:
                        factura.delete()
                    reservas = Reserva.objects.filter(lote = lote)
                    for reserva in reservas:
                        reserva.delete()
                    lote.delete()
                manzana.delete()
            fraccion.delete()
            
            #Se loggea la accion del usuario
            id_objeto = fraccion_id
            codigo_lote = ''
            loggear_accion(request.user, "Borrar(con todos sus lotes y movimientos)", "Fraccion", id_objeto, codigo_lote)
            message = "Se borro la Fraccion y todos sus lotes y movimientos asociados."
            #return HttpResponseRedirect('/fracciones/listado')
            return HttpResponseRedirect(reverse('frontend_listado_fracciones'))
                
        else:
            form = FraccionFormAdd(data, instance=object_list)
            if form.is_valid():
                message = "Se actualizaron los datos."
                data['fecha_aprobacion'] = datetime.datetime.strptime(data['fecha_aprobacion'], "%d/%m/%Y")
                form.save(commit=False)
                
                #Se loggea la accion del usuario
                id_objeto = form.instance.id
                codigo_lote = ''
                loggear_accion(request.user, "Actualizar", "Fraccion", id_objeto, codigo_lote)
                
                object_list.save()
                #return HttpResponseRedirect('/fracciones/listado')
            else:
                message = "No se pudo actualizar los datos."
    else:        
        form = FraccionForm(instance=object_list)
                
    c = RequestContext(request, {
        'fraccion': object_list,
        'form': form,
        'message': message,
        'grupo': grupo,
    })
    return HttpResponse(t.render(c))

# Funcion para agregar una nueva fraccion.
def agregar_fracciones(request):
    
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.ADD_FRACCION):
            t = loader.get_template('fracciones/agregar2.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo                                     })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))   

    if request.method == 'POST':
        form = FraccionForm(request.POST)
        lotes_por_manzana = request.POST['lotes_por_manzana']
        lotes_por_manzana = lotes_por_manzana.split(",")
        if form.is_valid():
            fraccion = form.save()
            
            #Se loggea la accion del usuario
            id_objeto = form.instance.id
            codigo_lote = ''
            loggear_accion(request.user, "Agregar", "Fraccion", id_objeto, codigo_lote)
            
            cantidad_manzanas = fraccion.cantidad_manzanas
            # cantidad_lotes = fraccion.cantidad_lotes
            for i in range(1, cantidad_manzanas + 1):
                manzana = Manzana()
                manzana.fraccion = fraccion
                manzana.nro_manzana = i
                manzana.cantidad_lotes = lotes_por_manzana[i - 1]
                manzana.save()
            # Agregar las cantidad_manzanas que correspondan
            # total_manzanas = form.
            # while 
            # Redireccionamos al listado de clientes luego de agregar el nuevo cliente.
            #return HttpResponseRedirect('/fracciones/listado')
            return HttpResponseRedirect(reverse('frontend_listado_fracciones'))
    else:
        form = FraccionForm()

    c = RequestContext(request, {
        'form': form,
    })
    return HttpResponse(t.render(c))
def listar_busqueda_fracciones(request):
    
    busqueda = request.POST['busqueda']
    tipo_busqueda = request.POST['tipo_busqueda']
    object_list=[]
    
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_FRACCIONES):
            t = loader.get_template('fracciones/listado.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login')) 
        
    if tipo_busqueda == "numero":
        
        object_list = Fraccion.objects.filter(pk=busqueda)
        
    if tipo_busqueda == "nombre_fraccion":
        object_list = Fraccion.objects.filter(pk=busqueda)
    
    if tipo_busqueda == "nombre_propietario":
        propietario_list = Propietario.objects.filter(pk=busqueda)
        for prop in propietario_list:
            query = Fraccion.objects.filter(propietario_id=prop.id)
            if query:
                for f in query:
                    object_list.append(f)
       
        
    paginator = Paginator(object_list, 15)
    page = request.GET.get('page')
    try:
        lista = paginator.page(page)
    except PageNotAnInteger:
        lista = paginator.page(1)
    except EmptyPage:
        lista = paginator.page(paginator.num_pages)
    
    c = RequestContext(request, {
      'object_list': lista,
    })
    
    return HttpResponse(t.render(c))