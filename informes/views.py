# -*- encoding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template import RequestContext, loader
from principal.models import Propietario, Fraccion, Lote, Manzana, PagoDeCuotas, Venta, Reserva, CambioDeLotes, RecuperacionDeLotes, TransferenciaDeLotes 
from operator import itemgetter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse, resolve
from calendar import monthrange
from principal.common_functions import get_nro_cuota
import json
from django.db import connection
import xlwt
import math
from principal.common_functions import *
from principal import permisos

# Funcion principal del modulo de lotes.
def informes(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_OPCIONES):
            t = loader.get_template('informes/index.html')
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

def lotes_libres(request): 
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
                if (filtros_establecidos(request.GET,'lotes_libres') == False):
                    t = loader.get_template('informes/lotes_libres.html')
                    c = RequestContext(request, {
                        'object_list': [],
                    })
                    return HttpResponse(t.render(c))
                else: #Parametros seteados
                    tipo_busqueda=request.GET['tipo_busqueda']
                    t = loader.get_template('informes/lotes_libres.html')
                    fraccion_ini=request.GET['frac1']
                    fraccion_fin=request.GET['frac2']
                    f1=request.GET['fraccion_ini']
                    f2=request.GET['fraccion_fin']
                    ultimo="&tipo_busqueda="+tipo_busqueda+"&fraccion_ini="+f1+"&frac1="+fraccion_ini+"&fraccion_fin="+f2+"&frac2="+fraccion_fin
                    object_list = []  # lista de lotes
                    if fraccion_ini and fraccion_fin:
                        
                        manzanas = Manzana.objects.filter(fraccion_id__range=(fraccion_ini, fraccion_fin)).order_by('fraccion_id', 'nro_manzana')
                        for m in manzanas:
                            lotes = Lote.objects.filter(manzana=m.id, estado="1").order_by('nro_lote')
                            for l in lotes:
                                object_list.append(l)                                  
                    else:       
                        object_list = Lote.objects.filter(estado="1").order_by('nro_lote')
                     
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
                        lote['fraccion_id']=unicode(lote_item.manzana.fraccion.id)
                        lote['fraccion']=unicode(lote_item.manzana.fraccion)
                        lote['lote']=unicode(lote_item.manzana).zfill(3) + "/" + unicode(lote_item.nro_lote).zfill(4)
                        lote['superficie']=lote_item.superficie                                    
                        lote['precio_contado']=unicode('{:,}'.format(lote_item.precio_contado)).replace(",", ".")                    
                        lote['precio_credito']=unicode('{:,}'.format(lote_item.precio_credito)).replace(",", ".")                    
                        lote['importe_cuota']=unicode('{:,}'.format(precio_cuota)).replace(",", ".")
                    # Se suman los TOTALES por FRACCION
                        total_superficie_fraccion += lote_item.superficie 
                        total_contado_fraccion += lote_item.precio_contado
                        total_credito_fraccion += lote_item.precio_credito
                        total_importe_cuotas += precio_cuota
                        total_lotes += 1
                    #Es el ultimo lote, cerrar totales de fraccion
                        if (len(object_list)-1 == index):
                            lote['total_importe_cuotas'] = unicode('{:,}'.format(total_importe_cuotas)).replace(",", ".") 
                            lote['total_credito_fraccion'] =  unicode('{:,}'.format(total_credito_fraccion)).replace(",", ".")
                            lote['total_contado_fraccion'] =  unicode('{:,}'.format(total_contado_fraccion)).replace(",", ".")
                            lote['total_superficie_fraccion'] =  unicode('{:,}'.format(total_superficie_fraccion)).replace(",", ".")
                            lote['total_lotes'] =  unicode('{:,}'.format(total_lotes)).replace(",", ".")
                    #Hay cambio de lote pero NO es el ultimo elemento todavia
                        elif (lote_item.manzana.fraccion.id != object_list[index+1].manzana.fraccion.id):
                            lote['total_importe_cuotas'] = unicode('{:,}'.format(total_importe_cuotas)).replace(",", ".") 
                            lote['total_credito_fraccion'] =  unicode('{:,}'.format(total_credito_fraccion)).replace(",", ".")
                            lote['total_contado_fraccion'] =  unicode('{:,}'.format(total_contado_fraccion)).replace(",", ".")
                            lote['total_superficie_fraccion'] =  unicode('{:,}'.format(total_superficie_fraccion)).replace(",", ".")
                            lote['total_lotes'] =  unicode('{:,}'.format(total_lotes)).replace(",", ".")
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
                t = loader.get_template('index2.html')
                grupo= request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))                
        else:
            return HttpResponseRedirect(reverse('login')) 
    
    else:
        t = loader.get_template('informes/lotes_libres.html')
        c = RequestContext(request, {
            # 'object_list': lista,
            # 'fraccion': f,
        })
        return HttpResponse(t.render(c))    

def listar_busqueda_lotes(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_INFORMES):
            t = loader.get_template('informes/lotes_libres.html')
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login')) 
    
    busqueda = request.POST['busqueda']
    if busqueda:
        x = unicode(busqueda)
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
        if verificar_permisos(request.user.id, permisos.VER_INFORMES):
            t = loader.get_template('informes/detalle_pagos_cliente.html')
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login')) 

    if venta != '' and cliente != '':
        object_list = PagoDeCuotas.objects.filter(venta_id=venta, cliente_id=cliente).order_by('fecha_de_pago')
        a = len(object_list)
        if a > 0:
            for i in object_list:
                i.fecha_de_pago = i.fecha_de_pago.strftime("%d/%m/%Y")
                i.total_de_cuotas = unicode('{:,}'.format(i.total_de_cuotas)).replace(",", ".")
                i.total_de_mora = unicode('{:,}'.format(i.total_de_mora)).replace(",", ".")
                i.total_de_pago = unicode('{:,}'.format(i.total_de_pago)).replace(",", ".")
            
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

