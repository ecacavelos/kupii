# -*- encoding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template import RequestContext, loader
from principal.models import Propietario, Fraccion, Lote, Manzana, PagoDeCuotas, Venta, Reserva, CambioDeLotes, RecuperacionDeLotes, TransferenciaDeLotes, Factura 
from operator import itemgetter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from datetime import datetime, timedelta, date
from django.core.urlresolvers import reverse, resolve
from calendar import monthrange
from principal.common_functions import get_nro_cuota
import json
from django.db import connection
import xlwt
import math
from principal.common_functions import *
from principal import permisos
from operator import itemgetter, attrgetter

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
                        manzanas = Manzana.objects.filter(fraccion_id__range=(fraccion_ini, fraccion_fin)).order_by('fraccion', 'nro_manzana')
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
                    total_lotes_fraccion = 0
                    total_general_lotes = 0
                    misma_fraccion = True
                    for index, lote_item in enumerate(object_list):
                        lote={}
                    # Se setean los datos de cada fila
                        if misma_fraccion == True:
                            misma_fraccion = False
                            lote['misma_fraccion'] = misma_fraccion 
                        precio_cuota=int(math.ceil(lote_item.precio_credito/130))
                        lote['fraccion_id']=unicode(lote_item.manzana.fraccion.id)
                        lote['fraccion']=unicode(lote_item.manzana.fraccion)
                        lote['lote']=unicode(lote_item.manzana).zfill(3) + "/" + unicode(lote_item.nro_lote).zfill(4)
                        lote['superficie']=lote_item.superficie                                    
                        lote['precio_contado']=unicode('{:,}'.format(lote_item.precio_contado)).replace(",", ".")                    
                        lote['precio_credito']=unicode('{:,}'.format(lote_item.precio_credito)).replace(",", ".")                    
                        lote['importe_cuota']=unicode('{:,}'.format(precio_cuota)).replace(",", ".")
                        lote['id'] = lote_item.id
                        lote['ultimo_registro'] = False
                        #ESTEEE
                    # Se suman los TOTALES por FRACCION
                        total_superficie_fraccion += lote_item.superficie 
                        total_contado_fraccion += lote_item.precio_contado
                        total_credito_fraccion += lote_item.precio_credito
                        total_importe_cuotas += precio_cuota
                        total_lotes_fraccion += 1
                        total_general_lotes +=1
                    #Es el ultimo lote, cerrar totales de fraccion
                        if (len(object_list)-1 == index):
                            lote['total_importe_cuotas'] = unicode('{:,}'.format(total_importe_cuotas)).replace(",", ".") 
                            lote['total_credito_fraccion'] =  unicode('{:,}'.format(total_credito_fraccion)).replace(",", ".")
                            lote['total_contado_fraccion'] =  unicode('{:,}'.format(total_contado_fraccion)).replace(",", ".")
                            lote['total_superficie_fraccion'] =  unicode('{:,}'.format(total_superficie_fraccion)).replace(",", ".")
                            lote['total_lotes'] =  unicode('{:,}'.format(total_lotes_fraccion)).replace(",", ".")
                            lote['total_general_lotes'] =  unicode('{:,}'.format(total_general_lotes)).replace(",", ".")
                            lote['ultimo_registro'] = True
                            
                    #Hay cambio de fraccion pero NO es el ultimo elemento todavia
                        elif (lote_item.manzana.fraccion.id != object_list[index+1].manzana.fraccion.id):
                            lote['total_importe_cuotas'] = unicode('{:,}'.format(total_importe_cuotas)).replace(",", ".") 
                            lote['total_credito_fraccion'] =  unicode('{:,}'.format(total_credito_fraccion)).replace(",", ".")
                            lote['total_contado_fraccion'] =  unicode('{:,}'.format(total_contado_fraccion)).replace(",", ".")
                            lote['total_superficie_fraccion'] =  unicode('{:,}'.format(total_superficie_fraccion)).replace(",", ".")
                            lote['total_lotes'] =  unicode('{:,}'.format(total_lotes_fraccion)).replace(",", ".")
                        # Se CERAN  los TOTALES por FRACCION
                            total_importe_cuotas = 0
                            total_contado_fraccion = 0
                            total_credito_fraccion = 0
                            total_superficie_fraccion = 0
                            total_lotes_fraccion = 0
                            misma_fraccion = True
                            
                        
                            
                        lotes.append(lote)
                    #sin paginacion
                    lista = lotes
                    #cantidad de registros a mostrar, determinada por el usuario
