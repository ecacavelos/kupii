from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template import RequestContext, loader
from principal.models import Lote, Venta, Manzana, Fraccion, Propietario, Cliente, RecuperacionDeLotes
from lotes.forms import LoteForm, FraccionManzana
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.core.urlresolvers import reverse, resolve
# Funcion principal del modulo de lotes.
from principal.common_functions import verificar_permisos, loggear_accion
from principal import permisos
from django.contrib.auth.models import User
from django.db import connection
def lotes(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_OPCIONES):
            t = loader.get_template('lotes/index.html')
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

# Funcion para consultar el listado de todas las lotes.
def consultar_lotes(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_LOTES):
            t = loader.get_template('lotes/listado.html')
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
    
    object_list = Lote.objects.all().order_by( 'manzana__fraccion','manzana__nro_manzana', 'nro_lote')[:15]
    
    for lote in object_list:
        if lote.estado == '3':
            try:
                venta = Venta.objects.filter(lote_id = lote.id).order_by('-fecha_de_venta')
                venta = venta[0]
                cliente = venta.cliente
                lote.cliente = cliente
            except Exception, error:
                lote.cliente = 'Lote de estado "vendido" sin venta asociada'
                print "El lote vendido no esta asociado a una venta."
        
        
    
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
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_LOTES):
            t = loader.get_template('lotes/detalle.html')
            grupo= request.user.groups.get().id
    
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

    object_list = Lote.objects.get(pk=lote_id)
    message = ''
    message_id = "message"
    
    ventas_relacionadas = Venta.objects.filter(lote=lote_id)

    if request.method == 'POST':
        request.POST = request.POST.copy()
        data = request.POST
        if data.get('boton_guardar'):
            form = LoteForm(data, instance=object_list)
            data['nro_lote'] = int(data['nro_lote'])    
            data['precio_contado'] = int(data['precio_contado'].replace(".", "")) 
            data['precio_credito'] = int(data['precio_credito'].replace(".", ""))
            data['precio_costo'] = int(data['precio_costo'].replace(".", ""))
            if form.is_valid():
                message = "Se actualizaron los datos."
                message_id = "message-success"
                form.save(commit=False)
                
                #Se loggea la accion del usuario
                id_objeto = form.instance.id
                codigo_lote = form.instance.codigo_paralot
                loggear_accion(request.user, "Actualizar", "Lote", id_objeto, codigo_lote)
                
                object_list.save()
        elif data.get('boton_borrar'):
            f = Lote.objects.get(pk=lote_id)
            codigo_lote = f.codigo_paralot
            f.delete()
            
            #Se loggea la accion del usuario
            id_objeto = lote_id
            loggear_accion(request.user, "Borrar lote("+codigo_lote+")", "Factura", id_objeto, codigo_lote)
            
            #return HttpResponseRedirect('/lotes/listado')
            return HttpResponseRedirect(reverse('frontend_listado_lotes'))
        
        elif data.get('boton_guardar_a_recuperacion'):
            form = LoteForm(data, instance=object_list)
            data['nro_lote'] = int(data['nro_lote'])    
            data['precio_contado'] = int(data['precio_contado'].replace(".", "")) 
            data['precio_credito'] = int(data['precio_credito'].replace(".", ""))
            data['precio_costo'] = int(data['precio_costo'].replace(".", ""))
            if form.is_valid():
                message = "Se actualizaron los datos."
                message_id = "message-success"
                form.save(commit=False)
                
                #Se loggea la accion del usuario
                id_objeto = form.instance.id
                codigo_lote = form.instance.codigo_paralot
                loggear_accion(request.user, "Actualizar", "Lote", id_objeto, codigo_lote)
                
                object_list.save()
            
            #return HttpResponseRedirect('/movimientos/recuperacion_lotes/')
            return HttpResponseRedirect(reverse('frontend_recuperacion_lotes'))
    else:
        form = LoteForm(instance=object_list)
    
    c = RequestContext(request, {
        'lote': object_list,
        'ventas_relacionadas': ventas_relacionadas,
        'form': form,
        'message_id': message_id,
        'message': message,
        'grupo': grupo
    })
    return HttpResponse(t.render(c))