def clientes_atrasados(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
                t = loader.get_template('informes/clientes_atrasados.html')
                fecha_actual= datetime.now()            
                filtros = filtros_establecidos(request.GET,'clientes_atrasados')
                cliente_atrasado= {}
                clientes_atrasados= []
                meses_peticion = 0
                fraccion =''
                query = (
                '''
                SELECT pm.nro_manzana manzana, pl.nro_lote lote, pl.id lote_id, pc.id, pc.nombres || ' ' || apellidos cliente, (pp.cantidad_de_cuotas - pv.pagos_realizados) cuotas_atrasadas,
                pv.pagos_realizados cuotas_pagadas, pv.precio_de_cuota importe_cuota,
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
                    fraccion = request.GET['fraccion']
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
                            ultimo_pago = PagoDeCuotas.objects.filter(cliente_id= cliente_atrasado['id']).order_by('-fecha_de_pago')[:1].get()
                        except PagoDeCuotas.DoesNotExist:
                            ultimo_pago = None
                            
                        if ultimo_pago != None:
                            fecha_ultimo_pago = ultimo_pago.fecha_de_pago         
                        
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
                            
                        #Seteamos los campos restantes
                        total_atrasado = meses_diferencia * cliente_atrasado['importe_cuota']
                        cliente_atrasado['fecha_ultimo_pago']= fecha_ultimo_pago.strftime("%Y-%m-%d")
                        cliente_atrasado['lote']=(unicode(cliente_atrasado['manzana']).zfill(3) + "/" + unicode(cliente_atrasado['lote']).zfill(4))
                        cliente_atrasado['total_atrasado'] = unicode('{:,}'.format(total_atrasado)).replace(",", ".")
                        cliente_atrasado['importe_cuota'] = unicode('{:,}'.format(cliente_atrasado['importe_cuota'])).replace(",", ".")
                        cliente_atrasado['total_pagado'] = unicode('{:,}'.format(cliente_atrasado['total_pagado'])).replace(",", ".")
                        cliente_atrasado['valor_total_lote'] = unicode('{:,}'.format(cliente_atrasado['valor_total_lote'])).replace(",", ".") 
                    if meses_peticion == 0:
                        meses_peticion =''  
                    a = len(clientes_atrasados)
                    if a > 0:                    
                        ultimo="&fraccion="+unicode(fraccion)+"&meses_atraso="+unicode(meses_peticion)
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
                        ultimo="&fraccion="+unicode(fraccion)+"&meses_atraso="+unicode(meses_peticion)
                        c = RequestContext(request, {
                            'fraccion': fraccion,                        
                            'meses_atraso': meses_peticion,
                            'ultimo': ultimo,
                            'object_list': clientes_atrasados                       
                        })
                        return HttpResponse(t.render(c))                 
                except Exception, error:
                    print error    
                    #return HttpResponseServerError("No se pudo obtener el Listado de Clientes Atrasados.")
            else:
                t = loader.get_template('index2.html')
                grupo= request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))
        else:
            return HttpResponseRedirect(reverse('login'))
        
       

def informe_general(request):    
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
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
                        where pc.fecha_de_pago >= \''''+ unicode(fecha_ini_parsed) +               
                        '''\' and pc.fecha_de_pago <= \'''' + unicode(fecha_fin_parsed) +
                        '''\' and f.id >= ''' + fraccion_ini +
                        '''
                        and f.id <= ''' + fraccion_fin +
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
                        cuota['fraccion_id']=unicode(cuota_item.lote.manzana.fraccion.id)
                        cuota['fraccion']=unicode(cuota_item.lote.manzana.fraccion)
                        cuota['lote']=unicode(cuota_item.lote)
                        cuota['cliente']=unicode(cuota_item.cliente)
                        cuota['cuota_nro']=unicode(nro_cuota)+'/'+unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                        cuota['plan_de_pago']=cuota_item.plan_de_pago.nombre_del_plan
                        cuota['fecha_pago']=unicode(cuota_item.fecha_de_pago)
                        cuota['total_de_cuotas']=unicode('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".") 
                        cuota['total_de_mora']=unicode('{:,}'.format(cuota_item.total_de_mora)).replace(",", ".")
                        cuota['total_de_pago']=unicode('{:,}'.format(cuota_item.total_de_pago)).replace(",", ".")
    
                        #Se suman los totales por fraccion
                        total_cuotas+=cuota_item.total_de_cuotas
                        total_mora+=cuota_item.total_de_mora
                        total_pagos+=cuota_item.total_de_pago
                        
                        #Es el ultimo lote, cerramos los totales de fraccion
                        if (len(object_list)-1 == i):
                            cuota['total_cuotas']=unicode('{:,}'.format(total_cuotas)).replace(",", ".") 
                            cuota['total_mora']=unicode('{:,}'.format(total_mora)).replace(",", ".")
                            cuota['total_pago']=unicode('{:,}'.format(total_pagos)).replace(",", ".")
                            
                        #Hay cambio de lote pero NO es el ultimo elemento todavia
                        elif (cuota_item.lote.manzana.fraccion.id != object_list[i+1].lote.manzana.fraccion.id):
                            cuota['total_cuotas']=unicode('{:,}'.format(total_cuotas)).replace(",", ".") 
                            cuota['total_mora']=unicode('{:,}'.format(total_mora)).replace(",", ".")
                            cuota['total_pago']=unicode('{:,}'.format(total_pagos)).replace(",", ".")
                        
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
                t = loader.get_template('index2.html')
                grupo= request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))               
        else:
            return HttpResponseRedirect(reverse('login'))
         
def liquidacion_propietarios(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
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
                                fila={}
                                ok=True
                                fraccion_id = request.GET['busqueda']
                                fraccion = Fraccion.objects.get(pk=fraccion_id)                 
                                print('Fraccion: ' + fraccion.nombre + '\n')
                                manzana_list = Manzana.objects.filter(fraccion_id=fraccion_id).order_by('id')                
                                for m in manzana_list:
                                    lotes_list = Lote.objects.filter(manzana_id=m.id).order_by('id')
                                    for l in lotes_list:
                                        ventas = Venta.objects.filter(lote_id=l.id)
                                        #Obteniendo la ultima venta
                                        for item_venta in ventas:                                           
                                            try:
                                                RecuperacionDeLotes.objects.get(venta=item_venta.id)
                                            except RecuperacionDeLotes.DoesNotExist:
                                                #se encontro la venta no recuperada, la venta actual
                                                venta = item_venta 
                                        pagos = get_pago_cuotas(venta, fecha_ini_parsed,fecha_fin_parsed)
                                        if pagos:
                                            for pago in pagos:
                                                montos = calculo_montos_liquidacion_propietarios(pago,venta)
                                                monto_inmobiliaria = montos['monto_inmobiliaria']
                                                monto_propietario = montos['monto_propietario']
                                                # Se setean los datos de cada fila
                                                fila={}
                                                fila['misma_fraccion'] = ok
                                                fila['fraccion']=unicode(fraccion)
                                                fila['fecha_de_pago']=unicode(pago['fecha_de_pago'])
                                                fila['lote']=unicode(l)
                                                fila['cliente']=unicode(venta.cliente)
                                                fila['nro_cuota']=unicode(pago['nro_cuota_y_total'])
                                                fila['total_de_cuotas']=unicode(pago['monto'])
                                                fila['monto_inmobiliaria']=unicode(monto_inmobiliaria)
                                                fila['monto_propietario']=unicode(monto_propietario)
                                                ok=False
                                                # Se suman los TOTALES por FRACCION
                                                total_monto_inm += int(monto_inmobiliaria)
                                                total_monto_prop += int(monto_propietario)
                                                total_monto_pagado += int(pago['monto'])
                                                filas.append(fila)
                                                #Acumulamos para los TOTALES GENERALES
                                                total_general_pagado += int(pago['monto'])
                                                total_general_inm += int(monto_inmobiliaria)
                                                total_general_prop += int(monto_propietario)
                                if total_monto_inm != 0 or total_monto_prop !=0 or total_monto_pagado !=0: 
                                    #Totales por FRACCION
                                    fila['total_monto_pagado']=unicode(total_monto_pagado)
                                    fila['total_monto_inmobiliaria']=unicode(total_monto_inm)
                                    fila['total_monto_propietario']=unicode(total_monto_prop)
                                    
                                #Totales GENERALES
                                fila['total_general_pagado']=unicode(total_general_pagado)
                                fila['total_general_inmobiliaria']=unicode(total_general_inm)
                                fila['total_general_propietario']=unicode(total_general_prop)
                                
                            except Exception, error:
                                print error                                                                                       
                        else:
                            try:
                                fila={} 
                                propietario_id = request.GET['busqueda']
                                fracciones = Fraccion.objects.filter(propietario_id=propietario_id).order_by('id')
                                for f in fracciones:
                                    # Se CERAN  los TOTALES por FRACCION
                                    total_monto_pagado = 0
                                    total_monto_inm = 0
                                    total_monto_prop = 0
                                    ok=True
                                    manzanas = Manzana.objects.filter(fraccion_id=f.id)
                                    for m in manzanas:
                                        lotes = Lote.objects.filter(manzana_id=m.id)
                                        for l in lotes:
                                            ventas = Venta.objects.filter(lote_id=l.id)
                                            for item_venta in ventas:
                                                print 'Obteniendo la ultima venta'
                                                try:
                                                    RecuperacionDeLotes.objects.get(venta=item_venta.id)
                                                except RecuperacionDeLotes.DoesNotExist:
                                                    print 'se encontro la venta no recuperada, la venta actual'
                                                    venta = item_venta
                                            pagos = get_pago_cuotas(venta, fecha_ini_parsed,fecha_fin_parsed)
                                            if pagos:
                                                for pago in pagos:
                                                    montos = calculo_montos_liquidacion_propietarios(pago,venta)
                                                    monto_inmobiliaria = montos['monto_inmobiliaria']
                                                    monto_propietario = montos['monto_propietario']
                                                    # Se setean los datos de cada fila
                                                    fila={}
                                                    fila['misma_fraccion'] = ok
                                                    fila['fraccion']=unicode(f)
                                                    fila['fecha_de_pago']=unicode(pago['fecha_de_pago'])
                                                    fila['lote']=unicode(l)
                                                    fila['cliente']=unicode(venta.cliente)
                                                    fila['nro_cuota']=unicode(pago['nro_cuota_y_total'])
                                                    fila['total_de_cuotas']=unicode(pago['monto'])
                                                    fila['monto_inmobiliaria']=unicode(monto_inmobiliaria)
                                                    fila['monto_propietario']=unicode(monto_propietario)
                                                    ok=False
                                                    # Se suman los TOTALES por FRACCION
                                                    total_monto_inm += int(monto_inmobiliaria)
                                                    total_monto_prop += int(monto_propietario)
                                                    total_monto_pagado += int(pago['monto'])
                                                    filas.append(fila)
                                                    #Acumulamos para los TOTALES GENERALES
                                                    total_general_pagado += int(pago['monto'])
                                                    total_general_inm += int(monto_inmobiliaria)
                                                    total_general_prop += int(monto_propietario)
                                    if total_monto_inm != 0 or total_monto_prop !=0 or total_monto_pagado !=0: 
                                        #Totales por FRACCION
                                        fila['total_monto_pagado']=unicode(total_monto_pagado)
                                        fila['total_monto_inmobiliaria']=unicode(total_monto_inm)
                                        fila['total_monto_propietario']=unicode(total_monto_prop)
                                
                                if total_monto_inm != 0 or total_monto_prop !=0 or total_monto_pagado !=0:        
                                    #Totales por FRACCION
                                    fila['total_monto_pagado']=unicode(total_monto_pagado)
                                    fila['total_monto_inmobiliaria']=unicode(total_monto_inm)
                                    fila['total_monto_propietario']=unicode(total_monto_prop)
                                #Totales GENERALES
                                fila['total_general_pagado']=unicode(total_general_pagado)
                                fila['total_general_inmobiliaria']=unicode(total_general_inm)
                                fila['total_general_propietario']=unicode(total_general_prop)
              
                            except Exception, error:
                                print error                            
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
                t = loader.get_template('index2.html')
                grupo= request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))                                 
        else:
            return HttpResponseRedirect(reverse('login'))

