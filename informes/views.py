# -*- encoding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template import RequestContext, loader
from principal.models import Propietario, Fraccion, Lote, Manzana, PagoDeCuotas, Venta, Reserva, CambioDeLotes, RecuperacionDeLotes, TransferenciaDeLotes 
from operator import itemgetter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from datetime import datetime, timedelta
from calendar import monthrange
from principal.common_functions import get_nro_cuota
from django.utils import simplejson
from django.db import connection
import xlwt
import math

# Funcion principal del modulo de lotes.
def informes(request):
    
    if request.user.is_authenticated():
        t = loader.get_template('informes/index.html')
        c = RequestContext(request, {})
        return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login") 

def lotes_libres(request): 
    if request.method == 'GET':
        if request.user.is_authenticated():
            if (filtros_establecidos(request.GET,'lotes_libres') == False):
                t = loader.get_template('informes/lotes_libres.html')
                c = RequestContext(request, {
                    'object_list': [],
                })
                return HttpResponse(t.render(c))
            else: #Parametros seteados
                tipo_busqueda=request.GET['tipo_busqueda']
                t = loader.get_template('informes/lotes_libres.html')
                if(tipo_busqueda=='codigo'):
                    fraccion_ini=request.GET['fraccion_ini']
                    fraccion_fin=request.GET['fraccion_fin']
                    f1=""
                    f2=""
                    ultimo="&tipo_busqueda="+tipo_busqueda+"&fraccion_ini="+fraccion_ini+"&frac1="+f1+"&fraccion_fin="+fraccion_fin+"&frac2="+f2               
                if(tipo_busqueda=='nombre'):
                    fraccion_ini=request.GET['frac1']
                    fraccion_fin=request.GET['frac2']
                    f1=request.GET['fraccion_ini']
                    f2=request.GET['fraccion_fin']
                    ultimo="&tipo_busqueda="+tipo_busqueda+"&fraccion_ini="+f1+"&frac1="+fraccion_ini+"&fraccion_fin="+f2+"&frac2="+fraccion_fin
                object_list=[]#lista de lotes
                if fraccion_ini and fraccion_fin:
                    manzanas= Manzana.objects.filter(fraccion_id__range=(fraccion_ini,fraccion_fin))
                    for m in manzanas:
                        lotes = Lote.objects.filter(manzana=m.id)
                        for l in lotes:
                            object_list.append(l)                                         
                else:       
                    object_list = Lote.objects.filter(estado="1").order_by('manzana', 'nro_lote')
                 
                lotes=[]
                total_importe_cuotas = 0
                total_contado_fraccion = 0
                total_credito_fraccion = 0
                total_superficie_fraccion = 0
                total_lotes = 0
                for index, lote_item in enumerate(object_list):
                    lote={}
                # Se setean los datos de cada fila 
                    precio_cuota=int(math.ceil(lote_item.precio_credito/130))
                    lote['fraccion_id']=str(lote_item.manzana.fraccion.id)
                    lote['fraccion']=str(lote_item.manzana.fraccion)
                    lote['lote']=str(lote_item.manzana).zfill(3) + "/" + str(lote_item.nro_lote).zfill(4)
                    lote['superficie']=lote_item.superficie                                    
                    lote['precio_contado']=str('{:,}'.format(lote_item.precio_contado)).replace(",", ".")                    
                    lote['precio_credito']=str('{:,}'.format(lote_item.precio_credito)).replace(",", ".")                    
                    lote['importe_cuota']=str('{:,}'.format(precio_cuota)).replace(",", ".")
                # Se suman los TOTALES por FRACCION
                    total_superficie_fraccion += lote_item.superficie 
                    total_contado_fraccion += lote_item.precio_contado
                    total_credito_fraccion += lote_item.precio_credito
                    total_importe_cuotas += precio_cuota
                    total_lotes += 1
                #Es el ultimo lote, cerrar totales de fraccion
                    if (len(object_list)-1 == index):
                        lote['total_importe_cuotas'] = str('{:,}'.format(total_importe_cuotas)).replace(",", ".") 
                        lote['total_credito_fraccion'] =  str('{:,}'.format(total_credito_fraccion)).replace(",", ".")
                        lote['total_contado_fraccion'] =  str('{:,}'.format(total_contado_fraccion)).replace(",", ".")
                        lote['total_superficie_fraccion'] =  str('{:,}'.format(total_superficie_fraccion)).replace(",", ".")
                        lote['total_lotes'] =  str('{:,}'.format(total_lotes)).replace(",", ".")
                #Hay cambio de lote pero NO es el ultimo elemento todavia
                    elif (lote_item.manzana.fraccion.id != object_list[index+1].manzana.fraccion.id):
                        lote['total_importe_cuotas'] = str('{:,}'.format(total_importe_cuotas)).replace(",", ".") 
                        lote['total_credito_fraccion'] =  str('{:,}'.format(total_credito_fraccion)).replace(",", ".")
                        lote['total_contado_fraccion'] =  str('{:,}'.format(total_contado_fraccion)).replace(",", ".")
                        lote['total_superficie_fraccion'] =  str('{:,}'.format(total_superficie_fraccion)).replace(",", ".")
                        lote['total_lotes'] =  str('{:,}'.format(total_lotes)).replace(",", ".")
                    # Se CERAN  los TOTALES por FRACCION
                        total_importe_cuotas = 0
                        total_contado_fraccion = 0
                        total_credito_fraccion = 0
                        total_superficie_fraccion = 0
                        total_lotes = 0
                    lotes.append(lote)
                
                paginator = Paginator(lotes, 25)
                page = request.GET.get('page')
                try:
                    lista = paginator.page(page)
                except PageNotAnInteger:
                    lista = paginator.page(1)
                except EmptyPage:
                    lista = paginator.page(paginator.num_pages)                
                c = RequestContext(request, {
                    'tipo_busqueda' : tipo_busqueda,
                    'fraccion_ini': fraccion_ini,
                    'fraccion_fin': fraccion_fin,
                    'ultimo': ultimo,
                    'lista_lotes': lista,
                    'frac1' : f1,
                    'frac2' : f2
                })
                return HttpResponse(t.render(c))                
        else:
            return HttpResponseRedirect("/login") 
    
    else:
        c = RequestContext(request, {
            # 'object_list': lista,
            # 'fraccion': f,
        })
        return HttpResponse(t.render(c))    

def listar_busqueda_lotes(request):
    
    if request.user.is_authenticated():
        t = loader.get_template('informes/lotes_libres.html')
    else:
        return HttpResponseRedirect("/login") 
    
    busqueda = request.POST['busqueda']
    if busqueda:
        x = str(busqueda)
        fraccion_int = int(x[0:3])
        manzana_int = int(x[4:7])
        lote_int = int(x[8:])
        manzana = Manzana.objects.get(fraccion_id=fraccion_int, nro_manzana=manzana_int)
        lote = Lote.objects.get(manzana=manzana.id, nro_lote=lote_int)
        object_list = Lote.objects.filter(pk=lote.id, estado="1").order_by('manzana', 'nro_lote')
    
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

def listar_clientes_atrasados(request):
    
    venta = request.GET['venta_id']
    cliente = request.GET['cliente_id']    

    if request.user.is_authenticated():
        t = loader.get_template('informes/detalle_pagos_cliente.html')
    else:
        return HttpResponseRedirect("/login") 

    if venta != '' and cliente != '':    
    
        object_list = PagoDeCuotas.objects.filter(venta_id=venta, cliente_id=cliente).order_by('fecha_de_pago')
        a = len(object_list)
        if a > 0:
            for i in object_list:
                i.fecha_de_pago = i.fecha_de_pago.strftime("%d/%m/%Y")
                i.total_de_cuotas = str('{:,}'.format(i.total_de_cuotas)).replace(",", ".")
                i.total_de_mora = str('{:,}'.format(i.total_de_mora)).replace(",", ".")
                i.total_de_pago = str('{:,}'.format(i.total_de_pago)).replace(",", ".")
            
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
    if request.method == 'GET':
        if request.user.is_authenticated():
            t = loader.get_template('informes/clientes_atrasados.html')
            fecha_actual= datetime.now()            
            filtros = filtros_establecidos(request.GET,'clientes_atrasados')
            cliente_atrasado= {}
            clientes_atrasados= []
            meses_peticion = 0
            fraccion =''
            query = (
            '''
            SELECT pm.nro_manzana manzana, pl.nro_lote lote, pc.nombres || ' ' || apellidos cliente, (pp.cantidad_de_cuotas - pv.pagos_realizados) cuotas_atrasadas,
            pv.pagos_realizados cuotas_pagadas, pv.precio_de_cuota importe_cuota, (pp.cantidad_de_cuotas - pv.pagos_realizados) * pv.precio_de_cuota total_atrasado,
            (pv.pagos_realizados * pv.precio_de_cuota) total_pagado, pp.cantidad_de_cuotas * pv.precio_de_cuota valor_total_lote,
            (pv.pagos_realizados*100/pp.cantidad_de_cuotas) porc_pagado
            FROM principal_lote pl, principal_cliente pc, principal_venta pv, principal_manzana pm, principal_plandepago pp  
            WHERE pv.plan_de_pago_id = pp.id AND pv.lote_id = pl.id AND pv.cliente_id = pc.id
            AND (pp.cantidad_de_cuotas - pv.pagos_realizados) > 0 AND pl.manzana_id = pm.id AND pp.tipo_de_plan='credito'
            '''
            )      
            if filtros == 0:
                meses_peticion = 0
                c = RequestContext(request, {
                    'object_list': [],
                })
                return HttpResponse(t.render(c))            
            elif filtros == 1:
                fraccion = request.GET['fraccion']
                query += "AND  pm.fraccion_id =  %s"
                cursor = connection.cursor()
                cursor.execute(query, [fraccion])              
            elif filtros == 2:
                meses_peticion = int(request.GET['meses_atraso'])
                query += "AND (pp.cantidad_de_cuotas - pv.pagos_realizados) = %s"
                cursor = connection.cursor()
                cursor.execute(query, [meses_peticion])  
            else:
                fraccion = request['fraccion']
                meses_peticion = int(request.GET['meses_atraso'])
                query += "AND pm.fraccion_id =  %s"
                cursor = connection.cursor()
                cursor.execute(query, [fraccion]) 
            
            try:
                dias = meses_peticion*30
                results= cursor.fetchall()
                desc = cursor.description
                for r in results:
                    i = 0
                    cliente_atrasado = {}
                    while i < len(desc):
                        cliente_atrasado[desc[i][0]] = r[i]
                        i = i+1
                    try:
                        ultimo_pago = PagoDeCuotas.objects.filter(lote__nro_lote= cliente_atrasado['lote']).order_by('-fecha_de_pago')[:1].get()
                    except PagoDeCuotas.DoesNotExist:
                        ultimo_pago = None
                        
                    if ultimo_pago != None:
                        fecha_ultimo_pago = ultimo_pago.fecha_de_pago
                    
                    cliente_atrasado['fecha_ultimo_pago']= fecha_ultimo_pago
                    
                    
                    f1 = fecha_actual.date()
                    f2 = fecha_ultimo_pago
                    diferencia = (f1-f2).days
                    meses_diferencia =  int(diferencia /30)
                    #En el caso de que las cuotas que debe son menores a la diferencia de meses de la fecha de ultimo pago y la actual
                    if meses_diferencia > cliente_atrasado['cuotas_atrasadas']:
                        meses_diferencia = cliente_atrasado['cuotas_atrasadas']
                        
                    if meses_diferencia >= meses_peticion:
                        cliente_atrasado['cuotas_atrasadas'] = meses_diferencia                           
                        clientes_atrasados.append(cliente_atrasado)                  
                        print ("Venta agregada")
                        print (" ")
                    else:
                        print ("Venta no agregada")
                        print (" ")
                if meses_peticion == 0:
                    meses_peticion =''  
                a = len(clientes_atrasados)
                if a > 0:                    
                    ultimo="&fraccion="+str(fraccion)+"&meses_atraso="+str(meses_peticion)
                    paginator = Paginator(clientes_atrasados, 25)
                    page = request.GET.get('page')
                    try:
                        lista = paginator.page(page)
                    except PageNotAnInteger:
                        lista = paginator.page(1)
                    except EmptyPage:
                        lista = paginator.page(paginator.num_pages)                
                    c = RequestContext(request, {
                        'fraccion': fraccion,                        
                        'meses_atraso': meses_peticion,
                        'ultimo': ultimo,
                        'object_list': lista,
                        'clientes_atrasados' : clientes_atrasados                        
                    })                     
                    return HttpResponse(t.render(c))
                else:
                    ultimo="&fraccion="+str(fraccion)+"&meses_atraso="+str(meses_peticion)
                    c = RequestContext(request, {
                        'fraccion': fraccion,                        
                        'meses_atraso': meses_peticion,
                        'ultimo': ultimo,
                        'object_list': clientes_atrasados                       
                    })
                    return HttpResponse(t.render(c))                 
            except Exception, error:
                print error    
                return HttpResponseServerError("No se pudo obtener el Listado de Clientes Atrasados.")
        else:
            return HttpResponseRedirect("/login")
        
       