# Funcion que detalla las ventas relacionadas a un lote determinado.
def detalle_ventas_lote(request, venta_id):
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_LOTES):  
            t = loader.get_template('lotes/detalle_ventas.html')
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
        if verificar_permisos(request.user.id, permisos.ADD_LOTE):
            t = loader.get_template('lotes/agregar2.html')
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
    
    message = ""    

    if request.method == 'POST':
        form = LoteForm(request.POST)
        if form.is_valid():
            form.save()
            id_objeto = form.instance.id
            codigo_lote = form.instance.codigo_paralot
            
            ##id_objeto = 1
            #codigo_lote = 'lalala'
            # Redireccionamos al listado de lotes luego de agregar el nuevo lote.
            loggear_accion(request.user, "Agregar", "Lote", id_objeto, codigo_lote)
            #return HttpResponseRedirect('/lotes/listado')
            return HttpResponseRedirect(reverse('frontend_listado_lotes'))
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
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_LOTES): 
            t = loader.get_template('lotes/listado.html')
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
    
    
    
    busqueda = request.GET.get('busqueda','')
    tipo_busqueda=request.GET.get('tipo_busqueda','')
    busqueda_label = request.GET.get('busqueda_label','')
    
    
    #se busca un lote
    
                    
    lista_lotes=[]        
    if(tipo_busqueda=='cedula'):
        if busqueda != '':       
            ventas=Venta.objects.filter(cliente_id=busqueda)
            for venta in ventas:
                lote=Lote.objects.get(pk=venta.lote_id)
                lista_lotes.append(lote)
        else:
            clientes = Cliente.objects.filter(cedula__icontains=busqueda_label)
            for cliente in clientes:
                ventas = Venta.objects.filter(cliente_id = cliente.id)
                for venta in ventas:
                    lote=Lote.objects.get(pk=venta.lote_id)
                    if lote.estado == '3':
                        lote.cliente = venta.cliente
                        lista_lotes.append(lote)
            
                        
    
    if(tipo_busqueda=='nombre'):
        if busqueda != '':
            ventas=Venta.objects.filter(cliente_id=busqueda, lote__estado = '3')
            for venta in ventas:
                lote=Lote.objects.get(pk=venta.lote_id)
                if lote.estado == '3':
                    lote.cliente = venta.cliente
                    lista_lotes.append(lote)
        else:
            query = (
                        '''
                        SELECT id
                        FROM principal_cliente
                        WHERE CONCAT (UPPER(nombres), ' ', UPPER(apellidos)) like UPPER('%'''+busqueda_label+'''%')
                        '''
            )
                        
            cursor = connection.cursor()
            cursor.execute(query)      
            results= cursor.fetchall()
            lista_clientes = []
            for r in results:
                ventas = Venta.objects.filter(cliente_id = r[0], lote__estado = '3')
                for venta in ventas:
                    try:
                        lote=Lote.objects.get(pk=venta.lote_id)
                        lote.cliente = venta.cliente
                        lista_lotes.append(lote)
                    except Exception, error:
                        print "No existe el lote "+ unicode(venta.lote_id) +" de la venta "+unicode(venta.id)
                        
                        
            
        
    if(tipo_busqueda=='codigo'):
        if busqueda != '':
            lote=Lote.objects.get(pk=busqueda)
            lista_lotes.append(lote)
        else:
            lista_lotes = Lote.objects.filter(codigo_paralot__icontains=busqueda_label).order_by('manzana__fraccion', 'manzana__nro_manzana', 'nro_lote')
            for lote in lista_lotes:
                if lote.estado == '3':
                    try:
                        venta = Venta.objects.filter(lote_id = lote.id).order_by('-fecha_de_venta')
                        venta = venta[0]
                        cliente = venta.cliente
                        lote.cliente = cliente
                    except Exception, error:
                        lote.cliente = 'Lote de estado "vendido" sin venta asociada'
                        print "El lote vendido no esta asociado a una venta."
                    
    ultima_busqueda = "&tabla=&busqueda="+busqueda+"&tipo_busqueda="+tipo_busqueda+"&busqueda_label="+busqueda_label
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
        'ultima_busqueda': ultima_busqueda,
    })
    return HttpResponse(t.render(c))


   
        
         
    
    
    
    
    