def liquidacion_vendedores(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
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
                    fecha_ini_parsed = unicode(datetime.strptime(fecha_ini, "%d/%m/%Y").date())
                    fecha_fin_parsed = unicode(datetime.strptime(fecha_fin, "%d/%m/%Y").date())
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
                        #Si el plan de pago tiene hasta 12 cuotas, los vendedores cobran una comision sobre todas las cuotas.
                        cuotas_para_vendedor=((cuota_item.plan_de_pago_vendedores.cantidad_cuotas)*(cuota_item.plan_de_pago_vendedores.intervalos))-cuota_item.plan_de_pago_vendedores.cuota_inicial                  
                        #A los vendedores le corresponde comision por las primeras 4 (maximo 5) cuotas impares.
                        if( (nro_cuota%2!=0 and nro_cuota<=cuotas_para_vendedor) or (cuota_item.plan_de_pago.cantidad_de_cuotas<=12 and nro_cuota<=12) ):                                                                        
                            if k==0:
                                #Guardamos la primera fraccion que cumple con la condicion, para tener algo con que comparar.
                                fraccion_actual=cuota_item.lote.manzana.fraccion.id
                            k+=1
                            print k
                            if(cuota_item.lote.manzana.fraccion.id==fraccion_actual):                              
                                #comision de las cuotas
                                com=int(cuota_item.total_de_cuotas*(float(cuota_item.plan_de_pago_vendedores.porcentaje_de_cuotas)/float(100)))
                                if(cuota_item.venta.entrega_inicial):
                                    #comision de la entrega inicial, si la hubiere
                                    com_inicial=int(cuota_item.venta.entrega_inicial*(float(cuota_item.plan_de_pago_vendedores.porcentaje_cuota_inicial)/float(100)))
                                    cuota['concepto']="Entrega Inicial"
                                    cuota['cuota_nro']=unicode(0)+'/'+unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                                    cuota['comision']=unicode('{:,}'.format(com_inicial)).replace(",", ".")
                                else:
                                    cuota['concepto']="Pago de Cuota" 
                                    cuota['cuota_nro']=unicode(nro_cuota)+'/'+unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                                    cuota['comision']=unicode('{:,}'.format(com)).replace(",", ".")
                                cuota['fraccion']=unicode(cuota_item.lote.manzana.fraccion)
                                cuota['cliente']=unicode(cuota_item.cliente)
                                cuota['fraccion_id']=cuota_item.lote.manzana.fraccion.id
                                cuota['lote']=unicode(cuota_item.lote)
                                cuota['fecha_pago']=unicode(cuota_item.fecha_de_pago)
                                cuota['importe']=unicode('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".") 
      
        
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
                                anterior['total_importe']=unicode('{:,}'.format(total_importe)).replace(",", ".")
                                anterior['total_comision']=unicode('{:,}'.format(total_comision)).replace(",", ".")
            
                                #Se CERAN  los TOTALES por FRACCION                            
                                total_importe=0
                                total_comision=0                                                                                
                                com=int(cuota_item.total_de_cuotas*(float(cuota_item.plan_de_pago_vendedores.porcentaje_de_cuotas)/float(100)))
                                if(cuota_item.venta.entrega_inicial):
                                    #comision de la entrega inicial, si la hubiere
                                    com_inicial=int(cuota_item.venta.entrega_inicial*(float(cuota_item.plan_de_pago_vendedores.porcentaje_cuota_inicial)/float(100)))
                                    cuota['concepto']="Entrega Inicial"
                                    cuota['cuota_nro']=unicode(0)+'/'+unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                                    cuota['comision']=unicode('{:,}'.format(com_inicial)).replace(",", ".")
                                else:
                                    cuota['concepto']="Pago de Cuota" 
                                    cuota['cuota_nro']=unicode(nro_cuota)+'/'+unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                                    cuota['comision']=unicode('{:,}'.format(com)).replace(",", ".")
                                cuota['fraccion']=unicode(cuota_item.lote.manzana.fraccion)
                                cuota['cliente']=unicode(cuota_item.cliente)
                                cuota['fraccion_id']=cuota_item.lote.manzana.fraccion.id
                                cuota['lote']=unicode(cuota_item.lote)
                                cuota['fecha_pago']=unicode(cuota_item.fecha_de_pago)
                                cuota['importe']=unicode('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".") 
                                #Sumamos los totales por fraccion
                                total_importe+=cuota_item.total_de_cuotas
                                total_comision+=com 
                                fraccion_actual=cuota_item.lote.manzana.fraccion.id
                                anterior=cuota
                                ultimo=cuota
                            total_general_importe+=cuota_item.total_de_cuotas
                            total_general_comision+=com
                            cuotas.append(cuota)                        
                        #Si es el ultimo lote, cerramos totales de fraccion
                        if (len(object_list)-1 == i):
                            try:
                                ultimo['total_importe']=unicode('{:,}'.format(total_importe)).replace(",", ".") 
                                ultimo['total_comision']=unicode('{:,}'.format(total_comision)).replace(",", ".")             
                                ultimo['total_general_importe']=unicode('{:,}'.format(total_general_importe)).replace(",", ".") 
                                ultimo['total_general_comision']=unicode('{:,}'.format(total_general_comision)).replace(",", ".")          
                            except Exception, error:
                                print error 
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
                t = loader.get_template('index2.html')
                grupo= request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))   
        else:    
            return HttpResponseRedirect(reverse('login')) 
        
def liquidacion_gerentes(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
                if (filtros_establecidos(request.GET,'liquidacion_gerentes') == False):                
                    t = loader.get_template('informes/liquidacion_gerentes.html')
                    c = RequestContext(request, {
                       'object_list': [],
                    })
                    return HttpResponse(t.render(c))                
                else:#Parametros seteados
                    t = loader.get_template('informes/liquidacion_gerentes.html')
                    fecha = request.GET['fecha']
                    tipo_liquidacion = request.GET['tipo_liquidacion']
                    fecha_ini = request.GET['fecha_ini']
                    fecha_fin = request.GET['fecha_fin']
                    fecha_ini_parsed = unicode(datetime.strptime(fecha_ini, "%d/%m/%Y").date())
                    fecha_fin_parsed = unicode(datetime.strptime(fecha_fin, "%d/%m/%Y").date())
                    query=(
                    '''
                    select pc.* from principal_pagodecuotas pc, principal_lote l, principal_manzana m, principal_fraccion f
                    where pc.fecha_de_pago >= \''''+ fecha_ini_parsed +               
                    '''\' and pc.fecha_de_pago <= \'''' + fecha_fin_parsed +
                    '''\'                 
                    and (pc.lote_id = l.id and l.manzana_id=m.id and m.fraccion_id=f.id) order by pc.vendedor_id, f.id, pc.fecha_de_pago
                    '''
                    )                    
            
                    lista_pagos=list(PagoDeCuotas.objects.raw(query))
                    
                    if tipo_liquidacion == 'gerente_ventas':
                        tipo_gerente="Gerente de Ventas"
                    if tipo_liquidacion == 'gerente_admin':
                        tipo_gerente="Gerente Administrativo"
                    
                    #totales por vendedor
                    total_importe=0
                    total_comision=0
                    
                    #totales generales
                    total_general_importe=0
                    total_general_comision=0
                    k=0 #variable de control
                    cuotas=[]
                    #Seteamos los datos de las filas
                    for i, cuota_item in enumerate (lista_pagos):                
                        nro_cuota=get_nro_cuota(cuota_item)
                        cuota={}
                        com=0        
                        #Esta es una regla de negocio, los vendedores cobran comisiones segun el numero de cuota, maximo hasta la cuota Nro 9.
                        #Si el plan de pago tiene hasta 12 cuotas, los vendedores cobran una comision sobre todas las cuotas.
                        cuotas_para_vendedor=((cuota_item.plan_de_pago_vendedores.cantidad_cuotas)*(cuota_item.plan_de_pago_vendedores.intervalos))-cuota_item.plan_de_pago_vendedores.cuota_inicial                  
                        #A los vendedores le corresponde comision por las primeras 4 (maximo 5) cuotas impares.
                        if( (nro_cuota%2!=0 and nro_cuota<=cuotas_para_vendedor) or (cuota_item.plan_de_pago.cantidad_de_cuotas<=12 and nro_cuota<=12) ):                                                                        
                            if k==0:
                                #Guardamos el vendedor asociado a la primera cuota que cumple con la condicion, para tener algo con que comparar.
                                vendedor_actual=cuota_item.vendedor.id
                                fraccion_actual=cuota_item.lote.manzana.fraccion
                            k+=1
                            #print k
                            if(cuota_item.vendedor.id==vendedor_actual and cuota_item.lote.manzana.fraccion==fraccion_actual):                              
                                #comision de las cuotas
                                com=int(cuota_item.total_de_cuotas*(float(cuota_item.plan_de_pago_vendedores.porcentaje_de_cuotas)/float(100)))
                                if(cuota_item.venta.entrega_inicial):
                                    #comision de la entrega inicial, si la hubiere
                                    com_inicial=int(cuota_item.venta.entrega_inicial*(float(cuota_item.plan_de_pago_vendedores.porcentaje_cuota_inicial)/float(100)))
                                    cuota['concepto']="Entrega Inicial"
                                    cuota['cuota_nro']=unicode(0)+'/'+unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                                    cuota['comision']=unicode('{:,}'.format(com_inicial)).replace(",", ".")
                                else:
                                    cuota['concepto']="Pago de Cuota" 
                                    cuota['cuota_nro']=unicode(nro_cuota)+'/'+unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                                    cuota['comision']=unicode('{:,}'.format(com)).replace(",", ".")
                                cuota['fraccion']=unicode(cuota_item.lote.manzana.fraccion)
                                cuota['vendedor']=unicode(cuota_item.vendedor)
                                cuota['fraccion_id']=cuota_item.lote.manzana.fraccion.id
                                cuota['lote']=unicode(cuota_item.lote)
                                cuota['fecha_pago']=unicode(cuota_item.fecha_de_pago)
                                cuota['importe']=unicode('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".")   
        
                                #Sumamos los totales por vendedor
                                total_importe+=cuota_item.total_de_cuotas
                                total_comision+=com
                                #Guardamos el ultimo lote que cumple la condicion en dos variables, por si se convierta en el ultimo lote para cerrar la fraccion
                                #actual, o por si sea el ultimo lote de la lista.
                                anterior=cuota                            
                                ultimo=cuota                       
                            #Hay cambio de lote pero NO es el ultimo elemento todavia
                            else:                                                                                              
                                com=int(cuota_item.total_de_cuotas*(float(cuota_item.plan_de_pago_vendedores.porcentaje_de_cuotas)/float(100)))
                                if(cuota_item.venta.entrega_inicial):
                                    #comision de la entrega inicial, si la hubiere
                                    com_inicial=int(cuota_item.venta.entrega_inicial*(float(cuota_item.plan_de_pago_vendedores.porcentaje_cuota_inicial)/float(100)))
                                    cuota['concepto']="Entrega Inicial"
                                    cuota['cuota_nro']=unicode(0)+'/'+unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                                    cuota['comision']=unicode('{:,}'.format(com_inicial)).replace(",", ".")
                                else:
                                    cuota['concepto']="Pago de Cuota" 
                                    cuota['cuota_nro']=unicode(nro_cuota)+'/'+unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                                    cuota['comision']=unicode('{:,}'.format(com)).replace(",", ".")
                                cuota['fraccion']=unicode(cuota_item.lote.manzana.fraccion)
                                cuota['vendedor']=unicode(cuota_item.vendedor)
                                cuota['fraccion_id']=cuota_item.lote.manzana.fraccion.id
                                cuota['lote']=unicode(cuota_item.lote)
                                cuota['fecha_pago']=unicode(cuota_item.fecha_de_pago)
                                cuota['importe']=unicode('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".")
                                cuota['total_importe']=unicode('{:,}'.format(total_importe)).replace(",", ".")
                                cuota['total_comision']=unicode('{:,}'.format(total_comision)).replace(",", ".") 
                                
                                #Se CERAN  los TOTALES por VENDEDOR                          
                                total_importe=0
                                total_comision=0                                        
                                
                                #Sumamos los totales por fraccion
                                total_importe+=cuota_item.total_de_cuotas
                                total_comision+=com 
                                vendedor_actual=cuota_item.vendedor.id
                                fraccion_actual=cuota_item.lote.manzana.fraccion
                                ultimo=cuota
                            total_general_importe+=cuota_item.total_de_cuotas
                            total_general_comision+=com
                            cuotas.append(cuota)                        
                        #Si es el ultimo lote, cerramos totales de fraccion
                        if (len(lista_pagos)-1 == i):
                            try:
                                ultimo['total_importe']=unicode('{:,}'.format(total_importe)).replace(",", ".") 
                                ultimo['total_comision']=unicode('{:,}'.format(total_comision)).replace(",", ".")             
                                ultimo['total_general_importe']=unicode('{:,}'.format(total_general_importe)).replace(",", ".") 
                                ultimo['total_general_comision']=unicode('{:,}'.format(total_general_comision)).replace(",", ".")          
                            except Exception, error:
                                print error 
                                pass
                                         
                    monto_calculado=int(math.ceil((float(total_general_importe)*float(0.1))/float(2)))   
                    monto_calculado=unicode('{:,}'.format(monto_calculado)).replace(",", ".")
            
                c = RequestContext(request, {
                    'monto_calculado' : monto_calculado,
                    'cuotas' : cuotas,
                    'fecha' : fecha,
                    'fecha_ini' : fecha_ini,
                    'fecha_fin' : fecha_fin,
                    'tipo_liquidacion' : tipo_liquidacion,
                    'tipo_gerente' : tipo_gerente
                })
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

# def informe_movimientos(request):
#     if request.method == 'GET':
#         if request.user.is_authenticated():
#             if (filtros_establecidos(request.GET,'informe_movimientos') == False):
#                 t = loader.get_template('informes/informe_movimientos.html')
#                 c = RequestContext(request, {
#                     'object_list': [],
#                 })
#                 return HttpResponse(t.render(c))
#             else: #Parametros seteados
#                 t = loader.get_template('informes/informe_movimientos.html')
#                 lote_id=request.GET['lote_id']
#                 fecha_ini=request.GET['fecha_ini']
#                 fecha_fin=request.GET['fecha_fin']
#                 x = unicode(lote_id)
#                 fraccion_int = int(x[0:3])
#                 manzana_int = int(x[4:7])
#                 lote_int = int(x[8:])
#                 manzana = Manzana.objects.get(fraccion_id=fraccion_int, nro_manzana=manzana_int)
#                 lote = Lote.objects.get(manzana=manzana.id, nro_lote=lote_int)
#                 lista_movimientos=[]
#                 print 'lote->'+unicode(lote.id)
#                 if fecha_ini != '' and fecha_fin != "":    
#                     fecha_ini_parsed = datetime.strptime(fecha_ini, "%d/%m/%Y").date()
#                     fecha_fin_parsed = datetime.strptime(fecha_fin, "%d/%m/%Y").date()                
#                     try:
#                         lista_pagos = PagoDeCuotas.objects.filter(lote_id=lote.id, fecha_de_pago__range=(fecha_ini_parsed, fecha_fin_parsed))
#                     except Exception, error:
#                         print error
#                         lista_pagos = []
#                         pass 
#                     try:
#                         lista_ventas = Venta.objects.get(lote_id=lote.id, fecha_de_venta__range=(fecha_ini_parsed, fecha_fin_parsed))
#                     except Exception, error:
#                         print error
#                         lista_ventas = []
#                         pass 
#                     try:
#                         lista_reservas = Reserva.objects.get(lote_id=lote.id, fecha_de_reserva__range=(fecha_ini_parsed, fecha_fin_parsed))
#                     except Exception, error:
#                         print error
#                         lista_reservas = []
#                         pass 
#                     try:
#                         lista_cambios = CambioDeLotes.objects.get(lote_id=lote.id, fecha_de_cambio__range=(fecha_ini_parsed, fecha_fin_parsed))
#                     except Exception, error:
#                         print error
#                         lista_cambios = []
#                         pass 
#                     try:
#                         lista_recuperaciones = RecuperacionDeLotes.objects.get(lote_id=lote.id, fecha_de_recuperacion__range=(fecha_ini_parsed, fecha_fin_parsed))
#                     except Exception, error:
#                         print error
#                         lista_recuperaciones = []
#                         pass
#                     try: 
#                         lista_transferencias = TransferenciaDeLotes.objects.get(lote_id=lote.id, fecha_de_transferencia__range=(fecha_ini_parsed, fecha_fin_parsed))
#                     except Exception, error:
#                         print error
#                         lista_transferencias = []
#                         pass                 
#                 else:
#                     try:
#                         lista_pagos = PagoDeCuotas.objects.filter(lote_id=lote.id).order_by('fecha_de_pago')
#                     except Exception, error:
#                         print error
#                         lista_pagos = []
#                         pass
#                     try:
#                         lista_ventas = Venta.objects.get(lote_id=lote.id)
#                     except Exception, error:
#                         print error
#                         lista_ventas =[] 
#                         pass
#                     try:
#                         lista_reservas = Reserva.objects.get(lote_id=lote.id)
#                     except Exception, error:
#                         print error
#                         lista_reservas = []
#                         pass    
#                     try:    
#                         lista_cambios = CambioDeLotes.objects.get(lote_nuevo_id=lote.id)
#                     except Exception, error:
#                         print error
#                         lista_cambios = []
#                         pass
#                     try:    
#                         lista_recuperaciones = RecuperacionDeLotes.objects.get(lote_id=lote.id)
#                     except Exception, error:
#                         print error
#                         lista_recuperaciones = []
#                         pass
#                     try:    
#                         lista_transferencias = TransferenciaDeLotes.objects.get(lote_id=lote.id)
#                     except Exception, error:
#                         print error
#                         lista_transferencias = []
#                         pass
#                 if lista_ventas:
#                     venta = []
#                     venta.append(lista_ventas.fecha_de_venta)
#                     venta.append(lista_ventas.cliente)
#                     venta.append(unicode(0) + '/' + unicode(lista_ventas.plan_de_pago.cantidad_de_cuotas))
#                     venta.append("Entrega inicial")
#                     venta.append(unicode('{:,}'.format(lista_ventas.precio_final_de_venta)).replace(",","."))
#                     venta.append(unicode('{:,}'.format(lista_ventas.entrega_inicial)).replace(",","."))
#                     venta.append(unicode('{:,}'.format(lista_ventas.precio_final_de_venta-lista_ventas.entrega_inicial)).replace(",","."))
#                     lista_movimientos.append(venta)
#                 if lista_pagos:  
#                     saldo_anterior=lista_ventas.precio_final_de_venta
#                     monto=lista_ventas.entrega_inicial
#                     saldo=saldo_anterior-monto
#                     for pago in lista_pagos:
#                         saldo_anterior=saldo
#                         monto=pago.total_de_cuotas
#                         saldo=saldo_anterior-monto
#                         cuota =[]
#                         cuota.append(pago.fecha_de_pago)
#                         cuota.append(pago.cliente)
#                         cuota.append(unicode(get_nro_cuota(pago)) + '/' + unicode(pago.plan_de_pago.cantidad_de_cuotas))
#                         cuota.append("Pago de Cuota")
#                         cuota.append(unicode('{:,}'.format(saldo_anterior)).replace(",","."))
#                         cuota.append(unicode('{:,}'.format(monto)).replace(",","."))
#                         cuota.append(unicode('{:,}'.format(saldo)).replace(",","."))
#                         lista_movimientos.append(cuota)
#                 if lista_recuperaciones:
#                     for pago in lista_pagos:
#                         cuota =[]
#                         cuota.append(pago.fecha_de_pago)
#                         cuota.append(pago.cliente)
#                         cuota.append(unicode(get_nro_cuota(pago)) + '/' + unicode(pago.plan_de_pago.cantidad_de_cuotas))
#                         cuota.append("Cuota Recuperada")
#                         cuota.append(" ")
#                         cuota.append(unicode('{:,}'.format(pago.total_de_cuotas)).replace(",","."))
#                         cuota.append(" ")
#                         lista_movimientos.append(cuota)
#             
#                 ultimo="&lote_id="+lote_id+"&fecha_ini="+fecha_ini+"&fecha_fin="+fecha_fin
#                 paginator = Paginator(lista_movimientos, 25)
#                 page = request.GET.get('page')
#                 try:
#                     lista = paginator.page(page)
#                 except PageNotAnInteger:
#                     lista = paginator.page(1)
#                 except EmptyPage:
#                     lista = paginator.page(paginator.num_pages) 
#                 c = RequestContext(request, {
#                     'lista_movimientos': lista,
#                     'lote_id' : lote_id,
#                     'fecha_ini' : fecha_ini,
#                     'fecha_fin' : fecha_fin,
#                     'ultimo': ultimo
#                 })
#                 return HttpResponse(t.render(c)) 
#         else:
#             return HttpResponseRedirect(reverse('login')) 



def informe_movimientos(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
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
                    x = unicode(lote_id)
                    fraccion_int = int(x[0:3])
                    manzana_int = int(x[4:7])
                    lote_int = int(x[8:])
                    manzana = Manzana.objects.get(fraccion_id=fraccion_int, nro_manzana=manzana_int)
                    lote = Lote.objects.get(manzana=manzana.id, nro_lote=lote_int)
                    lista_movimientos=[]
                    print 'lote->'+unicode(lote.id)
                    if fecha_ini != '' and fecha_fin != '':    
                        fecha_ini_parsed = datetime.strptime(fecha_ini, "%d/%m/%Y").date()
                        fecha_fin_parsed = datetime.strptime(fecha_fin, "%d/%m/%Y").date()                
                        try:
                            lista_ventas = Venta.objects.filter(lote_id=lote.id, fecha_de_venta__range=(fecha_ini_parsed, fecha_fin_parsed)).order_by('-fecha_de_venta')
                            lista_reservas = Reserva.objects.filter(lote_id=lote.id, fecha_de_reserva__range=(fecha_ini_parsed, fecha_fin_parsed))
                            lista_cambios = CambioDeLotes.objects.filter(Q(lote_nuevo_id=lote.id) |Q(lote_a_cambiar=lote.id), fecha_de_cambio__range=(fecha_ini_parsed, fecha_fin_parsed))
                            lista_transferencias = TransferenciaDeLotes.objects.filter(lote_id=lote.id, fecha_de_transferencia__range=(fecha_ini_parsed, fecha_fin_parsed))
                        except Exception, error:
                            print error
                            lista_ventas = []
                            lista_reservas = []
                            lista_cambios = []
                            lista_transferencias = []
                            pass 
                    else:                  
                        try:
                            lista_ventas = Venta.objects.filter(lote_id=lote.id).order_by('-fecha_de_venta')
                            lista_cambios = CambioDeLotes.objects.filter(Q(lote_nuevo_id=lote.id) |Q(lote_a_cambiar=lote.id))
                            lista_reservas = Reserva.objects.filter(lote_id=lote.id)                        
                            lista_transferencias = TransferenciaDeLotes.objects.filter(lote_id=lote.id)
                        except Exception, error:
                            print error
                            lista_ventas =[] 
                            lista_reservas = []
                            lista_cambios = []
                            lista_transferencias = []
                            pass
                    if lista_ventas:
                        print('Hay ventas asociadas a este lote')
                        lista_movimientos = []
                        # En este punto tenemos ventas asociadas a este lote
                        for item_venta in lista_ventas:
                            try: 
                                resumen_venta = {}
                                resumen_venta['fecha_de_venta'] = item_venta.fecha_de_venta 
                                resumen_venta['cliente'] = item_venta.cliente 
                                resumen_venta['cantidad_de_cuotas'] = item_venta.plan_de_pago.cantidad_de_cuotas 
                                resumen_venta['precio_final'] = unicode('{:,}'.format(item_venta.precio_final_de_venta)).replace(",",".")
                                resumen_venta['entrega_inicial'] = unicode('{:,}'.format(item_venta.entrega_inicial)).replace(",",".") 
                                RecuperacionDeLotes.objects.get(venta=item_venta.id)
                                try:
                                    venta_pagos_query_set = get_pago_cuotas(item_venta,None,None)
                                    resumen_venta['recuperacion'] = True
                                except PagoDeCuotas.DoesNotExist:
                                    venta_pagos_query_set = []
                            except RecuperacionDeLotes.DoesNotExist:
                                print 'se encontro la venta no recuperada, la venta actual'                            
                                try:
                                    venta_pagos_query_set = get_pago_cuotas(item_venta,None,None)
                                    resumen_venta['recuperacion'] = False
                                except PagoDeCuotas.DoesNotExist:
                                    venta_pagos_query_set = [] 
                            
                            ventas_pagos_list = []
                            ventas_pagos_list.insert(0,resumen_venta) #El primer elemento de la lista de pagos es el resumen de la venta
                            saldo_anterior=item_venta.precio_final_de_venta
                            monto=item_venta.entrega_inicial
                            saldo=saldo_anterior-monto
                            for pago in venta_pagos_query_set:
                                saldo_anterior=saldo                             
                                monto= long(pago['monto'])
                                saldo=saldo_anterior-monto
                                cuota ={}
                                cuota['fecha_de_pago'] = pago['fecha_de_pago']
                                cuota['id'] = pago['id']
                                cuota['nro_cuota'] = pago['nro_cuota_y_total']
                                cuota['saldo_anterior'] = saldo_anterior
                                cuota['monto'] = pago['monto']
                                cuota['saldo'] = saldo
                                ventas_pagos_list.append(cuota)
                            lista_movimientos.append(ventas_pagos_list)    
                    mostrar_transferencias = False
                    mostrar_mvtos = False
                    mostrar_reservas = False
                    mostrar_cambios = False
                    
                    if lista_movimientos:
                        mostrar_mvtos = True
                    if lista_cambios:
                        mostrar_cambios = True
                    if lista_reservas:
                        mostrar_reservas = True
                    if lista_transferencias:
                        mostrar_transferencias = True
    
                        
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
                        'lista_ventas': lista,
                        'lista_cambios': lista_cambios,
                        'lista_transferencias': lista_transferencias,
                        'lista_reservas': lista_reservas,
                        'mostrar_transferencias': mostrar_transferencias,
                        'mostrar_reservas': mostrar_reservas,
                        'mostrar_cambios': mostrar_cambios,
                        'mostrar_mvtos': mostrar_mvtos,
                        'lote_id' : lote_id,
                        'fecha_ini' : fecha_ini,
                        'fecha_fin' : fecha_fin,
                        'ultimo': ultimo
                    })
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
        
        
        
def lotes_libres_reporte_excel(request):
    # TODO: Danilo, utiliza este template para poner tu logi
    fraccion_ini=request.GET['fraccion_ini']
    fraccion_fin=request.GET['fraccion_fin']
    object_list = []  
    if fraccion_ini and fraccion_fin:
        manzanas = Manzana.objects.filter(fraccion_id__range=(fraccion_ini, fraccion_fin)).order_by('fraccion_id', 'nro_manzana')
        for m in manzanas:
            lotes = Lote.objects.filter(manzana=m.id, estado="1").order_by('nro_lote')
            for l in lotes:
                object_list.append(l)                                  
    else:       
        object_list = Lote.objects.filter(estado="1").order_by('nro_lote')
     
      
    #Totales por FRACCION
    total_importe_cuotas = 0
    total_contado_fraccion = 0
    total_credito_fraccion = 0
    total_superficie_fraccion = 0
    total_lotes = 0 
    
    #Totales GENERALES
    total_general_cuotas = 0
    total_general_contado = 0
    total_general_credito = 0
    total_general_superficie = 0
    total_general_lotes = 0   
    
    lotes = []          
    for index, lote_item in enumerate(object_list):
        lote={}
        # Se setean los datos de cada fila 
        precio_cuota=int(math.ceil(lote_item.precio_credito/130))
        lote['fraccion_id']=unicode(lote_item.manzana.fraccion.id)
        lote['fraccion']=unicode(lote_item.manzana.fraccion)
        lote['lote']=unicode(lote_item.manzana).zfill(3) + "/" + unicode(lote_item.nro_lote).zfill(4)
        lote['superficie']=lote_item.superficie                                    
        lote['precio_contado']=unicode('{:,}'.format(lote_item.precio_contado)).replace(",", ".")                    
        lote['precio_credito']=unicode('{:,}'.format(lote_item.precio_credito)).replace(",", ".")                    
        lote['importe_cuota']=unicode('{:,}'.format(precio_cuota)).replace(",", ".")
        # Se suman los TOTALES por FRACCION
        total_superficie_fraccion += lote_item.superficie 
        total_contado_fraccion += lote_item.precio_contado
        total_credito_fraccion += lote_item.precio_credito
        total_importe_cuotas += precio_cuota
        total_lotes += 1
        
        # Se suman los TOTALES GENERALES
        total_general_cuotas += precio_cuota
        total_general_contado += lote_item.precio_contado
        total_general_credito += lote_item.precio_credito
        total_general_superficie += lote_item.superficie 
        total_general_lotes += 1
        
        #Es el ultimo lote, cerrar totales de fraccion
        if (len(object_list)-1 == index):
            lote['total_importe_cuotas'] = unicode('{:,}'.format(total_importe_cuotas)).replace(",", ".") 
            lote['total_credito_fraccion'] =  unicode('{:,}'.format(total_credito_fraccion)).replace(",", ".")
            lote['total_contado_fraccion'] =  unicode('{:,}'.format(total_contado_fraccion)).replace(",", ".")
            lote['total_superficie_fraccion'] =  unicode('{:,}'.format(total_superficie_fraccion)).replace(",", ".")
            lote['total_lotes'] =  unicode('{:,}'.format(total_lotes)).replace(",", ".")
            
            lote['total_general_cuotas'] = unicode('{:,}'.format(total_general_cuotas)).replace(",", ".") 
            lote['total_general_credito'] =  unicode('{:,}'.format(total_general_credito)).replace(",", ".")
            lote['total_general_contado'] =  unicode('{:,}'.format(total_general_contado)).replace(",", ".")
            lote['total_general_superficie'] =  unicode('{:,}'.format(total_general_superficie)).replace(",", ".")
            lote['total_general_lotes'] =  unicode('{:,}'.format(total_general_lotes)).replace(",", ".")
            
        #Hay cambio de lote pero NO es el ultimo elemento todavia
        elif (lote_item.manzana.fraccion.id != object_list[index+1].manzana.fraccion.id):
            lote['total_importe_cuotas'] = unicode('{:,}'.format(total_importe_cuotas)).replace(",", ".") 
            lote['total_credito_fraccion'] =  unicode('{:,}'.format(total_credito_fraccion)).replace(",", ".")
            lote['total_contado_fraccion'] =  unicode('{:,}'.format(total_contado_fraccion)).replace(",", ".")
            lote['total_superficie_fraccion'] =  unicode('{:,}'.format(total_superficie_fraccion)).replace(",", ".")
            lote['total_lotes'] =  unicode('{:,}'.format(total_lotes)).replace(",", ".")
        # Se CERAN  los TOTALES por FRACCION
            total_importe_cuotas = 0
            total_contado_fraccion = 0
            total_credito_fraccion = 0
            total_superficie_fraccion = 0
            total_lotes = 0
        lotes.append(lote)
       
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
    sheet.write(0, 6, "Precio Cuota", style)  
    #contador de filas
    c=0   
    for lote in lotes:
        c+=1
        sheet.write(c, 0, lote['fraccion'])
        sheet.write(c, 1, lote['fraccion_id'])
        sheet.write(c, 2, lote['lote'])
        sheet.write(c, 3, lote['superficie'])
        sheet.write(c, 4, lote['precio_contado'])
        sheet.write(c, 5, lote['precio_credito'])
        sheet.write(c, 6, lote['importe_cuota'])
        try: 
            if lote['total_importe_cuotas']:
                c += 1
                sheet.write(c, 0, "Totales de Fraccion", style2)  
                sheet.write(c, 2, lote['total_lotes'], style2)
                sheet.write(c, 3, lote['total_superficie_fraccion'], style2)
                sheet.write(c, 4, lote['total_contado_fraccion'], style2)
                sheet.write(c, 5, lote['total_credito_fraccion'], style2)
                sheet.write(c, 6, lote['total_importe_cuotas'], style2)
            
            if lote['total_general_cuotas']:
                c += 1
                sheet.write(c, 0, "Totales Generales", style2)  
                sheet.write(c, 2, lote['total_general_lotes'], style2)
                sheet.write(c, 3, lote['total_general_superficie'], style2)
                sheet.write(c, 4, lote['total_general_contado'], style2)
                sheet.write(c, 5, lote['total_general_credito'], style2)
                sheet.write(c, 6, lote['total_general_cuotas'], style2)            
        except Exception, error:
            print error 
            pass
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
            SELECT pm.nro_manzana manzana, pl.nro_lote lote, pl.id lote_id, pc.id, pc.nombres || ' ' || apellidos cliente, (pp.cantidad_de_cuotas - pv.pagos_realizados) cuotas_atrasadas,
            pv.pagos_realizados cuotas_pagadas, pv.precio_de_cuota importe_cuota,
            (pv.pagos_realizados * pv.precio_de_cuota) total_pagado, pp.cantidad_de_cuotas * pv.precio_de_cuota valor_total_lote,
            (pv.pagos_realizados*100/pp.cantidad_de_cuotas) porc_pagado
            FROM principal_lote pl, principal_cliente pc, principal_venta pv, principal_manzana pm, principal_plandepago pp  
            WHERE pv.plan_de_pago_id = pp.id AND pv.lote_id = pl.id AND pv.cliente_id = pc.id
            AND (pp.cantidad_de_cuotas - pv.pagos_realizados) > 0 AND pl.manzana_id = pm.id AND pp.tipo_de_plan='credito'
            '''
    )      
    if filtros == 0:
        meses_peticion = 0               
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
        fraccion = request.GET['fraccion']
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
                ultimo_pago = PagoDeCuotas.objects.filter(cliente_id= cliente_atrasado['id']).order_by('-fecha_de_pago')[:1].get()
            except PagoDeCuotas.DoesNotExist:
                ultimo_pago = None
                
            if ultimo_pago != None:
                fecha_ultimo_pago = ultimo_pago.fecha_de_pago         
                
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
                    
            #Seteamos los campos restantes
            total_atrasado = meses_diferencia * cliente_atrasado['importe_cuota']
            cliente_atrasado['fecha_ultimo_pago']= datetime.strptime(unicode(fecha_ultimo_pago), "%Y-%m-%d").date()
            cliente_atrasado['lote']=(unicode(cliente_atrasado['manzana']).zfill(3) + "/" + unicode(cliente_atrasado['lote']).zfill(4))
            cliente_atrasado['total_atrasado'] = unicode('{:,}'.format(total_atrasado)).replace(",", ".")
            cliente_atrasado['importe_cuota'] = unicode('{:,}'.format(cliente_atrasado['importe_cuota'])).replace(",", ".")
            cliente_atrasado['total_pagado'] = unicode('{:,}'.format(cliente_atrasado['total_pagado'])).replace(",", ".")
            cliente_atrasado['valor_total_lote'] = unicode('{:,}'.format(cliente_atrasado['valor_total_lote'])).replace(",", ".") 
        if meses_peticion == 0:
            meses_peticion =''  
    
    except Exception, error:
        print error    
        #return HttpResponseServerError("No se pudo obtener el Listado de Clientes Atrasados.")              
    if clientes_atrasados:        
        sheet.write(0, 0, "Cliente", style)
        sheet.write(0, 1, "Lote", style)
        sheet.write(0, 2, "Cuotas Atras.", style)
        sheet.write(0, 3, "Cuotas Pagadas", style)
        sheet.write(0, 4, "Importe c/ cuota", style)
        sheet.write(0, 5, "Total Atrasado", style)
        sheet.write(0, 6, "Total Pagado", style)
        sheet.write(0, 7, "Valor Total del Lote", style)
        sheet.write(0, 8, "% Pagado", style)
        sheet.write(0, 9, "Fec. Ult. Pago", style)
        i = 0
        c = 1
        for i in range(len(clientes_atrasados)):        
            sheet.write(c, 0, clientes_atrasados[i]['cliente'])
            sheet.write(c, 1, unicode(clientes_atrasados[i]['lote']))
            sheet.write(c, 2, unicode(clientes_atrasados[i]['cuotas_atrasadas']))
            sheet.write(c, 3, unicode(clientes_atrasados[i]['cuotas_pagadas']))
            sheet.write(c, 4, unicode(clientes_atrasados[i]['importe_cuota']))
            sheet.write(c, 5, unicode(clientes_atrasados[i]['total_atrasado']))
            sheet.write(c, 6, unicode(clientes_atrasados[i]['total_pagado']))
            sheet.write(c, 7, unicode(clientes_atrasados[i]['valor_total_lote']))
            sheet.write(c, 8, unicode(clientes_atrasados[i]['porc_pagado']))
            sheet.write(c, 9,unicode(clientes_atrasados[i]['fecha_ultimo_pago']))
            c += 1
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
            where pc.fecha_de_pago >= \''''+ unicode(fecha_ini_parsed) +               
            '''\' and pc.fecha_de_pago <= \'''' + unicode(fecha_fin_parsed) +
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
        cuota['fraccion_id']=unicode(cuota_item.lote.manzana.fraccion.id)
        cuota['fraccion']=unicode(cuota_item.lote.manzana.fraccion)
        cuota['lote']=unicode(cuota_item.lote)
        cuota['cliente']=unicode(cuota_item.cliente)
        cuota['cuota_nro']=unicode(nro_cuota)+'/'+unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
        cuota['plan_de_pago']=cuota_item.plan_de_pago.nombre_del_plan
        cuota['fecha_pago']=unicode(cuota_item.fecha_de_pago)
        cuota['total_de_cuotas']=unicode('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".") 
        cuota['total_de_mora']=unicode('{:,}'.format(cuota_item.total_de_mora)).replace(",", ".")
        cuota['total_de_pago']=unicode('{:,}'.format(cuota_item.total_de_pago)).replace(",", ".")

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
            cuota['total_cuotas']=unicode('{:,}'.format(total_cuotas)).replace(",", ".") 
            cuota['total_mora']=unicode('{:,}'.format(total_mora)).replace(",", ".")
            cuota['total_pago']=unicode('{:,}'.format(total_pagos)).replace(",", ".")
                
            cuota['total_general_cuotas']=unicode('{:,}'.format(total_general_cuotas)).replace(",", ".") 
            cuota['total_general_mora']=unicode('{:,}'.format(total_general_mora)).replace(",", ".")
            cuota['total_general_pago']=unicode('{:,}'.format(total_general_pagos)).replace(",", ".")
                        
        #Hay cambio de lote pero NO es el ultimo elemento todavia
        elif (cuota_item.lote.manzana.fraccion.id != object_list[i+1].lote.manzana.fraccion.id):
            cuota['total_cuotas']=unicode('{:,}'.format(total_cuotas)).replace(",", ".") 
            cuota['total_mora']=unicode('{:,}'.format(total_mora)).replace(",", ".")
            cuota['total_pago']=unicode('{:,}'.format(total_pagos)).replace(",", ".")
                    
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
        except Exception, error:
            print error
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
            ok= True               
            for m in manzana_list:
                lotes_list = Lote.objects.filter(manzana_id=m.id).order_by('id')
                for l in lotes_list:
                    ventas = Venta.objects.filter(lote_id=l.id)
                    #Obteniendo la ultima venta
                    for item_venta in ventas:                                           
                        try:
                            RecuperacionDeLotes.objects.get(venta=item_venta.id)
                        except RecuperacionDeLotes.DoesNotExist:
                            #se encontro la venta no recuperada, la venta actual
                            venta = item_venta
                    pagos = get_pago_cuotas(venta, fecha_ini_parsed,fecha_fin_parsed)
                    if pagos:
                        for pago in pagos:
                            montos = calculo_montos_liquidacion_propietarios(pago,venta)
                            monto_inmobiliaria = montos['monto_inmobiliaria']
                            monto_propietario = montos['monto_propietario']
                            # Se setean los datos de cada fila
                            fila={}
                            fila['misma_fraccion'] = ok
                            fila['fraccion']=unicode(fraccion)
                            fila['fecha_de_pago']=unicode(pago['fecha_de_pago'])
                            fila['lote']=unicode(l)
                            fila['cliente']=unicode(venta.cliente)
                            fila['nro_cuota']=unicode(pago['nro_cuota_y_total'])
                            fila['total_de_cuotas']=unicode(pago['monto'])
                            fila['monto_inmobiliaria']=unicode(monto_inmobiliaria)
                            fila['monto_propietario']=unicode(monto_propietario)
                            ok=False
                            # Se suman los TOTALES por FRACCION
                            total_monto_inm += int(monto_inmobiliaria)
                            total_monto_prop += int(monto_propietario)
                            total_monto_pagado += int(pago['monto'])
                            filas.append(fila)
                            #Acumulamos para los TOTALES GENERALES
                            total_general_pagado += int(pago['monto'])
                            total_general_inm += int(monto_inmobiliaria)
                            total_general_prop += int(monto_propietario)
            if total_monto_inm != 0 or total_monto_prop !=0 or total_monto_pagado !=0:
                #Totales por FRACCION
                fila['total_monto_pagado']=unicode(total_monto_pagado)
                fila['total_monto_inmobiliaria']=unicode(total_monto_inm)
                fila['total_monto_propietario']=unicode(total_monto_prop)
                
            #Totales GENERALES
            fila['total_general_pagado']=unicode(total_general_pagado)
            fila['total_general_inmobiliaria']=unicode(total_general_inm)
            fila['total_general_propietario']=unicode(total_general_prop)
            #filas.sort(key=lambda x:x.fecha_de_pago)
        except Exception, error:
            print error                                                                    
    else:
        try:
            fila={}
            propietario_id = request.GET['busqueda']
            fracciones = Fraccion.objects.filter(propietario_id=propietario_id).order_by('id')
            for f in fracciones:
                # Se CERAN  los TOTALES por FRACCION
                total_monto_pagado = 0
                total_monto_inm = 0
                total_monto_prop = 0
                ok=True
                manzanas = Manzana.objects.filter(fraccion_id=f.id)
                for m in manzanas:
                    lotes = Lote.objects.filter(manzana_id=m.id)
                    for l in lotes:
                        ventas = Venta.objects.filter(lote_id=l.id)
                        for item_venta in ventas:
                            try:
                                RecuperacionDeLotes.objects.get(venta=item_venta.id)
                            except RecuperacionDeLotes.DoesNotExist:
                                venta = item_venta
                        pagos = get_pago_cuotas(venta, fecha_ini_parsed,fecha_fin_parsed)
                        if pagos:
                            for pago in pagos:
                                montos = calculo_montos_liquidacion_propietarios(pago,venta)
                                monto_inmobiliaria = montos['monto_inmobiliaria']
                                monto_propietario = montos['monto_propietario']
                                # Se setean los datos de cada fila
                                fila={}
                                fila['misma_fraccion'] = ok
                                fila['fraccion']=unicode(f)
                                fila['fecha_de_pago']=unicode(pago['fecha_de_pago'])
                                fila['lote']=unicode(l)
                                fila['cliente']=unicode(venta.cliente)
                                fila['nro_cuota']=unicode(pago['nro_cuota_y_total'])
                                fila['total_de_cuotas']=unicode(pago['monto'])
                                fila['monto_inmobiliaria']=unicode(monto_inmobiliaria)
                                fila['monto_propietario']=unicode(monto_propietario)
                                ok=False
                                # Se suman los TOTALES por FRACCION
                                total_monto_inm += int(monto_inmobiliaria)
                                total_monto_prop += int(monto_propietario)
                                total_monto_pagado += int(pago['monto'])
                                filas.append(fila)
                                #Acumulamos para los TOTALES GENERALES
                                total_general_pagado += int(pago['monto'])
                                total_general_inm += int(monto_inmobiliaria)
                                total_general_prop += int(monto_propietario)
                if total_monto_inm != 0 or total_monto_prop !=0 or total_monto_pagado !=0:
                    #Totales por FRACCION
                    fila['total_monto_pagado']=unicode('{:,}'.format(total_monto_pagado)).replace(",", ".")
                    fila['total_monto_inmobiliaria']=unicode('{:,}'.format(total_monto_inm)).replace(",", ".")
                    fila['total_monto_propietario']=unicode('{:,}'.format(total_monto_prop)).replace(",", ".")
                    
            if total_monto_inm != 0 or total_monto_prop !=0 or total_monto_pagado !=0:        
                #Totales por FRACCION
                fila['total_monto_pagado']=unicode('{:,}'.format(total_monto_pagado)).replace(",", ".")
                fila['total_monto_inmobiliaria']=unicode('{:,}'.format(total_monto_inm)).replace(",", ".")
                fila['total_monto_propietario']=unicode('{:,}'.format(total_monto_prop)).replace(",", ".")
            #Totales GENERALES
            fila['total_general_pagado']=unicode('{:,}'.format(total_general_pagado)).replace(",", ".")
            fila['total_general_inmobiliaria']=unicode('{:,}'.format(total_general_inm)).replace(",", ".")
            fila['total_general_propietario']=unicode('{:,}'.format(total_general_prop)).replace(",", ".")                         
        except Exception, error:
            print error
        
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    style = xlwt.easyxf('pattern: pattern solid, fore_colour green;'
                              'font: name Arial, bold True;')   
    style2 = xlwt.easyxf('font: name Arial, bold True;')
    style3 = xlwt.easyxf('font: name Arial, bold True;align: horiz center')
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
        if pago['misma_fraccion']:
            #sheet.write(c, 0, "Fraccion: " + pago['fraccion'],style2)                  
            sheet.write_merge(c,c,0,6, pago['fraccion'],style3)
            c +=1
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
        except Exception, error:
            print error 
            pass
        try:
            if (pago['total_general_pagado']): 
                c+=1            
                sheet.write(c, 0, "Liquidacion", style2)
                sheet.write(c, 4, pago['total_general_pagado'],style2)
                sheet.write(c, 5, pago['total_general_inmobiliaria'], style2)
                sheet.write(c, 6, pago['total_general_propietario'], style2)
        except Exception, error:
            print error 
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
    fecha_ini_parsed = unicode(datetime.strptime(fecha_ini, "%d/%m/%Y").date())
    fecha_fin_parsed = unicode(datetime.strptime(fecha_fin, "%d/%m/%Y").date())
    
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
                #comision de las cuotas
                com=int(cuota_item.total_de_cuotas*(float(cuota_item.plan_de_pago_vendedores.porcentaje_de_cuotas)/float(100)))
                if(cuota_item.venta.entrega_inicial):
                    #comision de la entrega inicial, si la hubiere
                    com_inicial=int(cuota_item.venta.entrega_inicial*(float(cuota_item.plan_de_pago_vendedores.porcentaje_cuota_inicial)/float(100)))
                    cuota['concepto']="Entrega Inicial"
                    cuota['cuota_nro']=unicode(0)+'/'+unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                    cuota['comision']=unicode('{:,}'.format(com_inicial)).replace(",", ".")
                else:
                    cuota['concepto']="Pago de Cuota" 
                    cuota['cuota_nro']=unicode(nro_cuota)+'/'+unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                    cuota['comision']=unicode('{:,}'.format(com)).replace(",", ".")
                    
                cuota['fraccion']=unicode(cuota_item.lote.manzana.fraccion)
                cuota['cliente']=unicode(cuota_item.cliente)
                cuota['fraccion_id']=cuota_item.lote.manzana.fraccion.id
                cuota['lote']=unicode(cuota_item.lote)
                cuota['fecha_pago']=unicode(cuota_item.fecha_de_pago)
                cuota['importe']=unicode('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".") 
  
    
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
                anterior['total_importe']=unicode('{:,}'.format(total_importe)).replace(",", ".")
                anterior['total_comision']=unicode('{:,}'.format(total_comision)).replace(",", ".")
        
                #Se CERAN  los TOTALES por FRACCION                            
                total_importe=0
                total_comision=0                                                                                
                com=int(cuota_item.total_de_cuotas*(float(cuota_item.plan_de_pago_vendedores.porcentaje_de_cuotas)/float(100)))
                if(cuota_item.venta.entrega_inicial):
                    #comision de la entrega inicial, si la hubiere
                    com_inicial=int(cuota_item.venta.entrega_inicial*(float(cuota_item.plan_de_pago_vendedores.porcentaje_cuota_inicial)/float(100)))
                    cuota['concepto']="Entrega Inicial"
                    cuota['cuota_nro']=unicode(0)+'/'+unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                    cuota['comision']=unicode('{:,}'.format(com_inicial)).replace(",", ".")
                else:
                    cuota['concepto']="Pago de Cuota" 
                    cuota['cuota_nro']=unicode(nro_cuota)+'/'+unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                    cuota['comision']=unicode('{:,}'.format(com)).replace(",", ".")
                    
                cuota['fraccion']=unicode(cuota_item.lote.manzana.fraccion)
                cuota['cliente']=unicode(cuota_item.cliente)
                cuota['fraccion_id']=cuota_item.lote.manzana.fraccion.id
                cuota['lote']=unicode(cuota_item.lote)
                cuota['fecha_pago']=unicode(cuota_item.fecha_de_pago)
                cuota['importe']=unicode('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".") 
                
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
                ultimo['total_importe']=unicode('{:,}'.format(total_importe)).replace(",", ".") 
                ultimo['total_comision']=unicode('{:,}'.format(total_comision)).replace(",", ".")             
                ultimo['total_general_importe']=unicode('{:,}'.format(total_general_importe)).replace(",", ".") 
                ultimo['total_general_comision']=unicode('{:,}'.format(total_general_comision)).replace(",", ".")          
            except Exception, error:
                print error 
                pass
            
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
    sheet.write(0, 4, "Tipo Cuota", style)
    sheet.write(0, 5, "Cuota Nro.", style)
    sheet.write(0, 6, "Fecha de Pago", style)
    sheet.write(0, 7, "Importe", style)
    sheet.write(0, 8, "Comision", style)
     
    # contador de filas
    c = 0
    for cuota in cuotas:
        c+=1            
        sheet.write(c, 0, cuota['cliente'])
        sheet.write(c, 1, cuota['fraccion'])
        sheet.write(c, 2, cuota['fraccion_id'])
        sheet.write(c, 3, cuota['lote'])
        sheet.write(c, 4, cuota['concepto'])
        sheet.write(c, 5, cuota['cuota_nro'])
        sheet.write(c, 6, cuota['fecha_pago'])
        sheet.write(c, 7, cuota['importe']) 
        sheet.write(c, 8, cuota['comision'])
        try: 
            if cuota['total_importe']:
                c+=1 
                sheet.write(c, 0, "Totales de Fraccion", style2)
                sheet.write(c, 7, cuota['total_importe'])
                sheet.write(c, 8, cuota['total_comision'])           
                # si es la ultima fila    
            if (cuota['total_general_importe']):
                c+=1
                sheet.write(c, 0, "Totales del Vendedor", style2)
                sheet.write(c, 7, cuota['total_general_importe'])
                sheet.write(c, 8, cuota['total_general_comision'])
        except Exception, error:
            print error 
            pass
    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo         
    response['Content-Disposition'] = 'attachment; filename=' + 'liquidacion_vendedores.xls'
    wb.save(response)
    return response 

def liquidacion_gerentes_reporte_excel(request):      
    tipo_liquidacion = request.GET['tipo_liquidacion']
    fecha_ini = request.GET['fecha_ini']
    fecha_fin = request.GET['fecha_fin']
    fecha_ini_parsed = unicode(datetime.strptime(fecha_ini, "%d/%m/%Y").date())
    fecha_fin_parsed = unicode(datetime.strptime(fecha_fin, "%d/%m/%Y").date())
    query=(
    '''
    select pc.* from principal_pagodecuotas pc, principal_lote l, principal_manzana m, principal_fraccion f
    where pc.fecha_de_pago >= \''''+ fecha_ini_parsed +               
    '''\' and pc.fecha_de_pago <= \'''' + fecha_fin_parsed +
    '''\'                 
    and (pc.lote_id = l.id and l.manzana_id=m.id and m.fraccion_id=f.id) order by pc.vendedor_id, f.id, pc.fecha_de_pago
    '''
    )                    

    print(query)
    lista_pagos=list(PagoDeCuotas.objects.raw(query))
    if tipo_liquidacion == 'gerente_ventas':
        tipo_gerente="Gerente de Ventas"
    if tipo_liquidacion == 'gerente_admin':
        tipo_gerente="Gerente Administrativo"
                
    #totales por vendedor
    total_importe=0
    total_comision=0
                
    #totales generales
    total_general_importe=0
    total_general_comision=0
    k=0 #variable de control
    cuotas=[]
    #Seteamos los datos de las filas
    for i, cuota_item in enumerate (lista_pagos):                
        nro_cuota=get_nro_cuota(cuota_item)
        cuota={}
        com=0        
        #Esta es una regla de negocio, los vendedores cobran comisiones segun el numero de cuota, maximo hasta la cuota Nro 9.
        #Si el plan de pago tiene hasta 12 cuotas, los vendedores cobran una comision sobre todas las cuotas.
        cuotas_para_vendedor=((cuota_item.plan_de_pago_vendedores.cantidad_cuotas)*(cuota_item.plan_de_pago_vendedores.intervalos))-cuota_item.plan_de_pago_vendedores.cuota_inicial                  
        #A los vendedores le corresponde comision por las primeras 4 (maximo 5) cuotas impares.
        if( (nro_cuota%2!=0 and nro_cuota<=cuotas_para_vendedor) or (cuota_item.plan_de_pago.cantidad_de_cuotas<=12 and nro_cuota<=12) ):                                                                        
            if k==0:
                #Guardamos el vendedor asociado a la primera cuota que cumple con la condicion, para tener algo con que comparar.
                vendedor_actual=cuota_item.vendedor.id
                fraccion_actual=cuota_item.lote.manzana.fraccion
            k+=1
            #print k
            if(cuota_item.vendedor.id==vendedor_actual and cuota_item.lote.manzana.fraccion==fraccion_actual):                              
                #comision de las cuotas
                com=int(cuota_item.total_de_cuotas*(float(cuota_item.plan_de_pago_vendedores.porcentaje_de_cuotas)/float(100)))
                if(cuota_item.venta.entrega_inicial):
                    #comision de la entrega inicial, si la hubiere
                    com_inicial=int(cuota_item.venta.entrega_inicial*(float(cuota_item.plan_de_pago_vendedores.porcentaje_cuota_inicial)/float(100)))
                    cuota['concepto']="Entrega Inicial"
                    cuota['cuota_nro']=unicode(0)+'/'+unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                    cuota['comision']=unicode('{:,}'.format(com_inicial)).replace(",", ".")
                else:
                    cuota['concepto']="Pago de Cuota" 
                    cuota['cuota_nro']=unicode(nro_cuota)+'/'+unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                    cuota['comision']=unicode('{:,}'.format(com)).replace(",", ".")
                cuota['fraccion']=unicode(cuota_item.lote.manzana.fraccion)
                cuota['vendedor']=unicode(cuota_item.vendedor)
                cuota['fraccion_id']=cuota_item.lote.manzana.fraccion.id
                cuota['lote']=unicode(cuota_item.lote)
                cuota['fecha_pago']=unicode(cuota_item.fecha_de_pago)
                cuota['importe']=unicode('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".")   

                #Sumamos los totales por vendedor
                total_importe+=cuota_item.total_de_cuotas
                total_comision+=com
                #Guardamos el ultimo lote que cumple la condicion en dos variables, por si se convierta en el ultimo lote para cerrar la fraccion
                #actual, o por si sea el ultimo lote de la lista.
                anterior=cuota                            
                ultimo=cuota                       
            #Hay cambio de lote pero NO es el ultimo elemento todavia
            else:                                                                                              
                com=int(cuota_item.total_de_cuotas*(float(cuota_item.plan_de_pago_vendedores.porcentaje_de_cuotas)/float(100)))
                if(cuota_item.venta.entrega_inicial):
                    #comision de la entrega inicial, si la hubiere
                    com_inicial=int(cuota_item.venta.entrega_inicial*(float(cuota_item.plan_de_pago_vendedores.porcentaje_cuota_inicial)/float(100)))
                    cuota['concepto']="Entrega Inicial"
                    cuota['cuota_nro']=unicode(0)+'/'+unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                    cuota['comision']=unicode('{:,}'.format(com_inicial)).replace(",", ".")
                else:
                    cuota['concepto']="Pago de Cuota" 
                    cuota['cuota_nro']=unicode(nro_cuota)+'/'+unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                    cuota['comision']=unicode('{:,}'.format(com)).replace(",", ".")
                cuota['fraccion']=unicode(cuota_item.lote.manzana.fraccion)
                cuota['vendedor']=unicode(cuota_item.vendedor)
                cuota['fraccion_id']=cuota_item.lote.manzana.fraccion.id
                cuota['lote']=unicode(cuota_item.lote)
                cuota['fecha_pago']=unicode(cuota_item.fecha_de_pago)
                cuota['importe']=unicode('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".")
                cuota['total_importe']=unicode('{:,}'.format(total_importe)).replace(",", ".")
                cuota['total_comision']=unicode('{:,}'.format(total_comision)).replace(",", ".") 
                
                #Se CERAN  los TOTALES por VENDEDOR                          
                total_importe=0
                total_comision=0                                        
                
                #Sumamos los totales por fraccion
                total_importe+=cuota_item.total_de_cuotas
                total_comision+=com 
                vendedor_actual=cuota_item.vendedor.id
                fraccion_actual=cuota_item.lote.manzana.fraccion
                ultimo=cuota
            total_general_importe+=cuota_item.total_de_cuotas
            total_general_comision+=com
            cuotas.append(cuota)                        
        #Si es el ultimo lote, cerramos totales de fraccion
        if (len(lista_pagos)-1 == i):
            try:
                ultimo['total_importe']=unicode('{:,}'.format(total_importe)).replace(",", ".") 
                ultimo['total_comision']=unicode('{:,}'.format(total_comision)).replace(",", ".")             
                ultimo['total_general_importe']=unicode('{:,}'.format(total_general_importe)).replace(",", ".") 
                ultimo['total_general_comision']=unicode('{:,}'.format(total_general_comision)).replace(",", ".")          
            except Exception, error:
                print error 
                pass
                                     
    monto_calculado=int(math.ceil((float(total_general_importe)*float(0.1))/float(2)))   
    monto_calculado=unicode('{:,}'.format(monto_calculado)).replace(",", ".")

            
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    style = xlwt.easyxf('pattern: pattern solid, fore_colour green;'
                              'font: name Arial, bold True;')   
    style2 = xlwt.easyxf('font: name Arial, bold True;')
    # cabeceras
    sheet.write(0, 0, "Fecha", style)
    sheet.write(0, 1, "Vendedor", style)
    sheet.write(0, 2, "Cuota Nro.", style)
    sheet.write(0, 3, "Importe", style)
    sheet.write(0, 4, "Comision", style)
       
    # contador de filas
    c = 0
    for i, cuota in enumerate(cuotas): 
        if(i==len(cuotas)-1):
            try:        
                if (cuota['total_general_importe']):
                    c+= 1
                    sheet.write(c, 0, unicode(cuota['fecha_pago']))
                    sheet.write(c, 1, unicode(cuota['vendedor']))
                    sheet.write(c, 2, unicode(cuota['cuota_nro']))       
                    sheet.write(c, 3, unicode(cuota['importe']))
                    sheet.write(c, 4, unicode(cuota['comision']))       
                    c += 1
                    sheet.write(c, 0, "Totales del Vendedor", style2)
                    sheet.write(c, 3, unicode(cuota['total_importe']))
                    sheet.write(c, 4, unicode(cuota['total_comision']))    
                    c += 1
                    sheet.write(c, 0, "Totales Generales", style2)
                    sheet.write(c, 3, unicode(cuota['total_general_importe']))
                    sheet.write(c, 4, unicode(cuota['total_general_comision']))    
            except Exception, error:
                print error 
                pass
        else:           
            try:
                if (cuota['total_importe']):
                    c += 1
                    sheet.write(c, 0, "Totales del Vendedor", style2)
                    sheet.write(c, 3, unicode(cuota['total_importe']))
                    sheet.write(c, 4, unicode(cuota['total_comision']))                                 
            except Exception, error:
                print error 
                pass
            c+=1                        
            sheet.write(c, 0, unicode(cuota['fecha_pago']))
            sheet.write(c, 1, unicode(cuota['vendedor']))
            sheet.write(c, 2, unicode(cuota['cuota_nro']))       
            sheet.write(c, 3, unicode(cuota['importe']))
            sheet.write(c, 4, unicode(cuota['comision']))           
    c+=2
    sheet.write(c, 0, "Gerente: ", style2)
    sheet.write(c, 1, tipo_gerente, style2)
    c+=1
    sheet.write(c, 0, "Liquidacion: ", style2)
    sheet.write(c, 1, monto_calculado, style2)
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
    x = unicode(lote)
    fraccion_int = int(x[0:3])
    manzana_int = int(x[4:7])
    lote_int = int(x[8:])
    manzana = Manzana.objects.get(fraccion_id=fraccion_int, nro_manzana=manzana_int)
    lote = Lote.objects.get(manzana=manzana.id, nro_lote=lote_int)
    print 'lote->'+unicode(lote.id)
    if fecha_ini != '' and fecha_fin != "":    
        fecha_ini_parsed = datetime.strptime(fecha_ini, "%d/%m/%Y").date()
        fecha_fin_parsed = datetime.strptime(fecha_fin, "%d/%m/%Y").date()
        try:
            lista_ventas = Venta.objects.filter(lote_id=lote.id, fecha_de_venta__range=(fecha_ini_parsed, fecha_fin_parsed)).order_by('-fecha_de_venta')
            lista_reservas = Reserva.objects.filter(lote_id=lote.id, fecha_de_reserva__range=(fecha_ini_parsed, fecha_fin_parsed))
            lista_cambios = CambioDeLotes.objects.filter(Q(lote_nuevo_id=lote.id) |Q(lote_a_cambiar=lote.id), fecha_de_cambio__range=(fecha_ini_parsed, fecha_fin_parsed))
            lista_transferencias = TransferenciaDeLotes.objects.filter(lote_id=lote.id, fecha_de_transferencia__range=(fecha_ini_parsed, fecha_fin_parsed))
        except Exception, error:
            print error
            lista_ventas = []
            lista_reservas = []
            lista_cambios = []
            lista_transferencias = []
            pass
    else:
        try:
            lista_ventas = Venta.objects.filter(lote_id=lote.id).order_by('-fecha_de_venta')
            lista_cambios = CambioDeLotes.objects.filter(Q(lote_nuevo_id=lote.id) |Q(lote_a_cambiar=lote.id))
            lista_reservas = Reserva.objects.filter(lote_id=lote.id)                        
            lista_transferencias = TransferenciaDeLotes.objects.filter(lote_id=lote.id)
        except Exception, error:
            print error
            lista_ventas =[] 
            lista_reservas = []
            lista_cambios = []
            lista_transferencias = []
            pass
    if lista_ventas:
        print('Hay ventas asociadas a este lote')
        lista_movimientos = []
        # En este punto tenemos ventas asociadas a este lote
        for item_venta in lista_ventas:
            try: 
                venta = []
                venta.append(item_venta.fecha_de_venta)
                venta.append(item_venta.cliente)
                venta.append(unicode(0) + '/' + unicode(item_venta.plan_de_pago.cantidad_de_cuotas))
                venta.append("Entrega inicial")
                venta.append(unicode('{:,}'.format(item_venta.precio_final_de_venta)).replace(",","."))
                venta.append(unicode('{:,}'.format(item_venta.entrega_inicial)).replace(",","."))
                venta.append(unicode('{:,}'.format(item_venta.precio_final_de_venta-item_venta.entrega_inicial)).replace(",","."))
                lista_movimientos.append(venta)
                RecuperacionDeLotes.objects.get(venta=item_venta.id)
                try:
                    venta_pagos_query_set = get_pago_cuotas(item_venta,None,None)
                except PagoDeCuotas.DoesNotExist:
                    venta_pagos_query_set = []
            except RecuperacionDeLotes.DoesNotExist:
                print 'se encontro la venta no recuperada, la venta actual'                            
                try:
                    venta_pagos_query_set = get_pago_cuotas(item_venta,None,None)
                except PagoDeCuotas.DoesNotExist:
                    venta_pagos_query_set = [] 
            saldo_anterior=item_venta.precio_final_de_venta
            monto=item_venta.entrega_inicial
            saldo=saldo_anterior-monto
            for pago in venta_pagos_query_set:
                saldo_anterior=saldo                             
                monto= long(pago['monto'])
                saldo=saldo_anterior-monto
                cuota =[]
                cuota.append(pago['fecha_de_pago'])
                cuota.append(item_venta.cliente)
                cuota.append(pago['nro_cuota_y_total'])
                cuota.append("Pago de Cuota")
                cuota.append(unicode('{:,}'.format(saldo_anterior)).replace(",","."))
                cuota.append(unicode('{:,}'.format(monto)).replace(",","."))
                cuota.append(unicode('{:,}'.format(saldo)).replace(",","."))
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
        sheet.write(c, 0, unicode(lista_movimientos[i][0]))
        sheet.write(c, 1, unicode(lista_movimientos[i][1]))
        sheet.write(c, 2, unicode(lista_movimientos[i][2]))
        sheet.write(c, 3, unicode(lista_movimientos[i][3]))
        sheet.write(c, 4, unicode(lista_movimientos[i][4]))
        sheet.write(c, 5, unicode(lista_movimientos[i][5]))
        sheet.write(c, 6, unicode(lista_movimientos[i][6]))
        c+=1
    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo         
    response['Content-Disposition'] = 'attachment; filename=' + 'informe_movimientos.xls'
    wb.save(response)
    return response       

def informe_ventas(request):    
    if request.method == 'GET':
        if request.user.is_authenticated():
            if (filtros_establecidos(request.GET,'informe_ventas') == False):
                t = loader.get_template('informes/informe_ventas.html')
                c = RequestContext(request, {
                    'object_list': [],
                })
                return HttpResponse(t.render(c))
            else: #Parametros seteados
                t = loader.get_template('informes/informe_ventas.html')
                lote_id=request.GET['lote_id']
                #ultimo="&tipo_busqueda="+tipo_busqueda+"&fraccion_ini="+f1+"&frac1="+fraccion_ini+"&fraccion_fin="+f2+"&frac2="+fraccion_fin+"&fecha_ini="+fecha_ini+"&fecha_fin="+fecha_fin
                x = unicode(lote_id)
                fraccion_int = int(x[0:3])
                manzana_int = int(x[4:7])
                lote_int = int(x[8:])
                manzana = Manzana.objects.get(fraccion_id=fraccion_int, nro_manzana=manzana_int)
                lote = Lote.objects.get(manzana=manzana.id, nro_lote=lote_int)
                object_list=list(Venta.objects.filter(lote_id=lote.id))               
                               
                paginator = Paginator(object_list, 25)
                page = request.GET.get('page')
                try:
                    lista = paginator.page(page)
                except PageNotAnInteger:
                    lista = paginator.page(1)
                except EmptyPage:
                    lista = paginator.page(paginator.num_pages) 
                   
                c = RequestContext(request, {
                    'lista_ventas': lista,
                    'lote_id' : lote_id
                })
                return HttpResponse(t.render(c))                
        else:
            return HttpResponseRedirect(reverse('login'))
        
            


def calculo_montos_liquidacion_propietarios(pago,venta):
    try:                                                     
        cuotas_para_propietario=((venta.plan_de_pago.cantidad_cuotas_inmobiliaria)*(venta.plan_de_pago.intervalos_cuotas_inmobiliaria))-venta.plan_de_pago.inicio_cuotas_inmobiliaria
        if(int(pago['nro_cuota'])<=cuotas_para_propietario):
            if(int(pago['nro_cuota']) % 2 != 0):    
                monto_inmobiliaria = pago['monto']
                monto_propietario = 0
            else:
                monto_inmobiliaria = int(int(pago['monto']) * (float(venta.plan_de_pago.porcentaje_cuotas_inmobiliaria) / float(100)))
                monto_propietario = int(pago['monto']) - monto_inmobiliaria
        else:
            monto_inmobiliaria = int(int(pago['monto']) * (float(venta.plan_de_pago.porcentaje_cuotas_inmobiliaria) / float(100)))
            monto_propietario = int(pago['monto']) - monto_inmobiliaria
        
        monto={}
        monto['monto_propietario'] = monto_propietario
        monto['monto_inmobiliaria'] = monto_inmobiliaria
        return monto
    except Exception, error:
        print error