def informe_general(request):    
    if request.method == 'GET':
        if request.user.is_authenticated():
            if (filtros_establecidos(request.GET,'informe_general') == False):
                t = loader.get_template('informes/informe_general.html')
                c = RequestContext(request, {
                    'object_list': [],
                })
                return HttpResponse(t.render(c))
            else: #Parametros seteados
                t = loader.get_template('informes/informe_general.html')
                tipo_busqueda=request.GET['tipo_busqueda']
                fecha_ini=request.GET['fecha_ini']
                fecha_fin=request.GET['fecha_fin']
                if(tipo_busqueda=='codigo'):
                    fraccion_ini=request.GET['fraccion_ini']
                    fraccion_fin=request.GET['fraccion_fin']
                    f1=""
                    f2=""
                    ultimo="&tipo_busqueda="+tipo_busqueda+"&fraccion_ini="+fraccion_ini+"&frac1="+f1+"&fraccion_fin="+fraccion_fin+"&frac2="+f2+"&fecha_ini="+fecha_ini+"&fecha_fin="+fecha_fin                              
                if(tipo_busqueda=='nombre'):
                    fraccion_ini=request.GET['frac1']
                    fraccion_fin=request.GET['frac2']
                    f1=request.GET['fraccion_ini']
                    f2=request.GET['fraccion_fin']
                    ultimo="&tipo_busqueda="+tipo_busqueda+"&fraccion_ini="+f1+"&frac1="+fraccion_ini+"&fraccion_fin="+f2+"&frac2="+fraccion_fin+"&fecha_ini="+fecha_ini+"&fecha_fin="+fecha_fin
                if fecha_ini == '' and fecha_fin == '':
                    query=(
                    '''
                    select pc.* from principal_pagodecuotas pc, principal_lote l, principal_manzana m, principal_fraccion f
                    where f.id>=''' + fraccion_ini +
                    '''
                    and f.id<=''' + fraccion_fin +
                    '''
                    and (pc.lote_id = l.id and l.manzana_id=m.id and m.fraccion_id=f.id) order by f.id
                    '''
                    )
                else:
                    fecha_ini_parsed = datetime.strptime(fecha_ini, "%d/%m/%Y").date()
                    fecha_fin_parsed = datetime.strptime(fecha_fin, "%d/%m/%Y").date()
                    query=(
                    '''
                    select pc.* from principal_pagodecuotas pc, principal_lote l, principal_manzana m, principal_fraccion f
                    where pc.fecha_de_pago >= \''''+ str(fecha_ini_parsed) +               
                    '''\' and pc.fecha_de_pago <= \'''' + str(fecha_fin_parsed) +
                    '''\' and f.id>=''' + fraccion_ini +
                    '''
                    and f.id<=''' + fraccion_fin +
                    '''
                    and (pc.lote_id = l.id and l.manzana_id=m.id and m.fraccion_id=f.id) order by f.id,pc.fecha_de_pago
                    '''
                    )
                
                object_list=list(PagoDeCuotas.objects.raw(query))
 
                cuotas=[]
                total_cuotas=0
                total_mora=0
                total_pagos=0
                for i, cuota_item in enumerate(object_list):
                    #Se setean los datos de cada fila
                    cuota={}
                    nro_cuota=get_nro_cuota(cuota_item)
                    cuota['fraccion_id']=str(cuota_item.lote.manzana.fraccion.id)
                    cuota['fraccion']=str(cuota_item.lote.manzana.fraccion)
                    cuota['lote']=str(cuota_item.lote)
                    cuota['cliente']=str(cuota_item.cliente)
                    cuota['cuota_nro']=str(nro_cuota)+'/'+str(cuota_item.plan_de_pago.cantidad_de_cuotas)
                    cuota['plan_de_pago']=cuota_item.plan_de_pago.nombre_del_plan
                    cuota['fecha_pago']=str(cuota_item.fecha_de_pago)
                    cuota['total_de_cuotas']=str('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".") 
                    cuota['total_de_mora']=str('{:,}'.format(cuota_item.total_de_mora)).replace(",", ".")
                    cuota['total_de_pago']=str('{:,}'.format(cuota_item.total_de_pago)).replace(",", ".")

                    #Se suman los totales por fraccion
                    total_cuotas+=cuota_item.total_de_cuotas
                    total_mora+=cuota_item.total_de_mora
                    total_pagos+=cuota_item.total_de_pago
                    
                    #Es el ultimo lote, cerramos los totales de fraccion
                    if (len(object_list)-1 == i):
                        cuota['total_cuotas']=str('{:,}'.format(total_cuotas)).replace(",", ".") 
                        cuota['total_mora']=str('{:,}'.format(total_mora)).replace(",", ".")
                        cuota['total_pago']=str('{:,}'.format(total_pagos)).replace(",", ".")
                        
                    #Hay cambio de lote pero NO es el ultimo elemento todavia
                    elif (cuota_item.lote.manzana.fraccion.id != object_list[i+1].lote.manzana.fraccion.id):
                        cuota['total_cuotas']=str('{:,}'.format(total_cuotas)).replace(",", ".") 
                        cuota['total_mora']=str('{:,}'.format(total_mora)).replace(",", ".")
                        cuota['total_pago']=str('{:,}'.format(total_pagos)).replace(",", ".")
                    
                    #Se CERAN  los TOTALES por FRACCION
                        total_cuotas=0
                        total_mora=0
                        total_pagos=0
                    
                    cuotas.append(cuota)                
                
                
                paginator = Paginator(cuotas, 25)
                page = request.GET.get('page')
                try:
                    lista = paginator.page(page)
                except PageNotAnInteger:
                    lista = paginator.page(1)
                except EmptyPage:
                    lista = paginator.page(paginator.num_pages) 
                c = RequestContext(request, {
                    'tipo_busqueda' : tipo_busqueda,
                    'fraccion_ini': fraccion_ini,
                    'fraccion_fin': fraccion_fin,
                    'fecha_ini': fecha_ini,
                    'fecha_fin': fecha_fin,
                    'lista_cuotas': lista,
                    'ultimo': ultimo,
                    'frac1' : f1,
                    'frac2' : f2
                })
                return HttpResponse(t.render(c))                
        else:
            return HttpResponseRedirect("/login")
         
def liquidacion_propietarios(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if (filtros_establecidos(request.GET,'liquidacion_propietarios') == False):
                t = loader.get_template('informes/liquidacion_propietarios.html')                
                c = RequestContext(request, {
                    'object_list': [],
                })
                return HttpResponse(t.render(c))
            else: # Parametros SETEADOS
                t = loader.get_template('informes/liquidacion_propietarios.html')   
                try:             
                    fecha_ini = request.GET['fecha_ini']
                    fecha_fin = request.GET['fecha_fin']
                    fecha_ini_parsed = datetime.strptime(fecha_ini, "%d/%m/%Y").date()
                    fecha_fin_parsed = datetime.strptime(fecha_fin, "%d/%m/%Y").date()
                    tipo_busqueda = request.GET['tipo_busqueda']
                    filas = []
                    lista_pagos = []
                    lista_totales = []
                    lotes = []
                    #Totales por FRACCION
                    total_monto_pagado = 0
                    total_monto_inm = 0
                    total_monto_prop = 0
                    
                    #Totales GENERALES
                    total_general_pagado = 0
                    total_general_inm = 0
                    total_general_prop = 0
                    
                    monto_inmobiliaria = 0
                    monto_propietario = 0
                    busqueda = request.GET['busqueda']
                    busqueda_label = request.GET['busqueda_label']                    
                    if tipo_busqueda == "fraccion":
                        try:
                            fraccion_id = request.GET['busqueda']
                            fraccion = Fraccion.objects.get(pk=fraccion_id)                 
                            print('Fraccion: ' + fraccion.nombre + '\n')
                            manzana_list = Manzana.objects.filter(fraccion_id=fraccion_id).order_by('id')                
                            for m in manzana_list:
                                lotes_list = Lote.objects.filter(manzana_id=m.id).order_by('id')
                                for l in lotes_list:
                                    pagos = PagoDeCuotas.objects.filter(lote_id=l.id , fecha_de_pago__range=[fecha_ini_parsed, fecha_fin_parsed]).order_by('fecha_de_pago')
                                    if pagos:
                                        for pago in pagos:
                                            lista_pagos.append(pago)
                            lista_pagos.sort(key=lambda x:x.fecha_de_pago)
                        except Exception, error:
                            print error                      
                        try:
                            for i, pago in enumerate(lista_pagos):                        
                                #print pago.id
                                nro_cuota = get_nro_cuota(pago)
                                cuotas_para_propietario=((pago.plan_de_pago.cantidad_cuotas_inmobiliaria)*(pago.plan_de_pago.intervalos_cuotas_inmobiliaria))-pago.plan_de_pago.inicio_cuotas_inmobiliaria
                                if(nro_cuota<=cuotas_para_propietario): 
                                    if(nro_cuota % 2 != 0):    
                                        monto_inmobiliaria = pago.total_de_cuotas
                                        monto_propietario = 0
                                    else:
                                        monto_inmobiliaria = int(pago.total_de_cuotas * (float(pago.plan_de_pago.porcentaje_cuotas_inmobiliaria) / float(100)))
                                        monto_propietario = pago.total_de_cuotas - monto_inmobiliaria
                                else:
                                    monto_inmobiliaria = int(pago.total_de_cuotas * (float(pago.plan_de_pago.porcentaje_cuotas_inmobiliaria) / float(100)))
                                    monto_propietario = pago.total_de_cuotas - monto_inmobiliaria
                                    
                                fila={}
                                total_monto_inm += monto_inmobiliaria
                                total_monto_prop += monto_propietario
                                total_monto_pagado += pago.total_de_cuotas
                                fila['fraccion']=str(pago.lote.manzana.fraccion)
                                fila['fecha_de_pago']=str(pago.fecha_de_pago)
                                fila['lote']=str(pago.lote)
                                fila['cliente']=str(pago.cliente)
                                fila['nro_cuota']=str(nro_cuota) + '/' + str(pago.plan_de_pago.cantidad_de_cuotas)
                                fila['total_de_cuotas']=str('{:,}'.format(pago.total_de_cuotas)).replace(",", ".")
                                fila['monto_inmobiliaria']=str('{:,}'.format(monto_inmobiliaria)).replace(",", ".")
                                fila['monto_propietario']=str('{:,}'.format(monto_propietario)).replace(",", ".")
                                
                                total_general_pagado += pago.total_de_cuotas
                                total_general_inm += monto_inmobiliaria
                                total_general_prop += monto_propietario
                                filas.append(fila)
                            fila['total_general_pagado']=str('{:,}'.format(total_general_pagado)).replace(",", ".")
                            fila['total_general_inmobiliaria']=str('{:,}'.format(total_general_inm)).replace(",", ".")
                            fila['total_general_propietario']=str('{:,}'.format(total_general_prop)).replace(",", ".")
                        except Exception, error:
                            print error                    
                                                                                       
                    else:
                        try:
                            propietario_id = request.GET['busqueda']
                            fracciones = Fraccion.objects.filter(propietario_id=propietario_id).order_by('id')
                            for f in fracciones:
                                manzanas = Manzana.objects.filter(fraccion_id=f.id)
                                for m in manzanas:
                                    lotes = Lote.objects.filter(manzana_id=m.id)
                                    for l in lotes:
                                        pagos = PagoDeCuotas.objects.filter(lote_id=l.id , fecha_de_pago__range=[fecha_ini_parsed, fecha_fin_parsed])
                                        if pagos:
                                            for pago in pagos:                                                                                                
                                                lista_pagos.append(pago)
                                                #lista_pagos.sort(key=lambda x:x.fecha_de_pago) 
                                                #print lista_pagos[0].as_json()                         
                        except Exception, error:
                            print error
                        for i, pago in enumerate(lista_pagos):
                            print pago.id
                            nro_cuota = get_nro_cuota(pago)
                            cuotas_para_propietario=((pago.plan_de_pago.cantidad_cuotas_inmobiliaria)*(pago.plan_de_pago.intervalos_cuotas_inmobiliaria))-pago.plan_de_pago.inicio_cuotas_inmobiliaria
                            if(nro_cuota<=cuotas_para_propietario): 
                                if(nro_cuota % 2 != 0):    
                                    monto_inmobiliaria = pago.total_de_cuotas
                                    monto_propietario = 0
                                else:
                                    monto_inmobiliaria = int(pago.total_de_cuotas * (float(pago.plan_de_pago.porcentaje_cuotas_inmobiliaria) / float(100)))
                                    monto_propietario = pago.total_de_cuotas - monto_inmobiliaria
                            else:
                                monto_inmobiliaria = int(pago.total_de_cuotas * (float(pago.plan_de_pago.porcentaje_cuotas_inmobiliaria) / float(100)))
                                monto_propietario = pago.total_de_cuotas - monto_inmobiliaria

                            # Se setean los datos de cada fila
                            fila={}
                            fila['fraccion']=str(pago.lote.manzana.fraccion)
                            fila['fecha_de_pago']=str(pago.fecha_de_pago)
                            fila['lote']=str(pago.lote)
                            fila['cliente']=str(pago.cliente)
                            fila['nro_cuota']=str(nro_cuota) + '/' + str(pago.plan_de_pago.cantidad_de_cuotas)
                            fila['total_de_cuotas']=str('{:,}'.format(pago.total_de_cuotas)).replace(",", ".")
                            fila['monto_inmobiliaria']=str('{:,}'.format(monto_inmobiliaria)).replace(",", ".")
                            fila['monto_propietario']=str('{:,}'.format(monto_propietario)).replace(",", ".")
                            
                            # Se suman los TOTALES por FRACCION
                            total_monto_inm += monto_inmobiliaria
                            total_monto_prop += monto_propietario
                            total_monto_pagado += pago.total_de_cuotas
                                
                            #Es el ultimo lote, cerrar totales de fraccion
                            if (len(lista_pagos)-1 == i):                                
                                #Totales por FRACCION
                                fila['total_monto_pagado']=str('{:,}'.format(total_monto_pagado)).replace(",", ".")
                                fila['total_monto_inmobiliaria']=str('{:,}'.format(total_monto_inm)).replace(",", ".")
                                fila['total_monto_propietario']=str('{:,}'.format(total_monto_prop)).replace(",", ".")
                                
                                #Totales GENERALES
                                fila['total_general_pagado']=str('{:,}'.format(total_general_pagado)).replace(",", ".")
                                fila['total_general_inmobiliaria']=str('{:,}'.format(total_general_inm)).replace(",", ".")
                                fila['total_general_propietario']=str('{:,}'.format(total_general_prop)).replace(",", ".")
                                
                            #Hay cambio de lote pero NO es el ultimo elemento todavia
                            elif (pago.lote.manzana.fraccion.id != lista_pagos[i+1].lote.manzana.fraccion.id):
                                #Totales por FRACCION
                                fila['total_monto_pagado']=str('{:,}'.format(total_monto_pagado)).replace(",", ".")
                                fila['total_monto_inmobiliaria']=str('{:,}'.format(total_monto_inm)).replace(",", ".")
                                fila['total_monto_propietario']=str('{:,}'.format(total_monto_prop)).replace(",", ".")
                                
                                # Se CERAN  los TOTALES por FRACCION
                                total_monto_pagado = 0
                                total_monto_inm = 0
                                total_monto_prop = 0
                            
                            #Acumulamos para los TOTALES GENERALES
                            total_general_pagado += pago.total_de_cuotas
                            total_general_inm += monto_inmobiliaria
                            total_general_prop += monto_propietario
                            filas.append(fila)
                    ultimo="&tipo_busqueda="+tipo_busqueda+"&busqueda="+busqueda+"&busqueda_label="+busqueda_label+"&fecha_ini="+fecha_ini+"&fecha_fin="+fecha_fin
                    paginator = Paginator(filas, 25)
                    page = request.GET.get('page')
                    try:
                        lista = paginator.page(page)
                    except PageNotAnInteger:
                        lista = paginator.page(1)
                    except EmptyPage:
                        lista = paginator.page(paginator.num_pages)          
                    c = RequestContext(request, {
                        'object_list': lista,
                        'lista_totales' : lista_totales,
                        'fecha_ini':fecha_ini,
                        'fecha_fin':fecha_fin,
                        'tipo_busqueda':tipo_busqueda,
                        'busqueda':busqueda,
                        'busqueda_label':busqueda_label,
                        'ultimo': ultimo
                    })
                    return HttpResponse(t.render(c))    
                except Exception, error:
                    print error                                 
        else:
            return HttpResponseRedirect("/login")

def liquidacion_vendedores(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if (filtros_establecidos(request.GET,'liquidacion_vendedores') == False):                
                t = loader.get_template('informes/liquidacion_vendedores.html')
                c = RequestContext(request, {
                   'object_list': [],
                })
                return HttpResponse(t.render(c))                
            else:#Parametros seteados
                t = loader.get_template('informes/liquidacion_vendedores.html')
                fecha_ini = request.GET['fecha_ini']
                fecha_fin = request.GET['fecha_fin']
                fecha_ini_parsed = str(datetime.strptime(fecha_ini, "%d/%m/%Y").date())
                fecha_fin_parsed = str(datetime.strptime(fecha_fin, "%d/%m/%Y").date())
                busqueda_label = request.GET['busqueda_label']
                vendedor_id=request.GET['busqueda']
                print("vendedor_id ->" + vendedor_id)
                
                query=(
                '''
                select pc.* from principal_pagodecuotas pc, principal_lote l, principal_manzana m, principal_fraccion f
                where pc.fecha_de_pago >= \''''+ fecha_ini_parsed +               
                '''\' and pc.fecha_de_pago <= \'''' + fecha_fin_parsed +
                '''\' and pc.vendedor_id=''' + vendedor_id +                
                ''' 
                and (pc.lote_id = l.id and l.manzana_id=m.id and m.fraccion_id=f.id) order by f.id,pc.fecha_de_pago
                '''
                )                    
                    
                object_list=list(PagoDeCuotas.objects.raw(query))
                cuotas=[]
                #totales por fraccion
                total_importe=0
                total_comision=0
                #totales generales
                total_general_importe=0
                total_general_comision=0
                k=0 #variable de control
                #Seteamos los datos de las filas
                for i, cuota_item in enumerate (object_list):                
                    nro_cuota=get_nro_cuota(cuota_item)
                    cuota={}
                    com=0        
                    #Esta es una regla de negocio, los vendedores cobran comisiones segun el numero de cuota, maximo hasta la cuota Nro 9.
                    cuotas_para_vendedor=((cuota_item.plan_de_pago_vendedores.cantidad_cuotas)*(cuota_item.plan_de_pago_vendedores.intervalos))-cuota_item.plan_de_pago_vendedores.cuota_inicial                  
                    #A los vendedores le corresponde comision por las primeras 4 (maximo 5) cuotas impares.
                    if(nro_cuota%2!=0 and nro_cuota<=cuotas_para_vendedor):                                                                        
                        if k==0:
                            #Guardamos la primera fraccion que cumple con la condicion, para tener algo con que comparar.
                            fraccion_actual=cuota_item.lote.manzana.fraccion.id
                        k+=1
                        print k
                        if(cuota_item.lote.manzana.fraccion.id==fraccion_actual):                              
                            com=int(cuota_item.total_de_cuotas*(float(cuota_item.plan_de_pago_vendedores.porcentaje_de_cuotas)/float(100)))
                            cuota['fraccion']=str(cuota_item.lote.manzana.fraccion)
                            cuota['cliente']=str(cuota_item.cliente)
                            cuota['fraccion_id']=cuota_item.lote.manzana.fraccion.id
                            cuota['lote']=str(cuota_item.lote)
                            cuota['cuota_nro']=str(nro_cuota)+'/'+str(cuota_item.plan_de_pago.cantidad_de_cuotas)
                            cuota['fecha_pago']=str(cuota_item.fecha_de_pago)
                            cuota['importe']=str('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".") 
                            cuota['comision']=str('{:,}'.format(com)).replace(",", ".") 
    
                            #Sumamos los totales por fraccion
                            total_importe+=cuota_item.total_de_cuotas
                            total_comision+=com
                            print cuota_item  
                            #Guardamos el ultimo lote que cumple la condicion en dos variables, por si se covnierta en el ultimo lote para cerrar la fraccion
                            #actual, o por si sea el ultimo lote de la lista.
                            anterior=cuota                            
                            ultimo=cuota                       
                        #Hay cambio de lote pero NO es el ultimo elemento todavia
                        else:
                            anterior['total_importe']=str('{:,}'.format(total_importe)).replace(",", ".")
                            anterior['total_comision']=str('{:,}'.format(total_comision)).replace(",", ".")
                            #Se CERAN  los TOTALES por FRACCION                            
                            total_importe=0
                            total_comision=0                                                                                
                            com=int(cuota_item.total_de_cuotas*(float(cuota_item.plan_de_pago_vendedores.porcentaje_de_cuotas)/float(100)))
                            cuota['fraccion']=str(cuota_item.lote.manzana.fraccion)
                            cuota['cliente']=str(cuota_item.cliente)
                            cuota['fraccion_id']=cuota_item.lote.manzana.fraccion.id
                            cuota['lote']=str(cuota_item.lote)
                            cuota['cuota_nro']=str(nro_cuota)+'/'+str(cuota_item.plan_de_pago.cantidad_de_cuotas)
                            cuota['fecha_pago']=str(cuota_item.fecha_de_pago)
                            cuota['importe']=str('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".") 
                            cuota['comision']=str('{:,}'.format(com)).replace(",", ".") 
                            #Sumamos los totales por fraccion
                            total_importe+=cuota_item.total_de_cuotas
                            total_comision+=com 
                            fraccion_actual=cuota_item.lote.manzana.fraccion.id
                            ultimo=cuota
                        total_general_importe+=cuota_item.total_de_cuotas
                        total_general_comision+=com
                        cuotas.append(cuota)                        
                    #Si es el ultimo lote, cerramos totales de fraccion
                    if (len(object_list)-1 == i):
                        try:
                            ultimo['total_importe']=str('{:,}'.format(total_importe)).replace(",", ".") 
                            ultimo['total_comision']=str('{:,}'.format(total_comision)).replace(",", ".")             
                            ultimo['total_general_importe']=str('{:,}'.format(total_general_importe)).replace(",", ".") 
                            ultimo['total_general_comision']=str('{:,}'.format(total_general_comision)).replace(",", ".")          
                        except:
                            pass
            ultimo="&busqueda_label="+busqueda_label+"&busqueda="+vendedor_id+"&fecha_ini="+fecha_ini+"&fecha_fin="+fecha_fin         
            paginator = Paginator(cuotas, 25)
            page = request.GET.get('page')
            try:
                lista = paginator.page(page)
            except PageNotAnInteger:
                lista = paginator.page(1)
            except EmptyPage:
                lista = paginator.page(paginator.num_pages) 
            c = RequestContext(request, {
                'lista_cuotas': lista,
                'fecha_ini':fecha_ini,
                'fecha_fin':fecha_fin,
                'busqueda':vendedor_id,
                'busqueda_label':busqueda_label,
                'ultimo': ultimo
            })
            return HttpResponse(t.render(c))    
        else:    
            return HttpResponseRedirect("/login") 
def liquidacion_gerentes(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if (filtros_establecidos(request.GET,'liquidacion_gerentes') == False):                
                t = loader.get_template('informes/liquidacion_gerentes.html')
                c = RequestContext(request, {
                   'object_list': [],
                })
                return HttpResponse(t.render(c))                
            else:#Parametros seteados
                t = loader.get_template('informes/liquidacion_gerentes.html')
                fecha_ini=request.GET['fecha_ini']
                fecha_fin=request.GET['fecha_fin']
                fecha_ini_parsed = str(datetime.strptime(fecha_ini, "%d/%m/%Y").date())
                fecha_fin_parsed = str(datetime.strptime(fecha_fin, "%d/%m/%Y").date())
                fraccion_id=request.GET['busqueda']
                busqueda_label = request.GET['busqueda_label']
                print("fraccion_id ->" + fraccion_id)
                query=(
                '''
                select pc.* from principal_pagodecuotas pc, principal_lote l, principal_manzana m, principal_fraccion f
                where pc.fecha_de_pago >= \''''+ fecha_ini_parsed +               
                '''\' and pc.fecha_de_pago <= \'''' + fecha_fin_parsed +
                '''\' and f.id=''' + fraccion_id +                
                ''' 
                and (pc.lote_id = l.id and l.manzana_id=m.id and m.fraccion_id=f.id) order by f.id,pc.fecha_de_pago
                '''
                )                   
                    
                object_list=list(PagoDeCuotas.objects.raw(query))
                cuotas=[]
                total_monto_pagado=0
                total_monto_gerente=0
                #Seteamos los datos de las filas
                for i, cuota_item in enumerate (object_list):
                    nro_cuota=get_nro_cuota(cuota_item)
                    cuota={}
                    monto_gerente=0
                    if(nro_cuota%2!=0 and nro_cuota<=cuota_item.plan_de_pago_vendedores.cantidad_cuotas):
                        monto_gerente=int(cuota_item.total_de_cuotas*(float(cuota_item.plan_de_pago.porcentaje_cuotas_gerente)/float(100)))
                    cuota['fraccion_id']=cuota_item.lote.manzana.fraccion.id
                    cuota['fraccion']=str(cuota_item.lote.manzana.fraccion)
                    cuota['cuota_nro']=str(nro_cuota)+'/'+str(cuota_item.plan_de_pago.cantidad_de_cuotas)
                    cuota['cliente']=str(cuota_item.cliente)                    
                    cuota['lote']=str(cuota_item.lote)                   
                    cuota['fecha_pago']=str(cuota_item.fecha_de_pago)
                    cuota['monto_pagado']=str('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".") 
                    cuota['monto_gerente']=str('{:,}'.format(monto_gerente)).replace(",", ".") 
                        
                    #Sumamos los totales por fraccion
                    total_monto_pagado+=cuota_item.total_de_cuotas
                    total_monto_gerente+=monto_gerente
                    #Si es el ultimo lote, cerramos totales de fraccion
                    if (len(object_list)-1 == i):
                        cuota['total_monto_pagado']=str('{:,}'.format(total_monto_pagado)).replace(",", ".") 
                        cuota['total_monto_gerente']=str('{:,}'.format(total_monto_gerente)).replace(",", ".")
                        
                    #Hay cambio de lote pero NO es el ultimo elemento todavia
                    elif (cuota_item.lote.manzana.fraccion.id != object_list[i+1].lote.manzana.fraccion.id):
                        cuota['total_monto_pagado']=str('{:,}'.format(total_monto_pagado)).replace(",", ".") 
                        cuota['total_monto_gerente']=str('{:,}'.format(total_monto_gerente)).replace(",", ".")
                        #Se CERAN  los TOTALES por FRACCION
                        total_monto_pagado=0
                        total_monto_gerente=0
                    cuotas.append(cuota)
                            
            
            ultimo="&busqueda_label="+busqueda_label+"&busqueda="+fraccion_id+"&fecha_ini="+fecha_ini+"&fecha_fin="+fecha_fin         
            paginator = Paginator(cuotas, 25)
            page = request.GET.get('page')
            try:
                lista = paginator.page(page)
            except PageNotAnInteger:
                lista = paginator.page(1)
            except EmptyPage:
                lista = paginator.page(paginator.num_pages)          
            c = RequestContext(request, {
                'lista_cuotas': lista,
                'fecha_ini':fecha_ini,
                'fecha_fin':fecha_fin,
                'fraccion': fraccion_id,
                'busqueda_label' : busqueda_label,
                'ultimo' : ultimo
            })
            return HttpResponse(t.render(c))    
        else:    
            return HttpResponseRedirect("/login") 

def informe_movimientos(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if (filtros_establecidos(request.GET,'informe_movimientos') == False):
                t = loader.get_template('informes/informe_movimientos.html')
                c = RequestContext(request, {
                    'object_list': [],
                })
                return HttpResponse(t.render(c))
            else: #Parametros seteados
                t = loader.get_template('informes/informe_movimientos.html')
                lote_id=request.GET['lote_id']
                fecha_ini=request.GET['fecha_ini']
                fecha_fin=request.GET['fecha_fin']
                x = str(lote_id)
                fraccion_int = int(x[0:3])
                manzana_int = int(x[4:7])
                lote_int = int(x[8:])
                manzana = Manzana.objects.get(fraccion_id=fraccion_int, nro_manzana=manzana_int)
                lote = Lote.objects.get(manzana=manzana.id, nro_lote=lote_int)
                lista_movimientos=[]
                print 'lote->'+str(lote.id)
                if fecha_ini != '' and fecha_fin != "":    
                    fecha_ini_parsed = datetime.strptime(fecha_ini, "%d/%m/%Y").date()
                    fecha_fin_parsed = datetime.strptime(fecha_fin, "%d/%m/%Y").date()                
                    try:
                        lista_pagos = PagoDeCuotas.objects.filter(lote_id=lote.id, fecha_de_pago__range=(fecha_ini_parsed, fecha_fin_parsed))
                    except Exception, error:
                        print error
                        lista_pagos = []
                        pass 
                    try:
                        lista_ventas = Venta.objects.get(lote_id=lote.id, fecha_de_venta__range=(fecha_ini_parsed, fecha_fin_parsed))
                    except Exception, error:
                        print error
                        lista_ventas = []
                        pass 
                    try:
                        lista_reservas = Reserva.objects.get(lote_id=lote.id, fecha_de_reserva__range=(fecha_ini_parsed, fecha_fin_parsed))
                    except Exception, error:
                        print error
                        lista_reservas = []
                        pass 
                    try:
                        lista_cambios = CambioDeLotes.objects.get(lote_id=lote.id, fecha_de_cambio__range=(fecha_ini_parsed, fecha_fin_parsed))
                    except Exception, error:
                        print error
                        lista_cambios = []
                        pass 
                    try:
                        lista_recuperaciones = RecuperacionDeLotes.objects.get(lote_id=lote.id, fecha_de_recuperacion__range=(fecha_ini_parsed, fecha_fin_parsed))
                    except Exception, error:
                        print error
                        lista_recuperaciones = []
                        pass
                    try: 
                        lista_transferencias = TransferenciaDeLotes.objects.get(lote_id=lote.id, fecha_de_transferencia__range=(fecha_ini_parsed, fecha_fin_parsed))
                    except Exception, error:
                        print error
                        lista_transferencias = []
                        pass                 
                else:
                    try:
                        lista_pagos = PagoDeCuotas.objects.filter(lote_id=lote.id).order_by('fecha_de_pago')
                    except Exception, error:
                        print error
                        lista_pagos = []
                        pass
                    try:
                        lista_ventas = Venta.objects.get(lote_id=lote.id)
                    except Exception, error:
                        print error
                        lista_ventas =[] 
                        pass
                    try:
                        lista_reservas = Reserva.objects.get(lote_id=lote.id)
                    except Exception, error:
                        print error
                        lista_reservas = []
                        pass    
                    try:    
                        lista_cambios = CambioDeLotes.objects.get(lote_nuevo_id=lote.id)
                    except Exception, error:
                        print error
                        lista_cambios = []
                        pass
                    try:    
                        lista_recuperaciones = RecuperacionDeLotes.objects.get(lote_id=lote.id)
                    except Exception, error:
                        print error
                        lista_recuperaciones = []
                        pass
                    try:    
                        lista_transferencias = TransferenciaDeLotes.objects.get(lote_id=lote.id)
                    except Exception, error:
                        print error
                        lista_transferencias = []
                        pass
                if lista_ventas:
                    venta = []
                    venta.append(lista_ventas.fecha_de_venta)
                    venta.append(lista_ventas.cliente)
                    venta.append(str(0) + '/' + str(lista_ventas.plan_de_pago.cantidad_de_cuotas))
                    venta.append("Entrega inicial")
                    venta.append(str('{:,}'.format(lista_ventas.precio_final_de_venta)).replace(",","."))
                    venta.append(str('{:,}'.format(lista_ventas.entrega_inicial)).replace(",","."))
                    venta.append(str('{:,}'.format(lista_ventas.precio_final_de_venta-lista_ventas.entrega_inicial)).replace(",","."))
                    lista_movimientos.append(venta)
                if lista_pagos:  
                    saldo_anterior=lista_ventas.precio_final_de_venta
                    monto=lista_ventas.entrega_inicial
                    saldo=saldo_anterior-monto
                    for pago in lista_pagos:
                        saldo_anterior=saldo
                        monto=pago.total_de_cuotas
                        saldo=saldo_anterior-monto
                        cuota =[]
                        cuota.append(pago.fecha_de_pago)
                        cuota.append(pago.cliente)
                        cuota.append(str(get_nro_cuota(pago)) + '/' + str(pago.plan_de_pago.cantidad_de_cuotas))
                        cuota.append("Pago de Cuota")
                        cuota.append(str('{:,}'.format(saldo_anterior)).replace(",","."))
                        cuota.append(str('{:,}'.format(monto)).replace(",","."))
                        cuota.append(str('{:,}'.format(saldo)).replace(",","."))
                        lista_movimientos.append(cuota)
                if lista_recuperaciones:
                    for pago in lista_pagos:
                        cuota =[]
                        cuota.append(pago.fecha_de_pago)
                        cuota.append(pago.cliente)
                        cuota.append(str(get_nro_cuota(pago)) + '/' + str(pago.plan_de_pago.cantidad_de_cuotas))
                        cuota.append("Cuota Recuperada")
                        cuota.append(" ")
                        cuota.append(str('{:,}'.format(pago.total_de_cuotas)).replace(",","."))
                        cuota.append(" ")
                        lista_movimientos.append(cuota)
            
                ultimo="&lote_id="+lote_id+"&fecha_ini="+fecha_ini+"&fecha_fin="+fecha_fin
                paginator = Paginator(lista_movimientos, 25)
                page = request.GET.get('page')
                try:
                    lista = paginator.page(page)
                except PageNotAnInteger:
                    lista = paginator.page(1)
                except EmptyPage:
                    lista = paginator.page(paginator.num_pages) 
                c = RequestContext(request, {
                    'lista_movimientos': lista,
                    'lote_id' : lote_id,
                    'fecha_ini' : fecha_ini,
                    'fecha_fin' : fecha_fin,
                    'ultimo': ultimo
                })
                return HttpResponse(t.render(c)) 
        else:
            return HttpResponseRedirect("/login") 

def lotes_libres_reporte_excel(request):
    fraccion_ini=request.GET['fraccion_ini']
    fraccion_fin=request.GET['fraccion_fin']
    # TODO: Danilo, utiliza este template para poner tu logi
       
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    style = xlwt.easyxf('pattern: pattern solid, fore_colour green;'
                              'font: name Arial, bold True;')   
    style2 = xlwt.easyxf('font: name Arial, bold True;')
    # cabeceras
    sheet.write(0, 0, "Fraccion", style)
    sheet.write(0, 1, "Fraccion ID", style)    
    sheet.write(0, 2, "Lote Nro.", style)
    sheet.write(0, 3, "Superficie", style)    
    sheet.write(0, 4, "Precio Contado", style)    
    sheet.write(0, 5, "Precio Crediro", style)
    sheet.write(0, 6, "Precio Costo", style)
    # totales por fraccion
    total_lotes = 0
    total_superficie = 0
    total_contado = 0
    total_credito = 0
    total_importe_cuotas = 0
    # totales generales
    total_general_lotes = 0
    total_general_superficie = 0
    total_general_contado = 0
    total_general_credito = 0
    total_general_importe_cuotas = 0
        
    object_list = []  # lista de lotes
    if fraccion_ini and fraccion_fin:
        manzanas = Manzana.objects.filter(fraccion_id__range=(fraccion_ini, fraccion_fin)).order_by('fraccion')
        for m in manzanas:
            lotes = Lote.objects.filter(manzana=m.id)
            for l in lotes:
                object_list.append(l)
             
    else:       
        object_list = Lote.objects.filter(estado="1").order_by('manzana', 'nro_lote')
     
    lotes = []
    for i in object_list:
        lote = {}
        precio_cuota = int(math.ceil(i.precio_credito/130))
        lote['fraccion_id'] = str(i.manzana.fraccion.id)
        lote['fraccion'] = str(i.manzana.fraccion)
        lote['lote'] = str(i.manzana).zfill(3) + "/" + str(i.nro_lote).zfill(4)
        lote['superficie'] = i.superficie
        lote['precio_contado'] = i.precio_contado
        lote['precio_credito'] = i.precio_credito
        lote['importe_cuota'] =  precio_cuota
        lotes.append(lote)
    # contador de filas
    c = 0
    fraccion_actual = lotes[0]['fraccion_id']
    for i in range(len(lotes)):
        # se suman los totales generales
        total_general_lotes += 1
        total_general_superficie += lotes[i]['superficie'] 
        total_general_contado += lotes[i]['precio_contado'] 
        total_general_credito += lotes[i]['precio_credito']
        total_general_importe_cuotas += lotes[i]['importe_cuota']
        # se suman los totales por fracion
        if (lotes[i]['fraccion_id'] == fraccion_actual):
            c+=1
            total_lotes += 1
            total_superficie += lotes[i]['superficie'] 
            total_contado += lotes[i]['precio_contado'] 
            total_credito += lotes[i]['precio_credito']
            total_importe_cuotas += lotes[i]['importe_cuota']
                    
            sheet.write(c, 0, str(lotes[i]['fraccion']))
            sheet.write(c, 1, str(lotes[i]['fraccion_id']))
            sheet.write(c, 2, str(lotes[i]['lote']))
            sheet.write(c, 3, str(lotes[i]['superficie']))
            sheet.write(c, 4, str('{:,}'.format(lotes[i]['precio_contado']).replace(",", ".")))
            sheet.write(c, 5, str('{:,}'.format(lotes[i]['precio_credito']).replace(",", ".")))
            sheet.write(c, 6, str('{:,}'.format(lotes[i]['importe_cuota']).replace(",", ".")))
        else: 
            c += 1
            sheet.write(c, 0, "Totales de Fraccion", style2)  
            sheet.write(c, 2, str('{:,}'.format(total_lotes)).replace(",", "."))
            sheet.write(c, 3, total_superficie)
            sheet.write(c, 4, str('{:,}'.format(total_contado)).replace(",", "."))
            sheet.write(c, 5, str('{:,}'.format(total_credito)).replace(",", "."))
            sheet.write(c, 6, total_importe_cuotas)
            c += 1
            
            sheet.write(c, 0, str(lotes[i]['fraccion']))
            sheet.write(c, 1, str(lotes[i]['fraccion_id']))
            sheet.write(c, 2, str(lotes[i]['lote']))
            sheet.write(c, 3, str(lotes[i]['superficie']))
            sheet.write(c, 4, str('{:,}'.format(lotes[i]['precio_contado']).replace(",", ".")))
            sheet.write(c, 5, str('{:,}'.format(lotes[i]['precio_credito']).replace(",", ".")))
            sheet.write(c, 6, str('{:,}'.format(lotes[i]['importe_cuota']).replace(",", ".")))     
            fraccion_actual = lotes[i]['fraccion_id']
            total_lotes = 0
            total_superficie = 0
            total_contado = 0
            total_credito = 0
            total_costo = 0           
            
            total_superficie += lotes[i]['superficie'] 
            total_contado += lotes[i]['precio_contado'] 
            total_credito += lotes[i]['precio_credito']
            total_costo += lotes[i]['importe_cuota']
            total_lotes += 1
        # si es la ultima fila    
        if (i == len(lotes) - 1):   
            c += 1           
            sheet.write(c, 0, "Totales de Fraccion", style2)  
            sheet.write(c, 2, str('{:,}'.format(total_lotes)).replace(",", "."))
            sheet.write(c, 3, total_superficie)
            sheet.write(c, 4, str('{:,}'.format(total_contado)).replace(",", "."))
            sheet.write(c, 5, str('{:,}'.format(total_credito)).replace(",", "."))
            sheet.write(c, 6, str('{:,}'.format(total_importe_cuotas)).replace(",", "."))
            
        
            
    c += 1
    sheet.write(c, 0, "Totales Generales", style2)
    sheet.write(c, 2, str('{:,}'.format(total_general_lotes)).replace(",", "."))
    sheet.write(c, 3, total_general_superficie)
    sheet.write(c, 4, str('{:,}'.format(total_general_contado)).replace(",", "."))
    sheet.write(c, 5, str('{:,}'.format(total_general_credito)).replace(",", "."))
    sheet.write(c, 6, str('{:,}'.format(total_general_importe_cuotas)).replace(",", "."))
    
    
    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo         
    response['Content-Disposition'] = 'attachment; filename=' + 'lotes_libres.xls'
    wb.save(response)
    return response

def clientes_atrasados_reporte_excel(request):
    
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    style = xlwt.easyxf('pattern: pattern solid, fore_colour green;'
                              'font: name Arial, bold True;')   
    style2 = xlwt.easyxf('font: name Arial, bold True;')
    
    fecha_actual= datetime.now()            
    filtros = filtros_establecidos(request.GET,'clientes_atrasados')
    cliente_atrasado= {}
    clientes_atrasados= []
    meses_peticion = 0
    fraccion =''
    query = (
    '''
    SELECT pm.nro_manzana manzana, pl.nro_lote lote, pc.nombres || ' ' || apellidos cliente, (pp.cantidad_de_cuotas - pv.pagos_realizados) cuotas_atrasadas,
    pv.pagos_realizados cuotas_pagadas, pv.precio_de_cuota importe_cuota, (pp.cantidad_de_cuotas - pv.pagos_realizados) * pv.precio_de_cuota total_atrasado,
    (pv.pagos_realizados * pv.precio_de_cuota) total_pagado, pp.cantidad_de_cuotas * pv.precio_de_cuota valor_total_lote,
    (pv.pagos_realizados*100/pp.cantidad_de_cuotas) porc_pagado
    FROM principal_lote pl, principal_cliente pc, principal_venta pv, principal_manzana pm, principal_plandepago pp  
    WHERE pv.plan_de_pago_id = pp.id AND pv.lote_id = pl.id AND pv.cliente_id = pc.id
    AND (pp.cantidad_de_cuotas - pv.pagos_realizados) > 0 AND pl.manzana_id = pm.id AND pp.tipo_de_plan='credito'
    '''
    )      
    if filtros == 0:
        meses_peticion = 0
        c = RequestContext(request, {
            'object_list': [],
        })
        return HttpResponse(t.render(c))            
    elif filtros == 1:
        fraccion = request.GET['fraccion']
        query += "AND  pm.fraccion_id =  %s"
        cursor = connection.cursor()
        cursor.execute(query, [fraccion])              
    elif filtros == 2:
        meses_peticion = int(request.GET['meses_atraso'])
        query += "AND (pp.cantidad_de_cuotas - pv.pagos_realizados) = %s"
        cursor = connection.cursor()
        cursor.execute(query, [meses_peticion])  
    else:
        fraccion = request['fraccion']
        meses_peticion = int(request.GET['meses_atraso'])
        query += "AND pm.fraccion_id =  %s"
        cursor = connection.cursor()
        cursor.execute(query, [fraccion]) 
    
    try:
        dias = meses_peticion*30
        results= cursor.fetchall()
        desc = cursor.description
        for r in results:
            i = 0
            cliente_atrasado = {}
            while i < len(desc):
                cliente_atrasado[desc[i][0]] = r[i]
                i = i+1
            try:
                ultimo_pago = PagoDeCuotas.objects.filter(lote__nro_lote= cliente_atrasado['lote']).order_by('-fecha_de_pago')[:1].get()
            except PagoDeCuotas.DoesNotExist:
                ultimo_pago = None
                
            if ultimo_pago != None:
                fecha_ultimo_pago = ultimo_pago.fecha_de_pago
            
            cliente_atrasado['fecha_ultimo_pago']= fecha_ultimo_pago
            
            
            f1 = fecha_actual.date()
            f2 = fecha_ultimo_pago
            diferencia = (f1-f2).days
            meses_diferencia =  int(diferencia /30)
            #En el caso de que las cuotas que debe son menores a la diferencia de meses de la fecha de ultimo pago y la actual
            if meses_diferencia > cliente_atrasado['cuotas_atrasadas']:
                meses_diferencia = cliente_atrasado['cuotas_atrasadas']
                
            if meses_diferencia >= meses_peticion:
                cliente_atrasado['cuotas_atrasadas'] = meses_diferencia                           
                clientes_atrasados.append(cliente_atrasado)                  
                print ("Venta agregada")
                print (" ")
            else:
                print ("Venta no agregada")
                print (" ")
        if meses_peticion == 0:
            meses_peticion =''  
        a = len(clientes_atrasados)
    except Exception, error:
        print error    
        return HttpResponseServerError("No se pudo obtener el Listado de Clientes Atrasados.")
                  
    if a > 0:
        # a=len(object_list)
        sheet.write(0, 0, "Manzana", style)
        sheet.write(0, 1, "Lote", style)
        sheet.write(0, 2, "Cliente", style)
        sheet.write(0, 3, "Cuotas Atras.", style)
        sheet.write(0, 4, "Cuotas Pagadas", style)
        sheet.write(0, 5, "Importe c/ cuota", style)
        sheet.write(0, 6, "Total Atrasado", style)
        sheet.write(0, 7, "Total Pagado", style)
        sheet.write(0, 8, "Valor Total del Lote", style)
        sheet.write(0, 9, "% Pagado", style)
        sheet.write(0, 10, "Fec. Ult. Pago", style)
        i = 0
        c = 1
        for i in range(len(clientes_atrasados)):        
            sheet.write(c, 0, str(clientes_atrasados[i]['manzana']))
            sheet.write(c, 1, str(clientes_atrasados[i]['lote']))
            sheet.write(c, 2, str(clientes_atrasados[i]['cliente']))
            sheet.write(c, 3, str(clientes_atrasados[i]['cuotas_atrasadas']))
            sheet.write(c, 4, str(clientes_atrasados[i]['cuotas_pagadas']))
            sheet.write(c, 5, str(clientes_atrasados[i]['importe_cuota']))
            sheet.write(c, 6, str(clientes_atrasados[i]['total_atrasado']))
            sheet.write(c, 7, str(clientes_atrasados[i]['total_pagado']))
            sheet.write(c, 8, str(clientes_atrasados[i]['valor_total_lote']))
            sheet.write(c, 9, str(clientes_atrasados[i]['porc_pagado']))
            sheet.write(c, 10,str(clientes_atrasados[i]['fecha_ultimo_pago']))
            c += 1
        
    else:
        lista = clientes_atrasados
    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo         
    response['Content-Disposition'] = 'attachment; filename=' + 'clientes_atrasados.xls'
    wb.save(response)
    return response
        
def informe_general_reporte_excel(request):   
    fecha_ini=request.GET['fecha_ini']
    fecha_fin=request.GET['fecha_fin']
    fraccion_ini=request.GET['fraccion_ini']
    fraccion_fin=request.GET['fraccion_fin']
    cuotas=[]    
    if fecha_ini == '' and fecha_fin == '':
        query=(
            '''
            select pc.* from principal_pagodecuotas pc, principal_lote l, principal_manzana m, principal_fraccion f
            where f.id>=''' + fraccion_ini +
            '''
            and f.id<=''' + fraccion_fin +
            '''
            and (pc.lote_id = l.id and l.manzana_id=m.id and m.fraccion_id=f.id) order by f.id
            '''
        )
    else:
        fecha_ini_parsed = datetime.strptime(fecha_ini, "%d/%m/%Y").date()
        fecha_fin_parsed = datetime.strptime(fecha_fin, "%d/%m/%Y").date()
        query=(
            '''
            select pc.* from principal_pagodecuotas pc, principal_lote l, principal_manzana m, principal_fraccion f
            where pc.fecha_de_pago >= \''''+ str(fecha_ini_parsed) +               
            '''\' and pc.fecha_de_pago <= \'''' + str(fecha_fin_parsed) +
            '''\' and f.id>=''' + fraccion_ini +
            '''
            and f.id<=''' + fraccion_fin +
            '''
            and (pc.lote_id = l.id and l.manzana_id=m.id and m.fraccion_id=f.id) order by f.id,pc.fecha_de_pago
            '''
        )
    object_list=list(PagoDeCuotas.objects.raw(query)) 
    #Totales por FRACCION
    total_cuotas=0
    total_mora=0
    total_pagos=0
      
    #Totales GENERALES
    total_general_cuotas=0
    total_general_mora=0
    total_general_pagos=0
        
    for i, cuota_item in enumerate(object_list):
        #Se setean los datos de cada fila
        cuota={}
        nro_cuota=get_nro_cuota(cuota_item)
        cuota['fraccion_id']=str(cuota_item.lote.manzana.fraccion.id)
        cuota['fraccion']=str(cuota_item.lote.manzana.fraccion)
        cuota['lote']=str(cuota_item.lote)
        cuota['cliente']=str(cuota_item.cliente)
        cuota['cuota_nro']=str(nro_cuota)+'/'+str(cuota_item.plan_de_pago.cantidad_de_cuotas)
        cuota['plan_de_pago']=cuota_item.plan_de_pago.nombre_del_plan
        cuota['fecha_pago']=str(cuota_item.fecha_de_pago)
        cuota['total_de_cuotas']=str('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".") 
        cuota['total_de_mora']=str('{:,}'.format(cuota_item.total_de_mora)).replace(",", ".")
        cuota['total_de_pago']=str('{:,}'.format(cuota_item.total_de_pago)).replace(",", ".")

        #Se suman los totales por fraccion
        total_cuotas+=cuota_item.total_de_cuotas
        total_mora+=cuota_item.total_de_mora
        total_pagos+=cuota_item.total_de_pago
            
        #Y acumulamos para los totales generales
        total_general_cuotas+=cuota_item.total_de_cuotas
        total_general_mora+=cuota_item.total_de_mora
        total_general_pagos+=cuota_item.total_de_pago
            
        #Es el ultimo lote, cerramos los totales de fraccion y los totales generales
        if (len(object_list)-1 == i):
            cuota['total_cuotas']=str('{:,}'.format(total_cuotas)).replace(",", ".") 
            cuota['total_mora']=str('{:,}'.format(total_mora)).replace(",", ".")
            cuota['total_pago']=str('{:,}'.format(total_pagos)).replace(",", ".")
                
            cuota['total_general_cuotas']=str('{:,}'.format(total_general_cuotas)).replace(",", ".") 
            cuota['total_general_mora']=str('{:,}'.format(total_general_mora)).replace(",", ".")
            cuota['total_general_pago']=str('{:,}'.format(total_general_pagos)).replace(",", ".")
                        
        #Hay cambio de lote pero NO es el ultimo elemento todavia
        elif (cuota_item.lote.manzana.fraccion.id != object_list[i+1].lote.manzana.fraccion.id):
            cuota['total_cuotas']=str('{:,}'.format(total_cuotas)).replace(",", ".") 
            cuota['total_mora']=str('{:,}'.format(total_mora)).replace(",", ".")
            cuota['total_pago']=str('{:,}'.format(total_pagos)).replace(",", ".")
                    
            #Se CERAN  los TOTALES por FRACCION
            total_cuotas=0
            total_mora=0
            total_pagos=0
                    
        cuotas.append(cuota)
        
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    style = xlwt.easyxf('pattern: pattern solid, fore_colour green;'
                              'font: name Arial, bold True;')   
    style2 = xlwt.easyxf('font: name Arial, bold True;')
    # cabeceras
    sheet.write(0, 0, "Fraccion", style)
    sheet.write(0, 1, "Lote Nro.", style)
    sheet.write(0, 2, "Cliente", style)
    sheet.write(0, 3, "Cuota Nro.", style)
    sheet.write(0, 4, "Plan de Pago", style)
    sheet.write(0, 5, "Fecha de Pago", style)
    sheet.write(0, 6, "Total de Cuotas", style)
    sheet.write(0, 7, "Total de Mora", style)
    sheet.write(0, 8, "Total de Pago", style)

    # contador de filas
    c = 0
    for cuota in cuotas:
        c += 1
        sheet.write(c, 0, cuota['fraccion'])
        sheet.write(c, 1, cuota['lote'])
        sheet.write(c, 2, cuota['cliente'])
        sheet.write(c, 3, cuota['cuota_nro'])
        sheet.write(c, 4, cuota['plan_de_pago'])
        sheet.write(c, 5, cuota['fecha_pago'])
        sheet.write(c, 6, cuota['total_de_cuotas'])
        sheet.write(c, 7, cuota['total_de_mora'])
        sheet.write(c, 8, cuota['total_de_pago'])
                       
        try:
            if cuota['total_cuotas']:
                c += 1            
                sheet.write(c, 0, "Totales de Fraccion", style2)
                sheet.write(c, 6, cuota['total_cuotas'], style2)
                sheet.write(c, 7, cuota['total_mora'], style2)
                sheet.write(c, 8, cuota['total_pago'], style2)
                           
            if cuota['total_general_cuotas']:
                c += 1            
                sheet.write(c, 0, "Totales Generales", style2)
                sheet.write(c, 6, cuota['total_general_cuotas'], style2)
                sheet.write(c, 7, cuota['total_general_mora'], style2)
                sheet.write(c, 8, cuota['total_general_pago'], style2)                
        except:
            pass
       
    
    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo         
    response['Content-Disposition'] = 'attachment; filename=' + 'informe_general.xls'
    wb.save(response)
    return response    
   
def liquidacion_propietarios_reporte_excel(request):
    fecha_ini = request.GET['fecha_ini']
    fecha_fin = request.GET['fecha_fin']
    fecha_ini_parsed = datetime.strptime(fecha_ini, "%d/%m/%Y").date()
    fecha_fin_parsed = datetime.strptime(fecha_fin, "%d/%m/%Y").date()
    tipo_busqueda = request.GET['tipo_busqueda']
    filas = []
    lista_pagos = []
    lotes = []
    #Totales por FRACCION
    total_monto_pagado = 0
    total_monto_inm = 0
    total_monto_prop = 0
                    
    #Totales GENERALES
    total_general_pagado = 0
    total_general_inm = 0
    total_general_prop = 0
                    
    monto_inmobiliaria = 0
    monto_propietario = 0                   
    if tipo_busqueda == "fraccion":
        try:
            fraccion_id = request.GET['busqueda']
            fraccion = Fraccion.objects.get(pk=fraccion_id)                 
            print('Fraccion: ' + fraccion.nombre + '\n')
            manzana_list = Manzana.objects.filter(fraccion_id=fraccion_id).order_by('id')                
            for m in manzana_list:
                lotes_list = Lote.objects.filter(manzana_id=m.id).order_by('id')
                for l in lotes_list:
                    pagos = PagoDeCuotas.objects.filter(lote_id=l.id , fecha_de_pago__range=[fecha_ini_parsed, fecha_fin_parsed]).order_by('fecha_de_pago')
                    if pagos:
                        for pago in pagos:
                            lista_pagos.append(pago)
                            lista_pagos.sort(key=lambda x:x.fecha_de_pago)
        except Exception, error:
            print error                      
        try:
            for i, pago in enumerate(lista_pagos):                        
                #print pago.id
                nro_cuota = get_nro_cuota(pago)
                cuotas_para_propietario=((pago.plan_de_pago.cantidad_cuotas_inmobiliaria)*(pago.plan_de_pago.intervalos_cuotas_inmobiliaria))-pago.plan_de_pago.inicio_cuotas_inmobiliaria
                if(nro_cuota<=cuotas_para_propietario): 
                    if(nro_cuota % 2 != 0):    
                        monto_inmobiliaria = pago.total_de_cuotas
                        monto_propietario = 0
                    else:
                        monto_inmobiliaria = int(pago.total_de_cuotas * (float(pago.plan_de_pago.porcentaje_cuotas_inmobiliaria) / float(100)))
                        monto_propietario = pago.total_de_cuotas - monto_inmobiliaria
                else:
                    monto_inmobiliaria = int(pago.total_de_cuotas * (float(pago.plan_de_pago.porcentaje_cuotas_inmobiliaria) / float(100)))
                    monto_propietario = pago.total_de_cuotas - monto_inmobiliaria
                                    
                fila={}
                total_monto_inm += monto_inmobiliaria
                total_monto_prop += monto_propietario
                total_monto_pagado += pago.total_de_cuotas
                fila['fraccion']=str(pago.lote.manzana.fraccion)
                fila['fecha_de_pago']=str(pago.fecha_de_pago)
                fila['lote']=str(pago.lote)
                fila['cliente']=str(pago.cliente)
                fila['nro_cuota']=str(nro_cuota) + '/' + str(pago.plan_de_pago.cantidad_de_cuotas)
                fila['total_de_cuotas']=str('{:,}'.format(pago.total_de_cuotas)).replace(",", ".")
                fila['monto_inmobiliaria']=str('{:,}'.format(monto_inmobiliaria)).replace(",", ".")
                fila['monto_propietario']=str('{:,}'.format(monto_propietario)).replace(",", ".")
                                
                total_general_pagado += pago.total_de_cuotas
                total_general_inm += monto_inmobiliaria
                total_general_prop += monto_propietario
                filas.append(fila)
            fila['total_general_pagado']=str('{:,}'.format(total_general_pagado)).replace(",", ".")
            fila['total_general_inmobiliaria']=str('{:,}'.format(total_general_inm)).replace(",", ".")
            fila['total_general_propietario']=str('{:,}'.format(total_general_prop)).replace(",", ".")
        except Exception, error:
            print error                    
                                                                                       
    else:
        try:
            propietario_id = request.GET['busqueda']
            fracciones = Fraccion.objects.filter(propietario_id=propietario_id).order_by('id')
            for f in fracciones:
                manzanas = Manzana.objects.filter(fraccion_id=f.id)
                for m in manzanas:
                    lotes = Lote.objects.filter(manzana_id=m.id)
                    for l in lotes:
                        pagos = PagoDeCuotas.objects.filter(lote_id=l.id , fecha_de_pago__range=[fecha_ini_parsed, fecha_fin_parsed])
                        if pagos:
                            for pago in pagos:                                                                                                
                                lista_pagos.append(pago)                        
        except Exception, error:
            print error
        try:
            for i, pago in enumerate(lista_pagos):
                print pago.id
                nro_cuota = get_nro_cuota(pago)
                cuotas_para_propietario=((pago.plan_de_pago.cantidad_cuotas_inmobiliaria)*(pago.plan_de_pago.intervalos_cuotas_inmobiliaria))-pago.plan_de_pago.inicio_cuotas_inmobiliaria
                if(nro_cuota<=cuotas_para_propietario): 
                    if(nro_cuota % 2 != 0):    
                        monto_inmobiliaria = pago.total_de_cuotas
                        monto_propietario = 0
                    else:
                        monto_inmobiliaria = int(pago.total_de_cuotas * (float(pago.plan_de_pago.porcentaje_cuotas_inmobiliaria) / float(100)))
                        monto_propietario = pago.total_de_cuotas - monto_inmobiliaria
                else:
                    monto_inmobiliaria = int(pago.total_de_cuotas * (float(pago.plan_de_pago.porcentaje_cuotas_inmobiliaria) / float(100)))
                    monto_propietario = pago.total_de_cuotas - monto_inmobiliaria

                # Se setean los datos de cada fila
                fila={}
                fila['fraccion']=str(pago.lote.manzana.fraccion)
                fila['fecha_de_pago']=str(pago.fecha_de_pago)
                fila['lote']=str(pago.lote)
                fila['cliente']=str(pago.cliente)
                fila['nro_cuota']=str(nro_cuota) + '/' + str(pago.plan_de_pago.cantidad_de_cuotas)
                fila['total_de_cuotas']=str('{:,}'.format(pago.total_de_cuotas)).replace(",", ".")
                fila['monto_inmobiliaria']=str('{:,}'.format(monto_inmobiliaria)).replace(",", ".")
                fila['monto_propietario']=str('{:,}'.format(monto_propietario)).replace(",", ".")
                            
                # Se suman los TOTALES por FRACCION
                total_monto_inm += monto_inmobiliaria
                total_monto_prop += monto_propietario
                total_monto_pagado += pago.total_de_cuotas
                                
                #Es el ultimo lote, cerrar totales de fraccion
                if (len(lista_pagos)-1 == i):                                
                    #Totales por FRACCION
                    fila['total_monto_pagado']=str('{:,}'.format(total_monto_pagado)).replace(",", ".")
                    fila['total_monto_inmobiliaria']=str('{:,}'.format(total_monto_inm)).replace(",", ".")
                    fila['total_monto_propietario']=str('{:,}'.format(total_monto_prop)).replace(",", ".")
                                
                    #Totales GENERALES
                    fila['total_general_pagado']=str('{:,}'.format(total_general_pagado)).replace(",", ".")
                    fila['total_general_inmobiliaria']=str('{:,}'.format(total_general_inm)).replace(",", ".")
                    fila['total_general_propietario']=str('{:,}'.format(total_general_prop)).replace(",", ".")
                                
                #Hay cambio de lote pero NO es el ultimo elemento todavia
                elif (pago.lote.manzana.fraccion.id != lista_pagos[i+1].lote.manzana.fraccion.id):
                    #Totales por FRACCION
                    fila['total_monto_pagado']=str('{:,}'.format(total_monto_pagado)).replace(",", ".")
                    fila['total_monto_inmobiliaria']=str('{:,}'.format(total_monto_inm)).replace(",", ".")
                    fila['total_monto_propietario']=str('{:,}'.format(total_monto_prop)).replace(",", ".")
                                
                    # Se CERAN  los TOTALES por FRACCION
                    total_monto_pagado = 0
                    total_monto_inm = 0
                    total_monto_prop = 0
                            
                #Acumulamos para los TOTALES GENERALES
                total_general_pagado += pago.total_de_cuotas
                total_general_inm += monto_inmobiliaria
                total_general_prop += monto_propietario
                filas.append(fila)
        except Exception, error:
            print error
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    style = xlwt.easyxf('pattern: pattern solid, fore_colour green;'
                              'font: name Arial, bold True;')   
    style2 = xlwt.easyxf('font: name Arial, bold True;')
    sheet.write(0, 0, "Fecha de Venta", style)
    sheet.write(0, 1, "Lote Nro.", style)
    sheet.write(0, 2, "Cliente", style)
    sheet.write(0, 3, "Cuota Nro.", style)
    sheet.write(0, 4, "Monto Pagado", style)
    sheet.write(0, 5, "Monto Inmobiliaria", style)
    sheet.write(0, 6, "Monto Propietario", style)
    
    c=0
    for pago in filas: 
        c += 1                     
        sheet.write(c, 0, pago['fecha_de_pago'])
        sheet.write(c, 1, pago['lote'])
        sheet.write(c, 2, pago['cliente'])
        sheet.write(c, 3, pago['nro_cuota'])
        sheet.write(c, 4, pago['total_de_cuotas'])
        sheet.write(c, 5, pago['monto_inmobiliaria'])
        sheet.write(c, 6, pago['monto_propietario'])
        
        
        try:
            if (pago['total_monto_pagado']): 
                c+=1            
                sheet.write(c, 0, "Liquidacion", style2)
                sheet.write(c, 4, pago['total_monto_pagado'],style2)
                sheet.write(c, 5, pago['total_monto_inmobiliaria'], style2)
                sheet.write(c, 6, pago['total_monto_propietario'], style2)
        except:
            pass
        try:
            if (pago['total_general_pagado']): 
                c+=1            
                sheet.write(c, 0, "Liquidacion", style2)
                sheet.write(c, 4, pago['total_general_pagado'],style2)
                sheet.write(c, 5, pago['total_general_inmobiliaria'], style2)
                sheet.write(c, 6, pago['total_general_propietario'], style2)
        except:
            pass
  
    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo         
    response['Content-Disposition'] = 'attachment; filename=' + 'liquidacion_propietarios.xls'
    wb.save(response)
    return response 

def liquidacion_vendedores_reporte_excel(request):   
    
    vendedor_id = request.GET['busqueda']
    print("vendedor_id ->" + vendedor_id);
    fecha_ini = request.GET['fecha_ini']
    fecha_fin = request.GET['fecha_fin']
    fecha_ini_parsed = str(datetime.strptime(fecha_ini, "%d/%m/%Y").date())
    fecha_fin_parsed = str(datetime.strptime(fecha_fin, "%d/%m/%Y").date())
    
    query=(
    '''
    select pc.* from principal_pagodecuotas pc, principal_lote l, principal_manzana m, principal_fraccion f
    where pc.fecha_de_pago >= \''''+ fecha_ini_parsed +               
    '''\' and pc.fecha_de_pago <= \'''' + fecha_fin_parsed +
    '''\' and pc.vendedor_id=''' + vendedor_id +                
    ''' 
    and (pc.lote_id = l.id and l.manzana_id=m.id and m.fraccion_id=f.id) order by f.id,pc.fecha_de_pago
    '''
    )                    
           
    object_list=list(PagoDeCuotas.objects.raw(query))
    cuotas=[]
    #totales por fraccion
    total_importe=0
    total_comision=0
    #totales generales
    total_general_importe=0
    total_general_comision=0
    k=0 #variable de control
    #Seteamos los datos de las filas
    for i, cuota_item in enumerate (object_list):                
        nro_cuota=get_nro_cuota(cuota_item)
        cuota={}
        com=0        
        #Esta es una regla de negocio, los vendedores cobran comisiones segun el numero de cuota, maximo hasta la cuota Nro 9.
        cuotas_para_vendedor=((cuota_item.plan_de_pago_vendedores.cantidad_cuotas)*(cuota_item.plan_de_pago_vendedores.intervalos))-cuota_item.plan_de_pago_vendedores.cuota_inicial                  
        #A los vendedores le corresponde comision por las primeras 4 (maximo 5) cuotas impares.
        if(nro_cuota%2!=0 and nro_cuota<=cuotas_para_vendedor):                                                                        
            if k==0:
                #Guardamos la primera fraccion que cumple con la condicion, para tener algo con que comparar.
                fraccion_actual=cuota_item.lote.manzana.fraccion.id
            k+=1            
            if(cuota_item.lote.manzana.fraccion.id==fraccion_actual):                              
                com=int(cuota_item.total_de_cuotas*(float(cuota_item.plan_de_pago_vendedores.porcentaje_de_cuotas)/float(100)))
                cuota['fraccion']=str(cuota_item.lote.manzana.fraccion)
                cuota['cliente']=str(cuota_item.cliente)
                cuota['fraccion_id']=cuota_item.lote.manzana.fraccion.id
                cuota['lote']=str(cuota_item.lote)
                cuota['cuota_nro']=str(nro_cuota)+'/'+str(cuota_item.plan_de_pago.cantidad_de_cuotas)
                cuota['fecha_pago']=str(cuota_item.fecha_de_pago)
                cuota['importe']=str('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".") 
                cuota['comision']=str('{:,}'.format(com)).replace(",", ".")
                    
                #Sumamos los totales por fraccion
                total_importe+=cuota_item.total_de_cuotas
                total_comision+=com
                print cuota_item  
                #Guardamos el ultimo lote que cumple la condicion en dos variables, por si se covnierta en el ultimo lote para cerrar la fraccion
                #actual, o por si sea el ultimo lote de la lista.
                anterior=cuota                            
                ultimo=cuota                       
                #Hay cambio de lote pero NO es el ultimo elemento todavia
            else:
                anterior['total_importe']=str('{:,}'.format(total_importe)).replace(",", ".")
                anterior['total_comision']=str('{:,}'.format(total_comision)).replace(",", ".")
                #Se CERAN  los TOTALES por FRACCION                            
                total_importe=0
                total_comision=0                                                                                
                com=int(cuota_item.total_de_cuotas*(float(cuota_item.plan_de_pago_vendedores.porcentaje_de_cuotas)/float(100)))
                cuota['fraccion']=str(cuota_item.lote.manzana.fraccion)
                cuota['cliente']=str(cuota_item.cliente)
                cuota['fraccion_id']=cuota_item.lote.manzana.fraccion.id
                cuota['lote']=str(cuota_item.lote)
                cuota['cuota_nro']=str(nro_cuota)+'/'+str(cuota_item.plan_de_pago.cantidad_de_cuotas)
                cuota['fecha_pago']=str(cuota_item.fecha_de_pago)
                cuota['importe']=str('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".") 
                cuota['comision']=str('{:,}'.format(com)).replace(",", ".") 
                #Sumamos los totales por fraccion
                total_importe+=cuota_item.total_de_cuotas
                total_comision+=com 
                fraccion_actual=cuota_item.lote.manzana.fraccion.id
                ultimo=cuota
            total_general_importe+=cuota_item.total_de_cuotas
            total_general_comision+=com
            print(cuota)
            cuotas.append(cuota)                        
        #Si es el ultimo lote, cerramos totales de fraccion
        if (len(object_list)-1 == i):
            ultimo['total_importe']=str('{:,}'.format(total_importe)).replace(",", ".") 
            ultimo['total_comision']=str('{:,}'.format(total_comision)).replace(",", ".")             
            ultimo['total_general_importe']=str('{:,}'.format(total_general_importe)).replace(",", ".") 
            ultimo['total_general_comision']=str('{:,}'.format(total_general_comision)).replace(",", ".")          
            
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    style = xlwt.easyxf('pattern: pattern solid, fore_colour green;'
                              'font: name Arial, bold True;')   
    style2 = xlwt.easyxf('font: name Arial, bold True;')
    # cabeceras
    sheet.write(0, 0, "Cliente", style)
    sheet.write(0, 1, "Nombre Fraccion", style)
    sheet.write(0, 2, "Fraccion", style)
    sheet.write(0, 3, "Lote Nro.", style)    
    sheet.write(0, 4, "Cuota Nro.", style)
    sheet.write(0, 5, "Fecha de Pago", style)
    sheet.write(0, 6, "Importe", style)
    sheet.write(0, 7, "Comision", style)
     
    # contador de filas
    c = 0
    for cuota in cuotas:
        c+=1            
        sheet.write(c, 0, cuota['cliente'])
        sheet.write(c, 1, cuota['fraccion'])
        sheet.write(c, 2, cuota['fraccion_id'])
        sheet.write(c, 3, cuota['lote'])
        sheet.write(c, 4, cuota['cuota_nro'])
        sheet.write(c, 5, cuota['fecha_pago'])
        sheet.write(c, 6, cuota['importe']) 
        sheet.write(c, 7, cuota['comision'])
        try: 
            if cuota['total_importe']:
                c+=1 
                sheet.write(c, 0, "Totales de Fraccion", style2)
                sheet.write(c, 6, cuota['total_importe'])
                sheet.write(c, 7, cuota['total_comision'])           
                # si es la ultima fila    
            if (cuota['total_general_importe']):
                c+=1
                sheet.write(c, 0, "Totales del Vendedor", style2)
                sheet.write(c, 6, cuota['total_general_importe'])
                sheet.write(c, 7, cuota['total_general_comision'])
        except:
            pass
    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo         
    response['Content-Disposition'] = 'attachment; filename=' + 'liquidacion_vendedores.xls'
    wb.save(response)
    return response 

def liquidacion_gerentes_reporte_excel(request): 
     
    fecha_ini = request.GET['fecha_ini']
    fecha_fin = request.GET['fecha_fin']
    fecha_ini_parsed = str(datetime.strptime(fecha_ini, "%d/%m/%Y").date())
    fecha_fin_parsed = str(datetime.strptime(fecha_fin, "%d/%m/%Y").date())
    fraccion_id = request.GET['fraccion']
    
    
    query = (
    '''
    select pc.* from principal_pagodecuotas pc, principal_lote l, principal_manzana m, principal_fraccion f
    where pc.fecha_de_pago >= \'''' + fecha_ini_parsed + 
    '''\' and pc.fecha_de_pago <= \'''' + fecha_fin_parsed + 
    '''\' and f.id=''' + fraccion_id + 
    ''' 
    and (pc.lote_id = l.id and l.manzana_id=m.id and m.fraccion_id=f.id) order by f.id,pc.fecha_de_pago
    '''
    )
        
        
    object_list = list(PagoDeCuotas.objects.raw(query))
    cuotas=[]
    #Seteamos los datos de las filas
    for i, cuota_item in enumerate (object_list):
        nro_cuota=get_nro_cuota(cuota_item)
        cuota={}
        monto_gerente=0
        if(nro_cuota%2!=0 and nro_cuota<=cuota_item.plan_de_pago_vendedores.cantidad_cuotas):
            monto_gerente=int(cuota_item.total_de_cuotas*(float(cuota_item.plan_de_pago.porcentaje_cuotas_gerente)/float(100)))
        cuota['fraccion']=str(cuota_item.lote.manzana.fraccion)
        cuota['cliente']=str(cuota_item.cliente)
        cuota['fraccion_id']=cuota_item.lote.manzana.fraccion.id
        cuota['lote']=str(cuota_item.lote)
        cuota['cuota_nro']=str(nro_cuota)+'/'+str(cuota_item.plan_de_pago.cantidad_de_cuotas)
        cuota['fecha_pago']=str(cuota_item.fecha_de_pago)
        cuota['monto_pagado']=cuota_item.total_de_cuotas
        cuota['monto_gerente']=monto_gerente
                        
        cuotas.append(cuota)
            
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    style = xlwt.easyxf('pattern: pattern solid, fore_colour green;'
                              'font: name Arial, bold True;')   
    style2 = xlwt.easyxf('font: name Arial, bold True;')
    # cabeceras
    sheet.write(0, 0, "Cliente", style)
    sheet.write(0, 1, "Nombre Fraccion", style)
    sheet.write(0, 2, "Fraccion", style)
    sheet.write(0, 3, "Lote Nro.", style)    
    sheet.write(0, 4, "Cuota Nro.", style)
    sheet.write(0, 5, "Fecha de Pago", style)
    sheet.write(0, 6, "Monto Pagado", style)
    sheet.write(0, 7, "Monto Gerente", style)
    
    # guardamos la primera fraccion para comparar
    fraccion_actual = cuotas[0]['fraccion_id']
    
    total_monto_pagado = 0
    total_monto_gerente= 0
    total_general_pagado = 0
    total_general_gerente = 0
    
    # contador de filas
    c = 0
    for i in range(len(cuotas)):
        # se suman los totales por fracion
        if (cuotas[i]['fraccion_id'] == fraccion_actual):
            c+=1            
            total_monto_pagado += cuotas[i]['monto_pagado']
            total_monto_gerente += cuotas[i]['monto_gerente']
            
            sheet.write(c, 0, str(cuotas[i]['cliente']))
            sheet.write(c, 1, str(cuotas[i]['fraccion']))
            sheet.write(c, 2, str(cuotas[i]['fraccion_id']))
            sheet.write(c, 3, str(cuotas[i]['lote']))
            sheet.write(c, 4, str(cuotas[i]['cuota_nro']))
            sheet.write(c, 5, str(cuotas[i]['fecha_pago']))
            sheet.write(c, 6, str('{:,}'.format(cuotas[i]['monto_pagado']).replace(",",".")))
            sheet.write(c, 7, str('{:,}'.format(cuotas[i]['monto_gerente']).replace(",",".")))
            
            
            # ... y acumulamos para los totales generales
            total_general_pagado += cuotas[i]['monto_pagado']
            total_general_gerente += cuotas[i]['monto_gerente'] 
        else:
            c+=1 
            sheet.write(c, 0, "Totales de Fraccion", style2)
            sheet.write(c, 6, str('{:,}'.format(total_monto_pagado)).replace(",","."))
            sheet.write(c, 7, str('{:,}'.format(total_monto_gerente)).replace(",","."))            
            c += 1
            fraccion_actual = cuotas[i]['fraccion_id']
            sheet.write(c, 0, str(cuotas[i]['cliente']))
            sheet.write(c, 1, str(cuotas[i]['fraccion']))
            sheet.write(c, 2, str(cuotas[i]['fraccion_id']))
            sheet.write(c, 3, str(cuotas[i]['lote']))
            sheet.write(c, 4, str(cuotas[i]['cuota_nro']))
            sheet.write(c, 5, str(cuotas[i]['fecha_pago']))
            sheet.write(c, 6, str('{:,}'.format(cuotas[i]['monto_pagado']).replace(",",".")))
            sheet.write(c, 7, str('{:,}'.format(cuotas[i]['monto_gerente']).replace(",",".")))         
            total_general_pagado += cuotas[i]['monto_pagado']
            total_general_gerente += cuotas[i]['monto_gerente'] 
            
            total_monto_pagado = 0
            total_monto_gerente= 0
            
            total_monto_pagado += cuotas[i]['monto_pagado']
            total_monto_gerente += cuotas[i]['monto_gerente']
        # si es la ultima fila    
        if (i == len(cuotas) - 1):   
            c += 1           
            sheet.write(c, 0, "Totales de Fraccion", style2)
            sheet.write(c, 6, str('{:,}'.format(total_monto_pagado)).replace(",","."))
            sheet.write(c, 7, str('{:,}'.format(total_monto_gerente)).replace(",","."))
            
    c += 1
    sheet.write(c, 0, "Totales del Gerente", style2)
    sheet.write(c, 6,  str('{:,}'.format(total_general_pagado, style2).replace(",",".")))
    sheet.write(c, 7, str('{:,}'.format(total_general_gerente, style2).replace(",",".")))
    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo         
    response['Content-Disposition'] = 'attachment; filename=' + 'liquidacion_gerentes.xls'
    wb.save(response)
    return response 

def informe_movimientos_reporte_excel(request):
    lista_movimientos = []
    lote= request.GET['lote_id']
    fecha_ini = request.GET['fecha_ini']
    fecha_fin = request.GET['fecha_fin']  
    x = str(lote)
    fraccion_int = int(x[0:3])
    manzana_int = int(x[4:7])
    lote_int = int(x[8:])
    manzana = Manzana.objects.get(fraccion_id=fraccion_int, nro_manzana=manzana_int)
    lote = Lote.objects.get(manzana=manzana.id, nro_lote=lote_int)
    print 'lote->'+str(lote.id)
    if fecha_ini != '' and fecha_fin != "":    
            fecha_ini_parsed = datetime.strptime(fecha_ini, "%d/%m/%Y").date()
            fecha_fin_parsed = datetime.strptime(fecha_fin, "%d/%m/%Y").date()                
            try:
                lista_pagos = PagoDeCuotas.objects.filter(lote_id=lote.id, fecha_de_pago__range=(fecha_ini_parsed, fecha_fin_parsed))
            except Exception, error:
                print error
                lista_pagos = []
                pass 
            try:
                lista_ventas = Venta.objects.get(lote_id=lote.id, fecha_de_venta__range=(fecha_ini_parsed, fecha_fin_parsed))
            except Exception, error:
                print error
                lista_ventas = []
                pass 
            try:
                lista_reservas = Reserva.objects.get(lote_id=lote.id, fecha_de_reserva__range=(fecha_ini_parsed, fecha_fin_parsed))
            except Exception, error:
                print error
                lista_reservas = []
                pass 
            try:
                lista_cambios = CambioDeLotes.objects.get(lote_id=lote.id, fecha_de_cambio__range=(fecha_ini_parsed, fecha_fin_parsed))
            except Exception, error:
                print error
                lista_cambios = []
                pass 
            try:
                lista_recuperaciones = RecuperacionDeLotes.objects.get(lote_id=lote.id, fecha_de_recuperacion__range=(fecha_ini_parsed, fecha_fin_parsed))
            except Exception, error:
                print error
                lista_recuperaciones = []
                pass
            try: 
                lista_transferencias = TransferenciaDeLotes.objects.get(lote_id=lote.id, fecha_de_transferencia__range=(fecha_ini_parsed, fecha_fin_parsed))
            except Exception, error:
                print error
                lista_transferencias = []
                pass 
    else:
            try:
                lista_pagos = PagoDeCuotas.objects.filter(lote_id=lote.id).order_by('fecha_de_pago')
            except Exception, error:
                print error
                lista_pagos = []
                pass
            try:
                lista_ventas = Venta.objects.get(lote_id=lote.id)
            except Exception, error:
                print error
                lista_ventas =[] 
                pass
            try:
                lista_reservas = Reserva.objects.get(lote_id=lote.id)
            except Exception, error:
                print error
                lista_reservas = []
                pass    
            try:    
                lista_cambios = CambioDeLotes.objects.get(lote_nuevo_id=lote.id)
            except Exception, error:
                print error
                lista_cambios = []
                pass
            try:    
                lista_recuperaciones = RecuperacionDeLotes.objects.get(lote_id=lote.id)
            except Exception, error:
                print error
                lista_recuperaciones = []
                pass
            try:    
                lista_transferencias = TransferenciaDeLotes.objects.get(lote_id=lote.id)
            except Exception, error:
                print error
                lista_transferencias = []
                pass
    venta = []
    venta.append(lista_ventas.fecha_de_venta)
    venta.append(lista_ventas.cliente)
    venta.append(str(0) + '/' + str(lista_ventas.plan_de_pago.cantidad_de_cuotas))
    venta.append("Entrega inicial")
    venta.append(str('{:,}'.format(lista_ventas.precio_final_de_venta)).replace(",","."))
    venta.append(str('{:,}'.format(lista_ventas.entrega_inicial)).replace(",","."))
    venta.append(str('{:,}'.format(lista_ventas.precio_final_de_venta-lista_ventas.entrega_inicial)).replace(",","."))
    lista_movimientos.append(venta)
    if lista_pagos:  
        saldo_anterior=lista_ventas.precio_final_de_venta
        monto=lista_ventas.entrega_inicial
        saldo=saldo_anterior-monto
        for pago in lista_pagos:
            saldo_anterior=saldo
            monto=pago.total_de_cuotas
            saldo=saldo_anterior-monto
            cuota =[]
            cuota.append(pago.fecha_de_pago)
            cuota.append(pago.cliente)
            cuota.append(str(get_nro_cuota(pago)) + '/' + str(pago.plan_de_pago.cantidad_de_cuotas))
            cuota.append("Pago de Cuota")
            cuota.append(str('{:,}'.format(saldo_anterior)).replace(",","."))
            cuota.append(str('{:,}'.format(monto)).replace(",","."))
            cuota.append(str('{:,}'.format(saldo)).replace(",","."))
            lista_movimientos.append(cuota)
    if lista_recuperaciones:
        for pago in lista_pagos:
            cuota =[]
            cuota.append(pago.fecha_de_pago)
            cuota.append(pago.cliente)
            cuota.append(str(get_nro_cuota(pago)) + '/' + str(pago.plan_de_pago.cantidad_de_cuotas))
            cuota.append("Cuota Recuperada")
            cuota.append(" ")
            cuota.append(str('{:,}'.format(pago.total_de_cuotas)).replace(",","."))
            cuota.append(" ")
            lista_movimientos.append(cuota)
            
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    style = xlwt.easyxf('pattern: pattern solid, fore_colour green;'
                              'font: name Arial, bold True;')   
    style2 = xlwt.easyxf('font: name Arial, bold True;')
    # cabeceras
    sheet.write(0, 0, "Fecha de Pago", style)
    sheet.write(0, 1, "Cliente", style) 
    sheet.write(0, 2, "Cuota Nro.", style)
    sheet.write(0, 3, "Tipo Cuota", style)    
    sheet.write(0, 4, "Saldo Anterior", style)        
    sheet.write(0, 5, "Monto", style)
    sheet.write(0, 6, "Saldo", style)
    c = 1
    for i in range(len(lista_movimientos)):
        sheet.write(c, 0, str(lista_movimientos[i][0]))
        sheet.write(c, 1, str(lista_movimientos[i][1]))
        sheet.write(c, 2, str(lista_movimientos[i][2]))
        sheet.write(c, 3, str(lista_movimientos[i][3]))
        sheet.write(c, 4, str(lista_movimientos[i][4]))
        sheet.write(c, 5, str(lista_movimientos[i][5]))
        sheet.write(c, 6, str(lista_movimientos[i][6]))
        c+=1
    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo         
    response['Content-Disposition'] = 'attachment; filename=' + 'informe_movimientos.xls'
    wb.save(response)
    return response     
    
def filtros_establecidos(request, tipo_informe):
    
    if tipo_informe == 'liquidacion_propietarios':        
        try:
            fecha_ini=request['fecha_ini']
            fecha_fin=request['fecha_fin']
            tipo_busqueda=request['tipo_busqueda']
            return True
        except:
            print('Parametros no seteados')
            return False
    elif tipo_informe == 'clientes_atrasados':
            #Puede filtrar solo por meses de atraso o solo por fraccion o sin ningun filtro
            try:
                if request['fraccion'] == '' and request['meses_atraso'] == '':               
                    return 0
                elif request['fraccion'] != '' and request['meses_atraso'] == '':
                    fraccion = request['fraccion']
                    return 1
                elif request['fraccion'] == ''and request['meses_atraso'] != '':
                    meses_atraso = request['meses_atraso']
                    return 2
                else:
                    fraccion = request['fraccion']
                    meses_atraso = request['meses_atraso']
                    return 3
            except:
                print('Parametros no seteados')
                return 0
    elif tipo_informe == 'lotes_libres':
        try:
            fraccion_ini=request['fraccion_ini']
            fraccion_fin=request['fraccion_fin']
            return True
        except:
            print('Parametros no seteados')
            
    elif tipo_informe == 'informe_movimientos':
        try:
            lote_id=request['lote_id']
            fecha_ini=request['fecha_ini']
            fecha_fin=request['fecha_fin']
            return True
        except:
            print('Parametros no seteados')
    elif tipo_informe == "informe_general":
        try:
            fraccion_ini=request['fraccion_ini']
            fraccion_fin=request['fraccion_fin']
            fecha_ini=request['fecha_ini']
            fecha_fin=request['fecha_fin']
            return True
        except:
            print('Parametros no seteados')
    elif tipo_informe == "liquidacion_vendedores":
        try:
            fecha_ini=request['fecha_ini']
            fecha_fin=request['fecha_fin']
            busqueda=request['busqueda']
            return True
        except:
            print('Parametros no seteados')      
    elif tipo_informe == "liquidacion_gerentes":
        try:
            fecha_ini=request['fecha_ini']
            fecha_fin=request['fecha_fin']
            busqueda=request['busqueda']
            return True
        except:
            print('Parametros no seteados')      
    return False
