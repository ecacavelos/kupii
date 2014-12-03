# -*- encoding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template import RequestContext, loader
from principal.models import Propietario, Fraccion, Lote, Manzana, PagoDeCuotas, Venta, Reserva, CambioDeLotes, RecuperacionDeLotes, TransferenciaDeLotes 
from operator import attrgetter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from datetime import datetime, timedelta
from calendar import monthrange
from principal.common_functions import get_nro_cuota
from django.utils import simplejson




import xlwt


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
                fraccion_ini=request.GET['fraccion_ini']
                fraccion_fin=request.GET['fraccion_fin']
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
                total_costo_fraccion = 0
                total_contado_fraccion = 0
                total_credito_fraccion = 0
                total_superficie_fraccion = 0
                total_lotes = 0
                for index, lote_item in enumerate(object_list):
                    lote={}
                # Se setean los datos de cada fila 
                    lote['fraccion_id']=str(lote_item.manzana.fraccion.id)
                    lote['fraccion']=str(lote_item.manzana.fraccion)
                    lote['lote']=str(lote_item.manzana).zfill(3) + "/" + str(lote_item.nro_lote).zfill(4)
                    lote['superficie']=lote_item.superficie                                    
                    lote['precio_contado']=str('{:,}'.format(lote_item.precio_contado)).replace(",", ".")                    
                    lote['precio_credito']=str('{:,}'.format(lote_item.precio_credito)).replace(",", ".")                    
                    lote['precio_costo']=str('{:,}'.format(lote_item.precio_credito)).replace(",", ".")
                # Se suman los TOTALES por FRACCION
                    total_superficie_fraccion += lote_item.superficie 
                    total_contado_fraccion += lote_item.precio_contado
                    total_credito_fraccion += lote_item.precio_credito
                    total_costo_fraccion += lote_item.precio_costo
                    total_lotes += 1
                #Es el ultimo lote, cerrar totales de fraccion
                    if (len(object_list)-1 == index):
                        lote['total_costo_fraccion'] = str('{:,}'.format(total_costo_fraccion)).replace(",", ".") 
                        lote['total_credito_fraccion'] =  str('{:,}'.format(total_credito_fraccion)).replace(",", ".")
                        lote['total_contado_fraccion'] =  str('{:,}'.format(total_contado_fraccion)).replace(",", ".")
                        lote['total_superficie_fraccion'] =  str('{:,}'.format(total_superficie_fraccion)).replace(",", ".")
                        lote['total_lotes'] =  str('{:,}'.format(total_lotes)).replace(",", ".")
                #Hay cambio de lote pero NO es el ultimo elemento todavia
                    elif (lote_item.manzana.fraccion.id != object_list[index+1].manzana.fraccion.id):
                        lote['total_costo_fraccion'] = str('{:,}'.format(total_costo_fraccion)).replace(",", ".") 
                        lote['total_credito_fraccion'] =  str('{:,}'.format(total_credito_fraccion)).replace(",", ".")
                        lote['total_contado_fraccion'] =  str('{:,}'.format(total_contado_fraccion)).replace(",", ".")
                        lote['total_superficie_fraccion'] =  str('{:,}'.format(total_superficie_fraccion)).replace(",", ".")
                        lote['total_lotes'] =  str('{:,}'.format(total_lotes)).replace(",", ".")
                    # Se CERAN  los TOTALES por FRACCION
                        total_costo_fraccion = 0
                        total_contado_fraccion = 0
                        total_credito_fraccion = 0
                        total_superficie_fraccion = 0
                        total_lotes = 0
                    lotes.append(lote)
                t = loader.get_template('informes/lotes_libres.html')
                c = RequestContext(request, {
                    'fraccion_ini': fraccion_ini,
                    'fraccion_fin': fraccion_fin,
                    'lista_lotes': lotes,
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
        ventas_a_cuotas = Venta.objects.filter(plan_de_pago_id__tipo_de_plan__iexact = 'credito', fecha_primer_vencimiento__lt=fecha_actual).order_by('cliente')
        object_list=[]
        clientes_atrasados=[]
        for v in ventas_a_cuotas:
            cliente_atrasado={}       
            cuotas_pagadas = v.pagos_realizados
            lote_ventas = v.lote
            cuotas_totales = v.plan_de_pago.cantidad_de_cuotas
            cuotas_atrasadas = cuotas_totales - cuotas_pagadas
            try:
                ultimo_pago = PagoDeCuotas.objects.filter(lote= lote_ventas.id).order_by('-fecha_de_pago')[:1].get()
            except PagoDeCuotas.DoesNotExist:
                ultimo_pago = None
            if ultimo_pago == None:
                fecha_ultimo_pago = v.fecha_primer_vencimiento
            else:
                fecha_ultimo_pago = ultimo_pago.fecha_de_pago
            
            if cuotas_totales != 0:
                porcentaje_pagado = (cuotas_pagadas * 100) / cuotas_totales
            else:
                porcentaje_pagado = 0
            cliente_atrasado['manzana']= lote_ventas.manzana.nro_manzana
            cliente_atrasado['lote']= lote_ventas.nro_lote
            cliente_atrasado['cliente']= v.cliente
            cliente_atrasado['cuotas_atrasadas']= cuotas_atrasadas
            cliente_atrasado['cuotas_pagadas']= v.pagos_realizados
            cliente_atrasado['importe_cuota']= str('{:,}'.format(v.precio_de_cuota)).replace(",", ".")
            cliente_atrasado['total_atrasado']= str('{:,}'.format(cuotas_atrasadas * v.precio_de_cuota)).replace(",", ".")
            cliente_atrasado['total_pagado']= str('{:,}'.format(cuotas_pagadas * v.precio_de_cuota)).replace(",", ".")
            cliente_atrasado['valor_total_lote']= str('{:,}'.format(v.precio_de_cuota * cuotas_totales)).replace(",", ".")
            cliente_atrasado['porc_pagado']=  porcentaje_pagado
            cliente_atrasado['fecha_ultimo_pago']= fecha_ultimo_pago
            fecha_primer_vencimiento = v.fecha_primer_vencimiento
            fecha_primer_vencimiento = datetime.combine(fecha_primer_vencimiento, datetime.min.time())
            #diferencia = monthdelta(fecha_actual, d2)
            fecha_resultante = fecha_actual - fecha_primer_vencimiento
            
                        
            print ("Id de venta: "+str(v.id))
            print ("Fecha Actual: "+str(fecha_actual))
            print ("Fecha 1er Vencimieto: "+str(fecha_primer_vencimiento))
            print ("Fecha resultante: "+str(fecha_resultante))
            f1 = fecha_actual.date()
            f2 = fecha_ultimo_pago
            diferencia = (f1-f2).days
            
            #diferencia = fecha_resultante.days()
            print ("Dias de Diferencia: "+str(diferencia))
            meses_diferencia = int (diferencia /30)
            print ("Meses de diferencia: "+str(meses_diferencia))
            print ("Meses de atraso solicitado: "+str(meses_peticion))
            
            if meses_diferencia >= meses_peticion:
                object_list.append(cliente_atrasado)
                print ("Venta agregada")
                print (" ")
            else:
                print ("Venta no agregada")
                print (" ")    
            #print (object_list)
            
        #f = []
        a = len(object_list)
        if a > 0:
            #for i in object_list:
                #lote = Lote.objects.get(pk=i.lote_id)
                #manzana = Manzana.objects.get(pk=lote.manzana_id)
                #f.append(Fraccion.objects.get(pk=manzana.fraccion_id))
                #i.fecha_de_venta = i.fecha_de_venta.strftime("%d/%m/%Y")
                #i.fecha_primer_vencimiento = i.fecha_primer_vencimiento.strftime("%d/%m/%Y")
                #i.precio_final_de_venta = str('{:,}'.format(i.precio_final_de_venta)).replace(",", ".")
                
            paginator = Paginator(object_list, 15)
            page = request.GET.get('page')
            try:
                lista = paginator.page(page)
            except PageNotAnInteger:
                lista = paginator.page(1)
            except EmptyPage:
                lista = paginator.page(paginator.num_pages)
            
            #reporte_clientes_atrasados(object_list)
        else:
            lista=object_list
                
        c = RequestContext(request, {
            'object_list': lista,
            #'fraccion': f,
        })
        return HttpResponse(t.render(c))    
           
    except Exception, error:
            print error    
            return HttpResponseServerError("No se pudo obtener el Listado de Clientes Atrasados.")


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
                fraccion_ini=request.GET['fraccion_ini']
                fraccion_fin=request.GET['fraccion_fin']
                fecha_ini=request.GET['fecha_ini']
                fecha_fin=request.GET['fecha_fin']
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
                t = loader.get_template('informes/informe_general.html')
                c = RequestContext(request, {
                    'fraccion_ini': fraccion_ini,
                    'fraccion_fin': fraccion_fin,
                    'fecha_ini': fecha_ini,
                    'fecha_fin': fecha_fin,
                    'lista_cuotas': cuotas,
                })
                return HttpResponse(t.render(c))                
        else:
            return HttpResponseRedirect("/login") 
                
            
    else:
        t = loader.get_template('informes/informe_general.html')
        c = RequestContext(request, {
            # 'object_list': lista,
            # 'fraccion': f,
        })
        return HttpResponse(t.render(c))    

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
                try:             
                    fecha_ini = request.GET['fecha_ini']
                    fecha_fin = request.GET['fecha_fin']
                    fecha_ini_parsed = datetime.strptime(fecha_ini, "%d/%m/%Y").date()
                    fecha_fin_parsed = datetime.strptime(fecha_fin, "%d/%m/%Y").date()
                    tipo_busqueda = request.GET['tipo_busqueda']
                    lista_fila = []
                    lista_pagos = []
                    lista_totales = []
                    pagos_list = []
                    # fracciones_list=[]
                    lista_lotes = []
                    pagos_list = []
                    total_monto_pagado = 0
                    total_monto_inm = 0
                    total_monto_prop = 0
                    monto_inmobiliaria = 0
                    monto_propietario = 0
                    busqueda = request.GET['busqueda']
                    if tipo_busqueda == "fraccion":
                        try:
                            fraccion_id = request.GET['busqueda']
                            fraccion = Fraccion.objects.get(pk=fraccion_id)                 
                            print('Fraccion: ' + fraccion.nombre + '\n')
                            manzana_list = Manzana.objects.filter(fraccion_id=fraccion_id)                
                            for m in manzana_list:
                                lotes_list = Lote.objects.filter(manzana_id=m.id)
                                for l in lotes_list:
                                    lista_lotes.append(l)
                                    pago = PagoDeCuotas.objects.filter(lote_id=l.id , fecha_de_pago__range=[fecha_ini_parsed, fecha_fin_parsed])
                                    if pago:
                                        pagos_list.append(pago)
                        except Exception, error:
                            print error
                            return HttpResponseServerError("La Fraccion no existe")
                        try:
                            for i in pagos_list:                        
                                for pago in i:
                                    print pago.id
                                    nro_cuota = get_nro_cuota(pago)
                                    if(nro_cuota % 2 != 0): 
                                        if nro_cuota <= pago.plan_de_pago.cantidad_cuotas_inmobiliaria:
                                            monto_inmobiliaria = pago.total_de_cuotas
                                            monto_propietario = 0
                                        else:                                             
                                            monto_inmobiliaria = int(pago.total_de_cuotas * (float(pago.plan_de_pago.porcentaje_cuotas_inmobiliaria) / float(100)))
                                            monto_propietario = pago.total_de_cuotas - monto_inmobiliaria
                                    else:
                                        monto_inmobiliaria = int(pago.total_de_cuotas * (float(pago.plan_de_pago.porcentaje_cuotas_inmobiliaria) / float(100)))
                                        monto_propietario = pago.total_de_cuotas - monto_inmobiliaria
                                        
                                    total_monto_inm += monto_inmobiliaria
                                    total_monto_prop += monto_propietario
                                    total_monto_pagado += pago.total_de_cuotas
                                    lista_fila.append(pago.fecha_de_pago)
                                    lista_fila.append(pago.lote)
                                    lista_fila.append(pago.cliente)
                                    lista_fila.append(str(nro_cuota) + '/' + str(pago.plan_de_pago.cantidad_de_cuotas))
                                    lista_fila.append(str('{:,}'.format(pago.total_de_cuotas)).replace(",", "."))
                                    lista_fila.append(str('{:,}'.format(monto_inmobiliaria)).replace(",", "."))
                                    lista_fila.append(str('{:,}'.format(monto_propietario)).replace(",", "."))                    
                                    lista_pagos.append(lista_fila)
                                    lista_fila = []
                            lista_totales.append(str('{:,}'.format(total_monto_pagado)).replace(",", "."))
                            lista_totales.append(str('{:,}'.format(total_monto_inm)).replace(",", "."))
                            lista_totales.append(str('{:,}'.format(total_monto_prop)).replace(",", "."))    
                        except Exception, error:
                            print error                    
                                                                                       
                    else:                
                        propietario = request.GET['busqueda']    
                        propietario_id = Propietario.objects.get(nombres__icontains=propietario)
                        fracciones_list = Fraccion.objects.filter(propietario_id=propietario_id)
                        for f in fracciones_list:
                            manzana_list = Manzana.objects.filter(fraccion_id=f.id)
                            for m in manzana_list:
                                lotes_list = Lote.objects.filter(manzana_id=m.id)
                                for l in lotes_list:
                                    lista_lotes.append(l)
                                    pago = PagoDeCuotas.objects.filter(lote_id=l.id , fecha_de_pago__range=[fecha_ini_parsed, fecha_fin_parsed])
                                    if pago:
                                        pagos_list.append(pago)                              
                        try:                                                 
                            for i in pagos_list:
                                for pago in i:
                                    print pago.id
                                    nro_cuota = get_nro_cuota(pago)
                                    if(nro_cuota % 2 != 0): 
                                        if nro_cuota <= pago.plan_de_pago.cantidad_cuotas_inmobiliaria:
                                            monto_inmobiliaria = pago.total_de_cuotas
                                            monto_propietario = 0
                                        else:                                             
                                            monto_inmobiliaria = int(pago.total_de_cuotas * (float(pago.plan_de_pago.porcentaje_cuotas_inmobiliaria) / float(100)))
                                            monto_propietario = pago.total_de_cuotas - monto_inmobiliaria
                                    else:
                                        monto_inmobiliaria = int(pago.total_de_cuotas * (float(pago.plan_de_pago.porcentaje_cuotas_inmobiliaria) / float(100)))
                                        monto_propietario = pago.total_de_cuotas - monto_inmobiliaria
                                             
                                    total_monto_inm += monto_inmobiliaria
                                    total_monto_prop += monto_propietario
                                    total_monto_pagado += pago.total_de_cuotas
                                     
                                    lista_fila.append(pago.fecha_de_pago)
                                    lista_fila.append(pago.lote)
                                    lista_fila.append(pago.cliente)
                                    lista_fila.append(str(nro_cuota) + '/' + str(pago.plan_de_pago.cantidad_de_cuotas))
                                    lista_fila.append(str('{:,}'.format(pago.total_de_cuotas)).replace(",", "."))
                                    lista_fila.append(str('{:,}'.format(monto_inmobiliaria)).replace(",", "."))
                                    lista_fila.append(str('{:,}'.format(monto_propietario)).replace(",", "."))                    
                                    lista_pagos.append(lista_fila)
                                    lista_fila = []
                            lista_totales.append(total_monto_pagado)
                            lista_totales.append(total_monto_inm)
                            lista_totales.append(total_monto_prop)     
                        except Exception, error:
                            print error        
                    t = loader.get_template('informes/liquidacion_propietarios.html')         
                    c = RequestContext(request, {
                        'object_list': lista_pagos,
                        'lista_totales' : lista_totales,
                        'fecha_ini':fecha_ini,
                        'fecha_fin':fecha_fin,
                        'tipo_busqueda':tipo_busqueda,
                        'busqueda':busqueda
                    })
                    return HttpResponse(t.render(c))    
                except Exception, error:
                    print error                                 
        else:
            return HttpResponseRedirect("/login")

                         

        
def liquidacion_vendedores(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            t = loader.get_template('informes/liquidacion_vendedores.html')
            c = RequestContext(request, {
                'object_list': [],
            })
            return HttpResponse(t.render(c))                
        else:
            return HttpResponseRedirect("/login") 

    if request.method == 'GET':
        if request.user.is_authenticated():
            t = loader.get_template('informes/liquidacion_vendedores.html')
            c = RequestContext(request, {
                'object_list': [],
            })
            return HttpResponse(t.render(c))                
        else:
            return HttpResponseRedirect("/login") 
        
    else:
        
        t = loader.get_template('informes/liquidacion_vendedores.html')
        c = RequestContext(request, {
            # 'pagos_list': pagos_list,
            # 'lista_totales_vendedor': lista_totales_vendedor,
        })
        return HttpResponse(t.render(c))
                
def liquidacion_gerentes(request):
    if request.method == 'GET':
        try:
            if request.user.is_authenticated():
                t = loader.get_template('informes/liquidacion_gerentes.html')
                c = RequestContext(request, {
                    'object_list': [],
                })
                return HttpResponse(t.render(c))                
            else:
                return HttpResponseRedirect("/login") 
        except Exception, error:
                print error
    if request.method == 'GET':
        try:
            if request.user.is_authenticated():
                t = loader.get_template('informes/liquidacion_gerentes.html')
                c = RequestContext(request, {
                    'object_list': [],
                })
                return HttpResponse(t.render(c))                
            else:
                return HttpResponseRedirect("/login") 
        except Exception, error:
                print error

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
            t = loader.get_template('informes/informe_movimientos.html')
            c = RequestContext(request, {
                'lista_movimientos': lista_movimientos,
                'lote_id' : lote_id,
                'fecha_ini' : fecha_ini,
                'fecha_fin' : fecha_fin     
            })
            return HttpResponse(t.render(c)) 
        else:
            return HttpResponseRedirect("/login") 

def lotes_libres_reporte_excel(request):
    fraccion_ini = request.GET['fraccion_ini']
    fraccion_fin = request.GET['fraccion_fin']
    # at = request.session.get('at', None)
    # TODO: Danilo, utiliza este template para poner tu logi
    # print ('Ejemplo de uso de parametros --> Parametro1' + request.GET['parametro1'])        
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
    total_costo = 0
    # totales generales
    total_general_lotes = 0
    total_general_superficie = 0
    total_general_contado = 0
    total_general_credito = 0
    total_general_costo = 0
        
    object_list = []  # lista de lotes
    if fraccion_ini and fraccion_fin:
        manzanas = Manzana.objects.filter(fraccion_id__range=(fraccion_ini, fraccion_fin))
        for m in manzanas:
            lotes = Lote.objects.filter(manzana=m.id)
            for l in lotes:
                object_list.append(l)
             
    else:       
        object_list = Lote.objects.filter(estado="1").order_by('manzana', 'nro_lote')
     
    lotes = []
    for i in object_list:
        lote = {}
        lote['fraccion_id'] = str(i.manzana.fraccion.id)
        lote['fraccion'] = str(i.manzana.fraccion)
        lote['lote'] = str(i.manzana).zfill(3) + "/" + str(i.nro_lote).zfill(4)
        lote['superficie'] = i.superficie
        lote['precio_contado'] = i.precio_contado
        lote['precio_credito'] = i.precio_credito
        lote['precio_costo'] = i.precio_costo
        lotes.append(lote)
    # contador de filas
    c = 1
    fraccion_actual = lotes[0]['fraccion_id']
    for i in range(len(lotes)):
        # se suman los totales generales
        total_general_lotes += 1
        total_general_superficie += lotes[i]['superficie'] 
        total_general_contado += lotes[i]['precio_contado'] 
        total_general_credito += lotes[i]['precio_credito']
        total_general_costo += lotes[i]['precio_costo']
        # se suman los totales por fracion
        if (lotes[i]['fraccion_id'] == fraccion_actual):
            
            total_lotes += 1
            total_superficie += lotes[i]['superficie'] 
            total_contado += lotes[i]['precio_contado'] 
            total_credito += lotes[i]['precio_credito']
            total_costo += lotes[i]['precio_costo']
                    
            sheet.write(c, 0, str(lotes[i]['fraccion']))
            sheet.write(c, 1, str(lotes[i]['fraccion_id']))
            sheet.write(c, 2, str(lotes[i]['lote']))
            sheet.write(c, 3, str(lotes[i]['superficie']))
            sheet.write(c, 4, str(lotes[i]['precio_contado']))
            sheet.write(c, 5, str(lotes[i]['precio_credito']))
            sheet.write(c, 6, str(lotes[i]['precio_costo']))
            c += 1

        else: 
            c += 1
            sheet.write(c, 0, "Totales de Fraccion", style2)  
            sheet.write(c, 2, str('{:,}'.format(total_lotes)).replace(",", "."))
            sheet.write(c, 3, total_superficie)
            sheet.write(c, 4, str('{:,}'.format(total_contado)).replace(",", "."))
            sheet.write(c, 5, str('{:,}'.format(total_credito)).replace(",", "."))
            sheet.write(c, 6, str('{:,}'.format(total_costo)).replace(",", "."))
            c += 1
            
            sheet.write(c, 0, str(lotes[i]['fraccion']))
            sheet.write(c, 1, str(lotes[i]['fraccion_id']))
            sheet.write(c, 2, str(lotes[i]['lote']))
            sheet.write(c, 3, str(lotes[i]['superficie']))
            sheet.write(c, 4, str(lotes[i]['precio_contado']))
            sheet.write(c, 5, str(lotes[i]['precio_credito']))
            sheet.write(c, 6, str(lotes[i]['precio_costo']))           
            fraccion_actual = lotes[i]['fraccion_id']
            total_lotes = 0
            total_superficie = 0
            total_contado = 0
            total_credito = 0
            total_costo = 0  
            
            
            
            total_superficie += lotes[i]['superficie'] 
            total_contado += lotes[i]['precio_contado'] 
            total_credito += lotes[i]['precio_credito']
            total_costo += lotes[i]['precio_costo']
            total_lotes += 1
            c += 1
        # si es la ultima fila    
        if (i == len(lotes) - 1):   
            c += 1           
            sheet.write(c, 0, "Totales de Fraccion", style2)  
            sheet.write(c, 2, str('{:,}'.format(total_lotes)).replace(",", "."))
            sheet.write(c, 3, total_superficie)
            sheet.write(c, 4, str('{:,}'.format(total_contado)).replace(",", "."))
            sheet.write(c, 5, str('{:,}'.format(total_credito)).replace(",", "."))
            sheet.write(c, 6, str('{:,}'.format(total_costo)).replace(",", "."))
            
        
            
    c += 1
    sheet.write(c, 0, "Totales Generales", style2)
    sheet.write(c, 2, str('{:,}'.format(total_general_lotes)).replace(",", "."))
    sheet.write(c, 3, total_general_superficie)
    sheet.write(c, 4, str('{:,}'.format(total_general_contado)).replace(",", "."))
    sheet.write(c, 5, str('{:,}'.format(total_general_credito)).replace(",", "."))
    sheet.write(c, 6, str('{:,}'.format(total_general_costo)).replace(",", "."))
    
    
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
    style2 = xlwt.easyxf('font: name Arial,66666 bold True;')
    
    if request.GET['meses_de_atraso'] == '':
        meses_peticion = 0
    else:
        meses_peticion = int(request.GET['meses_de_atraso']) 
    
    fecha_actual= datetime.now()
    ventas_a_cuotas = Venta.objects.filter(plan_de_pago_id__tipo_de_plan__iexact = 'credito', fecha_primer_vencimiento__lt=fecha_actual).order_by('cliente')
    object_list=[]
    for v in ventas_a_cuotas:
        cliente_atrasado={}       
        cuotas_pagadas = v.pagos_realizados
        lote_ventas = v.lote
        cuotas_totales = v.plan_de_pago.cantidad_de_cuotas
        cuotas_atrasadas = cuotas_totales - cuotas_pagadas
        try:
            ultimo_pago = PagoDeCuotas.objects.filter(lote= lote_ventas.id).order_by('-fecha_de_pago')[:1].get()
        except PagoDeCuotas.DoesNotExist:
            ultimo_pago = None
        if ultimo_pago == None:
            fecha_ultimo_pago = v.fecha_primer_vencimiento
        else:
            fecha_ultimo_pago = ultimo_pago.fecha_de_pago
        
        if cuotas_totales != 0:
            porcentaje_pagado = (cuotas_pagadas * 100) / cuotas_totales
        else:
            porcentaje_pagado = 0
        cliente_atrasado['manzana']= lote_ventas.manzana.nro_manzana
        cliente_atrasado['lote']= lote_ventas.nro_lote
        cliente_atrasado['cliente']= v.cliente
        cliente_atrasado['cuotas_atrasadas']= cuotas_atrasadas
        cliente_atrasado['cuotas_pagadas']= v.pagos_realizados
        cliente_atrasado['importe_cuota']= str('{:,}'.format(v.precio_de_cuota)).replace(",", ".")
        cliente_atrasado['total_atrasado']= str('{:,}'.format(cuotas_atrasadas * v.precio_de_cuota)).replace(",", ".")
        cliente_atrasado['total_pagado']= str('{:,}'.format(cuotas_pagadas * v.precio_de_cuota)).replace(",", ".")
        cliente_atrasado['valor_total_lote']= str('{:,}'.format(v.precio_de_cuota * cuotas_totales)).replace(",", ".")
        cliente_atrasado['porc_pagado']=  porcentaje_pagado
        cliente_atrasado['fecha_ultimo_pago']= fecha_ultimo_pago
        
        f1 = fecha_actual.date()
        f2 = fecha_ultimo_pago.date()
        diferencia = (f1 - f2).days
            
        print ("Dias de Diferencia: " + str(diferencia))
        meses_diferencia = int (diferencia / 30)
        print ("Meses de diferencia: " + str(meses_diferencia))
        print ("Meses de atraso solicitado: " + str(meses_peticion))
        if meses_diferencia >= meses_peticion:
            object_list.append(cliente_atrasado)
                          
    a = len(object_list)
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
        for i in range(len(object_list)):        
            sheet.write(c, 0, str(object_list[i].manzana))
            sheet.write(c, 1, str(object_list[i].lote))
            sheet.write(c, 2, str(object_list[i].cliente))
            sheet.write(c, 3, str(object_list[i].cuotas_atrasadas))
            sheet.write(c, 4, str(object_list[i].cuotas_pagadas))
            sheet.write(c, 5, str(object_list[i].importe_cuota))
            sheet.write(c, 6, str(object_list[i].total_atrasado))
            sheet.write(c, 7, str(object_list[i].total_pagado))
            sheet.write(c, 8, str(object_list[i].valor_total_lote))
            sheet.write(c, 9, str(object_list[i].porc_pagado))
            sheet.write(c, 10, str(object_list[i].fecha_ultimo_pago))
            c += 1
        
    else:
        lista = object_list
    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo         
    response['Content-Disposition'] = 'attachment; filename=' + 'clientes_atrasados.xls'
    wb.save(response)
    return response
        
def informe_general_reporte_excel(request):   
    fecha_ini = request.GET['fecha_ini']
    fecha_fin = request.GET['fecha_fin']
    fecha_ini_parsed = datetime.strptime(fecha_ini, "%d/%m/%Y").date()
    fecha_fin_parsed = datetime.strptime(fecha_fin, "%d/%m/%Y").date()
    fraccion_ini = request.GET['fraccion_ini']
    fraccion_fin = request.GET['fraccion_fin']
    query = (
    '''
    select pc.* from principal_pagodecuotas pc, principal_lote l, principal_manzana m, principal_fraccion f
    where pc.fecha_de_pago >= \'''' + str(fecha_ini_parsed) + 
    '''\' and pc.fecha_de_pago <= \'''' + str(fecha_fin_parsed) + 
    '''\' and f.id>=''' + fraccion_ini + 
    '''
    and f.id<=''' + fraccion_fin + 
    '''
    and (pc.lote_id = l.id and l.manzana_id=m.id and m.fraccion_id=f.id) order by f.id,pc.fecha_de_pago
    '''
    )
         
    print query
 
    object_list = list(PagoDeCuotas.objects.raw(query))
 
    cuotas = []
    for i in object_list:
        nro_cuota = get_nro_cuota(i)
        cuota = {}            
        cuota['fraccion_id'] = i.lote.manzana.fraccion.id
        cuota['fraccion'] = str(i.lote.manzana.fraccion)
        cuota['lote'] = str(i.lote)
        cuota['cliente'] = str(i.cliente)
        cuota['cuota_nro'] = str(nro_cuota) + '/' + str(i.plan_de_pago.cantidad_de_cuotas)
        cuota['plan_de_pago'] = i.plan_de_pago.nombre_del_plan
        cuota['fecha_pago'] = str(i.fecha_de_pago)
        cuota['total_de_cuotas'] = i.total_de_cuotas
        cuota['total_de_mora'] = i.total_de_mora
        cuota['total_de_pago'] = i.total_de_pago
        cuotas.append(cuota)
        
        # cuotas=object_list
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
    
    # wb.save('informe_general.xls')
    # guardamos la primera fraccion para comparar
    fraccion_actual = cuotas[0]['fraccion_id']
    
    total_cuotas = 0
    total_mora = 0
    total_pagos = 0
    total_general_cuotas = 0
    total_general_mora = 0
    total_general_pagos = 0
    
    # i=0
    # contador de filas
    c = 1
    for i in range(len(cuotas)):
    # for i,cuota in enumerate(cuotas,start=1):
        # se suman los totales por fracion
        if (cuotas[i]['fraccion_id'] == fraccion_actual):
            total_cuotas += cuotas[i]['total_de_cuotas']
            total_mora += cuotas[i]['total_de_mora']
            total_pagos += cuotas[i]['total_de_pago']
            
            sheet.write(c, 0, str(cuotas[i]['fraccion']))
            sheet.write(c, 1, str(cuotas[i]['lote']))
            sheet.write(c, 2, str(cuotas[i]['cliente']))
            sheet.write(c, 3, str(cuotas[i]['cuota_nro']))
            sheet.write(c, 4, str(cuotas[i]['plan_de_pago']))
            sheet.write(c, 5, str(cuotas[i]['fecha_pago']))
            sheet.write(c, 6, str(cuotas[i]['total_de_cuotas']))
            sheet.write(c, 7, str(cuotas[i]['total_de_mora']))
            sheet.write(c, 8, str(cuotas[i]['total_de_pago']))
            c += 1
            # ... y acumulamos para los totales generales
            total_general_cuotas += cuotas[i]['total_de_cuotas']
            total_general_mora += cuotas[i]['total_de_mora'] 
            total_general_pagos += cuotas[i]['total_de_pago'] 
            # si es la ultima fila

        else: 
            
            sheet.write(c, 0, "Totales de Fraccion", style2)
            sheet.write(c, 6, total_cuotas)
            sheet.write(c, 7, total_mora)
            sheet.write(c, 8, total_pagos)
            c += 1
            
            sheet.write(c, 0, str(cuotas[i]['fraccion']))
            sheet.write(c, 1, str(cuotas[i]['lote']))
            sheet.write(c, 2, str(cuotas[i]['cliente']))
            sheet.write(c, 3, str(cuotas[i]['cuota_nro']))
            sheet.write(c, 4, str(cuotas[i]['plan_de_pago']))
            sheet.write(c, 5, str(cuotas[i]['fecha_pago']))
            sheet.write(c, 6, str(cuotas[i]['total_de_cuotas']))
            sheet.write(c, 7, str(cuotas[i]['total_de_mora']))
            sheet.write(c, 8, str(cuotas[i]['total_de_pago']))
            
            fraccion_actual = cuotas[i]['fraccion_id']
            total_cuotas = 0;
            total_mora = 0;
            total_pagos = 0;
            total_cuotas += cuotas[i]['total_de_cuotas'];
            total_mora += cuotas[i]['total_de_mora'];
            total_pagos += cuotas[i]['total_de_pago'];
            
        if (i == len(cuotas) - 1):             
            sheet.write(c, 0, "Totales de Fraccion", style2)
            sheet.write(c, 6, total_cuotas, style2)
            sheet.write(c, 7, total_mora, style2)
            sheet.write(c, 8, total_pagos, style2)
            
            
    sheet.write(c + 1, 0, "Totales Generales", style2)
    sheet.write(c + 1, 6, total_general_cuotas, style2)
    sheet.write(c + 1, 7, total_general_mora, style2)
    sheet.write(c + 1, 8, total_general_pagos, style2)
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
    lista_fila = []
    lista_pagos = []
    lista_totales = []
    pagos_list = []
    fracciones_list = []
    c = 1
    if tipo_busqueda == "fraccion":
        fraccion_id = request.GET['busqueda']   
        manzana_list = Manzana.objects.filter(fraccion_id=fraccion_id)
        lista_lotes = []
        pagos_list = []
        total_monto_pagado = 0
        total_monto_inm = 0
        total_monto_prop = 0
        monto_inmobiliaria = 0
        monto_propietario = 0
        for m in manzana_list:
            lotes_list = Lote.objects.filter(manzana_id=m.id)
            for l in lotes_list:
                lista_lotes.append(l)
                pago = PagoDeCuotas.objects.filter(lote_id=l.id , fecha_de_pago__range=[fecha_ini_parsed, fecha_fin_parsed])
                if pago:
                    pagos_list.append(pago)                  
        for i in pagos_list:                        
            for pago in i:
                nro_cuota = get_nro_cuota(pago)
                if(nro_cuota % 2 != 0): 
                    if nro_cuota <= pago.plan_de_pago.cantidad_cuotas_inmobiliaria:
                        monto_inmobiliaria = pago.total_de_cuotas
                        monto_propietario = 0
                    else:
                        monto_inmobiliaria = int(pago.total_de_cuotas * (float(pago.plan_de_pago.porcentaje_cuotas_inmobiliaria) / float(100)))
                        monto_propietario = pago.total_de_cuotas - monto_inmobiliaria
                        
                else:
                    monto_inmobiliaria = int(pago.total_de_cuotas * (float(pago.plan_de_pago.porcentaje_cuotas_inmobiliaria) / float(100)))
                    monto_propietario = pago.total_de_cuotas - monto_inmobiliaria   
                total_monto_inm += monto_inmobiliaria
                total_monto_prop += monto_propietario
                total_monto_pagado += pago.total_de_cuotas  
                try:                      
                    lista_fila.append(pago.fecha_de_pago)
                    lista_fila.append(pago.lote)
                    lista_fila.append(pago.cliente)
                    lista_fila.append(str(nro_cuota) + '/' + str(pago.plan_de_pago.cantidad_de_cuotas))
                    lista_fila.append(str('{:,}'.format(pago.total_de_cuotas)).replace(",", "."))
                    lista_fila.append(str('{:,}'.format(monto_inmobiliaria)).replace(",", "."))
                    lista_fila.append(str('{:,}'.format(monto_propietario)).replace(",", "."))                    
                    lista_pagos.append(lista_fila)
                    lista_fila = []
                except Exception, error:
                    print error
                           
                    
        if pagos_list:
            lista_totales.append(str('{:,}'.format(total_monto_pagado)).replace(",", "."))
            lista_totales.append(str('{:,}'.format(total_monto_inm)).replace(",", "."))
            lista_totales.append(str('{:,}'.format(total_monto_prop)).replace(",", "."))
                                                                   
    else:
        try:
            propietario = request.GET['busqueda']    
            propietario_id = Propietario.objects.get(nombres__icontains=propietario)
            fracciones_list = Fraccion.objects.filter(propietario_id=propietario_id)
            for f in fracciones_list:
                manzana_list = Manzana.objects.filter(fraccion_id=f.id)
                lista_lotes = []
                pagos_list = []
                monto_propietario = 0
                for m in manzana_list:
                    lotes_list = Lote.objects.filter(manzana_id=m.id)
                    for l in lotes_list:
                        lista_lotes.append(l)
                        pago = PagoDeCuotas.objects.filter(lote_id=l.id , fecha_de_pago__range=[fecha_ini_parsed, fecha_fin_parsed])
                        if pago:
                            pagos_list.append(pago)
                                                              
            for i in pagos_list:
                nro_cuota = get_nro_cuota(pago)
                for pago in i:
                    if(nro_cuota % 2 != 0): 
                        if nro_cuota <= pago.plan_de_pago.cantidad_cuotas_inmobiliaria:
                            monto_inmobiliaria = pago.total_de_cuotas
                            monto_propietario = 0
                        else:
                            monto_inmobiliaria = int(pago.total_de_cuotas * (float(pago.plan_de_pago.porcentaje_cuotas_inmobiliaria) / float(100)))
                            monto_propietario = pago.total_de_cuotas - monto_inmobiliaria
                            
                    else:
                        monto_inmobiliaria = int(pago.total_de_cuotas * (float(pago.plan_de_pago.porcentaje_cuotas_inmobiliaria) / float(100)))
                        monto_propietario = pago.total_de_cuotas - monto_inmobiliaria   
                    total_monto_inm += monto_inmobiliaria
                    total_monto_prop += monto_propietario
                    total_monto_pagado += pago.total_de_cuotas              
                    try:
                        lista_fila.append(pago.fecha_de_pago)
                        lista_fila.append(pago.lote)
                        lista_fila.append(pago.cliente)
                        lista_fila.append(str(nro_cuota) + '/' + str(pago.plan_de_pago.cantidad_de_cuotas))
                        lista_fila.append(str('{:,}'.format(pago.total_de_cuotas)).replace(",", "."))
                        lista_fila.append(str('{:,}'.format(monto_inmobiliaria)).replace(",", "."))
                        lista_fila.append(str('{:,}'.format(monto_propietario)).replace(",", "."))                    
                        lista_pagos.append(lista_fila)                                
                        lista_fila = []
                    except Exception, error:
                        print error            
            if pagos_list:
                lista_totales.append(total_monto_pagado)
                lista_totales.append(total_monto_inm)
                lista_totales.append(total_monto_prop)
                                    
        except:
            lista_pagos = []
    
    a = len(lista_pagos)
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
    
    
    for i in range(len(lista_pagos)):                      
        sheet.write(c, 0, str(lista_pagos[i][0]))
        sheet.write(c, 1, str(lista_pagos[i][1]))
        sheet.write(c, 2, str(lista_pagos[i][2]))
        sheet.write(c, 3, str(lista_pagos[i][3]))
        sheet.write(c, 4, str(lista_pagos[i][4]))
        sheet.write(c, 5, str(lista_pagos[i][5]))
        sheet.write(c, 6, str(lista_pagos[i][6]))
        
        c += 1
        if (i == len(lista_pagos) - 1):             
            sheet.write(c, 0, "Liquidacion", style2)
            sheet.write(c, 4, total_monto_pagado)
            sheet.write(c, 5, total_monto_inm)
            sheet.write(c, 6, total_monto_prop)
        
  
    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo         
    response['Content-Disposition'] = 'attachment; filename=' + 'liquidacion_propietarios.xls'
    wb.save(response)
    return response 

def liquidacion_vendedores_reporte_excel(request):   
    
    vendedor_id = request.GET['busqueda']
    # print("vendedor_id ->" + vendedor_id);
    fecha_ini = request.GET['fecha_ini']
    fecha_fin = request.GET['fecha_fin']
    fecha_ini_parsed = str(datetime.strptime(fecha_ini, "%d/%m/%Y").date())
    fecha_fin_parsed = str(datetime.strptime(fecha_fin, "%d/%m/%Y").date())
    
    tipo_busqueda = request.GET['tipo_busqueda']
    if(tipo_busqueda == 'vendedor_id'):
        vendedor_id = request.GET['busqueda']
        print("vendedor_id ->" + vendedor_id)
    if(tipo_busqueda == 'nombre'):
        nombre_vendedor = request.GET['busqueda']
        print("nombre_vendedor ->" + nombre_vendedor)
        vendedor = Vendedor.objects.get(nombres__icontains=nombre_vendedor)
        vendedor_id = str(vendedor.id)
    query = (
    '''
    select pc.* from principal_pagodecuotas pc, principal_lote l, principal_manzana m, principal_fraccion f
    where pc.fecha_de_pago >= \'''' + fecha_ini_parsed + 
    '''\' and pc.fecha_de_pago <= \'''' + fecha_fin_parsed + 
    '''\' and pc.vendedor_id=''' + vendedor_id + 
    ''' 
    and (pc.lote_id = l.id and l.manzana_id=m.id and m.fraccion_id=f.id) order by f.id,pc.fecha_de_pago
    '''
    )
        
        
    object_list = list(PagoDeCuotas.objects.raw(query))
    cuotas = []
    for i in object_list:
        nro_cuota = get_nro_cuota(i)
        if(nro_cuota % 2 != 0 and nro_cuota < 10):
            cuota = {}            
            cuota['fraccion'] = str(i.lote.manzana.fraccion)
            cuota['cliente'] = str(i.cliente)
            cuota['fraccion_id'] = i.lote.manzana.fraccion.id
            cuota['lote'] = str(i.lote)
            cuota['cuota_nro'] = str(nro_cuota) + '/' + str(i.plan_de_pago.cantidad_de_cuotas)
            cuota['fecha_pago'] = str(i.fecha_de_pago)
            cuota['importe'] = i.total_de_cuotas
            cuota['comision'] = int(i.total_de_cuotas * (i.plan_de_pago_vendedores.porcentaje_de_cuotas / 100))
            cuotas.append(cuota)
            
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    style = xlwt.easyxf('pattern: pattern solid, fore_colour green;'
                              'font: name Arial, bold True;')   
    style2 = xlwt.easyxf('font: name Arial, bold True;')
    # cabeceras
    sheet.write(0, 0, "Cliente", style)
    sheet.write(0, 1, "Lote Nro.", style)    
    sheet.write(0, 2, "Cuota Nro.", style)
    sheet.write(0, 3, "Fecha de Pago", style)
    sheet.write(0, 4, "Importe", style)
    sheet.write(0, 5, "Comision", style)
    sheet.write(0, 6, "Fraccion", style)
    # wb.save('informe_general.xls')
    # guardamos la primera fraccion para comparar
    fraccion_actual = cuotas[0]['fraccion_id']
    
    total_importe = 0
    total_comision = 0
    total_general_importe = 0
    total_general_comision = 0
    
    # i=0
    # contador de filas
    c = 1
    for i in range(len(cuotas)):
    # for i,cuota in enumerate(cuotas,start=1):
        # se suman los totales por fracion
        if (cuotas[i]['fraccion_id'] == fraccion_actual):
            
            total_importe += cuotas[i]['importe']
            total_comision += cuotas[i]['comision']
            
            sheet.write(c, 0, str(cuotas[i]['cliente']))
            sheet.write(c, 1, str(cuotas[i]['lote']))
            sheet.write(c, 2, str(cuotas[i]['cuota_nro']))
            sheet.write(c, 3, str(cuotas[i]['fecha_pago']))
            sheet.write(c, 4, str(cuotas[i]['importe']))
            sheet.write(c, 5, str(cuotas[i]['comision']))
            sheet.write(c, 6, str(cuotas[i]['fraccion']))
            # print str(cuotas[i]['importe'])
            
            
            # ... y acumulamos para los totales generales
            total_general_importe += cuotas[i]['importe']
            total_general_comision += cuotas[i]['comision'] 
            c += 1 
           

        else: 
            c += 1
            sheet.write(c, 0, "Totales de Fraccion", style2)
            sheet.write(c, 4, total_importe)
            sheet.write(c, 5, total_comision)
            
            c += 1
            sheet.write(c, 0, str(cuotas[i]['cliente']))
            sheet.write(c, 1, str(cuotas[i]['lote']))
            sheet.write(c, 2, str(cuotas[i]['cuota_nro']))
            sheet.write(c, 3, str(cuotas[i]['fecha_pago']))
            sheet.write(c, 4, str(cuotas[i]['importe']))
            sheet.write(c, 5, str(cuotas[i]['comision']))
            sheet.write(c, 6, str(cuotas[i]['fraccion']))
            
            total_general_importe += cuotas[i]['importe']
            total_general_comision += cuotas[i]['comision'] 
            fraccion_actual = cuotas[i]['fraccion_id']
            total_importe = 0
            total_comision = 0
            
            total_importe += cuotas[i]['importe']
            total_comision += cuotas[i]['comision']
        # si es la ultima fila    
        if (i == len(cuotas) - 1):   
            c += 1           
            sheet.write(c, 0, "Totales de Fraccion", style2)
            sheet.write(c, 4, total_importe, style2)
            sheet.write(c, 5, total_comision, style2)
            
    c += 1
    sheet.write(c, 0, "Totales del Vendedor", style2)
    sheet.write(c, 4, total_general_importe, style2)
    sheet.write(c, 5, total_general_comision, style2)
    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo         
    response['Content-Disposition'] = 'attachment; filename=' + 'liquidacion_vendedores.xls'
    wb.save(response)
    return response 

def liquidacion_gerentes_reporte_excel(request): 
     
    # vendedor_id = request.GET['busqueda']
    # print("vendedor_id ->" + vendedor_id);
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
    cuotas = []
    for i in object_list:
        nro_cuota = get_nro_cuota(i)
        if(nro_cuota % 2 != 0 and nro_cuota < 10):
            cuota = {}            
            cuota['fraccion_id'] = i.lote.manzana.fraccion.id
            cuota['fraccion'] = str(i.lote.manzana.fraccion)
            cuota['cuota_nro'] = str(nro_cuota) + '/' + str(i.plan_de_pago.cantidad_de_cuotas)
            cuota['cliente'] = str(i.cliente)
            cuota['lote'] = str(i.lote)
            cuota['fecha_pago'] = str(i.fecha_de_pago)
            cuota['monto_pagado'] = i.total_de_cuotas
            cuota['monto_gerente'] = int(i.total_de_cuotas * (i.plan_de_pago.porcentaje_cuotas_gerente / 100))
            cuotas.append(cuota)
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    style = xlwt.easyxf('pattern: pattern solid, fore_colour green;'
                              'font: name Arial, bold True;')   
    style2 = xlwt.easyxf('font: name Arial, bold True;')
    # cabeceras
    sheet.write(0, 0, "Fecha de Pago", style)
    sheet.write(0, 1, "Fraccion", style)    
    sheet.write(0, 2, "Lote Nro.", style)
    sheet.write(0, 3, "Cliente", style)    
    sheet.write(0, 4, "Cuota Nro.", style)    
    sheet.write(0, 5, "Monto Pagado", style)
    sheet.write(0, 6, "Monto Gerente", style)
    
    # wb.save('informe_general.xls')
    # guardamos la primera fraccion para comparar
    fraccion_actual = cuotas[0]['fraccion_id']
    
    total_monto_pagado = 0
    total_monto_gerente = 0
    total_general_pagado = 0
    total_general_gerente = 0
    
    # i=0
    # contador de filas
    c = 1
    for i in range(len(cuotas)):
    # for i,cuota in enumerate(cuotas,start=1):
        # se suman los totales por fracion
        if (cuotas[i]['fraccion_id'] == fraccion_actual):
            
            total_monto_pagado += cuotas[i]['monto_pagado']
            total_monto_gerente += cuotas[i]['monto_gerente']
                    
            
            sheet.write(c, 0, str(cuotas[i]['fecha_pago']))
            sheet.write(c, 1, str(cuotas[i]['fraccion']))
            sheet.write(c, 2, str(cuotas[i]['lote']))
            sheet.write(c, 3, str(cuotas[i]['cliente']))
            sheet.write(c, 4, str(cuotas[i]['cuota_nro']))
            sheet.write(c, 5, str(cuotas[i]['monto_pagado']))
            sheet.write(c, 6, str(cuotas[i]['monto_gerente']))
            
            
            
            # ... y acumulamos para los totales generales
            total_general_pagado += cuotas[i]['monto_pagado']
            total_general_gerente += cuotas[i]['monto_gerente'] 
             
            c += 1

        else: 
            c += 1
            sheet.write(c, 0, "Totales de Fraccion", style2)
            sheet.write(c, 4, total_monto_pagado)
            sheet.write(c, 5, total_monto_gerente)
            
            c += 1
            sheet.write(c, 0, str(cuotas[i]['fecha_pago']))
            sheet.write(c, 1, str(cuotas[i]['fraccion']))
            sheet.write(c, 2, str(cuotas[i]['lote']))
            sheet.write(c, 3, str(cuotas[i]['cliente']))
            sheet.write(c, 4, str(cuotas[i]['cuota_nro']))
            sheet.write(c, 5, str(cuotas[i]['monto_pagado']))
            sheet.write(c, 6, str(cuotas[i]['monto_gerente']))
            
            
            total_general_pagado += cuotas[i]['monto_pagado']
            total_general_gerente += cuotas[i]['monto_gerente'] 
            fraccion_actual = cuotas[i]['fraccion_id']
        
            
            total_monto_pagado += cuotas[i]['monto_pagado']
            total_monto_gerente += cuotas[i]['monto_gerente']
        # si es la ultima fila    
        if (i == len(cuotas) - 1):   
            c += 1           
            sheet.write(c, 0, "Totales de Fraccion", style2)
            sheet.write(c, 4, total_monto_pagado, style2)
            sheet.write(c, 5, total_monto_gerente, style2)
            
    c += 1
    sheet.write(c, 0, "Totales Generales", style2)
    sheet.write(c, 5, total_general_pagado, style2)
    sheet.write(c, 6, total_general_gerente, style2)
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
    return False