#                     try:
#                         cant_reg = request.GET['cant_reg']
#                         if cant_reg=='todos':
#                             paginator = Paginator(lotes, len(lotes))
#                         else:
#                             p=range(int(cant_reg))
#                             paginator = Paginator(lotes, len(p))
#                     except:
#                         cant_reg=25
#                         paginator = Paginator(lotes, 25)
# 
#                     page = request.GET.get('page')
#                     try:
#                         lista = paginator.page(page)
#                     except PageNotAnInteger:
#                         lista = paginator.page(1)
#                     except EmptyPage:
#                         lista = paginator.page(paginator.num_pages)

                    c = RequestContext(request, {
                        'tipo_busqueda' : tipo_busqueda,
                        'fraccion_ini': fraccion_ini,
                        'fraccion_fin': fraccion_fin,
                        'ultimo': ultimo,
                        'lista_lotes': lista,
                        #'cant_reg':cant_reg,
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
        #return HttpResponseRedirect("/informes/clientes_atrasados")
        return HttpResponseRedirect(reverse('frontend_clientes_atrasados'))


def obtener_clientes_atrasados(filtros,fraccion, meses_peticion):

    # OBJETO QUE SE UTILIZA PARA CARGAR TODOS LOS CLIENTES ATRASADOS A MOSTRAR
    clientes_atrasados = []

    # QUERY PARA TRAER TODOS LOS LOTES DE LA FRACCION EN CUESTION
    query = (
        '''
        select lote.* from principal_fraccion fraccion, principal_manzana manzana, principal_lote lote WHERE manzana.id = lote.manzana_id AND manzana.fraccion_id = fraccion.id
        '''
    )

    # FILTROS:
    #     NI FRACCION NI MESES DE ATRASO SETEADOS
    #          RETURN 0
    #     FRACCION SETEADA PERO MESES DE ATRASO NO
    #         RETURN 1
    #     FRACCION NO SETEADA PERO SI MESES DE ATRASO
    #         return 2
    #     AMBOS SETEADOS
    #         RETURN 3

    if filtros == 0:
        return []
    elif filtros == 1:
        query += " AND  fraccion.id =  %s "
        cursor = connection.cursor()
        cursor.execute(query, [fraccion])
    elif filtros == 2:
        cursor = connection.cursor()
        cursor.execute(query, [meses_peticion])
    else:
        query += " AND fraccion.id =  %s"
        cursor = connection.cursor()
        cursor.execute(query, [fraccion])

        # Por ultimo, traemos ordenados los registros por el CODIGO DE LOTE
    query += " ORDER BY codigo_paralot "

    # try:
    results = cursor.fetchall()  # LOTES

    for r in results:  # RECORREMOS TODOS LOS LOTES DE LA FRACCION

        cliente_atrasado = {}

        # OBTENER LA ULTIMA VENTA Y SU DETALLE
        ultima_venta = get_ultima_venta(r[0])

        # SE TRATAN LOS CASOS EN DONDE NO SE ENCUENTRA VENTA PARA ALGUN LOTE.
        if ultima_venta != None:
            detalle_cuotas = get_cuotas_detail_by_lote(unicode(str(r[0])))
            hoy = date.today()
            cuotas_a_pagar = obtener_cuotas_a_pagar_full(ultima_venta, hoy, detalle_cuotas,500)  # Maximo atraso = 500 para tener un parametro maximo de atraso en las cuotas.
        else:
            cuotas_a_pagar = []

        if (len(cuotas_a_pagar) >= meses_peticion + 1):

            cuotas_atrasadas = len(cuotas_a_pagar);  # CUOTAS ATRASADAS
            cantidad_cuotas_pagadas = detalle_cuotas['cant_cuotas_pagadas'];  # CUOTAS PAGADAS

            # DATOS DEL CLIENTE
            cliente_atrasado['cliente'] = ultima_venta.cliente.nombres + ' ' + ultima_venta.cliente.apellidos
            cliente_atrasado['direccion_particular'] = ultima_venta.cliente.direccion_particular
            cliente_atrasado['direccion_cobro'] = ultima_venta.cliente.direccion_cobro
            cliente_atrasado['telefono_particular'] = ultima_venta.cliente.telefono_particular
            cliente_atrasado['celular_1'] = ultima_venta.cliente.celular_1

            # FECHA ULTIMO PAGO
            if (len(PagoDeCuotas.objects.filter(venta_id=ultima_venta.id).order_by('-fecha_de_pago')) > 0):
                cliente_atrasado['fecha_ultimo_pago'] = \
                PagoDeCuotas.objects.filter(venta_id=ultima_venta.id).order_by('-fecha_de_pago')[0].fecha_de_pago
            else:
                cliente_atrasado['fecha_ultimo_pago'] = 'Dato no disponible'

            cliente_atrasado['lote'] = ultima_venta.lote.codigo_paralot

            # IMPORTE CUOTA
            cliente_atrasado['importe_cuota'] = unicode('{:,}'.format(ultima_venta.precio_de_cuota)).replace(",", ".")

            # CUOTAS ATRASADAS
            cliente_atrasado['cuotas_atrasadas'] = unicode('{:,}'.format(cuotas_atrasadas)).replace(",", ".")

            # TOTAL ATRASO
            total_atrasado = cuotas_atrasadas * ultima_venta.precio_de_cuota;
            cliente_atrasado['total_atrasado'] = unicode('{:,}'.format(total_atrasado)).replace(",", ".")

            # CUOTAS PAGADAS
            cuotas_pagadas = unicode('{:,}'.format(cantidad_cuotas_pagadas)).replace(",", ".") + '/' + unicode(
                '{:,}'.format(detalle_cuotas['cantidad_total_cuotas'])).replace(",", ".")
            cliente_atrasado['cuotas_pagadas'] = cuotas_pagadas

            # TOTAL PAGADO
            total_pagado = cantidad_cuotas_pagadas * ultima_venta.precio_de_cuota;
            cliente_atrasado['total_pagado'] = unicode('{:,}'.format(total_pagado)).replace(",", ".")

            porcentaje_pagado = round(
                (float(cantidad_cuotas_pagadas) / float(detalle_cuotas['cantidad_total_cuotas'])) * 100);
            cliente_atrasado['porc_pagado'] = unicode('{:,}'.format(int(porcentaje_pagado))).replace(",", ".") + '%'

            clientes_atrasados.append(cliente_atrasado)

    return clientes_atrasados


def clientes_atrasados(request):

    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):

                # TEMPLATE A CARGAR
                t = loader.get_template('informes/clientes_atrasados.html')
                fecha_actual= datetime.datetime.now()

                # FILTROS DISPONIBLES
                filtros = filtros_establecidos(request.GET,'clientes_atrasados')

                # OBJETO QUE SE UTILIZA PARA CARGAR TODOS LOS CLIENTES ATRASADOS A MOSTRAR
                clientes_atrasados= []

                # PARAMETROS
                meses_peticion = 1
                fraccion =''


                # QUERY PARA TRAER TODOS LOS LOTES DE LA FRACCION EN CUESTION
                query = (
                '''
                select lote.* from principal_fraccion fraccion, principal_manzana manzana, principal_lote lote WHERE manzana.id = lote.manzana_id AND manzana.fraccion_id = fraccion.id
                '''
                )

                # FILTROS:
                #     NI FRACCION NI MESES DE ATRASO SETEADOS
                #          RETURN 0
                #     FRACCION SETEADA PERO MESES DE ATRASO NO
                #         RETURN 1
                #     FRACCION NO SETEADA PERO SI MESES DE ATRASO
                #         return 2
                #     AMBOS SETEADOS
                #         RETURN 3

                if filtros == 0:
                    c = RequestContext(request, {
                        'object_list': [],
                    })
                    return HttpResponse(t.render(c))
                elif filtros == 1:
                    fraccion = request.GET['fraccion']
                elif filtros == 2:
                    meses_peticion = int(request.GET['meses_atraso'])
                else:
                    fraccion = request.GET['fraccion']
                    meses_peticion = int(request.GET['meses_atraso'])

                clientes_atrasados = obtener_clientes_atrasados(filtros,fraccion, meses_peticion)
                if meses_peticion == 0:
                    meses_peticion =''
                a = len(clientes_atrasados)
                if a > 0:
                    ultimo="&fraccion="+unicode(fraccion)+"&meses_atraso="+unicode(meses_peticion)
                    lista = clientes_atrasados
                    c = RequestContext(request, {
                        'fraccion': fraccion,
                        'meses_atraso': meses_peticion,
                        'ultimo': ultimo,
                        'object_list': lista,
                        #'cant_reg':cant_reg,
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
                # except Exception, error:
                #     print error
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
        
       

def clientes_atrasados_2(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
                t = loader.get_template('informes/clientes_atrasados.html')
                fecha_actual= datetime.datetime.now()
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
                            cliente_persona = Cliente.objects.get(pk = cliente_atrasado['id'])
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
                        cliente_atrasado['fecha_ultimo_pago']= fecha_ultimo_pago.strftime("%d/%m/%Y")
                        cliente_atrasado['lote']=(unicode(cliente_atrasado['manzana']).zfill(3) + "/" + unicode(cliente_atrasado['lote']).zfill(4))
                        cliente_atrasado['total_atrasado'] = unicode('{:,}'.format(total_atrasado)).replace(",", ".")
                        cliente_atrasado['importe_cuota'] = unicode('{:,}'.format(cliente_atrasado['importe_cuota'])).replace(",", ".")
                        cliente_atrasado['total_pagado'] = unicode('{:,}'.format(cliente_atrasado['total_pagado'])).replace(",", ".")
                        cliente_atrasado['valor_total_lote'] = unicode('{:,}'.format(cliente_atrasado['valor_total_lote'])).replace(",", ".")
                        cliente_atrasado['direccion_particular'] = unicode (cliente_persona.direccion_particular)
                        cliente_atrasado['direccion_cobro']=  unicode (cliente_persona.direccion_cobro )
                        cliente_atrasado['telefono_particular'] = unicode (cliente_persona.telefono_particular)
                        cliente_atrasado['celular_1'] = unicode (cliente_persona.celular_1 )
                    if meses_peticion == 0:
                        meses_peticion =''
                    a = len(clientes_atrasados)
                    if a > 0:
                        ultimo="&fraccion="+unicode(fraccion)+"&meses_atraso="+unicode(meses_peticion)
                        lista = clientes_atrasados
                        #cantidad de registros a mostrar, determinada por el usuario
#                         try:
#                             cant_reg = request.GET['cant_reg']
#                             if cant_reg=='todos':
#                                 paginator = Paginator(clientes_atrasados, len(clientes_atrasados))
#                             else:
#                                 p=range(int(cant_reg))
#                                 paginator = Paginator(clientes_atrasados, len(p))
#                         except:
#                             cant_reg=25
#                             paginator = Paginator(clientes_atrasados, 25)
#
#                         page = request.GET.get('page')
#                         try:
#                             lista = paginator.page(page)
#                         except PageNotAnInteger:
#                             lista = paginator.page(1)
#                         except EmptyPage:
#                             lista = paginator.page(paginator.num_pages)

                        c = RequestContext(request, {
                            'fraccion': fraccion,
                            'meses_atraso': meses_peticion,
                            'ultimo': ultimo,
                            'object_list': lista,
                            #'cant_reg':cant_reg,
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
                    filas_fraccion = []
                    ultimo="&tipo_busqueda="+tipo_busqueda+"&fraccion_ini="+f1+"&frac1="+fraccion_ini+"&fraccion_fin="+f2+"&frac2="+fraccion_fin+"&fecha_ini="+fecha_ini+"&fecha_fin="+fecha_fin
                    g_fraccion = ''
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
                        fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date()
                        fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date()
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
                    
                    total_general_cuotas=0
                    total_general_mora=0
                    total_general_pagos=0
                    #ver esto
                    for i, cuota_item in enumerate(object_list):
                        #Se setean los datos de cada fila
                        cuota={}
                        cuota['misma_fraccion'] = True
                        nro_cuota=get_nro_cuota(cuota_item)
                        if g_fraccion == '':
                            g_fraccion = cuota_item.lote.manzana.fraccion.id
                            cuota['misma_fraccion'] = False
                        if g_fraccion != cuota_item.lote.manzana.fraccion.id:
                            
                            filas_fraccion[0]['misma_fraccion']= False
                            cuotas.extend(filas_fraccion)
                            filas_fraccion = []
                            
                            g_fraccion = cuota_item.lote.manzana.fraccion.id
                            
                            cuota={}
                            #cuota['misma_fraccion'] = False
                            cuota['total_cuotas']=unicode('{:,}'.format(total_cuotas)).replace(",", ".") 
                            cuota['total_mora']=unicode('{:,}'.format(total_mora)).replace(",", ".")
                            cuota['total_pago']=unicode('{:,}'.format(total_pagos)).replace(",", ".")
                            cuota['ultimo_pago'] = True
                            cuotas.append(cuota)
                            
                            total_cuotas=0
                            total_mora=0
                            total_pagos=0
                            
                            cuota = {}
                            cuota['misma_fraccion'] = False
                            cuota['ultimo_pago'] = False
                            cuota['fraccion_id']=unicode(cuota_item.lote.manzana.fraccion.id)
                            cuota['fraccion']=unicode(cuota_item.lote.manzana.fraccion)
                            cuota['lote']=unicode(cuota_item.lote)
                            cuota['cliente']=unicode(cuota_item.cliente)
                            cuota['cuota_nro']=unicode(nro_cuota)+'/'+unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                            cuota['plan_de_pago']=cuota_item.plan_de_pago.nombre_del_plan
                            cuota['fecha_pago']=unicode(cuota_item.fecha_de_pago.strftime("%d/%m/%Y"))
                            cuota['total_de_cuotas']=unicode('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".") 
                            cuota['total_de_mora']=unicode('{:,}'.format(cuota_item.total_de_mora)).replace(",", ".")
                            cuota['total_de_pago']=unicode('{:,}'.format(cuota_item.total_de_pago)).replace(",", ".")
                            #Se suman los totales por fraccion
                            total_cuotas+=cuota_item.total_de_cuotas
                            total_mora+=cuota_item.total_de_mora
                            total_pagos+=cuota_item.total_de_pago
                            
                            total_general_cuotas+=cuota_item.total_de_cuotas
                            total_general_mora+=cuota_item.total_de_mora
                            total_general_pagos+=cuota_item.total_de_pago
                            
                            filas_fraccion.append(cuota)
                            
                        else:
                            cuota['ultimo_pago'] = False
                            cuota['misma_fraccion'] = True
                            cuota['fraccion_id']=unicode(cuota_item.lote.manzana.fraccion.id)
                            cuota['fraccion']=unicode(cuota_item.lote.manzana.fraccion)
                            cuota['lote']=unicode(cuota_item.lote)
                            cuota['cliente']=unicode(cuota_item.cliente)
                            cuota['cuota_nro']=unicode(nro_cuota)+'/'+unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                            cuota['plan_de_pago']=cuota_item.plan_de_pago.nombre_del_plan
                            cuota['fecha_pago']=unicode(cuota_item.fecha_de_pago.strftime("%d/%m/%Y"))
                            cuota['total_de_cuotas']=unicode('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".") 
                            cuota['total_de_mora']=unicode('{:,}'.format(cuota_item.total_de_mora)).replace(",", ".")
                            cuota['total_de_pago']=unicode('{:,}'.format(cuota_item.total_de_pago)).replace(",", ".")
                            #Se suman los totales por fraccion
                            total_cuotas+=cuota_item.total_de_cuotas
                            total_mora+=cuota_item.total_de_mora
                            total_pagos+=cuota_item.total_de_pago
                            
                            total_general_cuotas+=cuota_item.total_de_cuotas
                            total_general_mora+=cuota_item.total_de_mora
                            total_general_pagos+=cuota_item.total_de_pago
                            
                            filas_fraccion.append(cuota)
                                        
                    cuotas.extend(filas_fraccion)
                    cuota={}    
                    cuota['total_cuotas']=unicode('{:,}'.format(total_cuotas)).replace(",", ".") 
                    cuota['total_mora']=unicode('{:,}'.format(total_mora)).replace(",", ".")
                    cuota['total_pago']=unicode('{:,}'.format(total_pagos)).replace(",", ".")
                    cuota['ultimo_pago'] = True
                    cuotas.append(cuota)
                    cuota = {}
                    cuota['total_general_cuotas']=unicode('{:,}'.format(total_general_cuotas)).replace(",", ".") 
                    cuota['total_general_mora']=unicode('{:,}'.format(total_general_mora)).replace(",", ".")
                    cuota['total_general_pago']=unicode('{:,}'.format(total_general_pagos)).replace(",", ".")
                    cuotas.append(cuota)
                    lista = cuotas
#                     #cantidad de registros a mostrar, determinada por el usuario
#                     try:
#                         cant_reg = request.GET['cant_reg']
#                         if cant_reg=='todos':
#                             paginator = Paginator(cuotas, len(cuotas))
#                         else:
#                             p=range(int(cant_reg))
#                             paginator = Paginator(cuotas, len(p))
#                     except:
#                         cant_reg=25
#                         paginator = Paginator(cuotas, 25)
#                     
# 
#                     page = request.GET.get('page')
#                     try:
#                         lista = paginator.page(page)
#                     except PageNotAnInteger:
#                         lista = paginator.page(1)
#                     except EmptyPage:
#                         lista = paginator.page(paginator.num_pages) 
                    c = RequestContext(request, {
                        'tipo_busqueda' : tipo_busqueda,
                        #'cant_reg': cant_reg,
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


#Funcion que devuelve la lista de pagos de para liquidacion de propietarios.
#
def obtener_pagos_liquidacion(entidad_id, tipo_busqueda, fecha_ini, fecha_fin, order_by, busqueda_laber):

    lista_ordenada = []
    filas = []

    if tipo_busqueda == "fraccion":
        lotes = []
        # Totales por FRACCION
        total_monto_pagado = 0
        total_monto_inm = 0
        total_monto_prop = 0

        # Totales GENERALES
        total_general_pagado = 0
        total_general_inm = 0
        total_general_prop = 0

        monto_inmobiliaria = 0
        monto_propietario = 0
        # lista_totales = []
        lista_pagos = []

        try:
            fila = {}
            ok = True
            pagos = []
            fraccion = Fraccion.objects.get(pk=entidad_id)
            # ventas = Venta.objects.filter(lote__manzana__fraccion =fraccion_id).order_by('lote_id')

            query = ('''
                SELECT
                  "principal_lote"."codigo_paralot",
                  "principal_venta"."id",
                  "principal_venta"."lote_id",
                  "principal_venta"."fecha_de_venta",
                  "principal_venta"."cliente_id",
                  "principal_venta"."vendedor_id",
                  "principal_venta"."plan_de_pago_id",
                  "principal_venta"."entrega_inicial",
                  "principal_venta"."precio_de_cuota",
                  "principal_venta"."precio_final_de_venta",
                  "principal_venta"."fecha_primer_vencimiento",
                  "principal_venta"."pagos_realizados",
                  "principal_venta"."importacion_paralot",
                  "principal_venta"."plan_de_pago_vendedor_id",
                  "principal_venta"."monto_cuota_refuerzo",
                  "principal_venta"."recuperado"
                FROM "principal_venta"
                  INNER JOIN "principal_lote" ON ("principal_venta"."lote_id" = "principal_lote"."id")
                  INNER JOIN "principal_manzana" ON ("principal_lote"."manzana_id" = "principal_manzana"."id")
                WHERE "principal_manzana"."fraccion_id" = %s
            ''')

            cursor = connection.cursor()
            cursor.execute(query, [entidad_id])
            ventas = cursor.fetchall()

            for venta_obtenida in ventas:

                venta = Venta.objects.get(pk=venta_obtenida[1])

                if venta.plan_de_pago.tipo_de_plan == "contado":
                    if venta.fecha_de_venta >= fecha_ini and venta.fecha_de_venta <= fecha_fin:
                        montos = calculo_montos_liquidacion_propietarios_contado(venta)
                        monto_inmobiliaria = montos['monto_inmobiliaria']
                        monto_propietario = montos['monto_propietario']
                        total_de_cuotas = int(venta.precio_final_de_venta)
                        fecha_pago_str = unicode(venta.fecha_de_venta)
                        fecha_pago = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                        fecha_pago_order = datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y")
                        # Se setean los datos de cada fila
                        fila = {}
                        fila['misma_fraccion'] = True
                        fila['fraccion'] = unicode(fraccion)
                        fila['fecha_de_pago'] = fecha_pago
                        fila['fecha_de_pago_order'] = fecha_pago_order
                        fila['lote'] = unicode(venta.lote)
                        fila['cliente'] = unicode(venta.cliente)
                        fila['nro_cuota'] = "Venta Contado"
                        fila['total_de_cuotas'] = unicode('{:,}'.format(total_de_cuotas)).replace(",", ".")
                        fila['monto_inmobiliaria'] = unicode('{:,}'.format(monto_inmobiliaria)).replace(",", ".")
                        fila['monto_propietario'] = unicode('{:,}'.format(monto_propietario)).replace(",", ".")

                        monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                        fecha_1 = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                        parts_1 = fecha_1.split("/")
                        year_1 = parts_1[2];
                        mes_1 = int(parts_1[1]) - 1;
                        mes_year = monthNames[mes_1] + "/" + year_1;
                        fila['mes'] = mes_year
                        # Se suman los TOTALES por FRACCION
                        # total_monto_inm += int(monto_inmobiliaria)
                        # total_monto_prop += int(monto_propietario)
                        # total_monto_pagado += int(venta.precio_final_de_venta)

                        filas.append(fila)
                        # Acumulamos para los TOTALES GENERALES
                        total_general_pagado += int(venta.precio_final_de_venta)
                        total_general_inm += int(monto_inmobiliaria)
                        total_general_prop += int(monto_propietario)

                if venta.entrega_inicial != 0:
                    if venta.fecha_de_venta >= fecha_ini and venta.fecha_de_venta <= fecha_fin:
                        montos = calculo_montos_liquidacion_propietarios_entrega_inicial(venta)
                        monto_inmobiliaria = montos['monto_inmobiliaria']
                        monto_propietario = montos['monto_propietario']
                        total_de_cuotas = int(venta.entrega_inicial)
                        fecha_pago_str = unicode(venta.fecha_de_venta)
                        fecha_pago = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                        fecha_pago_order = datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y")
                        # Se setean los datos de cada fila
                        fila = {}
                        fila['misma_fraccion'] = True
                        fila['fraccion'] = unicode(fraccion)
                        fila['fecha_de_pago'] = fecha_pago
                        fila['fecha_de_pago_order'] = fecha_pago_order
                        fila['lote'] = unicode(venta.lote)
                        fila['cliente'] = unicode(venta.cliente)
                        fila['nro_cuota'] = "Entrega Inicial"
                        fila['total_de_cuotas'] = unicode('{:,}'.format(total_de_cuotas)).replace(",", ".")
                        fila['monto_inmobiliaria'] = unicode('{:,}'.format(monto_inmobiliaria)).replace(",", ".")
                        fila['monto_propietario'] = unicode('{:,}'.format(monto_propietario)).replace(",", ".")

                        monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                        fecha_1 = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                        parts_1 = fecha_1.split("/")
                        year_1 = parts_1[2];
                        mes_1 = int(parts_1[1]) - 1;
                        mes_year = monthNames[mes_1] + "/" + year_1;
                        fila['mes'] = mes_year
                        # Se suman los TOTALES por FRACCION
                        # total_monto_inm += int(monto_inmobiliaria)
                        # total_monto_prop += int(monto_propietario)
                        # total_monto_pagado += int(venta.precio_final_de_venta)

                        filas.append(fila)
                        # Acumulamos para los TOTALES GENERALES
                        total_general_pagado += int(venta.entrega_inicial)
                        total_general_inm += int(monto_inmobiliaria)
                        total_general_prop += int(monto_propietario)

                pagos = get_pago_cuotas(venta, fecha_ini, fecha_fin)
                lista_cuotas_inm = []
                lista_cuotas_inm.append(venta.plan_de_pago.inicio_cuotas_inmobiliaria)
                numero_cuota = venta.plan_de_pago.inicio_cuotas_inmobiliaria
                for i in range(venta.plan_de_pago.cantidad_cuotas_inmobiliaria - 1):
                    numero_cuota += venta.plan_de_pago.intervalos_cuotas_inmobiliaria
                    lista_cuotas_inm.append(numero_cuota)

                for pago in pagos:
                    # try:
                    montos = calculo_montos_liquidacion_propietarios(pago, venta, lista_cuotas_inm)
                    monto_inmobiliaria = montos['monto_inmobiliaria']
                    monto_propietario = montos['monto_propietario']
                    total_de_cuotas = int(pago['monto'])
                    fecha_pago_str = unicode(pago['fecha_de_pago'])
                    fecha_pago = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                    fecha_pago_order = datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y")
                    # Se setean los datos de cada fila
                    fila = {}
                    fila['misma_fraccion'] = True
                    fila['fraccion'] = unicode(fraccion)
                    fila['fecha_de_pago'] = fecha_pago
                    fila['fecha_de_pago_order'] = fecha_pago_order
                    fila['lote'] = unicode(pago['lote'])
                    fila['cliente'] = unicode(venta.cliente)

                    cuotas_detalles = get_cuota_information_by_lote(pago['lote'].id, int(pago['nro_cuota']), True, True,
                                                                    venta)
                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                    fecha_1 = cuotas_detalles[0]['fecha']
                    parts_1 = fecha_1.split("/")
                    year_1 = parts_1[2];
                    mes_1 = int(parts_1[1]) - 1;
                    mes_year = monthNames[mes_1] + "/" + year_1;

                    fila['nro_cuota'] = unicode(pago['nro_cuota_y_total'])
                    fila['mes'] = mes_year
                    fila['total_de_cuotas'] = unicode('{:,}'.format(total_de_cuotas)).replace(",", ".")
                    fila['monto_inmobiliaria'] = unicode('{:,}'.format(monto_inmobiliaria)).replace(",", ".")
                    fila['monto_propietario'] = unicode('{:,}'.format(monto_propietario)).replace(",", ".")
                    # Se suman los TOTALES por FRACCION
                    total_monto_inm += int(monto_inmobiliaria)
                    total_monto_prop += int(monto_propietario)
                    total_monto_pagado += int(pago['monto'])
                    filas.append(fila)
                    # Acumulamos para los TOTALES GENERALES
                    total_general_pagado += int(pago['monto'])
                    total_general_inm += int(monto_inmobiliaria)
                    total_general_prop += int(monto_propietario)
                    # except Exception, error:
                    #    print error
                    #    print unicode(pago)


                    # if total_monto_inm != 0 or total_monto_prop !=0 or total_monto_pagado !=0:
                    # Totales por FRACCION
                    # fila['total_monto_pagado']=unicode('{:,}'.format(total_monto_pagado)).replace(",", ".")
                    # fila['total_monto_inmobiliaria']=unicode('{:,}'.format(total_monto_inm)).replace(",", ".")
                    # fila['total_monto_propietario']=unicode('{:,}'.format(total_monto_prop)).replace(",", ".")

            # Totales GENERALES
            # filas = sorted(filas, key=lambda f: f['fecha_de_pago_order'])
            # try:

            # ORDENAMIENTO
            if order_by == "fecha":
                lista_ordenada = sorted(filas, key=lambda k: k['fecha_de_pago'])
            if order_by == "codigo":
                lista_ordenada = sorted(filas, key=lambda k: k['lote'])

            lista_ordenada[0]['misma_fraccion'] = False
            # except Exception, error:
            #    print error
            fila = {}
            fila['total_general_pagado'] = unicode('{:,}'.format(total_general_pagado)).replace(",", ".")
            fila['total_general_inmobiliaria'] = unicode('{:,}'.format(total_general_inm)).replace(",", ".")
            fila['total_general_propietario'] = unicode('{:,}'.format(total_general_prop)).replace(",", ".")
            ley = int(round(total_general_pagado * 0.015))
            fila['ley'] = unicode('{:,}'.format(ley)).replace(",", ".")
            impuesto_renta = int(round((total_general_pagado - ley) * 0.045))
            fila['impuesto_renta'] = unicode('{:,}'.format(impuesto_renta)).replace(",", ".")
            iva_comision = int(round(total_general_inm * 0.1))
            fila['iva_comision'] = unicode('{:,}'.format(iva_comision)).replace(",", ".")
            fila['total_a_cobrar'] = unicode(
                '{:,}'.format(total_general_prop - (ley + impuesto_renta + iva_comision))).replace(",", ".")
            lista_ordenada.append(fila)

        except Exception, error:
            print error

    elif tipo_busqueda == "propietario":

        try:
            # fila={}
            propietario_id = entidad_id  # liquidacion_propietario_por_propietario
            # Se CERAN  los TOTALES por FRACCION
            total_monto_pagado = 0
            total_monto_inm = 0
            total_monto_prop = 0

            # Totales GENERALES
            total_general_pagado = 0
            total_general_inm = 0
            total_general_prop = 0
            ok = True
            filas_fraccion = []

            ventas = Venta.objects.filter(lote__manzana__fraccion__propietario=propietario_id).order_by(
                'lote__manzana__fraccion').select_related()
            ventas_id = []

            for venta in ventas:
                ventas_id.append(venta.id)

            pagos_de_cuotas_ventas = PagoDeCuotas.objects.filter(venta__in=ventas_id, fecha_de_pago__range=(
            fecha_ini, fecha_fin)).order_by('fecha_de_pago').prefetch_related('venta',
                                                                                            'venta__plan_de_pago',
                                                                                            'venta__lote__manzana__fraccion')
            cant_cuotas_pagadas_ventas = PagoDeCuotas.objects.filter(venta__in=ventas_id,
                                                                     fecha_de_pago__lt=fecha_ini).values(
                'venta_id').annotate(Sum('nro_cuotas_a_pagar')).prefetch_related('venta_id')

            no_recu = None
            g_fraccion = ""
            cambio = 0
            fila = {}
            for venta in ventas:
                if venta.fecha_de_venta >= fecha_ini and venta.fecha_de_venta <= fecha_fin:
                    if venta.plan_de_pago.tipo_de_plan == "contado":

                        if g_fraccion == "":
                            g_fraccion = venta.lote.manzana.fraccion

                        if venta.lote.manzana.fraccion != g_fraccion:
                            # Totales por FRACCION
                            try:
                                filas_fraccion = sorted(filas_fraccion, key=lambda f: (f['fecha_de_pago_order']))
                            except Exception, error:
                                print error + ": " + fecha_pago_str

                            filas_fraccion[0]['misma_fraccion'] = False
                            filas.extend(filas_fraccion)
                            filas_fraccion = []
                            fila = {}
                            fila['total_monto_pagado'] = unicode('{:,}'.format(total_monto_pagado)).replace(",", ".")
                            fila['total_monto_inmobiliaria'] = unicode('{:,}'.format(total_monto_inm)).replace(",", ".")
                            fila['total_monto_propietario'] = unicode('{:,}'.format(total_monto_prop)).replace(",", ".")

                            total_monto_inm = 0
                            total_monto_prop = 0
                            total_monto_pagado = 0

                            fila['ultimo_pago'] = True
                            filas.append(fila)
                            g_fraccion = venta.lote.manzana.fraccion
                            ok = True
                        else:

                            montos = calculo_montos_liquidacion_propietarios_contado(venta)
                            monto_inmobiliaria = montos['monto_inmobiliaria']
                            monto_propietario = montos['monto_propietario']
                            total_de_cuotas = int(venta.precio_final_de_venta)
                            fecha_pago_str = unicode(venta.fecha_de_venta)
                            fecha_pago = unicode(
                                datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                            fecha_pago_order = venta.fecha_de_venta
                            # Se setean los datos de cada fila
                            fila = {}
                            fila['misma_fraccion'] = True
                            fila['fraccion'] = unicode(venta.lote.manzana.fraccion)
                            fila['fecha_de_pago'] = fecha_pago
                            fila['fecha_de_pago_order'] = fecha_pago_order
                            fila['lote'] = unicode(venta.lote)
                            fila['cliente'] = unicode(venta.cliente)
                            fila['nro_cuota'] = "Venta Contado"
                            fila['total_de_cuotas'] = unicode('{:,}'.format(total_de_cuotas)).replace(",", ".")
                            fila['monto_inmobiliaria'] = unicode('{:,}'.format(monto_inmobiliaria)).replace(",", ".")
                            fila['monto_propietario'] = unicode('{:,}'.format(monto_propietario)).replace(",", ".")

                            monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov",
                                          "Dic"];
                            fecha_1 = unicode(
                                datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                            parts_1 = fecha_1.split("/")
                            year_1 = parts_1[2];
                            mes_1 = int(parts_1[1]) - 1;
                            mes_year = monthNames[mes_1] + "/" + year_1;
                            fila['mes'] = mes_year
                            # Se suman los TOTALES por FRACCION
                            total_monto_inm += int(monto_inmobiliaria)
                            total_monto_prop += int(monto_propietario)
                            total_monto_pagado += int(venta.precio_final_de_venta)

                            # filas.append(fila)
                            # Acumulamos para los TOTALES GENERALES
                            total_general_pagado += int(venta.precio_final_de_venta)
                            total_general_inm += int(monto_inmobiliaria)
                            total_general_prop += int(monto_propietario)
                            filas_fraccion.append(fila)

                    if venta.entrega_inicial != 0:

                        if g_fraccion == "":
                            g_fraccion = venta.lote.manzana.fraccion

                        if venta.lote.manzana.fraccion != g_fraccion:
                            # Totales por FRACCION
                            try:
                                filas_fraccion = sorted(filas_fraccion, key=lambda f: (f['fecha_de_pago_order']))
                            except Exception, error:
                                print error + ": " + fecha_pago_str

                            filas_fraccion[0]['misma_fraccion'] = False
                            filas.extend(filas_fraccion)
                            filas_fraccion = []
                            fila = {}
                            fila['total_monto_pagado'] = unicode('{:,}'.format(total_monto_pagado)).replace(",", ".")
                            fila['total_monto_inmobiliaria'] = unicode('{:,}'.format(total_monto_inm)).replace(",", ".")
                            fila['total_monto_propietario'] = unicode('{:,}'.format(total_monto_prop)).replace(",", ".")

                            total_monto_inm = 0
                            total_monto_prop = 0
                            total_monto_pagado = 0

                            fila['ultimo_pago'] = True
                            filas.append(fila)
                            g_fraccion = venta.lote.manzana.fraccion
                            ok = True

                        else:

                            montos = calculo_montos_liquidacion_propietarios_entrega_inicial(venta)
                            monto_inmobiliaria = montos['monto_inmobiliaria']
                            monto_propietario = montos['monto_propietario']
                            total_de_cuotas = int(venta.entrega_inicial)
                            fecha_pago_str = unicode(venta.fecha_de_venta)
                            fecha_pago = unicode(
                                datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                            fecha_pago_order = venta.fecha_de_venta
                            # Se setean los datos de cada fila
                            fila = {}
                            fila['misma_fraccion'] = True
                            fila['fraccion'] = unicode(venta.lote.manzana.fraccion)
                            fila['fecha_de_pago'] = fecha_pago
                            fila['fecha_de_pago_order'] = fecha_pago_order
                            fila['lote'] = unicode(venta.lote)
                            fila['cliente'] = unicode(venta.cliente)
                            fila['nro_cuota'] = "Entrega Inicial"
                            fila['total_de_cuotas'] = unicode('{:,}'.format(total_de_cuotas)).replace(",", ".")
                            fila['monto_inmobiliaria'] = unicode('{:,}'.format(monto_inmobiliaria)).replace(",", ".")
                            fila['monto_propietario'] = unicode('{:,}'.format(monto_propietario)).replace(",", ".")

                            monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov",
                                          "Dic"];
                            fecha_1 = unicode(
                                datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                            parts_1 = fecha_1.split("/")
                            year_1 = parts_1[2];
                            mes_1 = int(parts_1[1]) - 1;
                            mes_year = monthNames[mes_1] + "/" + year_1;
                            fila['mes'] = mes_year

                            # Se suman los TOTALES por FRACCION
                            total_monto_inm += int(monto_inmobiliaria)
                            total_monto_prop += int(monto_propietario)
                            total_monto_pagado += int(venta.entrega_inicial)

                            # filas.append(fila)
                            # Acumulamos para los TOTALES GENERALES
                            total_general_pagado += int(venta.entrega_inicial)
                            total_general_inm += int(monto_inmobiliaria)
                            total_general_prop += int(monto_propietario)

                            filas_fraccion.append(fila)

                # print 'se encontro la venta no recuperada, la venta actual'
                pagos = []
                # pagos = get_pago_cuotas(venta, fecha_ini_parsed,fecha_fin_parsed)
                pagos = get_pago_cuotas(venta, fecha_ini, fecha_fin, pagos_de_cuotas_ventas,
                                        cant_cuotas_pagadas_ventas)
                lista_cuotas_inm = []
                lista_cuotas_inm.append(venta.plan_de_pago.inicio_cuotas_inmobiliaria)
                numero_cuota = venta.plan_de_pago.inicio_cuotas_inmobiliaria
                for i in range(venta.plan_de_pago.cantidad_cuotas_inmobiliaria - 1):
                    numero_cuota += venta.plan_de_pago.intervalos_cuotas_inmobiliaria
                    lista_cuotas_inm.append(numero_cuota)
                if pagos:
                    for pago in pagos:
                        # if pago['id'] == 1841840:
                        # print "este es"
                        try:

                            if g_fraccion == "":
                                g_fraccion = venta.lote.manzana.fraccion

                            if pago['fraccion'] != g_fraccion:
                                # Totales por FRACCION
                                try:
                                    filas_fraccion = sorted(filas_fraccion, key=lambda f: (f['fecha_de_pago_order']))
                                except Exception, error:
                                    print error + ": " + fecha_pago_str

                                filas_fraccion[0]['misma_fraccion'] = False
                                filas.extend(filas_fraccion)
                                filas_fraccion = []
                                fila = {}
                                fila['total_monto_pagado'] = unicode('{:,}'.format(total_monto_pagado)).replace(",",
                                                                                                                ".")
                                fila['total_monto_inmobiliaria'] = unicode('{:,}'.format(total_monto_inm)).replace(",",
                                                                                                                   ".")
                                fila['total_monto_propietario'] = unicode('{:,}'.format(total_monto_prop)).replace(",",
                                                                                                                   ".")

                                total_monto_inm = 0
                                total_monto_prop = 0
                                total_monto_pagado = 0

                                fila['ultimo_pago'] = True
                                filas.append(fila)
                                g_fraccion = pago['fraccion']
                                ok = True

                                montos = calculo_montos_liquidacion_propietarios(pago, venta, lista_cuotas_inm)
                                monto_inmobiliaria = montos['monto_inmobiliaria']
                                monto_propietario = montos['monto_propietario']
                                fecha_pago_str = unicode(pago['fecha_de_pago'])
                                try:
                                    fecha_pago = unicode(
                                        datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                except Exception, error:
                                    print error + ": " + fecha_pago_str

                                # Se setean los datos de cada fila
                                fila = {}
                                fila['misma_fraccion'] = True
                                fila['fraccion'] = unicode(venta.lote.manzana.fraccion)
                                fila['fecha_de_pago'] = fecha_pago
                                fila['fecha_de_pago_order'] = pago['fecha_de_pago']
                                fila['lote'] = unicode(pago['lote'])
                                fila['cliente'] = unicode(venta.cliente)
                                fila['nro_cuota'] = unicode(pago['nro_cuota_y_total'])
                                fila['total_de_cuotas'] = unicode('{:,}'.format(int(pago['monto']))).replace(",", ".")
                                fila['monto_inmobiliaria'] = unicode('{:,}'.format(monto_inmobiliaria)).replace(",",
                                                                                                                ".")
                                fila['monto_propietario'] = unicode('{:,}'.format(monto_propietario)).replace(",", ".")

                                cuotas_detalles = get_cuota_information_by_lote(pago['lote'].id, int(pago['nro_cuota']),
                                                                                True, True, venta)
                                monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct",
                                              "Nov", "Dic"];
                                fecha_1 = cuotas_detalles[0]['fecha']
                                parts_1 = fecha_1.split("/")
                                year_1 = parts_1[2];
                                mes_1 = int(parts_1[1]) - 1;
                                mes_year = monthNames[mes_1] + "/" + year_1;
                                fila['mes'] = mes_year

                                # if venta.lote.manzana.fraccion != g_fraccion:
                                ok = False
                                # Se suman los TOTALES por FRACCION
                                total_monto_inm += int(monto_inmobiliaria)
                                total_monto_prop += int(monto_propietario)
                                total_monto_pagado += int(pago['monto'])

                                # Acumulamos para los TOTALES GENERALES
                                total_general_pagado += int(pago['monto'])
                                total_general_inm += int(monto_inmobiliaria)
                                total_general_prop += int(monto_propietario)

                                filas_fraccion.append(fila)

                            else:

                                montos = calculo_montos_liquidacion_propietarios(pago, venta, lista_cuotas_inm)
                                monto_inmobiliaria = montos['monto_inmobiliaria']
                                monto_propietario = montos['monto_propietario']
                                fecha_pago_str = unicode(pago['fecha_de_pago'])
                                try:
                                    fecha_pago = unicode(
                                        datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                except Exception, error:
                                    print error + ": " + fecha_pago_str

                                # Se setean los datos de cada fila
                                fila = {}
                                fila['misma_fraccion'] = True
                                fila['fraccion'] = unicode(venta.lote.manzana.fraccion)
                                fila['fecha_de_pago'] = fecha_pago
                                fila['fecha_de_pago_order'] = pago['fecha_de_pago']
                                fila['lote'] = unicode(pago['lote'])
                                fila['cliente'] = unicode(venta.cliente)
                                fila['nro_cuota'] = unicode(pago['nro_cuota_y_total'])
                                fila['total_de_cuotas'] = unicode('{:,}'.format(int(pago['monto']))).replace(",", ".")
                                fila['monto_inmobiliaria'] = unicode('{:,}'.format(monto_inmobiliaria)).replace(",",
                                                                                                                ".")
                                fila['monto_propietario'] = unicode('{:,}'.format(monto_propietario)).replace(",", ".")

                                cuotas_detalles = get_cuota_information_by_lote(pago['lote'].id, int(pago['nro_cuota']),
                                                                                True, True, venta)
                                monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct",
                                              "Nov", "Dic"];
                                fecha_1 = cuotas_detalles[0]['fecha']
                                parts_1 = fecha_1.split("/")
                                year_1 = parts_1[2];
                                mes_1 = int(parts_1[1]) - 1;
                                mes_year = monthNames[mes_1] + "/" + year_1;
                                fila['mes'] = mes_year

                                # if venta.lote.manzana.fraccion != g_fraccion:
                                ok = False
                                # Se suman los TOTALES por FRACCION
                                total_monto_inm += int(monto_inmobiliaria)
                                total_monto_prop += int(monto_propietario)
                                total_monto_pagado += int(pago['monto'])

                                # Acumulamos para los TOTALES GENERALES
                                total_general_pagado += int(pago['monto'])
                                total_general_inm += int(monto_inmobiliaria)
                                total_general_prop += int(monto_propietario)

                                filas_fraccion.append(fila)

                        except Exception, error:
                            print "Error: " + unicode(error) + ", Id Pago: " + unicode(
                                pago['id']) + ", Fraccion: " + unicode(pago['fraccion']) + ", lote: " + unicode(
                                pago['lote']) + " Nro cuota: " + unicode(unicode(pago['nro_cuota_y_total']))

            # ORDENAMIENTO
            if order_by == "fecha":
                lista_ordenada = sorted(filas_fraccion, key=lambda k: k['fecha_de_pago'])
            if order_by == "codigo":
                lista_ordenada = sorted(filas_fraccion, key=lambda k: k['lote'])

            # Totales GENERALES
            # filas = sorted(filas, key=lambda f: f['fecha_de_pago'])
            if filas_fraccion != []:
                filas_fraccion = sorted(filas_fraccion, key=lambda f: (f['fecha_de_pago_order']))
                filas_fraccion[0]['misma_fraccion'] = False
                filas.extend(filas_fraccion)

                fila = {}
                fila['total_monto_pagado'] = unicode('{:,}'.format(total_monto_pagado)).replace(",", ".")
                fila['total_monto_inmobiliaria'] = unicode('{:,}'.format(total_monto_inm)).replace(",", ".")
                fila['total_monto_propietario'] = unicode('{:,}'.format(total_monto_prop)).replace(",", ".")
                total_monto_inm = 0
                total_monto_prop = 0
                total_monto_pagado = 0
                fila['ultimo_pago'] = True
                filas.append(fila)


            fila = {}
            fila['total_general_pagado'] = unicode('{:,}'.format(total_general_pagado)).replace(",", ".")
            fila['total_general_inmobiliaria'] = unicode('{:,}'.format(total_general_inm)).replace(",", ".")
            fila['total_general_propietario'] = unicode('{:,}'.format(total_general_prop)).replace(",", ".")
            ley = int(round(total_general_pagado * 0.015))
            fila['ley'] = unicode('{:,}'.format(ley)).replace(",", ".")
            impuesto_renta = int(round((total_general_pagado - ley) * 0.045))
            fila['impuesto_renta'] = unicode('{:,}'.format(impuesto_renta)).replace(",", ".")
            iva_comision = int(round(total_general_inm * 0.1))
            fila['iva_comision'] = unicode('{:,}'.format(iva_comision)).replace(",", ".")
            fila['total_a_cobrar'] = unicode(
                '{:,}'.format(total_general_prop - (ley + impuesto_renta + iva_comision))).replace(",", ".")
            filas.append(fila)
            filas[0]['misma_fraccion'] = False

        except Exception, error:
            print error


    return lista_ordenada


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

                        #PARAMETROS RECIBIDOS
                        fecha_ini = request.GET['fecha_ini']
                        fecha_fin = request.GET['fecha_fin']
                        fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date()
                        fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date()
                        tipo_busqueda = request.GET['tipo_busqueda']
                        order_by = request.GET['order_by']
                        busqueda_id = request.GET['busqueda']
                        busqueda_label = request.GET['busqueda_label']

                        #BUSQUEDA
                        lista_ordenada = obtener_pagos_liquidacion(busqueda_id,tipo_busqueda, fecha_ini_parsed, fecha_fin_parsed,order_by,busqueda_label)


                        ultimo="&tipo_busqueda="+tipo_busqueda+"&busqueda="+busqueda_id+"&busqueda_label="+busqueda_label+"&fecha_ini="+fecha_ini+"&fecha_fin="+fecha_fin+"&order_by="+order_by
                        
                        lista = lista_ordenada
                        #PAGINADOR
                        #paginator = Paginator(filas, 25)
                        #page = request.GET.get('page')
                        #try:
                        #    lista = paginator.page(page)
                        #except PageNotAnInteger:
                        #    lista = paginator.page(1)
                        #except EmptyPage:
                        #    lista = paginator.page(paginator.num_pages)          
                        c = RequestContext(request, {
                            'object_list': lista,
                            # 'lista_totales' : lista_totales,
                            'fecha_ini':fecha_ini,
                            'fecha_fin':fecha_fin,
                            'tipo_busqueda':tipo_busqueda,
                            'busqueda':busqueda_id,
                            'busqueda_label':busqueda_label,
                            'order_by': order_by,
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
                    fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date()
                    fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date()
                    busqueda_label = request.GET['busqueda_label']
                    vendedor_id=request.GET['busqueda']
                    print("vendedor_id ->" + vendedor_id)
                    
                    ventas = Venta.objects.filter(vendedor_id = vendedor_id).order_by('lote__manzana__fraccion').select_related()
                    ventas_id = []
                                
                    for venta in ventas:
                        ventas_id.append(venta.id)
                                
                    pagos_de_cuotas_ventas = PagoDeCuotas.objects.filter(venta__in=ventas_id,fecha_de_pago__range=(fecha_ini_parsed, fecha_fin_parsed)).order_by('fecha_de_pago').prefetch_related('venta', 'venta__plan_de_pago_vendedor','venta__lote__manzana__fraccion')
                    cant_cuotas_pagadas_ventas = PagoDeCuotas.objects.filter(venta__in=ventas_id, fecha_de_pago__lt=fecha_ini_parsed).values('venta_id').annotate(Sum('nro_cuotas_a_pagar')).prefetch_related('venta_id')
                    
                    filas_fraccion = []
                    filas=[]
                    
                    total_fraccion_monto_pagado=0
                    total_fraccion_monto_vendedor=0
                    
                    total_general_monto_pagado=0
                    total_general_monto_vendedor=0
                    
                    fecha_pago_str = ''
                    #ACAAA
                    g_fraccion = ''
                    for venta in ventas:
                        
                        if venta.fecha_de_venta >= fecha_ini_parsed and venta.fecha_de_venta <= fecha_fin_parsed:  
                            #preguntar por el plan de pago de la venta con el vendedor, si el vendedor lleva un % de la venta total, un % de la entrega inicial
                            
                            if venta.plan_de_pago_vendedor.tipo == 'contado':
                                
                                if g_fraccion == '':
                                    g_fraccion = venta.lote.manzana.fraccion
                                if venta.lote.manzana.fraccion != g_fraccion:
                                    #Totales por FRACCION
                                    
                                    if filas_fraccion:
                                        try:
                                            filas_fraccion = sorted(filas_fraccion, key=lambda f: (f['fecha_de_pago_order']))
                                        except Exception, error:
                                            print unicode(error) +": "+ fecha_pago_str                    
                                        filas_fraccion[0]['misma_fraccion']= False
                                        filas.extend(filas_fraccion)
                                        filas_fraccion = []
                                        fila = {}
                                        fila['total_monto_pagado']=unicode('{:,}'.format(total_fraccion_monto_pagado)).replace(",", ".")
                                        fila['total_monto_vendedor']=unicode('{:,}'.format(total_fraccion_monto_vendedor)).replace(",", ".")
                                                            
                                        total_fraccion_monto_pagado=0
                                        total_fraccion_monto_vendedor=0
                                                            
                                        fila['ultimo_pago'] = True
                                        filas.append(fila)
                                    g_fraccion = venta.lote.manzana.fraccion.nombre
                                    ok=True
                                else:
                                    montos = calculo_montos_liquidacion_vendedores_contado(venta)
                                    monto_vendedor = montos['monto_vendedor']
                                    fecha_pago_str = unicode(venta.fecha_de_venta)
                                    fecha_pago = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                    fecha_pago_order = venta.fecha_de_venta
                                    
                                    #Fraccion    Lote    Fecha de Pago    Cliente    Cuota Nº    Mes    Monto Pag Monto Prop.
                                    fila={}
                                    fila['fraccion'] = g_fraccion
                                    fila['plan']=unicode(venta.plan_de_pago_vendedor)
                                    fila['lote'] = venta.lote.codigo_paralot
                                    fila['fecha_de_pago'] = fecha_pago
                                    fila['fecha_de_pago_order'] = fecha_pago_order
                                    fila['cliente'] = venta.cliente
                                    fila['nro_cuota'] = 'Venta al Contado'
                                    fila['monto_pagado']= venta.precio_final_de_venta
                                    fila['monto_vendedor']= monto_vendedor
                                    fila['misma_fraccion'] = True
                                    
                                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                                    fecha_1 = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                    parts_1 = fecha_1.split("/")
                                    year_1 = parts_1[2];
                                    mes_1 = int(parts_1[1]) - 1;
                                    mes_year = monthNames[mes_1]+"/"+year_1;
                                    fila['mes'] = mes_year
                                    
                                    total_fraccion_monto_pagado+= fila['monto_pagado']
                                    total_fraccion_monto_vendedor += fila['monto_vendedor']
                                    
                                    total_general_monto_pagado+= fila['monto_pagado']
                                    total_general_monto_vendedor += fila['monto_vendedor']
                                    
                                    fila['monto_pagado'] = unicode('{:,}'.format(fila['monto_pagado'])).replace(",", ".")
                                    fila['monto_vendedor']= unicode('{:,}'.format(fila['monto_vendedor'])).replace(",", ".")
                                    
                                    filas_fraccion.append(fila)
                            
                            if venta.entrega_inicial > 0:
                                if g_fraccion == '':
                                    g_fraccion = venta.lote.manzana.fraccion
                                if venta.lote.manzana.fraccion != g_fraccion:
                                    #Totales por FRACCION
                                    if filas_fraccion:
                                        try:
                                            filas_fraccion = sorted(filas_fraccion, key=lambda f: (f['fecha_de_pago_order']))
                                        except Exception, error:
                                            print unicode(error) +": "+ fecha_pago_str                     
                                        filas_fraccion[0]['misma_fraccion']= False
                                        filas.extend(filas_fraccion)
                                        filas_fraccion = []
                                        fila = {}
                                        fila['total_monto_pagado']=unicode('{:,}'.format(total_fraccion_monto_pagado)).replace(",", ".")
                                        fila['total_monto_vendedor']=unicode('{:,}'.format(total_fraccion_monto_vendedor)).replace(",", ".")
                                                            
                                        total_fraccion_monto_pagado=0
                                        total_fraccion_monto_vendedor=0
                                                            
                                        fila['ultimo_pago'] = True
                                        filas.append(fila).append(fila)
                                    g_fraccion = venta.lote.manzana.fraccion
                                    ok=True
                                else:
                                    
                                    montos = calculo_montos_liquidacion_vendedores_entrega_inicial(venta)
                                    monto_vendedor = montos['monto_vendedor']
                                    fecha_pago_str = unicode(venta.fecha_de_venta)
                                    fecha_pago = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                    fecha_pago_order = venta.fecha_de_venta
                                    
                                    #Fraccion    Lote    Fecha de Pago    Cliente    Cuota Nº    Mes    Monto Pag Monto Prop.
                                    fila={}
                                    fila['fraccion'] = g_fraccion
                                    fila['plan']=unicode(venta.plan_de_pago_vendedor)
                                    fila['lote'] = venta.lote.codigo_paralot
                                    fila['fecha_de_pago'] = fecha_pago
                                    fila['fecha_de_pago_order'] = fecha_pago_order
                                    fila['cliente'] = venta.cliente
                                    fila['nro_cuota'] = 'Entrega Inicial'
                                    fila['monto_pagado']= venta.entrega_inicial
                                    fila['monto_vendedor']= monto_vendedor
                                    fila['misma_fraccion'] = True
                                    
                                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                                    fecha_1 = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                    parts_1 = fecha_1.split("/")
                                    year_1 = parts_1[2];
                                    mes_1 = int(parts_1[1]) - 1;
                                    mes_year = monthNames[mes_1]+"/"+year_1;
                                    fila['mes'] = mes_year
                                    
                                    total_fraccion_monto_pagado+= fila['monto_pagado']
                                    total_fraccion_monto_vendedor += fila['monto_vendedor']
                                    
                                    total_general_monto_pagado+= fila['monto_pagado']
                                    total_general_monto_vendedor += fila['monto_vendedor']
                                    
                                    fila['monto_pagado'] = unicode('{:,}'.format(fila['monto_pagado'])).replace(",", ".")
                                    fila['monto_vendedor']= unicode('{:,}'.format(fila['monto_vendedor'])).replace(",", ".")
                                    
                                    filas_fraccion.append(fila)
                                
                            
                        pagos = []    
                        pagos = get_pago_cuotas(venta, fecha_ini_parsed,fecha_fin_parsed, pagos_de_cuotas_ventas, cant_cuotas_pagadas_ventas)                                            
                        lista_cuotas_ven =[]
                        lista_cuotas_ven.append(venta.plan_de_pago_vendedor.cuota_inicial)
                        numero_cuota = venta.plan_de_pago_vendedor.cuota_inicial
                        for i in range(venta.plan_de_pago_vendedor.cantidad_cuotas -1):
                            numero_cuota +=  venta.plan_de_pago_vendedor.intervalos
                            lista_cuotas_ven.append(numero_cuota)
                                    
                        for pago in pagos:
                        #preguntar por el plan de pago de la venta con el vendedor, si el vendedor lleva un % del pago de acuerdo al nro de cuota que se está pagando
                            try:
                                
                                #if pago['id']== 1840987:
                                #    print "este es"
                                
                                if venta.lote.manzana.fraccion.nombre == 'VISTA AL PARANA':
                                    print "este es" 
                                                    
                                if g_fraccion == "":
                                    g_fraccion = venta.lote.manzana.fraccion
                                                    
                                if pago['fraccion'] != g_fraccion:
                                    #Totales por FRACCION
                                    if filas_fraccion:
                                        try:
                                            filas_fraccion = sorted(filas_fraccion, key=lambda f: (f['fecha_de_pago_order']))
                                        except Exception, error:
                                            print unicode(error) +": "+ fecha_pago_str          
                                        filas_fraccion[0]['misma_fraccion']= False
                                        filas.extend(filas_fraccion)
                                        filas_fraccion = []
                                        fila = {}
                                        fila['total_monto_pagado']=unicode('{:,}'.format(total_fraccion_monto_pagado)).replace(",", ".")
                                        fila['total_monto_vendedor']=unicode('{:,}'.format(total_fraccion_monto_vendedor)).replace(",", ".")
                                                            
                                        total_fraccion_monto_pagado=0
                                        total_fraccion_monto_vendedor=0
                                            
                                        fila['ultimo_pago'] = True
                                        filas.append(fila)
                                    g_fraccion = pago['fraccion']
                                    ok=True
                                                        
                                    montos = calculo_montos_liquidacion_vendedores(pago,venta, lista_cuotas_ven)
                                    monto_vendedor = montos['monto_vendedor']
                                    fecha_pago_str = unicode(pago['fecha_de_pago'])
                                    try:
                                        fecha_pago = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                    except Exception, error:
                                        print unicode(error) +": "+ fecha_pago_str
                                                         
                                    # Se setean los datos de cada fila
                                    fila={}
                                    fila['misma_fraccion'] = True
                                    fila['fraccion']=unicode(venta.lote.manzana.fraccion)
                                    fila['plan']=unicode(venta.plan_de_pago_vendedor)
                                    fila['fecha_de_pago']=fecha_pago
                                    fila['fecha_de_pago_order']=pago['fecha_de_pago']
                                    fila['lote']=unicode(pago['lote'])
                                    fila['cliente']=unicode(venta.cliente)
                                    fila['nro_cuota']=unicode(pago['nro_cuota_y_total'])
                                    fila['total_de_cuotas']=unicode('{:,}'.format(int(pago['monto']))).replace(",", ".")
                                    fila['monto_vendedor']=unicode('{:,}'.format(monto_vendedor)).replace(",", ".")
                                                         
                                    cuotas_detalles = get_cuota_information_by_lote(pago['lote'].id, int(pago['nro_cuota']) , True, True, venta)
                                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                                    fecha_1 = cuotas_detalles[0]['fecha'] 
                                    parts_1 = fecha_1.split("/")
                                    year_1 = parts_1[2];
                                    mes_1 = int(parts_1[1]) - 1;
                                    mes_year = monthNames[mes_1]+"/"+year_1;
                                    fila['mes'] = mes_year
                                                         
                                    #if venta.lote.manzana.fraccion != g_fraccion:
                                    if monto_vendedor != 0: 
                                        ok=False
                                        # Se suman los TOTALES por FRACCION
                                        total_fraccion_monto_vendedor += int(monto_vendedor)
                                        total_fraccion_monto_pagado += int(pago['monto'])
                                                             
                                        #Acumulamos para los TOTALES GENERALES
                                        total_general_monto_pagado += int(pago['monto'])
                                        total_general_monto_vendedor += int(monto_vendedor)
                                                            
                                        filas_fraccion.append(fila)
                                                        
                                else:
                                                        
                                                    
                                    montos = calculo_montos_liquidacion_vendedores(pago,venta, lista_cuotas_ven)
                                    monto_vendedor = montos['monto_vendedor']
                                    fecha_pago_str = unicode(pago['fecha_de_pago'])
                                    try:
                                        fecha_pago = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                    except Exception, error:
                                        print error +": "+ fecha_pago_str
                                                         
                                    # Se setean los datos de cada fila
                                    fila={}
                                    fila['misma_fraccion'] = True
                                    fila['fraccion']=unicode(venta.lote.manzana.fraccion)
                                    fila['plan']=unicode(venta.plan_de_pago_vendedor)
                                    fila['fecha_de_pago']=fecha_pago
                                    fila['fecha_de_pago_order']=pago['fecha_de_pago']
                                    fila['lote']=unicode(pago['lote'])
                                    fila['cliente']=unicode(venta.cliente)
                                    fila['nro_cuota']=unicode(pago['nro_cuota_y_total'])
                                    fila['total_de_cuotas']=unicode('{:,}'.format(int(pago['monto']))).replace(",", ".")
                                    fila['monto_vendedor']=unicode('{:,}'.format(monto_vendedor)).replace(",", ".")
                                                         
                                    cuotas_detalles = get_cuota_information_by_lote(pago['lote'].id, int(pago['nro_cuota']) , True, True, venta)
                                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                                    fecha_1 = cuotas_detalles[0]['fecha'] 
                                    parts_1 = fecha_1.split("/")
                                    year_1 = parts_1[2];
                                    mes_1 = int(parts_1[1]) - 1;
                                    mes_year = monthNames[mes_1]+"/"+year_1;
                                    fila['mes'] = mes_year
                                                         
                                    #if venta.lote.manzana.fraccion != g_fraccion:
                                    if monto_vendedor != 0: 
                                        ok=False
                                        # Se suman los TOTALES por FRACCION
                                        total_fraccion_monto_vendedor += int(monto_vendedor)
                                        total_fraccion_monto_pagado += int(pago['monto'])
                                                             
                                        #Acumulamos para los TOTALES GENERALES
                                        total_general_monto_pagado += int(pago['monto'])
                                        total_general_monto_vendedor += int(monto_vendedor)
                                                            
                                        filas_fraccion.append(fila)
                                                    
                                                    
                                                     
                                                    
                                                
                            except Exception, error:
                                    print "Error: "+ unicode(error)+ ", Id Pago: "+unicode(pago['id'])+ ", Fraccion: "+unicode(pago['fraccion'])+ ", lote: "+unicode(pago['lote']) +" Nro cuota: "+unicode(unicode(pago['nro_cuota_y_total']))
                                             
                #Totales GENERALES
                #filas = sorted(filas, key=lambda f: f['fecha_de_pago'])
                if filas_fraccion:
                    filas_fraccion = sorted(filas_fraccion, key=lambda f: (f['fecha_de_pago_order']))
                    filas_fraccion[0]['misma_fraccion']= False 
                    filas.extend(filas_fraccion)
                                    
                    fila = {}
                    fila['total_monto_pagado']=unicode('{:,}'.format(total_fraccion_monto_pagado)).replace(",", ".")
                    fila['total_monto_vendedor']=unicode('{:,}'.format(total_fraccion_monto_vendedor)).replace(",", ".")
                    total_fraccion_monto_vendedor = 0
                    total_fraccion_monto_pagado = 0
                    fila['ultimo_pago'] = True
                    filas.append(fila)
                                
                fila = {}
                fila['total_general_pagado']=unicode('{:,}'.format(total_general_monto_pagado)).replace(",", ".")
                fila['total_general_vendedor']=unicode('{:,}'.format(total_general_monto_vendedor)).replace(",", ".")
                ley = int(total_general_monto_pagado*0.015)
                filas.append(fila)
                filas[0]['misma_fraccion']= False
                    
                
                ultimo="&busqueda_label="+busqueda_label+"&busqueda="+vendedor_id+"&fecha_ini="+fecha_ini+"&fecha_fin="+fecha_fin         
                
                lista = filas
                
#                 paginator = Paginator(cuotas, 25)
#                 page = request.GET.get('page')
#                 try:
#                     lista = paginator.page(page)
#                 except PageNotAnInteger:
#                     lista = paginator.page(1)
#                 except EmptyPage:
#                     lista = paginator.page(paginator.num_pages) 
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
                    fecha_ini_parsed = unicode(datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date())
                    fecha_fin_parsed = unicode(datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date())
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
                        cuotas_para_vendedor=((cuota_item.plan_de_pago_vendedor.cantidad_cuotas)*(cuota_item.plan_de_pago_vendedor.intervalos))-cuota_item.plan_de_pago_vendedor.cuota_inicial                  
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
                                com=int(cuota_item.total_de_cuotas*(float(cuota_item.plan_de_pago_vendedor.porcentaje_de_cuotas)/float(100)))
                                if(cuota_item.venta.entrega_inicial):
                                    #comision de la entrega inicial, si la hubiere
                                    com_inicial=int(cuota_item.venta.entrega_inicial*(float(cuota_item.plan_de_pago_vendedor.porcentaje_cuota_inicial)/float(100)))
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
                                com=int(cuota_item.total_de_cuotas*(float(cuota_item.plan_de_pago_vendedor.porcentaje_de_cuotas)/float(100)))
                                if(cuota_item.venta.entrega_inicial):
                                    #comision de la entrega inicial, si la hubiere
                                    com_inicial=int(cuota_item.venta.entrega_inicial*(float(cuota_item.plan_de_pago_vendedor.porcentaje_cuota_inicial)/float(100)))
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

def informe_movimientos(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_FICHA_LOTE):
                if (filtros_establecidos(request.GET,'informe_movimientos') == False):
                    t = loader.get_template('informes/informe_movimientos.html')
                    c = RequestContext(request, {
                        'object_list': [],
                    })
                    return HttpResponse(t.render(c))
                else: #Parametros seteados
                    t = loader.get_template('informes/informe_movimientos.html')
                    lote_ini_orig=request.GET['lote_ini']
                    lote_fin_orig=request.GET['lote_fin']
                    fecha_ini=request.GET['fecha_ini']
                    fecha_fin=request.GET['fecha_fin']
                    lote_ini_parsed = unicode(lote_ini_orig)
                    lote_fin_parsed = unicode(lote_fin_orig)
                    fecha_ini_parsed = None
                    fecha_fin_parsed = None
                    lotes=[]
                    lotes.append(lote_ini_parsed)
                    lotes.append(lote_fin_parsed)
                    #print lotes
                    rango_lotes_id=[]
                    try:
                        for l in lotes:
                            fraccion_int = int(l[0:3])
                            manzana_int = int(l[4:7])
                            lote_int = int(l[8:])
                            manzana = Manzana.objects.get(fraccion_id=fraccion_int, nro_manzana=manzana_int)
                            lote = Lote.objects.get(manzana=manzana.id, nro_lote=lote_int)
                            rango_lotes_id.append(lote.id)
                        print rango_lotes_id
                    except Exception, error:
                        print error
                    lote_ini=str(rango_lotes_id[0])
                    lote_fin=str(rango_lotes_id[1])
                    lista_movimientos=[]
                    print 'lote inicial->'+unicode(lote_ini)
                    print 'lote final->'+unicode(lote_fin)
                    if fecha_ini != '' and fecha_fin != '':    
                        fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date()
                        fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date()
                        try:
                            lista_ventas = Venta.objects.filter(lote_id__range=(lote_ini, lote_fin)).order_by('lote__nro_lote')
                            lista_reservas = Reserva.objects.filter(lote_id__range=(lote_ini,lote_fin), fecha_de_reserva__range=(fecha_ini_parsed, fecha_fin_parsed))
                            lista_cambios = CambioDeLotes.objects.filter(Q(lote_nuevo_id__range=(lote_ini,lote_fin)) |Q(lote_a_cambiar__range=(lote_ini,lote_fin)), fecha_de_cambio__range=(fecha_ini_parsed, fecha_fin_parsed))
                            lista_transferencias = TransferenciaDeLotes.objects.filter(lote_id__range=(lote_ini,lote_fin), fecha_de_transferencia__range=(fecha_ini_parsed, fecha_fin_parsed))
                        except Exception, error:
                            print error
                            lista_ventas = []
                            lista_reservas = []
                            lista_cambios = []
                            lista_transferencias = []
                            pass 
                    else:                  
                        try:
                            lista_ventas = Venta.objects.filter(lote_id__range=(lote_ini, lote_fin)).order_by('lote__nro_lote')
                            lista_cambios = CambioDeLotes.objects.filter(Q(lote_nuevo_id__range=(lote_ini,lote_fin)) |Q(lote_a_cambiar__range=(lote_ini,lote_fin)))
                            lista_reservas = Reserva.objects.filter(lote_id__range=(lote_ini, lote_fin))
                            lista_transferencias = TransferenciaDeLotes.objects.filter(lote_id__range=(lote_ini, lote_fin))
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
                        try:
                            for item_venta in lista_ventas:
                                try:
                                    resumen_venta = {}
                                    fecha_venta_str = unicode(item_venta.fecha_de_venta)
                                    resumen_venta['fecha_de_venta'] = unicode(datetime.datetime.strptime(fecha_venta_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                    resumen_venta['lote']=item_venta.lote
                                    resumen_venta['cliente'] = item_venta.cliente
                                    resumen_venta['cantidad_de_cuotas'] = item_venta.plan_de_pago.cantidad_de_cuotas
                                    resumen_venta['precio_final'] = unicode('{:,}'.format(item_venta.precio_final_de_venta)).replace(",",".")
                                    resumen_venta['entrega_inicial'] = unicode('{:,}'.format(item_venta.entrega_inicial)).replace(",",".")
                                    resumen_venta['tipo_de_venta'] = item_venta.plan_de_pago.tipo_de_plan
                                    RecuperacionDeLotes.objects.get(venta=item_venta.id)
                                    try:
                                        venta_pagos_query_set = get_pago_cuotas_2(item_venta,fecha_ini_parsed, fecha_fin_parsed)
                                        resumen_venta['recuperacion'] = True
                                    except PagoDeCuotas.DoesNotExist:
                                        venta_pagos_query_set = []
                                except RecuperacionDeLotes.DoesNotExist:
                                    print 'se encontro la venta no recuperada, la venta actual'
                                    try:
                                        venta_pagos_query_set = get_pago_cuotas_2(item_venta,fecha_ini_parsed, fecha_fin_parsed)
                                        resumen_venta['recuperacion'] = False
                                    except PagoDeCuotas.DoesNotExist:
                                        venta_pagos_query_set = []

                                ventas_pagos_list = []
                                ventas_pagos_list.insert(0,resumen_venta) #El primer elemento de la lista de pagos es el resumen de la venta
                                saldo_anterior=item_venta.precio_final_de_venta
                                monto=item_venta.entrega_inicial
                                saldo=saldo_anterior-monto
                                tipo_de_venta = item_venta.plan_de_pago.tipo_de_plan
                                for pago in venta_pagos_query_set:
                                    saldo_anterior=saldo
                                    monto= long(pago['monto'])
                                    saldo=saldo_anterior-monto
                                    cuota ={}
                                    cuota['vencimiento'] = ""
                                    cuota['tipo_de_venta'] = tipo_de_venta
                                    fecha_pago_str = unicode(pago['fecha_de_pago'])
                                    cuota['fecha_de_pago'] = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                    cuota['id'] = pago['id']
                                    cuota['nro_cuota'] = pago['nro_cuota_y_total']
                                    
                                    cuotas_detalles = []
                                    cuotas_detalles = get_cuota_information_by_lote(pago['lote'].id, int(pago['nro_cuota']), True, True, item_venta)
                                    cuota['vencimiento'] = cuota['vencimiento']+ unicode(cuotas_detalles[0]['fecha'])+' '
                                    
                                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                                    fecha_1 = cuota['vencimiento']
                                    parts_1 = fecha_1.split("/")
                                    year_1 = parts_1[2];
                                    mes_1 = int(parts_1[1]) - 1;
                                    mes_year = monthNames[mes_1]+"/"+year_1;
                                    cuota['mes'] = mes_year
 
                                    cuota['saldo_anterior'] = unicode('{:,}'.format(int(saldo_anterior))).replace(",",".")
                                    cuota['monto'] =  unicode('{:,}'.format(int(pago['monto']))).replace(",",".")
                                    cuota['saldo'] =  unicode('{:,}'.format(int(saldo))).replace(",",".")
                                    ventas_pagos_list.append(cuota)
                                lista_movimientos.append(ventas_pagos_list)
                        except Exception, error:
                            print error

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
    
                        
                    ultimo="&lote_ini="+lote_ini_orig+"&lote_fin="+lote_fin_orig+"&fecha_ini="+fecha_ini+"&fecha_fin="+fecha_fin
                    
                    lista = lista_movimientos
#                     paginator = Paginator(lista_movimientos, 25)
#                     page = request.GET.get('page')
#                     try:
#                         lista = paginator.page(page)
#                     except PageNotAnInteger:
#                         lista = paginator.page(1)
#                     except EmptyPage:
#                         lista = paginator.page(paginator.num_pages)
                         
                    c = RequestContext(request, {
                        'lista_ventas': lista,
                        'lista_cambios': lista_cambios,
                        'lista_transferencias': lista_transferencias,
                        'lista_reservas': lista_reservas,
                        'mostrar_transferencias': mostrar_transferencias,
                        'mostrar_reservas': mostrar_reservas,
                        'mostrar_cambios': mostrar_cambios,
                        'mostrar_mvtos': mostrar_mvtos,
                        'lote_ini' : lote_ini_orig,
                        'lote_fin' : lote_fin_orig,
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
        manzanas = Manzana.objects.filter(fraccion_id__range=(fraccion_ini, fraccion_fin)).order_by('fraccion', 'nro_manzana')
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
    
    g_fraccion = ''
    
    lotes = []          
    for index, lote_item in enumerate(object_list):
        lote={}
        # Se setean los datos de cada fila 
        precio_cuota=int(math.ceil(lote_item.precio_credito/130))
        lote['fraccion_id']=unicode(lote_item.manzana.fraccion.id)
        lote['fraccion']=unicode(lote_item.manzana.fraccion)
        lote['lote']= lote_item.codigo_paralot
        lote['superficie']=lote_item.superficie                                    
        lote['precio_contado']=unicode('{:,}'.format(lote_item.precio_contado)).replace(",", ".")                    
        lote['precio_credito']=unicode('{:,}'.format(lote_item.precio_credito)).replace(",", ".")                    
        lote['importe_cuota']=unicode('{:,}'.format(precio_cuota)).replace(",", ".")
        lote['misma_fraccion'] = True
        lote['ultimo_lote'] = False
        if g_fraccion == '':
            g_fraccion = lote_item.manzana.fraccion

            
        
        # Se suman los TOTALES por FRACCION
        total_superficie_fraccion += lote_item.superficie 
        total_contado_fraccion += lote_item.precio_contado
        total_credito_fraccion += lote_item.precio_credito
        total_importe_cuotas += precio_cuota
        total_lotes += 1
        #Esteee
        
        # Se suman los TOTALES GENERALES
        total_general_cuotas += precio_cuota
        total_general_contado += lote_item.precio_contado
        total_general_credito += lote_item.precio_credito
        total_general_superficie += lote_item.superficie 
        total_general_lotes += 1
        
        #Es el ultimo lote, cerrar totales de fraccion
        if (len(object_list)-1 == index):
            lote['ultimo_lote'] = True
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
            lote['ultimo_lote'] = True
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
            
        if lote_item.manzana.fraccion != g_fraccion:
            g_fraccion = lote_item.manzana.fraccion
            lote['misma_fraccion'] = False
        lotes.append(lote)
    lotes[0]['misma_fraccion'] = False    
    #esteee
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    sheet.paper_size_code = 1
    style = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                              'font: name Gill Sans MT Condensed, bold True; align: horiz center')   
    style2 = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                         'font: name Gill Sans MT Condensed, bold True, height 160;')
    style3 = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160 ; align: horiz center')
    style4 = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160 ; align: horiz right')
    style5 = xlwt.easyxf('pattern: pattern solid, fore_colour white;''font: name Gill Sans MT Condensed, bold True, height 160 ; align: horiz right')
    
    style_normal = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160;')
    style_normal_centrado = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160; align: horiz center')
    
    style_fraccion = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                              'font: name Gill Sans MT Condensed, bold True; align: horiz center')  
    #Titulo
    #sheet.write_merge(0,0,0,7, 'PROPAR S.R.L.' ,style3)
    #sheet.write_merge(1,1,1,7, 'Sistema de Control de Loteamiento' ,style3)
    
    #sheet.header_str = 'PROPAR S.R.L.'
    periodo_1 = fraccion_ini
    periodo_2 = fraccion_fin
    usuario = unicode(request.user)
    sheet.header_str = (
     u"&LFecha: &D Hora: &T \nUsuario: "+usuario+" "
     u"&CPROPAR S.R.L.\n LOTES LIBRES "
     u"&RFraccion del "+periodo_1+" al "+periodo_2+" \nPage &P of &N"
     )
    #sheet.footer_str = 'things'
    
    
    
    c=0
    sheet.write_merge(c,c,0,4, "Lotes Libres", style) 
    #contador de filas
      
    for lote in lotes:
        c+=1
        '''
        sheet.write(c, 0, lote['fraccion'])
        sheet.write(c, 1, lote['fraccion_id'])
        '''
        try: 
            if lote['total_importe_cuotas'] and lote['ultimo_lote'] == False:
                c += 1
                sheet.write_merge(c,c,0,4, "Cantidad de Lotes libres de la fraccion: "+unicode(lote['total_lotes']), style2)
                '''
                sheet.write(c, 3, lote['total_superficie_fraccion'], style2)
                sheet.write(c, 4, lote['total_contado_fraccion'], style2)
                sheet.write(c, 5, lote['total_credito_fraccion'], style2)
                sheet.write(c, 6, lote['total_importe_cuotas'], style2)
                '''
        except Exception, error:
            print error 
            pass
        
        if lote['misma_fraccion'] == False:
            sheet.write_merge(c,c,0,4, "Fraccion: "+unicode(lote['fraccion']), style)
            c+=1
            sheet.write(c, 0, "Lote Nro.", style)
            sheet.write(c, 1, "Superficie", style)    
            sheet.write(c, 2, "Precio Contado", style)    
            sheet.write(c, 3, "Precio Credito", style)
            sheet.write(c, 4, "Precio Cuota", style)
            c+=1
             
        sheet.write(c, 0, lote['lote'], style_normal_centrado)
        sheet.write(c, 1, unicode(lote['superficie']) + ' mts2', style_normal_centrado)
        sheet.write(c, 2, lote['precio_contado'], style4)
        sheet.write(c, 3, lote['precio_credito'], style4)
        sheet.write(c, 4, lote['importe_cuota'], style4)
        try: 
            if lote['ultimo_lote'] == True:
                c += 1
                sheet.write_merge(c,c,0,4, "Cantidad de Lotes libres de la fraccion: "+unicode(lote['total_lotes']), style2)
                '''
                sheet.write(c, 3, lote['total_superficie_fraccion'], style2)
                sheet.write(c, 4, lote['total_contado_fraccion'], style2)
                sheet.write(c, 5, lote['total_credito_fraccion'], style2)
                sheet.write(c, 6, lote['total_importe_cuotas'], style2)
                '''
            if lote['total_general_cuotas']:
                c += 1
                sheet.write_merge(c,c,0,4, "Cantidad total de Lotes libres: "+unicode(lote['total_general_lotes']), style2)
                '''
                sheet.write(c, 3, lote['total_general_superficie'], style2)
                sheet.write(c, 4, lote['total_general_contado'], style2)
                sheet.write(c, 5, lote['total_general_credito'], style2)
                sheet.write(c, 6, lote['total_general_cuotas'], style2)
                '''         
        except Exception, error:
            print error 
            pass
    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo
    fecha_actual= datetime.datetime.now().date()
    fecha_str = unicode(fecha_actual)
    fecha = unicode(datetime.datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y"))         
    response['Content-Disposition'] = 'attachment; filename=' + 'lotes_libres_fraccion_del_'+periodo_1+'_a_'+periodo_2+'_'+fecha+'.xls'
    wb.save(response)
    return response

def clientes_atrasados_reporte_excel(request):
    

    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):

                fecha_actual = datetime.datetime.now()

                # FILTROS DISPONIBLES
                filtros = filtros_establecidos(request.GET, 'clientes_atrasados')

                # OBJETO QUE SE UTILIZA PARA CARGAR TODOS LOS CLIENTES ATRASADOS A MOSTRAR
                clientes_atrasados = []

                # PARAMETROS
                meses_peticion = 1
                fraccion = ''


                if filtros == 0:
                    meses_peticion = 0
                elif filtros == 1:
                    fraccion = request.GET['fraccion']
                elif filtros == 2:
                    meses_peticion = int(request.GET['meses_atraso'])
                else:
                    fraccion = request.GET['fraccion']
                    meses_peticion = int(request.GET['meses_atraso'])

                # # Por ultimo, traemos ordenados los registros por el CODIGO DE LOTE
                # query += " ORDER BY codigo_paralot "
                #
                # # try:
                # results = cursor.fetchall()  # LOTES
                #
                # for r in results:  # RECORREMOS TODOS LOS LOTES DE LA FRACCION
                #
                #     cliente_atrasado = {}
                #
                #     # OBTENER LA ULTIMA VENTA Y SU DETALLE
                #     ultima_venta = get_ultima_venta(r[0])
                #
                #     # SE TRATAN LOS CASOS EN DONDE NO SE ENCUENTRA VENTA PARA ALGUN LOTE.
                #     if ultima_venta != None:
                #         detalle_cuotas = get_cuotas_detail_by_lote(unicode(str(r[0])))
                #         hoy = date.today()
                #         cuotas_a_pagar = obtener_cuotas_a_pagar_full(ultima_venta, hoy, detalle_cuotas,
                #                                                      500)  # Maximo atraso = 500 para tener un parametro maximo de atraso en las cuotas.
                #     else:
                #         cuotas_a_pagar = []
                #
                #     if (len(cuotas_a_pagar) >= meses_peticion + 1):
                #
                #         cliente_atrasado[
                #             'cliente'] = ultima_venta.cliente.nombres + ' ' + ultima_venta.cliente.apellidos
                #
                #         if (len(PagoDeCuotas.objects.filter(venta_id=ultima_venta.id).order_by('-fecha_de_pago')) > 0):
                #             cliente_atrasado['fecha_ultimo_pago'] = \
                #             PagoDeCuotas.objects.filter(venta_id=ultima_venta.id).order_by('-fecha_de_pago')[
                #                 0].fecha_de_pago
                #         else:
                #             cliente_atrasado['fecha_ultimo_pago'] = 'Dato no disponible'
                #
                #         cliente_atrasado['lote'] = ultima_venta.lote.codigo_paralot
                #         cliente_atrasado['total_atrasado'] = unicode('{:,}'.format(cuotas_a_pagar[len(cuotas_a_pagar) - 1]['monto_sumatoria_cuotas'])).replace(",", ".")
                #         cliente_atrasado['importe_cuota'] = unicode(
                #             '{:,}'.format(ultima_venta.precio_de_cuota)).replace(",", ".")
                #         cliente_atrasado['total_pagado'] = unicode('{:,}'.format(
                #             detalle_cuotas['cant_cuotas_pagadas'] * ultima_venta.precio_de_cuota)).replace(",", ".")
                #         cliente_atrasado['cuotas_atrasadas'] = unicode('{:,}'.format(len(cuotas_a_pagar) - 1)).replace(",", ".")
                #         cuotas_pagadas = unicode('{:,}'.format(detalle_cuotas['cant_cuotas_pagadas'])).replace(",", ".") + '/' + unicode(
                #             '{:,}'.format(detalle_cuotas['cantidad_total_cuotas'])).replace(",", ".")
                #         cliente_atrasado['cuotas_pagadas'] = cuotas_pagadas
                #         porcentaje_pagado = round((float(detalle_cuotas['cant_cuotas_pagadas']) / float(detalle_cuotas['cantidad_total_cuotas'])) * 100);
                #         cliente_atrasado['porc_pagado'] = unicode('{:,}'.format(int(porcentaje_pagado))).replace(",", ".") + '%'
                #         cliente_atrasado['direccion_particular'] = ultima_venta.cliente.direccion_particular
                #         cliente_atrasado['direccion_cobro'] = ultima_venta.cliente.direccion_cobro
                #         cliente_atrasado['telefono_particular'] = ultima_venta.cliente.telefono_particular
                #         cliente_atrasado['celular_1'] = ultima_venta.cliente.celular_1
                #         clientes_atrasados.append(cliente_atrasado)

                # if meses_peticion == 0:
                #     meses_peticion = ''
                # a = len(clientes_atrasados)
            clientes_atrasados = obtener_clientes_atrasados(filtros, fraccion, meses_peticion)

            if clientes_atrasados:

                wb = xlwt.Workbook(encoding='utf-8')
                sheet = wb.add_sheet('test', cell_overwrite_ok=True)
                sheet.paper_size_code = 1
                # style = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                #                   'font: name Gill Sans MT Condensed, bold True, height 160; align: horiz center')
                # style2 = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160;')
                #
                # style3 = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160 ; align: horiz right')
                #
                # style4 = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160 ; align: horiz center')

                style = xlwt.easyxf('font: name Calibri, bold True; align: horiz center')
                style2 = xlwt.easyxf('pattern: pattern solid, fore_colour white; font: name Calibri; align: horiz right')
                style3 = xlwt.easyxf('font: name Calibri, height 200; align: horiz left')
                # style4 = xlwt.easyxf('pattern: pattern solid, fore_colour white; font: name Calibri')
                style4 = xlwt.easyxf('font: name Calibri, height 200; align: horiz center')

                usuario = unicode(request.user)
                sheet.header_str = (
                                u"&LFecha: &D Hora: &T \nUsuario: "+usuario+" "
                                u"&CPROPAR S.R.L.\n CLIENTES ATRASADOS "
                                u"&RMeses de Atraso: "+unicode(meses_peticion)+" \nPage &P of &N"
                                )

                # BORDES PARA las columnas de titulos
                borders = xlwt.Borders()
                borders.top = xlwt.Borders.THIN
                borders.bottom = xlwt.Borders.DOUBLE
                style.borders = borders

                # sheet.write(0, 0, "Cliente", style)
                # sheet.write(0, 1, "Lote", style)
                # sheet.write(0, 2, "C.A.", style)
                # sheet.write(0, 3, "C.P.", style)
                # sheet.write(0, 4, "Importe C", style)
                # sheet.write(0, 5, "Total A.", style)
                # sheet.write(0, 6, "Total P.", style)
                # sheet.write(0, 7, "Total Lote", style)
                # sheet.write(0, 8, "% P.", style)
                # sheet.write(0, 9, "Fecha U.P.", style)

                sheet.write(0, 0, "Cliente", style)
                sheet.write(0, 1, "Telefono", style)
                sheet.write(0, 2, "Direccion", style)
                sheet.write(0, 3, "Cod Lote", style)
                sheet.write(0, 4, "Cuotas Atras.", style)
                sheet.write(0, 5, "Cuotas Pag.", style)
                sheet.write(0, 6, "Importe Cuota", style)
                sheet.write(0, 7, "Total Atras.", style)
                sheet.write(0, 8, "Total Pag.", style)
                sheet.write(0, 9, "% Pag.", style)
                sheet.write(0, 10, "Fec Ult.Pago.", style)

                #Ancho de la columna Nombre
                col_nombre = sheet.col(0)
                col_nombre.width = 256 * 25   # 25 characters wide

                #Ancho de la columna Telefono
                col_lote = sheet.col(1)
                col_lote.width = 256 * 12   # 12 characters wide

                #Ancho de la columna Direccion
                col_nro_cuota = sheet.col(2)
                col_nro_cuota.width = 256 * 40   # 6 characters wide

                #Ancho de la columna Lote
                col_nro_cuota = sheet.col(3)
                col_nro_cuota.width = 256 * 15   # 6 characters wide

                #Ancho de la columna Cuotas Atras.
                col_nro_cuota = sheet.col(4)
                col_nro_cuota.width = 256 * 12   # 6 characters wide

                #Ancho de la columna Cuotas Pag.
                col_mes = sheet.col(5)
                col_mes.width = 256 * 12   # 8 characters wide

                #Ancho de la columna Imp. Cuota"
                col_monto_pagado = sheet.col(6)
                col_monto_pagado.width = 256 * 11   # 11 characters wide

                #Ancho de la columna Total Atras
                col_monto_inmo = sheet.col(7)
                col_monto_inmo.width = 256 * 14   # 15 characters wide

                #Ancho de la columna Total Pag
                col_nombre = sheet.col(8)
                col_nombre.width = 256 * 14   # 15 characters wide

                #Ancho de la columna % Pag
                col_nombre = sheet.col(9)
                col_nombre.width = 256 * 6   # 5 characters wide

                # Ancho de la columna Fecha
                col_fecha = sheet.col(10)
                col_fecha.width = 256 * 20  # 12 characters wide

                i = 0
                c = 1
                # for i in range(len(clientes_atrasados)):
                    # sheet.write(c, 0, clientes_atrasados[i]['cliente'],style2)
                    # sheet.write(c, 1, unicode(clientes_atrasados[i]['lote']),style4)
                    # sheet.write(c, 2, unicode(clientes_atrasados[i]['cuotas_atrasadas']),style4)
                    # sheet.write(c, 3, unicode(clientes_atrasados[i]['cuotas_pagadas']),style4)
                    # sheet.write(c, 4, unicode(clientes_atrasados[i]['importe_cuota']),style3)
                    # sheet.write(c, 5, unicode(clientes_atrasados[i]['total_atrasado']),style3)
                    # sheet.write(c, 6, unicode(clientes_atrasados[i]['total_pagado']),style3)
                    # # sheet.write(c, 7, unicode(clientes_atrasados[i]['valor_total_lote']),style3)
                    # sheet.write(c, 8, unicode(clientes_atrasados[i]['porc_pagado']),style4)
                    # sheet.write(c, 9,unicode(clientes_atrasados[i]['fecha_ultimo_pago']),style2)
                    # c += 1

                for i in range(len(clientes_atrasados)):
                    sheet.write(c, 0, clientes_atrasados[i]['cliente'], style3)
                    sheet.write(c, 1, unicode(clientes_atrasados[i]['telefono_particular']), style4)
                    sheet.write(c, 2, unicode('dir1: ' + clientes_atrasados[i]['direccion_particular'] + '  dir2: ' + clientes_atrasados[i]['direccion_cobro']), style4)
                    sheet.write(c, 3, unicode(clientes_atrasados[i]['lote']), style4)
                    sheet.write(c, 4, unicode(clientes_atrasados[i]['cuotas_atrasadas']), style4)
                    sheet.write(c, 5, unicode(clientes_atrasados[i]['cuotas_pagadas']), style4)
                    sheet.write(c, 6, unicode(clientes_atrasados[i]['importe_cuota']), style4)
                    sheet.write(c, 7, unicode(clientes_atrasados[i]['total_atrasado']), style4)
                    sheet.write(c, 8, unicode(clientes_atrasados[i]['total_pagado']),style4)
                    sheet.write(c, 9, unicode(clientes_atrasados[i]['porc_pagado']), style4)
                    sheet.write(c, 10, unicode(clientes_atrasados[i]['fecha_ultimo_pago']), style4)
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
    g_fraccion = ''
    filas_fraccion = []    
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
        fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date()
        fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date()
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
                    
    total_general_cuotas=0
    total_general_mora=0
    total_general_pagos=0
    #ver esto
    for i, cuota_item in enumerate(object_list):
        #Se setean los datos de cada fila
        cuota={}
        cuota['misma_fraccion'] = True
        nro_cuota=get_nro_cuota(cuota_item)
        if g_fraccion == '':
            g_fraccion = cuota_item.lote.manzana.fraccion.id
            cuota['misma_fraccion'] = False
        if g_fraccion != cuota_item.lote.manzana.fraccion.id:
            
            filas_fraccion[0]['misma_fraccion']= False
            cuotas.extend(filas_fraccion)
            filas_fraccion = []
                            
            g_fraccion = cuota_item.lote.manzana.fraccion.id
                            
            cuota={}
            #cuota['misma_fraccion'] = False
            cuota['total_cuotas']=unicode('{:,}'.format(total_cuotas)).replace(",", ".") 
            cuota['total_mora']=unicode('{:,}'.format(total_mora)).replace(",", ".")
            cuota['total_pago']=unicode('{:,}'.format(total_pagos)).replace(",", ".")
            cuota['ultimo_pago'] = True
            cuotas.append(cuota)
                            
            total_cuotas=0
            total_mora=0
            total_pagos=0
                            
            cuota = {}
            cuota['misma_fraccion'] = False
            cuota['ultimo_pago'] = False
            cuota['fraccion_id']=unicode(cuota_item.lote.manzana.fraccion.id)
            cuota['fraccion']=unicode(cuota_item.lote.manzana.fraccion)
            cuota['lote']=unicode(cuota_item.lote)
            cuota['cliente']=unicode(cuota_item.cliente)
            cuota['cuota_nro']=unicode(nro_cuota)+'/'+unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
            cuota['plan_de_pago']=cuota_item.plan_de_pago.nombre_del_plan
            cuota['fecha_pago']=unicode(cuota_item.fecha_de_pago.strftime("%d/%m/%Y"))
            cuota['total_de_cuotas']=unicode('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".") 
            cuota['total_de_mora']=unicode('{:,}'.format(cuota_item.total_de_mora)).replace(",", ".")
            cuota['total_de_pago']=unicode('{:,}'.format(cuota_item.total_de_pago)).replace(",", ".")
            #Se suman los totales por fraccion
            total_cuotas+=cuota_item.total_de_cuotas
            total_mora+=cuota_item.total_de_mora
            total_pagos+=cuota_item.total_de_pago
            
            total_general_cuotas+=cuota_item.total_de_cuotas
            total_general_mora+=cuota_item.total_de_mora
            total_general_pagos+=cuota_item.total_de_pago
                            
            filas_fraccion.append(cuota)
                            
        else:
            cuota['ultimo_pago'] = False
            cuota['misma_fraccion'] = True
            cuota['fraccion_id']=unicode(cuota_item.lote.manzana.fraccion.id)
            cuota['fraccion']=unicode(cuota_item.lote.manzana.fraccion)
            cuota['lote']=unicode(cuota_item.lote)
            cuota['cliente']=unicode(cuota_item.cliente)
            cuota['cuota_nro']=unicode(nro_cuota)+'/'+unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
            cuota['plan_de_pago']=cuota_item.plan_de_pago.nombre_del_plan
            cuota['fecha_pago']=unicode(cuota_item.fecha_de_pago.strftime("%d/%m/%Y"))
            cuota['total_de_cuotas']=unicode('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".") 
            cuota['total_de_mora']=unicode('{:,}'.format(cuota_item.total_de_mora)).replace(",", ".")
            cuota['total_de_pago']=unicode('{:,}'.format(cuota_item.total_de_pago)).replace(",", ".")
            #Se suman los totales por fraccion
            total_cuotas+=cuota_item.total_de_cuotas
            total_mora+=cuota_item.total_de_mora
            total_pagos+=cuota_item.total_de_pago
                        
            total_general_cuotas+=cuota_item.total_de_cuotas
            total_general_mora+=cuota_item.total_de_mora
            total_general_pagos+=cuota_item.total_de_pago
                            
            filas_fraccion.append(cuota)
                                        
    cuotas.extend(filas_fraccion)
    cuota={}    
    cuota['total_cuotas']=unicode('{:,}'.format(total_cuotas)).replace(",", ".") 
    cuota['total_mora']=unicode('{:,}'.format(total_mora)).replace(",", ".")
    cuota['total_pago']=unicode('{:,}'.format(total_pagos)).replace(",", ".")
    cuota['ultimo_pago'] = True
    cuotas.append(cuota)
    cuota = {}
    cuota['total_general_cuotas']=unicode('{:,}'.format(total_general_cuotas)).replace(",", ".") 
    cuota['total_general_mora']=unicode('{:,}'.format(total_general_mora)).replace(",", ".")
    cuota['total_general_pago']=unicode('{:,}'.format(total_general_pagos)).replace(",", ".")
    cuotas.append(cuota)
    lista = cuotas
        
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    sheet.paper_size_code = 1
    style = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                              'font: name Gill Sans MT Condensed, bold True; align: horiz center')   
    style2 = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                         'font: name Gill Sans MT Condensed, bold True, height 160;')
    style3 = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160 ; align: horiz center')
    style4 = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160 ; align: horiz right')
    style5 = xlwt.easyxf('pattern: pattern solid, fore_colour white;''font: name Gill Sans MT Condensed, bold True, height 160 ; align: horiz right')
    
    style_normal = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160;')
    style_normal_centrado = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160; align: horiz center')
    
    style_fraccion = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                              'font: name Gill Sans MT Condensed, bold True; align: horiz center')  
    #Titulo
    #sheet.write_merge(0,0,0,7, 'PROPAR S.R.L.' ,style3)
    #sheet.write_merge(1,1,1,7, 'Sistema de Control de Loteamiento' ,style3)
    
    #sheet.header_str = 'PROPAR S.R.L.'
    periodo_1 = fecha_ini
    periodo_2 = fecha_fin
    usuario = unicode(request.user)
    sheet.header_str = (
     u"&LFecha: &D Hora: &T \nUsuario: "+usuario+" "
     u"&CPROPAR S.R.L.\n INFORME GENERAL DE PAGOS  "
     u"&RPeriodo del "+periodo_1+" al "+periodo_2+" \nPage &P of &N"
     )
    # cabeceras
    #sheet.write(0, 0, "Fraccion", style)

    # contador de filas
    c = 0
    for cuota in cuotas:
        try:
        
            if cuota['total_monto'] == True and cuota['ultimo_pago'] == False: 
                c += 1            
                sheet.write(c, 0, "Totales de Fraccion", style2)
                sheet.write(c, 5, cuota['total_cuotas'], style5)
                sheet.write(c, 6, cuota['total_mora'], style5)
                sheet.write(c, 7, cuota['total_pago'], style5)
        except Exception, error:
                #print error 
                pass     
        c+=1
        try:    
            if cuota['misma_fraccion'] == False:
                sheet.write_merge(c,c,0,7, cuota['fraccion'],style_fraccion)
                c +=1
                
                sheet.write(c, 0, "Lote", style)
                sheet.write(c, 1, "Cliente", style)
                sheet.write(c, 2, "Cuota.", style)
                sheet.write(c, 3, "Plan de Pago", style)
                sheet.write(c, 4, "Fecha", style)
                sheet.write(c, 5, "Total Cuotas", style)
                sheet.write(c, 6, "Total Mora", style)
                sheet.write(c, 7, "Total Pago", style)
                c +=1                
                
            sheet.write(c, 0, cuota['lote'],style_normal_centrado)
            sheet.write(c, 1, cuota['cliente'],style_normal)
            sheet.write(c, 2, cuota['cuota_nro'],style_normal_centrado)
            sheet.write(c, 3, cuota['plan_de_pago'],style_normal)
            sheet.write(c, 4, cuota['fecha_pago'],style_normal_centrado)
            sheet.write(c, 5, cuota['total_de_cuotas'],style4)
            sheet.write(c, 6, cuota['total_de_mora'],style4)
            sheet.write(c, 7, cuota['total_de_pago'],style4)
            
        except Exception, error:
                print error 
                #pass
                       
        try:
            if (cuota['ultimo_pago'] == True): 
                c+=1            
                sheet.write_merge(c,c,0,4, "Totales de Fraccion", style2)
                sheet.write(c, 5, cuota['total_cuotas'], style5)
                sheet.write(c, 6, cuota['total_mora'], style5)
                sheet.write(c, 7, cuota['total_pago'], style5)
        except Exception, error:
                #print error 
                pass
        try:                   
            if cuota['total_general_cuotas']:
                c += 1
                sheet.write_merge(c,c,0,4, "Totales Generales", style2)
                sheet.write(c, 5, cuota['total_general_cuotas'], style5)
                sheet.write(c, 6, cuota['total_general_mora'], style5)
                sheet.write(c, 7, cuota['total_general_pago'], style5)                
        except Exception, error:
            #print error
            pass
    #holaaa
    
    #Ancho de la columna Lote
    col_lote = sheet.col(0)
    col_lote.width = 256 * 8   # 12 characters wide
            
    #Ancho de la columna Fecha
    col_fecha = sheet.col(4)
    col_fecha.width = 256 * 10   # 10 characters wide
            
    #Ancho de la columna Nombre
    col_nombre = sheet.col(1)
    col_nombre.width = 256 * 25   # 25 characters wide 
            
    #Ancho de la columna Nro cuota
    col_nro_cuota = sheet.col(2)
    col_nro_cuota.width = 256 * 6   # 6 characters wide
    
    #Ancho de la columna mes
    col_mes = sheet.col(3)
    col_mes.width = 256 * 20   # 8 characters wide
    
    #Ancho de la columna monto pagado
    col_monto_pagado = sheet.col(5)
    col_monto_pagado.width = 256 * 11   # 11 characters wide
    
    #Ancho de la columna monto inmobiliarioa
    col_monto_inmo = sheet.col(6)
    col_monto_inmo.width = 256 * 11   # 11 characters wide
            
    #Ancho de la columna monto propietario
    col_nombre = sheet.col(7)
    col_nombre.width = 256 * 11   # 11 characters wide
       
    
    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo         
    response['Content-Disposition'] = 'attachment; filename=' + 'informe_general.xls'
    wb.save(response)
    return response    
   
def liquidacion_propietarios_reporte_excel(request):


    if request.user.is_authenticated():

        fecha_ini = request.GET['fecha_ini']
        fecha_fin = request.GET['fecha_fin']
        fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date()
        fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date()
        tipo_busqueda = request.GET['tipo_busqueda']
        order_by = request.GET['order_by']
        busqueda_id = request.GET['busqueda']
        # busqueda_label = request.GET['busqueda_label']

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

        ley = request.GET['ley']
        impuesto_renta  = request.GET['impuesto_renta']
        iva_comision = request.GET['iva_comision']
        descripcion = request.GET.get('descripcion_otros_descuentos', '')
        monto_descuento = request.GET.get('monto_otros_descuentos', '')
        total_descuentos = request.GET.get('total_descuentos', '')
        total_a_cobrar = request.GET['total_a_cobrar']

        #busqueda_label = request.GET['busqueda_label']

        lista_ordenada = obtener_pagos_liquidacion(busqueda_id, tipo_busqueda, fecha_ini_parsed, fecha_fin_parsed, order_by, None)
        lista = lista_ordenada

        wb = xlwt.Workbook(encoding='utf-8')
        sheet = wb.add_sheet('Liquidacion', cell_overwrite_ok=True,)
        sheet.paper_size_code = 1
        style_titulos_columna = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                                  'font: name Calibri; align: horiz center')

        style_titulos_columna_resaltados_centrados = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                                  'font: name Calibri; align: horiz center')
        style_titulos_columna_resaltados= xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                                  'font: name Calibri')


        style_titulo_resumen = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                             'font: name Calibri, bold True, height 200;')

        style_datos_montos = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz right')
        style_datos_montos_subrayado = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz right')
        style_datos_montos_importante = xlwt.easyxf('font: name Calibri, bold True, height 200 ; align: horiz right')
        # style_datos = xlwt.easyxf('pattern: pattern solid, fore_colour white;''font: name Calibri, height 200 ; align: horiz right')

        style_normal = xlwt.easyxf('font: name Calibri, height 200;')
        style_normal_subrayado_palabra = xlwt.easyxf('font: name Calibri, height 200;')
        style_subrayado_normal = xlwt.easyxf('font: name Calibri, height 200;')
        style_subrayado_normal_titulo = xlwt.easyxf('font: name Calibri, height 200; align: horiz center')
        style_doble_subrayado = xlwt.easyxf('font: name Calibri, height 200;')
        style_datos_texto = xlwt.easyxf('font: name Calibri, height 200; align: horiz center')

        style_fraccion = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                                  'font: name Calibri; align: horiz center')

        style_datos_montos_importante_doble_borde = xlwt.easyxf('font: name Calibri, bold True, height 200 ; align: horiz right')

        # BORDES PARA las columnas de titulos
        borders = xlwt.Borders()
        borders.top = xlwt.Borders.THIN
        borders.bottom = xlwt.Borders.DOUBLE
        style_titulos_columna_resaltados_centrados.borders = borders
        style_datos_montos_importante_doble_borde.borders = borders
        style_titulos_columna_resaltados.borders = borders

        # Subrayado normal
        border_subrayado = xlwt.Borders()
        border_subrayado.bottom = xlwt.Borders.THIN
        style_subrayado_normal.borders = border_subrayado
        style_datos_montos_subrayado.borders = border_subrayado
        style_subrayado_normal_titulo.borders = border_subrayado

        # Doble Subrayado negritas
        border_doble_subrayado = xlwt.Borders()
        border_doble_subrayado.bottom = xlwt.Borders.THIN
        style_doble_subrayado.borders = border_doble_subrayado

        # font
        font = xlwt.Font()
        font.underline = True
        style_normal_subrayado_palabra.font = font



        #Titulo
        #sheet.write_merge(0,0,0,7, 'PROPAR S.R.L.' ,style3)
        #sheet.write_merge(1,1,1,7, 'Sistema de Control de Loteamiento' ,style3)

        #sheet.header_str = 'PROPAR S.R.L.'
        periodo_1 = fecha_ini
        periodo_2 = fecha_fin
        usuario = unicode(request.user)
        sheet.header_str = (
         u"&L&8Fecha: &D Hora: &T \nUsuario: "+usuario+" "
         u"&C&8PROPAR S.R.L.\n LIQUIDACION DE PROPIETARIOS "
         u"&R&8Periodo del "+periodo_1+" al "+periodo_2+" \nPage &P of &N"
         )
        sheet.footer_str = ''



        c=0
        for pago in lista:
                try:
                    if pago['total_monto_pagado'] == True and pago['ultimo_pago'] == False:
                        c+=1
                        sheet.write_merge(c,c,0,4, "Liquidacion", style_titulo_resumen)

                        sheet.write(c, 5, pago['total_monto_pagado'],style_datos_montos)
                        sheet.write(c, 6, pago['total_monto_inmobiliaria'], style_datos_montos)
                        sheet.write(c, 7, pago['total_monto_propietario'], style_datos_montos)
                except Exception, error:
                    print error
                    pass

                c += 1
                try:
                    if pago['misma_fraccion'] == False:
                        #sheet.write(c, 0, "Fraccion: " + pago['fraccion'],style2)
                        if tipo_busqueda == 'propietario' :
                            propietario = Propietario.objects.get(pk=busqueda_id)
                            fraccion_str = pago['fraccion'] + ' (' + propietario.nombres + ' ' + propietario.apellidos + ')'
                        elif tipo_busqueda == 'fraccion' :
                            fraccion = Fraccion.objects.get(pk=busqueda_id)
                            fraccion_str = pago['fraccion'] + ' (' + fraccion.propietario.nombres + ' ' + fraccion.propietario.apellidos + ')'
                        sheet.write_merge(c,c,0,7, fraccion_str ,style_fraccion)
                        c +=1
                        sheet.write(c, 0, 'Lote', style_titulos_columna_resaltados_centrados)
                        sheet.write(c, 1, 'Fecha de pago', style_titulos_columna_resaltados_centrados)
                        sheet.write(c, 2, 'Cliente', style_titulos_columna_resaltados_centrados)
                        sheet.write(c, 3, 'Nro cuota', style_titulos_columna_resaltados_centrados)
                        sheet.write(c, 4, 'Mes', style_titulos_columna_resaltados_centrados)
                        sheet.write(c, 5, 'Monto Pagado', style_titulos_columna_resaltados_centrados)
                        sheet.write(c, 6, 'Monto Inmob', style_titulos_columna_resaltados_centrados)
                        sheet.write(c, 7, 'Monto Prop', style_titulos_columna_resaltados_centrados)
                        c+=2

                    sheet.write(c, 0, pago['lote'],style_datos_texto)
                    sheet.write(c, 1, pago['fecha_de_pago'],style_datos_texto)
                    sheet.write(c, 2, pago['cliente'],style_normal)
                    sheet.write(c, 3, pago['nro_cuota'],style_datos_texto)
                    sheet.write(c, 4, pago['mes'],style_datos_texto)
                    sheet.write(c, 5, pago['total_de_cuotas'],style_datos_montos)
                    sheet.write(c, 6, pago['monto_inmobiliaria'],style_datos_montos)
                    sheet.write(c, 7, pago['monto_propietario'], style_datos_montos)
                except Exception, error:
                    print error

                try:
                    if (pago['ultimo_pago'] == True):
                        c+=1
                        sheet.write_merge(c,c,0,4, "Liquidacion", style_titulo_resumen)
                        sheet.write(c, 5, pago['total_monto_pagado'],style_datos_montos)
                        sheet.write(c, 6, pago['total_monto_inmobiliaria'], style_datos_montos)
                        sheet.write(c, 7, pago['total_monto_propietario'], style_datos_montos)
                except Exception, error:
                    print error
                    pass

                try:
                    if (pago['total_general_pagado']):
                        c+=1
                        sheet.write_merge(c,c,0,1, "Totales de la fracción: ", style_titulos_columna)
                        sheet.write(c, 5, pago['total_general_pagado'],style_datos_montos)
                        sheet.write(c, 6, pago['total_general_inmobiliaria'], style_datos_montos)
                        sheet.write(c, 7, pago['total_general_propietario'], style_datos_montos)
                        c+=1
                        sheet.write(c, 5, 'IVA',style_titulos_columna)
                        sheet.write(c, 6, pago['iva_comision'], style_datos_montos_subrayado)

                        iva_comision = int(pago['iva_comision'].replace(".", ""))
                        total_general_inmobiliaria = int(unicode(pago['total_general_inmobiliaria']).replace(".", ""))
                        general_inmobiliario_con_comision = iva_comision + total_general_inmobiliaria
                        general_inmobiliario_con_comision_txt = unicode('{:,}'.format(general_inmobiliario_con_comision)).replace(",", ".")


                        c+=1
                        sheet.write(c,6, general_inmobiliario_con_comision_txt, style_datos_montos)

                        c+=2

                        sheet.write_merge(c,c,1,6, "RESUMEN IMPOSITIVO Y OTROS DESCUENTOS",style_subrayado_normal_titulo)
                        c+=1
                        sheet.write(c, 1, "Liquidacion Total", style_normal)
                        sheet.write(c, 6, pago['total_general_pagado'], style_datos_montos)
                        # sheet.write_merge(c,c,4,5, general_inmobiliario_con_comision, style_datos_montos)

                        c+=1
                        sheet.write(c, 1, "Monto Inmobiliaria", style_normal)
                        sheet.write(c,5,general_inmobiliario_con_comision_txt, style_datos_montos)
                        # sheet.write_merge(c,c,3,4, pago['iva_comision'], style_datos_montos)
                        c+=1
                        sheet.write(c, 1, "Retención IVA",style_normal)
                        sheet.write(c, 5, pago['ley'], style_datos_montos)
                        # sheet.write_merge(c,c,3,4, pago['ley'], style_datos_montos)
                        c+=1
                        sheet.write(c, 1, "Imp Renta 4.5%", style_normal)
                        sheet.write(c, 5, pago['impuesto_renta'], style_datos_montos)
                        # sheet.write_merge(c,c,3,4, pago['impuesto_renta'], style_datos_montos)
                        c+=1
                        sheet.write(c,1, "Detalle de Otros Descuentos", style_normal_subrayado_palabra)
                        sheet.write(c,2, "", style_normal)
                        sheet.write(c, 5, '', style_datos_montos)
                        # sheet.write_merge(c,c,3,4,'', style_datos_montos)
                        c+=1
                        if descripcion !='':
                            sheet.write(c,1, descripcion, style_normal)
                            sheet.write(c, 5, monto_descuento, style_datos_montos)
                            # sheet.write_merge(c,c,3,4, monto_descuento, style_datos_montos)
                            c+=1
                        else:
                            sheet.write(c,1, "Sin otros descuentos", style_normal)
                            sheet.write(c, 5, "0", style_datos_montos_subrayado)
                            sheet.write(c, 6, "", style_datos_montos_subrayado)
                            # sheet.write_merge(c,c,3,4, "0", style_datos_montos)
                            c+=1

                        total_descuentos = int(pago['ley'].replace(".", "")) + int(pago['impuesto_renta'].replace(".", ""))+general_inmobiliario_con_comision+int(monto_descuento.replace(".", ""))
                        total_descuentos_txt= unicode('{:,}'.format(total_descuentos)).replace(",", ".")
                        sheet.write(c, 1, "Total descuentos", style_normal)
                        sheet.write(c, 6, total_descuentos_txt, style_datos_montos)
                        # sheet.write_merge(c,c,3,4, total_descuentos, style_datos_montos)
                        c+=1
                        sheet.write(c, 1, "Total a cobrar por el propietario: ", style_titulos_columna_resaltados)
                        sheet.write(c, 2, "", style_titulos_columna_resaltados)
                        sheet.write(c, 3, "", style_titulos_columna_resaltados)
                        sheet.write(c, 4, "", style_titulos_columna_resaltados)
                        sheet.write(c, 5, "", style_titulos_columna_resaltados)
                        sheet.write(c, 6, total_a_cobrar, style_datos_montos_importante_doble_borde)
                        # sheet.write(c, 7, total_a_cobrar, style_datos_montos_importante)


                except Exception, error:
                    print error
                    pass

                #Ancho de la columna Lote
                col_lote = sheet.col(0)
                col_lote.width = 256 * 10   # 12 characters wide

                #Ancho de la columna Fecha
                col_fecha = sheet.col(1)
                col_fecha.width = 256 * 12   # 10 characters wide

                #Ancho de la columna Nombre
                col_nombre = sheet.col(2)
                col_nombre.width = 256 * 25   # 25 characters wide

                #Ancho de la columna Nro cuota
                col_nro_cuota = sheet.col(3)
                col_nro_cuota.width = 256 * 8   # 6 characters wide

                #Ancho de la columna mes
                col_mes = sheet.col(4)
                col_mes.width = 256 * 8   # 8 characters wide

                #Ancho de la columna monto pagado
                col_monto_pagado = sheet.col(5)
                col_monto_pagado.width = 256 * 11   # 11 characters wide

                #Ancho de la columna monto inmobiliarioa
                col_monto_inmo = sheet.col(6)
                col_monto_inmo.width = 256 * 11   # 11 characters wide

                #Ancho de la columna monto propietario
                col_nombre = sheet.col(7)
                col_nombre.width = 256 * 11   # 11 characters wide

        response = HttpResponse(content_type='application/vnd.ms-excel')
        # Crear un nombre intuitivo
        fecha_actual= datetime.datetime.now().date()
        fecha_str = unicode(fecha_actual)
        fecha = unicode(datetime.datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y"))

        if tipo_busqueda == 'fraccion':
            fraccion = Fraccion.objects.get(pk=busqueda_id)
            response['Content-Disposition'] = 'attachment; filename=' + 'liq_prop_'+fraccion.nombre+'_'+fecha+'.xls'
        elif tipo_busqueda == 'propietario':
            propietario = Propietario.objects.get(pk=busqueda_id)
            response['Content-Disposition'] = 'attachment; filename=' + 'liq_prop_'+propietario.nombres + '_' + propietario.apellidos+'_'+fecha+'.xls'
        else:
            response['Content-Disposition'] = 'attachment; filename=' + 'liquidacion_propietario_.xls'
        wb.save(response)
        return response
    else:
       return HttpResponseRedirect(reverse('login'))



def liquidacion_vendedores_reporte_excel(request):   
    
    fecha_ini = request.GET['fecha_ini']
    fecha_fin = request.GET['fecha_fin']
    fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date()
    fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date()
    busqueda_label = request.GET['busqueda_label']
    vendedor_id=request.GET['busqueda']
    print("vendedor_id ->" + vendedor_id)
                    
    ventas = Venta.objects.filter(vendedor_id = vendedor_id).order_by('lote__manzana__fraccion').select_related()
    ventas_id = []
                                
    for venta in ventas:
        ventas_id.append(venta.id)
                                
    pagos_de_cuotas_ventas = PagoDeCuotas.objects.filter(venta__in=ventas_id,fecha_de_pago__range=(fecha_ini_parsed, fecha_fin_parsed)).order_by('fecha_de_pago').prefetch_related('venta', 'venta__plan_de_pago_vendedor','venta__lote__manzana__fraccion')
    cant_cuotas_pagadas_ventas = PagoDeCuotas.objects.filter(venta__in=ventas_id, fecha_de_pago__lt=fecha_ini_parsed).values('venta_id').annotate(Sum('nro_cuotas_a_pagar')).prefetch_related('venta_id')
                    
    filas_fraccion = []
    filas=[]
                    
    total_fraccion_monto_pagado=0
    total_fraccion_monto_vendedor=0
                    
    total_general_monto_pagado=0
    total_general_monto_vendedor=0
    
    b_fraccion = False
    b_vendedor = True
    
    vendedor = Vendedor.objects.get(pk = vendedor_id)
    
    g_nombre_fraccion = ''
    g_nombre_vendedor = vendedor.nombres+"_"+vendedor.apellidos
    
    fecha_pago_str = ''
                    
    g_fraccion = ''
    for venta in ventas:
                        
        if venta.fecha_de_venta >= fecha_ini_parsed and venta.fecha_de_venta <= fecha_fin_parsed:  
                            #preguntar por el plan de pago de la venta con el vendedor, si el vendedor lleva un % de la venta total, un % de la entrega inicial
                            
            if venta.plan_de_pago_vendedor.tipo == 'contado':
                                
                if g_fraccion == '':
                    g_fraccion = venta.lote.manzana.fraccion
                if venta.lote.manzana.fraccion != g_fraccion:
                    #Totales por FRACCION
                    try:
                        filas_fraccion = sorted(filas_fraccion, key=lambda f: (f['fecha_de_pago_order']))
                    except Exception, error:
                        print error +": "+ fecha_pago_str
                    if filas_fraccion:                     
                        filas_fraccion[0]['misma_fraccion']= False
                        filas.extend(filas_fraccion)
                        filas_fraccion = []
                        fila = {}
                        fila['total_monto_pagado']=unicode('{:,}'.format(total_fraccion_monto_pagado)).replace(",", ".")
                        fila['total_monto_vendedor']=unicode('{:,}'.format(total_fraccion_monto_vendedor)).replace(",", ".")
                                                            
                        total_fraccion_monto_pagado=0
                        total_fraccion_monto_vendedor=0
                                                            
                        fila['ultimo_pago'] = True
                        filas.append(fila)
                    g_fraccion = venta.lote.manzana.fraccion.nombre
                    ok=True
                else:
                    montos = calculo_montos_liquidacion_vendedores_contado(venta)
                    monto_vendedor = montos['monto_vendedor']
                    fecha_pago_str = unicode(venta.fecha_de_venta)
                    fecha_pago = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                    fecha_pago_order = venta.fecha_de_venta
                                    
                    #Fraccion    Lote    Fecha de Pago    Cliente    Cuota Nº    Mes    Monto Pag Monto Prop.
                    fila={}
                    fila['fraccion'] = g_fraccion
                    fila['plan']=unicode(venta.plan_de_pago_vendedor)
                    fila['lote'] = venta.lote.codigo_paralot
                    fila['fecha_de_pago'] = fecha_pago
                    fila['fecha_de_pago_order'] = fecha_pago_order
                    fila['cliente'] = venta.cliente
                    fila['nro_cuota'] = 'Venta al Contado'
                    fila['monto_pagado']= venta.precio_final_de_venta
                    fila['monto_vendedor']= monto_vendedor
                    fila['misma_fraccion'] = True
                                    
                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                    fecha_1 = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                    parts_1 = fecha_1.split("/")
                    year_1 = parts_1[2];
                    mes_1 = int(parts_1[1]) - 1;
                    mes_year = monthNames[mes_1]+"/"+year_1;
                    fila['mes'] = mes_year
                                    
                    total_fraccion_monto_pagado+= fila['monto_pagado']
                    total_fraccion_monto_vendedor += fila['monto_vendedor']
                    
                    total_general_monto_pagado+= fila['monto_pagado']
                    total_general_monto_vendedor += fila['monto_vendedor']
                    
                    fila['monto_pagado'] = unicode('{:,}'.format(fila['monto_pagado'])).replace(",", ".")
                    fila['monto_vendedor']= unicode('{:,}'.format(fila['monto_vendedor'])).replace(",", ".")
                                    
                    filas_fraccion.append(fila)
                            
            if venta.entrega_inicial > 0:
                if g_fraccion == '':
                    g_fraccion = venta.lote.manzana.fraccion
                if venta.lote.manzana.fraccion != g_fraccion:
                    #Totales por FRACCION
                    try:
                        filas_fraccion = sorted(filas_fraccion, key=lambda f: (f['fecha_de_pago_order']))
                    except Exception, error:
                        print error +": "+ fecha_pago_str
                    if filas_fraccion:                                     
                        filas_fraccion[0]['misma_fraccion']= False
                        filas.extend(filas_fraccion)
                        filas_fraccion = []
                        fila = {}
                        fila['total_monto_pagado']=unicode('{:,}'.format(total_fraccion_monto_pagado)).replace(",", ".")
                        fila['total_monto_vendedor']=unicode('{:,}'.format(total_fraccion_monto_vendedor)).replace(",", ".")
                                                            
                        total_fraccion_monto_pagado=0
                        total_fraccion_monto_vendedor=0
                                            
                        fila['ultimo_pago'] = True
                        filas.append(fila)
                    g_fraccion = venta.lote.manzana.fraccion
                    ok=True
                else:
                                    
                    montos = calculo_montos_liquidacion_vendedores_entrega_inicial(venta)
                    monto_vendedor = montos['monto_vendedor']
                    fecha_pago_str = unicode(venta.fecha_de_venta)
                    fecha_pago = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                    fecha_pago_order = venta.fecha_de_venta
                                    
                    #Fraccion    Lote    Fecha de Pago    Cliente    Cuota Nº    Mes    Monto Pag Monto Prop.
                    fila={}
                    fila['fraccion'] = g_fraccion
                    fila['plan']=unicode(venta.plan_de_pago_vendedor)
                    fila['lote'] = venta.lote.codigo_paralot
                    fila['fecha_de_pago'] = fecha_pago
                    fila['fecha_de_pago_order'] = fecha_pago_order
                    fila['cliente'] = venta.cliente
                    fila['nro_cuota'] = 'Entrega Inicial'
                    fila['monto_pagado']= venta.entrega_inicial
                    fila['monto_vendedor']= monto_vendedor
                    fila['misma_fraccion'] = True
                                    
                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                    fecha_1 = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                    parts_1 = fecha_1.split("/")
                    year_1 = parts_1[2];
                    mes_1 = int(parts_1[1]) - 1;
                    mes_year = monthNames[mes_1]+"/"+year_1;
                    fila['mes'] = mes_year
                                    
                    total_fraccion_monto_pagado+= fila['monto_pagado']
                    total_fraccion_monto_vendedor += fila['monto_vendedor']
                                    
                    total_general_monto_pagado+= fila['monto_pagado']
                    total_general_monto_vendedor += fila['monto_vendedor']
                    
                    fila['monto_pagado'] = unicode('{:,}'.format(fila['monto_pagado'])).replace(",", ".")
                    fila['monto_vendedor']= unicode('{:,}'.format(fila['monto_vendedor'])).replace(",", ".")
                                    
                    filas_fraccion.append(fila)
                                
                            
        pagos = []    
        pagos = get_pago_cuotas(venta, fecha_ini_parsed,fecha_fin_parsed, pagos_de_cuotas_ventas, cant_cuotas_pagadas_ventas)                                            
        lista_cuotas_ven =[]
        lista_cuotas_ven.append(venta.plan_de_pago_vendedor.cuota_inicial)
        numero_cuota = venta.plan_de_pago_vendedor.cuota_inicial
        for i in range(venta.plan_de_pago_vendedor.cantidad_cuotas -1):
            numero_cuota +=  venta.plan_de_pago_vendedor.intervalos
            lista_cuotas_ven.append(numero_cuota)
                    
        for pago in pagos:
            #preguntar por el plan de pago de la venta con el vendedor, si el vendedor lleva un % del pago de acuerdo al nro de cuota que se está pagando
            try:
                                    
                if g_fraccion == "":
                    g_fraccion = venta.lote.manzana.fraccion
                                                    
                if pago['fraccion'] != g_fraccion:
                    #Totales por FRACCION
                    try:
                        filas_fraccion = sorted(filas_fraccion, key=lambda f: (f['fecha_de_pago_order']))
                    except Exception, error:
                        print error +": "+ fecha_pago_str
                                                        
                    if filas_fraccion:         
                        filas_fraccion[0]['misma_fraccion']= False
                        filas.extend(filas_fraccion)
                        filas_fraccion = []
                        fila = {}
                        fila['total_monto_pagado']=unicode('{:,}'.format(total_fraccion_monto_pagado)).replace(",", ".")
                        fila['total_monto_vendedor']=unicode('{:,}'.format(total_fraccion_monto_vendedor)).replace(",", ".")
                                                            
                        total_fraccion_monto_pagado=0
                        total_fraccion_monto_vendedor=0
                                            
                        fila['ultimo_pago'] = True
                        filas.append(fila)
                    g_fraccion = pago['fraccion']
                    ok=True
                                                        
                    montos = calculo_montos_liquidacion_vendedores(pago,venta, lista_cuotas_ven)
                    monto_vendedor = montos['monto_vendedor']
                    fecha_pago_str = unicode(pago['fecha_de_pago'])
                    try:
                        fecha_pago = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                    except Exception, error:
                        print error +": "+ fecha_pago_str
                                                         
                    # Se setean los datos de cada fila
                    fila={}
                    fila['misma_fraccion'] = True
                    fila['fraccion']=unicode(venta.lote.manzana.fraccion)
                    fila['plan']=unicode(venta.plan_de_pago_vendedor)
                    fila['fecha_de_pago']=fecha_pago
                    fila['fecha_de_pago_order']=pago['fecha_de_pago']
                    fila['lote']=unicode(pago['lote'])
                    fila['cliente']=unicode(venta.cliente)
                    fila['nro_cuota']=unicode(pago['nro_cuota_y_total'])
                    fila['total_de_cuotas']=unicode('{:,}'.format(int(pago['monto']))).replace(",", ".")
                    fila['monto_vendedor']=unicode('{:,}'.format(monto_vendedor)).replace(",", ".")
                                                         
                    cuotas_detalles = get_cuota_information_by_lote(pago['lote'].id, int(pago['nro_cuota']) , True, True, venta)
                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                    fecha_1 = cuotas_detalles[0]['fecha'] 
                    parts_1 = fecha_1.split("/")
                    year_1 = parts_1[2];
                    mes_1 = int(parts_1[1]) - 1;
                    mes_year = monthNames[mes_1]+"/"+year_1;
                    fila['mes'] = mes_year
                                                         
                    #if venta.lote.manzana.fraccion != g_fraccion: 
                    if monto_vendedor != 0: 
                        ok=False
                        # Se suman los TOTALES por FRACCION
                        total_fraccion_monto_vendedor += int(monto_vendedor)
                        total_fraccion_monto_pagado += int(pago['monto'])
                                                             
                        #Acumulamos para los TOTALES GENERALES
                        total_general_monto_pagado += int(pago['monto'])
                        total_general_monto_vendedor += int(monto_vendedor)
                                                            
                        filas_fraccion.append(fila)
                                                        
                else:
                                                        
                                                    
                    montos = calculo_montos_liquidacion_vendedores(pago,venta, lista_cuotas_ven)
                    monto_vendedor = montos['monto_vendedor']
                    fecha_pago_str = unicode(pago['fecha_de_pago'])
                    try:
                        fecha_pago = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                    except Exception, error:
                        print error +": "+ fecha_pago_str
                                                         
                    # Se setean los datos de cada fila
                    fila={}
                    fila['misma_fraccion'] = True
                    fila['fraccion']=unicode(venta.lote.manzana.fraccion)
                    fila['plan']=unicode(venta.plan_de_pago_vendedor)
                    fila['fecha_de_pago']=fecha_pago
                    fila['fecha_de_pago_order']=pago['fecha_de_pago']
                    fila['lote']=unicode(pago['lote'])
                    fila['cliente']=unicode(venta.cliente)
                    fila['nro_cuota']=unicode(pago['nro_cuota_y_total'])
                    fila['total_de_cuotas']=unicode('{:,}'.format(int(pago['monto']))).replace(",", ".")
                    fila['monto_vendedor']=unicode('{:,}'.format(monto_vendedor)).replace(",", ".")
                                                        
                    cuotas_detalles = get_cuota_information_by_lote(pago['lote'].id, int(pago['nro_cuota']) , True, True, venta)
                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                    fecha_1 = cuotas_detalles[0]['fecha'] 
                    parts_1 = fecha_1.split("/")
                    year_1 = parts_1[2];
                    mes_1 = int(parts_1[1]) - 1;
                    mes_year = monthNames[mes_1]+"/"+year_1;
                    fila['mes'] = mes_year
                                                         
                    #if venta.lote.manzana.fraccion != g_fraccion: 
                    if monto_vendedor != 0: 
                        ok=False
                        # Se suman los TOTALES por FRACCION
                        total_fraccion_monto_vendedor += int(monto_vendedor)
                        total_fraccion_monto_pagado += int(pago['monto'])
                                                             
                        #Acumulamos para los TOTALES GENERALES
                        total_general_monto_pagado += int(pago['monto'])
                        total_general_monto_vendedor += int(monto_vendedor)
                                                            
                        filas_fraccion.append(fila)
                                                    
                                                    
                                                     
                                                    
                                                
            except Exception, error:
                print "Error: "+ unicode(error)+ ", Id Pago: "+unicode(pago['id'])+ ", Fraccion: "+unicode(pago['fraccion'])+ ", lote: "+unicode(pago['lote']) +" Nro cuota: "+unicode(unicode(pago['nro_cuota_y_total']))
                                             
    #Totales GENERALES
    #filas = sorted(filas, key=lambda f: f['fecha_de_pago'])
    if filas_fraccion:
        filas_fraccion = sorted(filas_fraccion, key=lambda f: (f['fecha_de_pago_order']))
        filas_fraccion[0]['misma_fraccion']= False 
        filas.extend(filas_fraccion)
                                    
        fila = {}
        fila['total_monto_pagado']=unicode('{:,}'.format(total_fraccion_monto_pagado)).replace(",", ".")
        fila['total_monto_vendedor']=unicode('{:,}'.format(total_fraccion_monto_vendedor)).replace(",", ".")
        total_fraccion_monto_vendedor = 0
        total_fraccion_monto_pagado = 0
        fila['ultimo_pago'] = True
        filas.append(fila)
                                
    fila = {}
    fila['total_general_pagado']=unicode('{:,}'.format(total_general_monto_pagado)).replace(",", ".")
    fila['total_general_vendedor']=unicode('{:,}'.format(total_general_monto_vendedor)).replace(",", ".")
    ley = int(total_general_monto_pagado*0.015)
    filas.append(fila)
    filas[0]['misma_fraccion']= False
                    
                
    ultimo="&busqueda_label="+busqueda_label+"&busqueda="+vendedor_id+"&fecha_ini="+fecha_ini+"&fecha_fin="+fecha_fin         
                
    lista = filas
    #aquiiiii   
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    sheet.paper_size_code = 1
    style = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                              'font: name Calibri, bold True; align: horiz center')
    style2 = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                         'font: name Calibri, bold True, height 200;')
    style3 = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz center')
    style4 = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz right')
    style5 = xlwt.easyxf('pattern: pattern solid, fore_colour white;''font: name Calibri, bold True, height 200 ; align: horiz right')
    
    style_normal = xlwt.easyxf('font: name Calibri, height 200;')
    style_normal_centrado = xlwt.easyxf('font: name Calibri, height 200; align: horiz center')
    
    style_fraccion = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                              'font: name Calibri, bold True; align: horiz center')
    #Titulo
    #sheet.write_merge(0,0,0,7, 'PROPAR S.R.L.' ,style3)
    #sheet.write_merge(1,1,1,7, 'Sistema de Control de Loteamiento' ,style3)
    
    #sheet.header_str = 'PROPAR S.R.L.'
    periodo_1 = fecha_ini
    periodo_2 = fecha_fin
    usuario = unicode(request.user)
    sheet.header_str = (
     u"&LFecha: &D Hora: &T \nUsuario: "+usuario+" "
     u"&CPROPAR S.R.L.\n LIQUIDACION DE VENDEDORES "
     u"&RPeriodo del "+periodo_1+" al "+periodo_2+" \nPage &P of &N"
     )
    #sheet.footer_str = 'things'
    
    
    
    c=0
    sheet.write_merge(c,c,0,6, "Liquidacion del Vendedor: "+busqueda_label, style)
    c+=1
    for pago in filas:
            try:
                if pago['total_monto_pagado'] == True and pago['ultimo_pago'] == False: 
                    c+=1            
                    sheet.write_merge(c,c,0,4, "Liquidacion", style2)
                    
                    sheet.write(c, 5, unicode(pago['total_monto_pagado']),style5)
                    sheet.write(c, 6, unicode(pago['total_monto_vendedor']), style5)
            except Exception, error:
                print error 
                pass
             
            c += 1
            try:
                if pago['misma_fraccion'] == False:
                    #sheet.write(c, 0, "Fraccion: " + pago['fraccion'],style2)                  
                    sheet.write_merge(c,c,0,7, unicode(pago['fraccion']),style_fraccion)
                    c +=1
                    sheet.write(c, 0, 'Lote', style)
                    sheet.write(c, 1, 'Fecha de pago', style)
                    sheet.write(c, 2, 'Cliente', style)
                    sheet.write(c, 3, 'Nro cuota', style)
                    sheet.write(c, 4, 'Mes', style)
                    sheet.write(c, 5, 'Monto Pagado', style)
                    sheet.write(c, 6, 'Monto Vendedor', style)
                    c +=1
                    
                sheet.write(c, 0, unicode(pago['lote']),style_normal_centrado)
                sheet.write(c, 1, unicode(pago['fecha_de_pago']),style_normal_centrado)
                sheet.write(c, 2, unicode(pago['cliente']),style_normal)
                sheet.write(c, 3, unicode(pago['nro_cuota']),style_normal_centrado)
                sheet.write(c, 4, unicode(pago['mes']),style_normal_centrado)
                try:
                    sheet.write(c, 5, unicode(pago['total_de_cuotas']),style4)
                except Exception, error:
                    sheet.write(c, 5, unicode(pago['monto_pagado']),style4)
                
                sheet.write(c, 6, unicode(pago['monto_vendedor']), style4)
            except Exception, error:
                print error
            
            try:
                if (pago['ultimo_pago'] == True): 
                    c+=1            
                    sheet.write_merge(c,c,0,4, "Liquidacion", style2)
                    sheet.write(c, 5, unicode(pago['total_monto_pagado']),style5)
                    sheet.write(c, 6, unicode(pago['total_monto_vendedor']), style5)
            except Exception, error:
                print error 
                pass
            
            try:
                if (pago['total_general_pagado']): 
                    c+=1            
                    sheet.write_merge(c,c,0,4, "Liquidacion Total", style2)
                    sheet.write(c, 5, unicode(pago['total_general_pagado']),style5)
                    sheet.write(c, 6, unicode(pago['total_general_vendedor']), style5)
                    
                    
            except Exception, error:
                print error 
                pass
            
            #Ancho de la columna Lote
            col_lote = sheet.col(0)
            col_lote.width = 256 * 10   # 12 characters wide
            
            #Ancho de la columna Fecha
            col_fecha = sheet.col(1)
            col_fecha.width = 256 * 12   # 10 characters wide
            
            #Ancho de la columna Nombre
            col_nombre = sheet.col(2)
            col_nombre.width = 256 * 25   # 25 characters wide 
            
            #Ancho de la columna Nro cuota
            col_nro_cuota = sheet.col(3)
            col_nro_cuota.width = 256 * 10   # 6 characters wide
            
            #Ancho de la columna mes
            col_mes = sheet.col(4)
            col_mes.width = 256 * 8   # 8 characters wide
            
            #Ancho de la columna monto pagado
            col_monto_pagado = sheet.col(5)
            col_monto_pagado.width = 256 * 11   # 11 characters wide
            
            #Ancho de la columna monto inmobiliarioa
            col_monto_inmo = sheet.col(6)
            col_monto_inmo.width = 256 * 11   # 11 characters wide
            
            #Ancho de la columna monto propietario
            col_nombre = sheet.col(7)
            col_nombre.width = 256 * 11   # 11 characters wide
  
    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo
    fecha_actual= datetime.datetime.now().date()
    fecha_str = unicode(fecha_actual)
    fecha = unicode(datetime.datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
    
    if b_fraccion:         
        response['Content-Disposition'] = 'attachment; filename=' + 'liq_vend_'+g_nombre_fraccion+'_'+fecha+'.xls'
    elif b_vendedor:
        response['Content-Disposition'] = 'attachment; filename=' + 'liq_vend_'+g_nombre_vendedor+'_'+fecha+'.xls'
    else:
        response['Content-Disposition'] = 'attachment; filename=' + 'liquidacion_vendedores_.xls'
    wb.save(response)
    return response

def liquidacion_gerentes_reporte_excel(request):      
    tipo_liquidacion = request.GET['tipo_liquidacion']
    fecha_ini = request.GET['fecha_ini']
    fecha_fin = request.GET['fecha_fin']
    fecha_ini_parsed = unicode(datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date())
    fecha_fin_parsed = unicode(datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date())
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
        cuotas_para_vendedor=((cuota_item.plan_de_pago_vendedor.cantidad_cuotas)*(cuota_item.plan_de_pago_vendedor.intervalos))-cuota_item.plan_de_pago_vendedor.cuota_inicial                  
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
                com=int(cuota_item.total_de_cuotas*(float(cuota_item.plan_de_pago_vendedor.porcentaje_de_cuotas)/float(100)))
                if(cuota_item.venta.entrega_inicial):
                    #comision de la entrega inicial, si la hubiere
                    com_inicial=int(cuota_item.venta.entrega_inicial*(float(cuota_item.plan_de_pago_vendedor.porcentaje_cuota_inicial)/float(100)))
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
                com=int(cuota_item.total_de_cuotas*(float(cuota_item.plan_de_pago_vendedor.porcentaje_de_cuotas)/float(100)))
                if(cuota_item.venta.entrega_inicial):
                    #comision de la entrega inicial, si la hubiere
                    com_inicial=int(cuota_item.venta.entrega_inicial*(float(cuota_item.plan_de_pago_vendedor.porcentaje_cuota_inicial)/float(100)))
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
    sheet.paper_size_code = 1
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
    lote_ini_orig=request.GET['lote_ini']
    lote_fin_orig=request.GET['lote_fin']
    fecha_ini=request.GET['fecha_ini']
    fecha_fin=request.GET['fecha_fin']
    lote_ini_parsed = unicode(lote_ini_orig)
    lote_fin_parsed = unicode(lote_fin_orig)
    fecha_ini_parsed = None
    fecha_fin_parsed = None
    lotes=[]
    lotes.append(lote_ini_parsed)
    lotes.append(lote_fin_parsed)
    #print lotes
    rango_lotes_id=[]
    try:
        for l in lotes:
            fraccion_int = int(l[0:3])
            manzana_int = int(l[4:7])
            lote_int = int(l[8:])
            manzana = Manzana.objects.get(fraccion_id=fraccion_int, nro_manzana=manzana_int)
            lote = Lote.objects.get(manzana=manzana.id, nro_lote=lote_int)
            rango_lotes_id.append(lote.id)
        print rango_lotes_id
    except Exception, error:
        print error
    lote_ini=str(rango_lotes_id[0])
    lote_fin=str(rango_lotes_id[1])
    lista_movimientos=[]
    print 'lote inicial->'+unicode(lote_ini)
    print 'lote final->'+unicode(lote_fin)
    if fecha_ini != '' and fecha_fin != '':    
        fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date()
        fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date()
        try:
            lista_ventas = Venta.objects.filter(lote_id__range=(lote_ini, lote_fin)).order_by('lote__nro_lote')
            lista_reservas = Reserva.objects.filter(lote_id__range=(lote_ini,lote_fin), fecha_de_reserva__range=(fecha_ini_parsed, fecha_fin_parsed))
            lista_cambios = CambioDeLotes.objects.filter(Q(lote_nuevo_id__range=(lote_ini,lote_fin)) |Q(lote_a_cambiar__range=(lote_ini,lote_fin)), fecha_de_cambio__range=(fecha_ini_parsed, fecha_fin_parsed))
            lista_transferencias = TransferenciaDeLotes.objects.filter(lote_id__range=(lote_ini,lote_fin), fecha_de_transferencia__range=(fecha_ini_parsed, fecha_fin_parsed))
        except Exception, error:
            print error
            lista_ventas = []
            lista_reservas = []
            lista_cambios = []
            lista_transferencias = []
            pass 
    else:                  
        try:
            lista_ventas = Venta.objects.filter(lote_id__range=(lote_ini, lote_fin)).order_by('lote__nro_lote')
            lista_cambios = CambioDeLotes.objects.filter(Q(lote_nuevo_id__range=(lote_ini,lote_fin)) |Q(lote_a_cambiar__range=(lote_ini,lote_fin)))
            lista_reservas = Reserva.objects.filter(lote_id__range=(lote_ini, lote_fin))
            lista_transferencias = TransferenciaDeLotes.objects.filter(lote_id__range=(lote_ini, lote_fin))
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
        try:
            for item_venta in lista_ventas:
                try:
                    resumen_venta = {}
                    fecha_venta_str = unicode(item_venta.fecha_de_venta)
                    resumen_venta['fecha_de_venta'] = unicode(datetime.datetime.strptime(fecha_venta_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                    resumen_venta['lote']=item_venta.lote
                    resumen_venta['cliente'] = item_venta.cliente
                    resumen_venta['cantidad_de_cuotas'] = item_venta.plan_de_pago.cantidad_de_cuotas
                    resumen_venta['precio_final'] = unicode('{:,}'.format(item_venta.precio_final_de_venta)).replace(",",".")
                    resumen_venta['entrega_inicial'] = unicode('{:,}'.format(item_venta.entrega_inicial)).replace(",",".")
                    resumen_venta['tipo_de_venta'] = item_venta.plan_de_pago.tipo_de_plan
                    RecuperacionDeLotes.objects.get(venta=item_venta.id)
                    try:
                        venta_pagos_query_set = get_pago_cuotas_2(item_venta,fecha_ini_parsed, fecha_fin_parsed)
                        resumen_venta['recuperacion'] = True
                    except PagoDeCuotas.DoesNotExist:
                        venta_pagos_query_set = []
                except RecuperacionDeLotes.DoesNotExist:
                    print 'se encontro la venta no recuperada, la venta actual'
                    try:
                        venta_pagos_query_set = get_pago_cuotas_2(item_venta,fecha_ini_parsed, fecha_fin_parsed)
                        resumen_venta['recuperacion'] = False
                    except PagoDeCuotas.DoesNotExist:
                        venta_pagos_query_set = []

                ventas_pagos_list = []
                ventas_pagos_list.insert(0,resumen_venta) #El primer elemento de la lista de pagos es el resumen de la venta
                saldo_anterior=item_venta.precio_final_de_venta
                monto=item_venta.entrega_inicial
                saldo=saldo_anterior-monto
                tipo_de_venta = item_venta.plan_de_pago.tipo_de_plan
                for pago in venta_pagos_query_set:
                    saldo_anterior=saldo
                    monto= long(pago['monto'])
                    saldo=saldo_anterior-monto
                    cuota ={}
                    cuota['vencimiento'] = ""
                    cuota['tipo_de_venta'] = tipo_de_venta
                    fecha_pago_str = unicode(pago['fecha_de_pago'])
                    cuota['fecha_de_pago'] = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                    cuota['id'] = pago['id']
                    cuota['nro_cuota'] = pago['nro_cuota_y_total']
                                    
                    cuotas_detalles = []
                    cuotas_detalles = get_cuota_information_by_lote(pago['lote'].id, int(pago['nro_cuota']), True, True, item_venta)
                    cuota['vencimiento'] = cuota['vencimiento']+ unicode(cuotas_detalles[0]['fecha'])+' '
                                    
                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                    fecha_1 = cuota['vencimiento']
                    parts_1 = fecha_1.split("/")
                    year_1 = parts_1[2];
                    mes_1 = int(parts_1[1]) - 1;
                    mes_year = monthNames[mes_1]+"/"+year_1;
                    cuota['mes'] = mes_year 
                    cuota['saldo_anterior'] = unicode('{:,}'.format(int(saldo_anterior))).replace(",",".")
                    cuota['monto'] =  unicode('{:,}'.format(int(pago['monto']))).replace(",",".")
                    cuota['saldo'] =  unicode('{:,}'.format(int(saldo))).replace(",",".")
                    ventas_pagos_list.append(cuota)
                lista_movimientos.append(ventas_pagos_list)
        except Exception, error:
            print error

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
    
                        
    ultimo="&lote_ini="+lote_ini_orig+"&lote_fin="+lote_fin_orig+"&fecha_ini="+fecha_ini+"&fecha_fin="+fecha_fin
    
    lista = lista_movimientos
            
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    sheet.paper_size_code = 1
    style = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                              'font: name Calibri, bold True, height 200; align: horiz center')
    style2 = xlwt.easyxf('font: name Calibri, height 200;')
        
    style3 = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz right')
        
    style4 = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz center')
        
    usuario = unicode(request.user)
    
    if fecha_ini != '' and fecha_fin != '':
        sheet.header_str = (
                            u"&LFecha: &D Hora: &T \nUsuario: "+usuario+" "
                            u"&CPROPAR S.R.L.\n MOVIMIENTOS DE LOTES "
                            u"&RPeriodo del : "+fecha_ini+" al "+fecha_fin+" \nPage &P of &N"
                            )
    else:
        sheet.header_str = (
                            u"&LFecha: &D Hora: &T \nUsuario: "+usuario+" "
                            u"&CPROPAR S.R.L.\n MOVIMIENTOS DE LOTES "
                            u"&RPage &P of &N"
                            )    
    
    
    c = 0
    
    
    if mostrar_mvtos == True:
        for venta in lista:
            for i, pago in enumerate(venta):
                if i == 0: 
                    if pago['recuperacion']:
                        # cabeceras
                        sheet.write_merge(c,c,0,6, "Venta lote: "+unicode(pago['lote'])+" a "+unicode(pago['cliente']), style)
                        c=c+1
                        sheet.write(c, 0, "Lote", style)
                        sheet.write(c, 1, "Fecha", style)
                        sheet.write(c, 2, "Cliente", style) 
                        sheet.write(c, 3, "Tipo", style)
                        sheet.write(c, 4, "Estado", style)        
                        sheet.write(c, 5, "Entrega Inicial", style)
                        sheet.write(c, 6, "Precio Venta", style)
                        
                        c=c+1
                        
                        sheet.write(c, 0, unicode(pago['lote']), style4)
                        sheet.write(c, 1, pago['fecha_de_venta'], style4)
                        sheet.write(c, 2, unicode(pago['cliente']), style2) 
                        sheet.write(c, 3, pago['tipo_de_venta'], style2)
                        sheet.write(c, 4, "VENTA RECUPERADA", style4)    
                        sheet.write(c, 5, pago['entrega_inicial'], style3)        
                        sheet.write(c, 6, pago['precio_final'], style3)
                        
                        if pago['tipo_de_venta'] == 'credito':
                            c=c+1
                            sheet.write_merge(c,c,0,6, "Pagos de la Venta: "+unicode(pago['lote'])+" a "+unicode(pago['cliente']), style)
                            c=c+1
                            sheet.write(c, 0, "Fecha", style)
                            sheet.write(c, 1, "Cuota", style)
                            sheet.write(c, 2, "Vencimiento", style) 
                            sheet.write(c, 3, "Mes", style)
                            sheet.write(c, 4, "Saldo Anterior", style)        
                            sheet.write(c, 5, "Monto", style)
                            sheet.write(c, 6, "Saldo", style)
                        
                        c=c+1
                        
                    else:
                        
                        # cabeceras
                        sheet.write_merge(c,c,0,6, "Venta lote: "+unicode(pago['lote'])+" a "+unicode(pago['cliente']), style)
                        c=c+1
                        sheet.write(c, 0, "Lote", style)
                        sheet.write(c, 1, "Fecha", style)
                        sheet.write(c, 2, "Cliente", style) 
                        sheet.write(c, 3, "Tipo", style)
                        sheet.write(c, 4, "Estado", style)        
                        sheet.write(c, 5, "Entrega Inicial", style)
                        sheet.write(c, 6, "Precio Venta", style)
                        
                        c=c+1
                        
                        sheet.write(c, 0, unicode(pago['lote']), style4)
                        sheet.write(c, 1, pago['fecha_de_venta'], style4)
                        sheet.write(c, 2, unicode(pago['cliente']), style2) 
                        sheet.write(c, 3, pago['tipo_de_venta'], style4)
                        sheet.write(c, 4, "VENTA ACTUAL", style4)    
                        sheet.write(c, 5, pago['entrega_inicial'], style3)        
                        sheet.write(c, 6, pago['precio_final'], style3)
                        
                        if pago['tipo_de_venta'] == 'credito':
                            c=c+1
                            sheet.write_merge(c,c,0,6, "Pagos de la Venta: "+unicode(pago['lote'])+" a "+unicode(pago['cliente']), style)
                            c=c+1
                            sheet.write(c, 0, "Fecha", style)
                            sheet.write(c, 1, "Cuota", style)
                            sheet.write(c, 2, "Vencimiento", style) 
                            sheet.write(c, 3, "Mes", style)
                            sheet.write(c, 4, "Saldo Anterior", style)        
                            sheet.write(c, 5, "Monto", style)
                            sheet.write(c, 6, "Saldo", style)
                        
                        c=c+1
                else:
                    
                    sheet.write(c, 0, pago['fecha_de_pago'], style4)
                    sheet.write(c, 1, pago['nro_cuota'], style4)
                    sheet.write(c, 2, pago['vencimiento'], style4) 
                    sheet.write(c, 3, pago['mes'], style4)
                    sheet.write(c, 4, pago['saldo_anterior'], style3)        
                    sheet.write(c, 5, pago['monto'], style3)
                    sheet.write(c, 6, pago['saldo'], style3)
                    
                    c=c+1

    if mostrar_cambios == True:
        #poner titulo de cambio
        sheet.write_merge(c,c,0,3, "Cambio de Lote", style)
        c=c+1
        sheet.write(c, 0, "Fecha", style)
        sheet.write(c, 1, "Cliente", style)
        sheet.write(c, 2, "Lote a Cambiar", style) 
        sheet.write(c, 3, "Lote Nuevo", style)
        
        c=c+1
        
        for cambio in lista_cambios:                        
            sheet.write(c, 0, unicode(datetime.datetime.strptime(unicode(cambio.fecha_de_cambio), "%Y-%m-%d").strftime("%d/%m/%Y")), style4)
            sheet.write(c, 1, unicode(cambio.cliente), style2)
            sheet.write(c, 2, unicode(cambio.lote_a_cambiar), style4)
            sheet.write(c, 3, unicode(cambio.lote_nuevo), style4)
            
            c=c+1
        
    if mostrar_reservas == True:
        #poner titulo de reserva y lote reservado
        sheet.write_merge(c,c,0,3, "Reserva de Lote", style)
        c=c+1
        sheet.write(c, 0, "Fecha", style)
        sheet.write(c, 1, "Cliente", style)
        sheet.write(c, 2, "Lote", style)
        c=c+1
        
        for reserva in lista_reservas:                        
            sheet.write(c, 0, unicode(datetime.datetime.strptime(unicode(reserva.fecha_de_reserva), "%Y-%m-%d").strftime("%d/%m/%Y")), style4)
            sheet.write(c, 1, unicode(reserva.cliente), style2)
            sheet.write(c, 2, unicode(reserva.lote), style4)
            c=c+1
        
    if mostrar_transferencias == True:
        #poner titulo de transferencia 
        sheet.write_merge(c,c,0,3, "Transferencia de Lote", style)
        c=c+1
        sheet.write(c, 0, "Fecha", style)
        sheet.write(c, 1, "Cliente Orig.", style) 
        sheet.write(c, 2, "Cliente Trans.", style)
        sheet.write(c, 3, "Vendedor", style)        
        sheet.write(c, 4, "Plan de Pago", style)
        
        c=c+1
        
        for transferencia in lista_transferencias:                        
            sheet.write(c, 0, unicode(datetime.datetime.strptime(unicode(transferencia.fecha_de_transferencia), "%Y-%m-%d").strftime("%d/%m/%Y")), style4)
            sheet.write(c, 1, unicode(transferencia.cliente_original), style2)
            sheet.write(c, 2, unicode(transferencia.cliente), style2)
            sheet.write(c, 3, unicode(transferencia.vendedor), style2)
            sheet.write(c, 4, unicode(transferencia.plan_de_pago), style2)
            
            c=c+1               
    
    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo         
    response['Content-Disposition'] = 'attachment; filename=' + 'informe_movimientos.xls'
    wb.save(response)
    return response       

def informe_ventas(request):    
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
                if (filtros_establecidos(request.GET,'informe_ventas') == False):
                    t = loader.get_template('informes/informe_ventas.html')
                    c = RequestContext(request, {
                        'object_list': [],
                    })
                    return HttpResponse(t.render(c))
                else: #Parametros seteados
                    lista_movimientos = []
                    t = loader.get_template('informes/informe_ventas.html')
                    lote_id=request.GET['busqueda']
                    busqueda_label=request.GET['busqueda_label']
                    busqueda = lote_id
                    lote = Lote.objects.get(pk=lote_id)
                    lista_ventas = Venta.objects.filter(lote_id=lote.id).order_by('-fecha_de_venta')
                    try:
                        for item_venta in lista_ventas:
                            try:
                                resumen_venta = {}
                                resumen_venta['id'] = item_venta.id
                                resumen_venta['fecha_de_venta'] = datetime.datetime.strptime(unicode(item_venta.fecha_de_venta), "%Y-%m-%d").strftime("%d/%m/%Y")
                                resumen_venta['lote']=item_venta.lote
                                resumen_venta['cliente'] = item_venta.cliente
                                resumen_venta['cantidad_de_cuotas'] = item_venta.plan_de_pago.cantidad_de_cuotas
                                resumen_venta['precio_final'] = unicode('{:,}'.format(item_venta.precio_final_de_venta)).replace(",",".")
                                resumen_venta['precio_de_cuota'] = unicode('{:,}'.format(item_venta.precio_de_cuota)).replace(",",".")
                                resumen_venta['fecha_primer_vencimiento'] = datetime.datetime.strptime(unicode(item_venta.fecha_primer_vencimiento), "%Y-%m-%d").strftime("%d/%m/%Y")
                                resumen_venta['entrega_inicial'] = unicode('{:,}'.format(item_venta.entrega_inicial)).replace(",",".")
                                resumen_venta['vendedor'] = item_venta.vendedor
                                resumen_venta['plan_de_pago'] = item_venta.plan_de_pago
                                resumen_venta['pagos_realizados'] = item_venta.pagos_realizados
                                resumen_venta['recuperado'] = item_venta.recuperado
                                
                                #venta_pagos_query_set = get_pago_cuotas(item_venta,None,None)
                                venta_pagos_query_set = PagoDeCuotas.objects.filter(venta_id=item_venta.id).order_by("fecha_de_pago","id")
                            except Exception, error:
                                print error
                            ventas_pagos_list = []
                            ventas_pagos_list.insert(0,resumen_venta) #El primer elemento de la lista de pagos es el resumen de la venta
                            contador_cuotas = 0
                            
                            for pago in venta_pagos_query_set:
                                cuota ={}
                                cuota['fecha_de_pago'] = datetime.datetime.strptime(unicode(pago.fecha_de_pago), "%Y-%m-%d").strftime("%d/%m/%Y")
                                cuota['id'] = pago.id
                                detalle_str = ""
                                cuota['detalle'] = ""
                                cuota['dias_atraso'] = ""
                                cuota['vencimiento'] = ""
                                try:
                                    cuota['id_transaccion'] = pago.transaccion.id
                                except:
                                    cuota['id_transaccion'] = None
                                
                                if pago.factura_id != None:
                                    cuota['factura'] = pago.factura
                                else:
                                    cuota['factura'] = None
                                #Si se paga mas de una cuota
                                if pago.nro_cuotas_a_pagar > 1:
                                    cuota['nro_cuota'] = unicode(contador_cuotas+1) +" al "+ unicode(contador_cuotas + pago.nro_cuotas_a_pagar)
                                    
                                    #detalle para fecha de vencimiento
                                    
                                    c= 0
                                    cuota['vencimiento'] = ""
                                    cuota['dias_atraso'] = ""
                                    for x in range(0, pago.nro_cuotas_a_pagar):
                                        contador_cuotas = contador_cuotas + 1
                                        cuotas_detalles = []
                                        cuotas_detalles = get_cuota_information_by_lote(lote_id,contador_cuotas, True, True)
                                        cuota['vencimiento'] = cuota['vencimiento']+ unicode(cuotas_detalles[0]['fecha'])+' '
                                        
                                        fecha_pago_parsed = datetime.datetime.strptime(cuota['fecha_de_pago'], "%d/%m/%Y").date()
                                        proximo_vencimiento_parsed = datetime.datetime.strptime(unicode(cuotas_detalles[0]['fecha']), "%d/%m/%Y").date()
                                        dias_atraso = obtener_dias_atraso(fecha_pago_parsed,proximo_vencimiento_parsed)
                                        cuota['dias_atraso'] = cuota['dias_atraso']+ " * "+ unicode(dias_atraso)+ " dias "
                                        
                                        c=c+1
                                        pago_detalle = pago.detalle
                                        monto_intereses = 0
                                        if pago_detalle != None and pago_detalle != '':
                                            #pago_detalle = json.dumps(pago_detalle)  
                                            pago_detalle = json.loads(pago_detalle)
                                            detalle_str = ""
                                            for x in range(0, len(pago_detalle)):
                                                try: 
                                                    detalle_str = detalle_str + " Intereses: "+  unicode('{:,}'.format(pago_detalle['item'+unicode(x)]['intereses'])).replace(",",".")
                                                    monto_intereses = monto_intereses + int (pago_detalle['item'+unicode(x)]['intereses'])  
                                                except Exception, error:
                                                    try:
                                                        detalle_str = detalle_str + " Gestion Cobranza: "+ unicode('{:,}'.format(int(pago_detalle['item'+unicode(x)]['gestion_cobranza']))).replace(",",".")   
                                                    except Exception, error:
                                                        print error
                                    
                                        
                                #si se paga solo una cuota    
                                else:
                                    contador_cuotas = contador_cuotas + pago.nro_cuotas_a_pagar
                                    #detalle para fecha de vencimiento
                                    cuotas_detalles = []
                                    cuotas_detalles = get_cuota_information_by_lote(lote_id,contador_cuotas, True, True, item_venta)
                                    cuota['vencimiento'] = unicode(cuotas_detalles[0]['fecha'])
                                    
                                    fecha_pago_parsed = datetime.datetime.strptime(cuota['fecha_de_pago'], "%d/%m/%Y").date()
                                    proximo_vencimiento_parsed = datetime.datetime.strptime(cuota['vencimiento'], "%d/%m/%Y").date()
                                    dias_atraso = obtener_dias_atraso(fecha_pago_parsed,proximo_vencimiento_parsed)
                                    cuota['dias_atraso'] = cuota['dias_atraso']+ " * "+ unicode(dias_atraso)+ " dias "
                                    
                                    cuota['nro_cuota'] = unicode(contador_cuotas)
                                    pago_detalle = pago.detalle
                                    monto_intereses = 0
                                    if pago_detalle != None and pago_detalle != '':
                                        #pago_detalle = json.dumps(pago_detalle)  
                                        pago_detalle = json.loads(pago_detalle)
                                        detalle_str = ""
                                        for x in range(0, len(pago_detalle)):
                                            try: 
                                                detalle_str = detalle_str + " Intereses: "+  unicode('{:,}'.format(pago_detalle['item'+unicode(x)]['intereses'])).replace(",",".")
                                                monto_intereses = monto_intereses + int (pago_detalle['item'+unicode(x)]['intereses'])  
                                            except Exception, error:
                                                try:
                                                    detalle_str = detalle_str + " Gestion Cobranza: "+ unicode('{:,}'.format(int(pago_detalle['item'+unicode(x)]['gestion_cobranza']))).replace(",",".")   
                                                except Exception, error:
                                                    print error
                                    
                                if pago.nro_cuotas_a_pagar > 1:
                                    monto_cuota = pago.total_de_pago - monto_intereses
                                    for x in range(x, pago.nro_cuotas_a_pagar+1):
                                        cuota['detalle'] = cuota['detalle'] + ' Monto Cuota: '+ unicode('{:,}'.format(monto_cuota/pago.nro_cuotas_a_pagar)).replace(",",".")
                                        
                                    cuota['detalle'] = cuota['detalle'] + detalle_str 
                                else:            
                                    monto_cuota = pago.total_de_pago - monto_intereses
                                    cuota['detalle'] = 'Monto Cuota: '+ unicode('{:,}'.format(monto_cuota)).replace(",",".") + detalle_str
                                
                                cuota['cantidad_cuotas'] = pago.nro_cuotas_a_pagar
                                cuota['monto'] =  unicode('{:,}'.format(pago.total_de_pago)).replace(",",".")
                                ventas_pagos_list.append(cuota)
                            lista_movimientos.append(ventas_pagos_list)
                    except Exception, error:
                        print error             

                    lista = lista_movimientos             

#                     paginator = Paginator(lista_movimientos, 25)
#                     page = request.GET.get('page')
#                     try:
#                         lista = paginator.page(page)
#                     except PageNotAnInteger:
#                         lista = paginator.page(1)
#                     except EmptyPage:
#                         lista = paginator.page(paginator.num_pages) 
                    
                    ultimo="&busqueda="+busqueda+"&busqueda_label="+busqueda_label
                    c = RequestContext(request, {
                        'lista_ventas': lista,
                        'lote_id' : lote_id,
                        'busqueda': busqueda,
                        'busqueda_label': busqueda_label,
                        'ultimo' : ultimo,
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
        
def informe_ventas_reporte_excel(request):
    lista_movimientos = []
    lote_id=request.GET['busqueda']
    busqueda_label=request.GET['busqueda_label']
    busqueda = lote_id
    lote = Lote.objects.get(pk=lote_id)
    lista_ventas = Venta.objects.filter(lote_id=lote.id).order_by('-fecha_de_venta')
    try:
                        for item_venta in lista_ventas:
                            try:
                                resumen_venta = {}
                                resumen_venta['id'] = item_venta.id
                                resumen_venta['fecha_de_venta'] = datetime.datetime.strptime(unicode(item_venta.fecha_de_venta), "%Y-%m-%d").strftime("%d/%m/%Y")
                                resumen_venta['lote']=item_venta.lote
                                resumen_venta['cliente'] = item_venta.cliente
                                resumen_venta['cantidad_de_cuotas'] = item_venta.plan_de_pago.cantidad_de_cuotas
                                resumen_venta['precio_final'] = unicode('{:,}'.format(item_venta.precio_final_de_venta)).replace(",",".")
                                resumen_venta['precio_de_cuota'] = unicode('{:,}'.format(item_venta.precio_de_cuota)).replace(",",".")
                                resumen_venta['fecha_primer_vencimiento'] = datetime.datetime.strptime(unicode(item_venta.fecha_primer_vencimiento), "%Y-%m-%d").strftime("%d/%m/%Y")
                                resumen_venta['entrega_inicial'] = unicode('{:,}'.format(item_venta.entrega_inicial)).replace(",",".")
                                resumen_venta['vendedor'] = item_venta.vendedor
                                resumen_venta['plan_de_pago'] = item_venta.plan_de_pago
                                resumen_venta['pagos_realizados'] = item_venta.pagos_realizados
                                resumen_venta['recuperado'] = item_venta.recuperado
                                
                                #venta_pagos_query_set = get_pago_cuotas(item_venta,None,None)
                                venta_pagos_query_set = PagoDeCuotas.objects.filter(venta_id=item_venta.id).order_by("fecha_de_pago","id")
                            except Exception, error:
                                print error
                            ventas_pagos_list = []
                            ventas_pagos_list.insert(0,resumen_venta) #El primer elemento de la lista de pagos es el resumen de la venta
                            contador_cuotas = 0
                            
                            for pago in venta_pagos_query_set:
                                cuota ={}
                                cuota['fecha_de_pago'] = datetime.datetime.strptime(unicode(pago.fecha_de_pago), "%Y-%m-%d").strftime("%d/%m/%Y")
                                cuota['id'] = pago.id
                                detalle_str = ""
                                cuota['detalle'] = ""
                                cuota['dias_atraso'] = ""
                                cuota['vencimiento'] = ""
                                try:
                                    cuota['id_transaccion'] = pago.transaccion.id
                                except:
                                    cuota['id_transaccion'] = None
                                
                                if pago.factura_id != None:
                                    cuota['factura'] = pago.factura
                                else:
                                    cuota['factura'] = None
                                #Si se paga mas de una cuota
                                if pago.nro_cuotas_a_pagar > 1:
                                    cuota['nro_cuota'] = unicode(contador_cuotas+1) +" al "+ unicode(contador_cuotas + pago.nro_cuotas_a_pagar)
                                    
                                    #detalle para fecha de vencimiento
                                    
                                    c= 0
                                    cuota['vencimiento'] = ""
                                    cuota['dias_atraso'] = ""
                                    for x in range(0, pago.nro_cuotas_a_pagar):
                                        contador_cuotas = contador_cuotas + 1
                                        cuotas_detalles = []
                                        cuotas_detalles = get_cuota_information_by_lote(lote_id,contador_cuotas, True, True)
                                        cuota['vencimiento'] = cuota['vencimiento']+ unicode(cuotas_detalles[0]['fecha'])+' '
                                        
                                        fecha_pago_parsed = datetime.datetime.strptime(cuota['fecha_de_pago'], "%d/%m/%Y").date()
                                        proximo_vencimiento_parsed = datetime.datetime.strptime(unicode(cuotas_detalles[0]['fecha']), "%d/%m/%Y").date()
                                        dias_atraso = obtener_dias_atraso(fecha_pago_parsed,proximo_vencimiento_parsed)
                                        cuota['dias_atraso'] = cuota['dias_atraso']+ " * "+ unicode(dias_atraso)+ " dias "
                                        
                                        c=c+1
                                        pago_detalle = pago.detalle
                                        monto_intereses = 0
                                        if pago_detalle != None and pago_detalle != '':
                                            #pago_detalle = json.dumps(pago_detalle)  
                                            pago_detalle = json.loads(pago_detalle)
                                            detalle_str = ""
                                            for x in range(0, len(pago_detalle)):
                                                try: 
                                                    detalle_str = detalle_str + " Intereses: "+  unicode('{:,}'.format(pago_detalle['item'+unicode(x)]['intereses'])).replace(",",".")
                                                    monto_intereses = monto_intereses + int (pago_detalle['item'+unicode(x)]['intereses'])  
                                                except Exception, error:
                                                    try:
                                                        detalle_str = detalle_str + " Gestion Cobranza: "+ unicode('{:,}'.format(int(pago_detalle['item'+unicode(x)]['gestion_cobranza']))).replace(",",".")   
                                                    except Exception, error:
                                                        print error
                                    
                                        
                                #si se paga solo una cuota    
                                else:
                                    contador_cuotas = contador_cuotas + pago.nro_cuotas_a_pagar
                                    #detalle para fecha de vencimiento
                                    cuotas_detalles = []
                                    cuotas_detalles = get_cuota_information_by_lote(lote_id,contador_cuotas, True, True, item_venta)
                                    cuota['vencimiento'] = unicode(cuotas_detalles[0]['fecha'])
                                    
                                    fecha_pago_parsed = datetime.datetime.strptime(cuota['fecha_de_pago'], "%d/%m/%Y").date()
                                    proximo_vencimiento_parsed = datetime.datetime.strptime(cuota['vencimiento'], "%d/%m/%Y").date()
                                    dias_atraso = obtener_dias_atraso(fecha_pago_parsed,proximo_vencimiento_parsed)
                                    cuota['dias_atraso'] = cuota['dias_atraso']+ " * "+ unicode(dias_atraso)+ " dias "
                                    
                                    cuota['nro_cuota'] = unicode(contador_cuotas)
                                    pago_detalle = pago.detalle
                                    monto_intereses = 0
                                    if pago_detalle != None and pago_detalle != '':
                                        #pago_detalle = json.dumps(pago_detalle)  
                                        pago_detalle = json.loads(pago_detalle)
                                        detalle_str = ""
                                        for x in range(0, len(pago_detalle)):
                                            try: 
                                                detalle_str = detalle_str + " Intereses: "+  unicode('{:,}'.format(pago_detalle['item'+unicode(x)]['intereses'])).replace(",",".")
                                                monto_intereses = monto_intereses + int (pago_detalle['item'+unicode(x)]['intereses'])  
                                            except Exception, error:
                                                try:
                                                    detalle_str = detalle_str + " Gestion Cobranza: "+ unicode('{:,}'.format(int(pago_detalle['item'+unicode(x)]['gestion_cobranza']))).replace(",",".")   
                                                except Exception, error:
                                                    print error
                                    
                                if pago.nro_cuotas_a_pagar > 1:
                                    monto_cuota = pago.total_de_pago - monto_intereses
                                    for x in range(x, pago.nro_cuotas_a_pagar+1):
                                        cuota['detalle'] = cuota['detalle'] + ' Monto Cuota: '+ unicode('{:,}'.format(monto_cuota/pago.nro_cuotas_a_pagar)).replace(",",".")
                                        
                                    cuota['detalle'] = cuota['detalle'] + detalle_str 
                                else:            
                                    monto_cuota = pago.total_de_pago - monto_intereses
                                    cuota['detalle'] = 'Monto Cuota: '+ unicode('{:,}'.format(monto_cuota)).replace(",",".") + detalle_str
                                
                                cuota['cantidad_cuotas'] = pago.nro_cuotas_a_pagar
                                cuota['monto'] =  unicode('{:,}'.format(pago.total_de_pago)).replace(",",".")
                                ventas_pagos_list.append(cuota)
                            lista_movimientos.append(ventas_pagos_list)
    except Exception, error:
                    print error             

    lista = lista_movimientos
            
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    sheet.paper_size_code = 1
    style = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                                'font: name Calibri, bold True, height 200; align: horiz center')
    style2 = xlwt.easyxf('font: name Calibri, height 200;')
                        
    style3 = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz right')
                        
    style4 = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz center')
                        
    usuario = unicode(request.user)
                    
    sheet.header_str = (
                        u"&LFecha: &D Hora: &T \nUsuario: "+usuario+" "
                        u"&CPROPAR S.R.L.\n INFORME VENTA DE LOTES "
                        u"&RPage &P of &N"
                        )    
                    
                    
    c = 0
                    
                    
    for venta in lista:
        for i, pago in enumerate(venta):
            if i == 0: 
                    # cabeceras
                    sheet.write_merge(c,c,0,6, "Venta lote: "+unicode(pago['lote'])+" Vendedor: "+unicode(pago['vendedor'])+" a Cliente: "+unicode(pago['cliente'])+ " el: "+unicode(pago['fecha_de_venta']), style)
                    c=c+1
                    sheet.write(c, 0, "Fecha 1er Vto.", style) 
                    sheet.write(c, 1, "Plan de Pago", style)
                    sheet.write(c, 2, "Entrega Inicial", style)
                    sheet.write(c, 3, "Precio Cuota", style)
                    sheet.write(c, 4, "Precio Venta", style)
                    sheet.write(c, 5, "Cuotas Pagadas", style)
                    sheet.write(c, 6, "Recuperado", style)
                                        
                    c=c+1
                                        
                    sheet.write(c, 0, pago['fecha_primer_vencimiento'], style4)
                    sheet.write(c, 1, unicode(pago['plan_de_pago']), style2)
                    sheet.write(c, 2, unicode(pago['entrega_inicial']), style3) 
                    sheet.write(c, 3, unicode(pago['precio_de_cuota']), style3)
                    sheet.write(c, 4, unicode(pago['precio_final']), style3)    
                    sheet.write(c, 5, unicode(pago['pagos_realizados']), style4)
                    if pago['recuperado']:
                        sheet.write(c, 6, "SI", style4)
                    else:
                        sheet.write(c, 6, "NO", style4)
                                        
                    if pago['plan_de_pago'].tipo_de_plan == 'credito':
                        c=c+1
                        sheet.write_merge(c,c,0,6, "Pagos de la Venta lote: "+unicode(pago['lote'])+" Vendedor: "+unicode(pago['vendedor'])+" a Cliente: "+unicode(pago['cliente'])+ " el: "+unicode(pago['fecha_de_venta']), style)
                        c=c+1
                        sheet.write(c, 0, "Fecha", style)
                        sheet.write(c, 1, "Cant. Cuotas", style)
                        sheet.write(c, 2, "Nro. Cuotas", style) 
                        sheet.write(c, 3, "Monto", style)
                        sheet.write(c, 4, "Factura", style)        
                        sheet.write(c, 5, "Transaccion", style)
                                        
                    c=c+1
                                        
            else:
                    
                sheet.write(c, 0, pago['fecha_de_pago'], style4)
                sheet.write(c, 1, unicode(pago['cantidad_cuotas']), style4)
                sheet.write(c, 2, unicode(pago['nro_cuota']), style4)
                sheet.write(c, 3, unicode(pago['monto']), style3)
                if pago['factura'] == None:
                    sheet.write(c, 4, "Sin Factura" , style4)        
                else:
                    sheet.write(c, 4, unicode(pago['factura'].numero) , style4)
                if pago['id_transaccion'] == None:
                    sheet.write(c, 5, "Interna" , style4)        
                else:
                    sheet.write(c, 5, unicode(pago['id_transaccion']), style4)
                
                    
                c=c+1
                
                col_nombre = sheet.col(1)
                col_nombre.width = 256 * 25
                
    response = HttpResponse(content_type='application/vnd.ms-excel')
                    # Crear un nombre intuitivo         
    response['Content-Disposition'] = 'attachment; filename=' + 'informe_movimientos.xls'
    wb.save(response)
    return response    
            


def calculo_montos_liquidacion_propietarios(pago,venta, lista_cuotas_inm):
    try:                                                     
        #cuotas_para_propietario=((venta.plan_de_pago.cantidad_cuotas_inmobiliaria)*(venta.plan_de_pago.intervalos_cuotas_inmobiliaria))-venta.plan_de_pago.inicio_cuotas_inmobiliaria
        #ultima_cuota_inmb = ((venta.plan_de_pago.cantidad_cuotas_inmobiliaria - 1) * venta.plan_de_pago.intervalos_cuotas_inmobiliaria) + venta.plan_de_pago.inicio_cuotas_inmobiliaria
        if(int(pago['nro_cuota']) in lista_cuotas_inm):
            monto_inmobiliaria = int(int(pago['monto']) * (float(venta.plan_de_pago.porcentaje_cuotas_inmobiliaria) / float(100)))
            monto_propietario = int(pago['monto']) - monto_inmobiliaria
            '''
            if(int(pago['nro_cuota']) % 2 != 0):    
                monto_inmobiliaria = pago['monto']
                monto_propietario = 0
            else:
                monto_inmobiliaria = int(int(pago['monto']) * (float(venta.plan_de_pago.porcentaje_cuotas_administracion) / float(100)))
                monto_propietario = int(pago['monto']) - monto_inmobiliaria
            '''
        else:
            monto_inmobiliaria = int(int(pago['monto']) * (float(venta.plan_de_pago.porcentaje_cuotas_administracion) / float(100)))
            monto_propietario = int(pago['monto']) - monto_inmobiliaria
        
        monto={}
        monto['monto_propietario'] = monto_propietario
        monto['monto_inmobiliaria'] = monto_inmobiliaria
        return monto
    except Exception, error:
        print error
        
def calculo_montos_liquidacion_vendedores(pago,venta, lista_cuotas_ven):
    try:                                                     
        #cuotas_para_propietario=((venta.plan_de_pago.cantidad_cuotas_inmobiliaria)*(venta.plan_de_pago.intervalos_cuotas_inmobiliaria))-venta.plan_de_pago.inicio_cuotas_inmobiliaria
        #ultima_cuota_inmb = ((venta.plan_de_pago.cantidad_cuotas_inmobiliaria - 1) * venta.plan_de_pago.intervalos_cuotas_inmobiliaria) + venta.plan_de_pago.inicio_cuotas_inmobiliaria
        if(int(pago['nro_cuota']) in lista_cuotas_ven):
            monto_vendedor = int(int(pago['monto']) * (float(venta.plan_de_pago_vendedor.porcentaje_de_cuotas) / float(100)))
            '''
            if(int(pago['nro_cuota']) % 2 != 0):    
                monto_inmobiliaria = pago['monto']
                monto_propietario = 0
            else:
                monto_inmobiliaria = int(int(pago['monto']) * (float(venta.plan_de_pago.porcentaje_cuotas_administracion) / float(100)))
                monto_propietario = int(pago['monto']) - monto_inmobiliaria
            '''
        else:
            #monto_vendedor = int(int(pago['monto']) * (float(venta.plan_de_pago_vendedor.porcentaje_de_cuotas) / float(100)))
            monto_vendedor = 0
        
        monto={}
        monto['monto_vendedor'] = monto_vendedor
        return monto
    except Exception, error:
        print error
        
def calculo_montos_liquidacion_propietarios_contado(venta):
    try:                                                     
        monto_inmobiliaria = int(int(venta.precio_final_de_venta) * (float(venta.plan_de_pago.porcentaje_inicial_inmobiliaria) / float(100)))
        monto_propietario = int(venta.precio_final_de_venta) - monto_inmobiliaria
        
        monto={}
        monto['monto_propietario'] = monto_propietario
        monto['monto_inmobiliaria'] = monto_inmobiliaria
        return monto
    except Exception, error:
        print error
        
def calculo_montos_liquidacion_propietarios_entrega_inicial(venta):
    try:                                                     
        monto_inmobiliaria = int(int(venta.entrega_inicial) * (float(venta.plan_de_pago.porcentaje_inicial_inmobiliaria) / float(100)))
        monto_propietario = int(venta.entrega_inicial) - monto_inmobiliaria
        
        monto={}
        monto['monto_propietario'] = monto_propietario
        monto['monto_inmobiliaria'] = monto_inmobiliaria
        return monto
    except Exception, error:
        print error
        
def calculo_montos_liquidacion_vendedores_contado(venta):
    try:                                                     
        monto_vendedor = int(int(venta.precio_final_de_venta)*(float(venta.plan_de_pago_vendedor.porcentaje_de_cuotas)/ float(100)))
        monto={}
        monto['monto_vendedor'] = monto_vendedor
        return monto
    except Exception, error:
        print error
        
def calculo_montos_liquidacion_vendedores_entrega_inicial(venta):
    try:                                                     
        monto_vendedor = int(int(venta.entrega_inicial)*(float(venta.plan_de_pago_vendedor.porcentaje_cuota_inicial)/ float(100)))
        
        monto={}
        monto['monto_vendedor'] = monto_vendedor
        return monto
    except Exception, error:
        print error
        
def calculo_montos_liquidacion_propietarios_2(pago,venta, lista_cuotas_inm):
    try:                                                     
        #cuotas_para_propietario=((venta.plan_de_pago.cantidad_cuotas_inmobiliaria)*(venta.plan_de_pago.intervalos_cuotas_inmobiliaria))-venta.plan_de_pago.inicio_cuotas_inmobiliaria
        #ultima_cuota_inmb = ((venta.plan_de_pago.cantidad_cuotas_inmobiliaria - 1) * venta.plan_de_pago.intervalos_cuotas_inmobiliaria) + venta.plan_de_pago.inicio_cuotas_inmobiliaria
        if(int(pago['nro_cuota']) in lista_cuotas_inm):
            monto_inmobiliaria = int(int(pago['monto']) * (float(venta.plan_de_pago.porcentaje_cuotas_inmobiliaria) / float(100)))
            monto_propietario = int(pago['monto']) - monto_inmobiliaria
            '''
            if(int(pago['nro_cuota']) % 2 != 0):    
                monto_inmobiliaria = pago['monto']
                monto_propietario = 0
            else:
                monto_inmobiliaria = int(int(pago['monto']) * (float(venta.plan_de_pago.porcentaje_cuotas_administracion) / float(100)))
                monto_propietario = int(pago['monto']) - monto_inmobiliaria
            '''
        else:
            monto_inmobiliaria = int(int(pago['monto']) * (float(venta.plan_de_pago.porcentaje_cuotas_administracion) / float(100)))
            monto_propietario = int(pago['monto']) - monto_inmobiliaria
        
        monto={}
        monto['monto_propietario'] = monto_propietario
        monto['monto_inmobiliaria'] = monto_inmobiliaria
        return monto
    except Exception, error:
        print error
        
        
def informe_facturacion(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
                if (filtros_establecidos(request.GET,'informe_facturacion') == False):
                    t = loader.get_template('informes/informe_facturacion.html')
                    grupo= request.user.groups.get().id                
                    c = RequestContext(request, {
                        'object_list': [],
                        'grupo': grupo
                    })
                    return HttpResponse(t.render(c))
                else: # Parametros SETEADOS
                    t = loader.get_template('informes/informe_facturacion.html')   
                    try:             
                        fecha_ini = request.GET['fecha_ini']
                        fecha_fin = request.GET['fecha_fin']
                        
                        busqueda = request.GET.get('busqueda','')
                        busqueda_label = request.GET.get('busqueda_label','')
                        
                        fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").strftime("%Y-%m-%d")
                        fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").strftime("%Y-%m-%d")
                        
                        filas = []
                        lista_totales = []
                        
                        
                        
                        
                        #Totales GENERALES
                        total_general_facturado = 0
                        total_general_exentas = 0
                        total_general_iva5 = 0
                        total_general_iva10 = 0
                        
                        try:
                            fila={}
                            grupo= request.user.groups.get().id
                            if grupo == 1:
                                if busqueda =='':
                                    facturas = Factura.objects.filter(anulado=False, fecha__range=(fecha_ini_parsed, fecha_fin_parsed))
                                else:
                                    facturas = Factura.objects.filter(anulado=False, fecha__range=(fecha_ini_parsed, fecha_fin_parsed), usuario = busqueda)
                            else:
                                facturas = Factura.objects.filter(anulado=False, fecha__range=(fecha_ini_parsed, fecha_fin_parsed), usuario = request.user)
                            
                            for factura in facturas:
                                
                                #Totales Factura
                                total_facturado = 0
                                total_exentas = 0
                                total_iva5 = 0
                                total_iva10 = 0
                                
                                fecha_str = unicode(factura.fecha)
                                fecha = unicode(datetime.datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                
                                # Se setean los datos de cada fila
                                fila={}
                                fila['id'] = factura.id
                                fila['fecha']= fecha
                                fila['numero']= factura.numero
                                fila['cliente']=unicode(factura.cliente)
                                fila['lote']=unicode(factura.lote.codigo_paralot)
                                fila['tipo']=unicode(factura.tipo)
                                if factura.usuario_id != None:
                                    fila['usuario']=unicode(factura.usuario)
                                
                                lista_detalles=json.loads(factura.detalle)
                                for key, value in lista_detalles.iteritems():
                                    total_exentas+=int(value['exentas'])
                                    total_iva5+=int(value['iva_5'])
                                    total_iva10+=int(value['iva_10'])
                                    total_facturado+=int(int(value['cantidad'])*int(value['precio_unitario'])) 
                                
                                fila['total_exentas']=unicode('{:,}'.format(total_exentas)).replace(",", ".")
                                fila['total_iva5']=unicode('{:,}'.format(total_iva5)).replace(",", ".")
                                fila['total_iva10']=unicode('{:,}'.format(total_iva10)).replace(",", ".")
                                fila['total_facturado']=unicode('{:,}'.format(total_facturado)).replace(",", ".")
                                
                                filas.append(fila)
                                
                                #Acumulamos para los TOTALES GENERALES
                                total_general_exentas += int(total_exentas)
                                total_general_iva5 += int(total_iva5)
                                total_general_iva10 += int(total_iva10)
                                total_general_facturado += int(total_facturado)
                                
                            #Totales GENERALES
                            fila['total_general_facturado']=unicode('{:,}'.format(total_general_facturado)).replace(",", ".")
                            fila['total_general_exentas']=unicode('{:,}'.format(total_general_exentas)).replace(",", ".")
                            fila['total_general_iva5']=unicode('{:,}'.format(total_general_iva5)).replace(",", ".")
                            fila['total_general_iva10']=unicode('{:,}'.format(total_general_iva10)).replace(",", ".")
                                
                        except Exception, error:
                            print error                                                                                       
                                                    
                        ultimo="&fecha_ini="+fecha_ini+"&fecha_fin="+fecha_fin+"&busqueda="+busqueda+"&busqueda_label"
                        lista = filas
                        
#                         paginator = Paginator(filas, 25)
#                         page = request.GET.get('page')
#                         try:
#                             lista = paginator.page(page)
#                         except PageNotAnInteger:
#                             lista = paginator.page(1)
#                         except EmptyPage:
#                             lista = paginator.page(paginator.num_pages)
                                      
                        c = RequestContext(request, {
                            'object_list': lista,
                            'lista_totales' : lista_totales,
                            'fecha_ini':fecha_ini,
                            'fecha_fin':fecha_fin,
                            'grupo': grupo,
                            'ultimo': ultimo,
                            'busqueda_label':busqueda_label,
                            'busqueda': busqueda,
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
        
def informe_facturacion_reporte_excel(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
                if (filtros_establecidos(request.GET,'informe_facturacion') == False):
                    t = loader.get_template('informes/informe_facturacion.html')                
                    c = RequestContext(request, {
                        'object_list': [],
                    })
                    return HttpResponse(t.render(c))
                else: # Parametros SETEADOS
                    t = loader.get_template('informes/informe_facturacion.html')   
                    try:             
                        fecha_ini = request.GET['fecha_ini']
                        fecha_fin = request.GET['fecha_fin']
                        
                        busqueda = request.GET.get('busqueda','')
                        busqueda_label = request.GET.get('busqueda_label','')
                        
                        fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").strftime("%Y-%m-%d")
                        fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").strftime("%Y-%m-%d")
                        
                        filas = []
                        lista_totales = []
                        
                        #Totales GENERALES
                        total_general_facturado = 0
                        total_general_exentas = 0
                        total_general_iva5 = 0
                        total_general_iva10 = 0
                        
                        try:
                            fila={}
                            grupo= request.user.groups.get().id
                            if grupo == 1:
                                if busqueda =='':
                                    facturas = Factura.objects.filter(anulado=False, fecha__range=(fecha_ini_parsed, fecha_fin_parsed))
                                else:
                                    facturas = Factura.objects.filter(anulado=False, fecha__range=(fecha_ini_parsed, fecha_fin_parsed), usuario = busqueda)
                            else:
                                facturas = Factura.objects.filter(anulado=False, fecha__range=(fecha_ini_parsed, fecha_fin_parsed), usuario = request.user)
                            
                            for factura in facturas:
                                
                                #Totales Factura
                                total_facturado = 0
                                total_exentas = 0
                                total_iva5 = 0
                                total_iva10 = 0
                                
                                fecha_str = unicode(factura.fecha)
                                fecha = unicode(datetime.datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                
                                # Se setean los datos de cada fila
                                fila={}
                                fila['id'] = factura.id
                                fila['fecha']= fecha
                                fila['numero']= factura.numero
                                fila['cliente']=unicode(factura.cliente)
                                fila['lote']=unicode(factura.lote.codigo_paralot)
                                fila['tipo']=unicode(factura.tipo)
                                if factura.usuario_id != None:
                                    fila['usuario']=unicode(factura.usuario)
                                
                                lista_detalles=json.loads(factura.detalle)
                                for key, value in lista_detalles.iteritems():
                                    total_exentas+=int(value['exentas'])
                                    total_iva5+=int(value['iva_5'])
                                    total_iva10+=int(value['iva_10'])
                                    total_facturado+=int(int(value['cantidad'])*int(value['precio_unitario'])) 
                                
                                fila['total_exentas']=unicode('{:,}'.format(total_exentas)).replace(",", ".")
                                fila['total_iva5']=unicode('{:,}'.format(total_iva5)).replace(",", ".")
                                fila['total_iva10']=unicode('{:,}'.format(total_iva10)).replace(",", ".")
                                fila['total_facturado']=unicode('{:,}'.format(total_facturado)).replace(",", ".")
                                
                                filas.append(fila)
                                
                                #Acumulamos para los TOTALES GENERALES
                                total_general_exentas += int(total_exentas)
                                total_general_iva5 += int(total_iva5)
                                total_general_iva10 += int(total_iva10)
                                total_general_facturado += int(total_facturado)
                                
                            #Totales GENERALES
                            fila['total_general_facturado']=unicode('{:,}'.format(total_general_facturado)).replace(",", ".")
                            fila['total_general_exentas']=unicode('{:,}'.format(total_general_exentas)).replace(",", ".")
                            fila['total_general_iva5']=unicode('{:,}'.format(total_general_iva5)).replace(",", ".")
                            fila['total_general_iva10']=unicode('{:,}'.format(total_general_iva10)).replace(",", ".")
                                
                        except Exception, error:
                            print error                                                                                       
                                                    
                        ultimo="&fecha_ini="+fecha_ini+"&fecha_fin="+fecha_fin+"&busqueda="+busqueda+"&busqueda_label"
                        lista = filas
                                                                                                              
                        wb = xlwt.Workbook(encoding='utf-8')
                        sheet = wb.add_sheet('test', cell_overwrite_ok=True)
                        sheet.paper_size_code = 1
                        style_titulo = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                                                  'font: name Calibri, bold True, height 200; align: horiz center')
                        style_normal = xlwt.easyxf('font: name Calibri, height 200;')
                            
                        style_derecha = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz right')
                            
                        style_centrado = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz center')
                        
                        style_titulo_derecha = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                                                  'font: name Calibri, bold True, height 200; align: horiz right')
                            
                        usuario = unicode(request.user)
                        
                        if busqueda != '':
                            sheet.header_str = (
                                                u"&LFecha: &D Hora: &T \nUsuario: "+usuario+" "
                                                u"&CPROPAR S.R.L.\n INFORME DE FACTURACION "
                                                u"&RPeriodo del : "+fecha_ini+" al "+fecha_fin+" \nPage &P of &N"
                                                )
                            
                            c = 0
                            sheet.write_merge(c,c,0,8, "Facturacion del Usuario: "+busqueda_label, style_titulo)
                            c=c+1
                            sheet.write(c, 0, 'Fecha',style_titulo)
                            sheet.write(c, 1, 'Numero',style_titulo)
                            sheet.write(c, 2, 'Lote',style_titulo)
                            sheet.write(c, 3, 'Cliente',style_titulo)
                            sheet.write(c, 4, 'Tipo',style_titulo)
                            sheet.write(c, 5, 'Exentas',style_titulo)
                            sheet.write(c, 6, 'IVA 5',style_titulo)
                            sheet.write(c, 7, 'IVA 10',style_titulo)
                            sheet.write(c, 8, 'Monto',style_titulo)
                            
                        else:
                            sheet.header_str = (
                                                u"&LFecha: &D Hora: &T \nUsuario: "+usuario+" "
                                                u"&CPROPAR S.R.L.\n INFORME DE FACTURACION "
                                                u"&RPeriodo del : "+fecha_ini+" al "+fecha_fin+" \nPage &P of &N"
                                                )
                        
                            c = 0
                            sheet.write_merge(c,c,0,8, "Facturacion de todos los Usuarios", style_titulo)
                            c=c+1
                            sheet.write(c, 0, 'Fecha',style_titulo)
                            sheet.write(c, 1, 'Numero',style_titulo)
                            sheet.write(c, 2, 'Lote',style_titulo)
                            sheet.write(c, 3, 'Cliente',style_titulo)
                            sheet.write(c, 4, 'Tipo',style_titulo)
                            sheet.write(c, 5, 'Exentas',style_titulo)
                            sheet.write(c, 6, 'IVA 5',style_titulo)
                            sheet.write(c, 7, 'IVA 10',style_titulo)
                            sheet.write(c, 8, 'Monto',style_titulo)
                        
                        for fila in filas:
                            
                            c += 1
                            sheet.write(c, 0, fila['fecha'],style_centrado)
                            sheet.write(c, 1, fila['numero'],style_centrado)
                            sheet.write(c, 2, fila['lote'],style_centrado)
                            sheet.write(c, 3, fila['cliente'],style_normal)
                            if fila['tipo'] == 'co':
                                sheet.write(c, 4, 'contado' ,style_centrado)
                            else:
                                sheet.write(c, 4, 'credito' ,style_centrado)
                            sheet.write(c, 5, fila['total_exentas'],style_derecha)
                            sheet.write(c, 6, fila['total_iva5'],style_derecha)
                            sheet.write(c, 7, fila['total_iva10'],style_derecha)
                            sheet.write(c, 8, fila['total_facturado'],style_derecha)
                            try:
                                if (fila['total_general_facturado']): 
                                    c+=1            
                                    sheet.write_merge(c,c,0,5, "Totales Facturados", style_titulo)
                                    sheet.write(c, 5, fila['total_general_exentas'],style_titulo_derecha)
                                    sheet.write(c, 6, fila['total_general_iva5'], style_titulo_derecha)
                                    sheet.write(c, 7, fila['total_general_iva10'], style_titulo_derecha)
                                    sheet.write(c, 8, fila['total_general_facturado'], style_titulo_derecha)
                            except Exception, error:
                                print error 
                                pass
                        #Ancho de la columna Lote
                        col_lote = sheet.col(2)
                        col_lote.width = 256 * 10   # 12 characters wide
                            
                        #Ancho de la columna Fecha
                        col_fecha = sheet.col(0)
                        col_fecha.width = 256 * 8   # 10 characters wide
                            
                        #Ancho de la columna Nombre
                        col_nombre = sheet.col(3)
                        col_nombre.width = 256 * 18   # 25 characters wide 
                        
                        #Ancho de la columna Nro cuota
                        col_nro_cuota = sheet.col(1)
                        col_nro_cuota.width = 256 * 10   # 6 characters wide
                            
                        #Ancho de la columna Nro cuota
                        col_nro_cuota = sheet.col(4)
                        col_nro_cuota.width = 256 * 5   # 6 characters wide
                            
                        #Ancho de la columna mes
                        col_mes = sheet.col(5)
                        col_mes.width = 256 * 11   # 8 characters wide
                            
                        #Ancho de la columna monto pagado
                        col_monto_pagado = sheet.col(6)
                        col_monto_pagado.width = 256 * 11   # 11 characters wide
                            
                        #Ancho de la columna monto inmobiliarioa
                        col_monto_inmo = sheet.col(7)
                        col_monto_inmo.width = 256 * 11   # 11 characters wide
                            
                        #Ancho de la columna monto propietario
                        col_nombre = sheet.col(8)
                        col_nombre.width = 256 * 11   # 11 characters wide
                        
                        
                      
                        response = HttpResponse(content_type='application/vnd.ms-excel')
                        # Crear un nombre intuitivo         
                        response['Content-Disposition'] = 'attachment; filename=' + 'informe_facturacion.xls'
                        wb.save(response)
                        return response
                    except Exception, error:
                            print error 
