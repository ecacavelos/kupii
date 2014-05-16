from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template import RequestContext, loader
from principal.models import Lote, Fraccion, Manzana, PagoDeCuotas, Venta
from lotes.forms import LoteForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from datetime import datetime, timedelta
from calendar import monthrange

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
            c = RequestContext(request, {
                'object_list': object_list,
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/informes/clientes_atrasados") 




def monthdelta(d1, d2):
    delta = 0
    while True:
        mdays = monthrange(d1.year, d1.month)[1]
        d1 += timedelta(days=mdays)
        if d1 <= d2:
            delta += 1
        else:
            break
    return delta

def clientes_atrasados(request):
    
    if request.user.is_authenticated():
        t = loader.get_template('informes/clientes_atrasados.html')
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login")
    
    
    try:
        
        if request.method == 'GET':
            meses_peticion = 0
        else:
            if request.POST['meses_de_atraso'] =='':
                meses_peticion = 0
            else:
                meses_peticion = int(request.POST['meses_de_atraso'])    
        dias = meses_peticion*30
        fecha_actual= datetime.now()
        ventas_a_cuotas = Venta.objects.filter(~Q(plan_de_pago = '2'), fecha_primer_vencimiento__lt=fecha_actual).order_by('cliente')
        object_list=[]
        for v in ventas_a_cuotas:
            fecha_primer_vencimiento = v.fecha_primer_vencimiento
            fecha_primer_vencimiento = datetime.combine(fecha_primer_vencimiento, datetime.min.time())
            #diferencia = monthdelta(fecha_actual, d2)
            fecha_resultante = fecha_actual - fecha_primer_vencimiento
            cuotas_pagadas = v.pagos_realizados
            print ("Id de venta: "+str(v.id))
            print ("Fecha Actual: "+str(fecha_actual))
            print ("Fecha 1er Vencimieto: "+str(fecha_primer_vencimiento))
            print ("Fecha resultante: "+str(fecha_resultante))
            f1 = fecha_actual.date()
            f2 = fecha_primer_vencimiento.date()
            diferencia = (f1-f2).days
            
            #diferencia = fecha_resultante.days()
            print ("Dias de Diferencia: "+str(diferencia))
            meses_diferencia = int (diferencia /30)
            print ("Meses de diferencia: "+str(meses_diferencia))
            print ("Meses de atraso solicitado: "+str(meses_peticion))
            
            if meses_diferencia >= meses_peticion and cuotas_pagadas < ((meses_diferencia+1) - meses_peticion) :
                object_list.append(v)
                print ("Venta agregada")
                print (" ")
            else:
                print ("Venta no agregada")
                print (" ")    
            #print (object_list)
            
        f = []
        a = len(object_list)
        if a > 0:
            for i in object_list:
                lote = Lote.objects.get(pk=i.lote_id)
                manzana = Manzana.objects.get(pk=lote.manzana_id)
                f.append(Fraccion.objects.get(pk=manzana.fraccion_id))
                i.fecha_de_venta = i.fecha_de_venta.strftime("%d/%m/%Y")
                i.fecha_primer_vencimiento = i.fecha_primer_vencimiento.strftime("%d/%m/%Y")
                i.precio_final_de_venta = str('{:,}'.format(i.precio_final_de_venta)).replace(",", ".")
                
            paginator = Paginator(object_list, 15)
            page = request.GET.get('page')
            try:
                lista = paginator.page(page)
            except PageNotAnInteger:
                lista = paginator.page(1)
            except EmptyPage:
                lista = paginator.page(paginator.num_pages)
        else:
            lista=object_list
                
        c = RequestContext(request, {
            'object_list': lista,
            'fraccion': f,
        })
        return HttpResponse(t.render(c))    
           
    except Exception, error:
            print error    
            return HttpResponseServerError("No se pudo obtener el Listado de Clientes Atrasados.")


def informe_general(request):
    
    if request.method=='GET':
        try:
            if request.user.is_authenticated():
                t = loader.get_template('informes/informe_general.html')
                c = RequestContext(request, {
                    'object_list': [],
                })
                return HttpResponse(t.render(c))                
            else:
                return HttpResponseRedirect("/login") 
        except Exception, error:
                print error
    else:
        try:
            if request.user.is_authenticated():
                t = loader.get_template('informes/informe_general.html')                
            else:
                return HttpResponseRedirect("/login") 
    
            fraccion_ini=request.POST['fraccion_ini']
            fraccion_fin=request.POST['fraccion_fin']
        
            fecha_ini=request.POST['fecha_ini']
            fecha_fin=request.POST['fecha_fin']
            fecha_ini_parsed = datetime.strptime(fecha_ini, "%d/%m/%Y").date()
            fecha_fin_parsed = datetime.strptime(fecha_fin, "%d/%m/%Y").date()
        
            try:
                #Obtenemos el lote correspondiente a cada fraccion
                lista_lotes=[]
                object_list=[]
                manzanas_list=Manzana.objects.filter(fraccion_id__gte=fraccion_ini,fraccion_id__lte=fraccion_fin)
                for m in manzanas_list:
                    lotes_list=Lote.objects.filter(manzana_id=m.id)
                    for l in lotes_list:
                        lista_lotes.append(l)
                
                #for lote in lista_lotes:
                for lote in lista_lotes:
                    lista_pagos=PagoDeCuotas.objects.filter(lote_id=lote.id,fecha_de_pago__range=(fecha_ini_parsed,fecha_fin_parsed))
                    for p in lista_pagos:
                        object_list.append(p)
                                
                     
                #object_list =lista.objects.filter(fecha_de_pago___range=(fecha_ini_parsed,fecha_fin_parsed))
                                
            except Exception, error:
                print error
            a = len(object_list)
            f=[]
            if a>0:
                monto_total_cobrado=0
                try:
                    for i in object_list:
                        i.fecha_de_pago=i.fecha_de_pago.strftime("%d/%m/%Y")
                        i.total_de_cuotas=str('{:,}'.format(i.total_de_cuotas)).replace(",", ".")
                        i.total_de_mora=str('{:,}'.format(i.total_de_mora)).replace(",", ".")
                        i.total_de_pago=str('{:,}'.format(i.total_de_pago)).replace(",", ".")
                        #monto_total_cobrado+=i.total_de_pago
                        
                
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
                except Exception, error:
                    print error
        except:   
            return HttpResponseServerError("No se pudo obtener el Listado de Pagos de Lotes.")

   


            

    