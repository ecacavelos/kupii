from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template import RequestContext, loader
from principal.models import Lote, Fraccion, Manzana, PagoDeCuotas, Venta
from lotes.forms import LoteForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


# Funcion principal del modulo de lotes.
def informes(request):
    
    if request.user.is_authenticated():
        t = loader.get_template('informes/index.html')
        c = RequestContext(request, {})
        return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login") 

def lotes_libres(request):
    
    
    if request.user.is_authenticated():
        t = loader.get_template('informes/lotes_libres.html')
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login") 
    
    object_list = Lote.objects.filter(estado="1").order_by('manzana', 'nro_lote')
    
    total_lotes = object_list.count()
    m=[]
    f=[]
    
    for i in range(0, total_lotes): 
        manzana_id = object_list[i].manzana_id
        m.append(Manzana.objects.get(pk = manzana_id))
        
        #setattr(object_list[i], 'nro_manzana', m.nro_manzana)
        fraccion_id = m[i].fraccion_id
        f.append(Fraccion.objects.get(pk = fraccion_id))
        #setattr(object_list[i], 'fraccion', fraccion_id)
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
        'manzana': m,
        'fraccion': f,
        
    })
    return HttpResponse(t.render(c))

def listar_busqueda_lotes(request):
    
    busqueda = request.POST['busqueda']
    
    if request.user.is_authenticated():
        t = loader.get_template('informes/lotes_libres.html')
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login") 
    
    x=str(busqueda)
    fraccion_int = int(x[0:3])
    manzana_int =int(x[4:7])
    lote_int = int(x[8:])
    myfraccion = Fraccion.objects.filter(id=fraccion_int)
    fraccion_manzanas = Manzana.objects.filter(fraccion=myfraccion)
    for manzana in fraccion_manzanas:
        if manzana.nro_manzana == manzana_int:
            mymanzana = manzana
        
    object_list = Lote.objects.filter(manzana_id=mymanzana.id, nro_lote=lote_int, estado="1")
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
        'manzana': fraccion_manzanas,
        'fraccion': myfraccion,
        
    })
    return HttpResponse(t.render(c))

def listar_clientes_atrasados(request):
    
    venta = request.GET['venta_id']
    cliente = request.GET['cliente_id']    

    if request.user.is_authenticated():
        t = loader.get_template('informes/detalle_pagos_cliente.html')
    else:
        return HttpResponseRedirect("/login") 

    if venta != '' and cliente !='':    
    
        object_list = PagoDeCuotas.objects.filter(venta_id=venta,cliente_id=cliente).order_by('fecha_de_pago' )
        a= len(object_list)
        if a > 0:
            for i in object_list:
                i.fecha_de_pago=i.fecha_de_pago.strftime("%d/%m/%Y")
                i.total_de_cuotas=str('{:,}'.format(i.total_de_cuotas)).replace(",", ".")
                i.total_de_mora=str('{:,}'.format(i.total_de_mora)).replace(",", ".")
                i.total_de_pago=str('{:,}'.format(i.total_de_pago)).replace(",", ".")
            
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
        else:
            return HttpResponseRedirect("/informes/clientes_atrasados")
    else:
        return HttpResponseRedirect("/informes/clientes_atrasados") 



def clientes_atrasados(request):
    
    if request.user.is_authenticated():
        t = loader.get_template('informes/clientes_atrasados.html')
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login") 
    meses = 2
    try:
        
        object_list = Venta.objects.filter(~Q(plan_de_pago = '2'), ).order_by('cliente')
        f = []
        a = len(object_list)
        if a > 0:
            for i in object_list:
                lote = Lote.objects.get(pk=i.lote_id)
                manzana = Manzana.objects.get(pk=lote.manzana_id)
                f.append(Fraccion.objects.get(pk=manzana.fraccion_id))
                i.fecha_de_venta = i.fecha_de_venta.strftime("%d/%m/%Y")
                i.precio_final_de_venta = str('{:,}'.format(i.precio_final_de_venta)).replace(",", ".")
                
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
                'fraccion': f,
            })
            return HttpResponse(t.render(c))       
    except:    
        return HttpResponseServerError("No se pudo obtener el Listado de Clientes Atrasados.")





