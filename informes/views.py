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
            
        #f = []
        a = len(object_list)
        if a > 0:
            for i in object_list:
                #lote = Lote.objects.get(pk=i.lote_id)
                #manzana = Manzana.objects.get(pk=lote.manzana_id)
                #f.append(Fraccion.objects.get(pk=manzana.fraccion_id))
                #i.fecha_de_venta = i.fecha_de_venta.strftime("%d/%m/%Y")
                #i.fecha_primer_vencimiento = i.fecha_primer_vencimiento.strftime("%d/%m/%Y")
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
            #'fraccion': f,
        })
        return HttpResponse(t.render(c))    
           
    except Exception, error:
            print error    
            return HttpResponseServerError("No se pudo obtener el Listado de Clientes Atrasados.")


def informe_general(request):
    
    if request.method=='GET':

        if request.user.is_authenticated():
            t = loader.get_template('informes/informe_general.html')
            c = RequestContext(request, {
                'object_list': [],
            })
            return HttpResponse(t.render(c))                
        else:
            return HttpResponseRedirect("/login") 
    
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
                
                
                for lote in lista_lotes:
                    lista_pagos=PagoDeCuotas.objects.filter(lote_id=lote.id,fecha_de_pago__range=(fecha_ini_parsed,fecha_fin_parsed))
                    for p in lista_pagos:
                        object_list.append(p)
                                
                     
                
                                
            except Exception, error:
                print error
            a = len(object_list)
            
            if a>0:
                lista_total_cuotas=[0]
                lista_total_mora=[0]
                lista_total_pagos=[0]
                monto_total_cuotas=[0]
                monto_total_mora=[0]
                monto_total_pagos=[0]
                #lista que guarda los indices de principio y fin de una determinada fraccion
                lista_cambios=[0]
                
                total_acumulado_cuotas=0
                total_acumulado_mora=0
                total_acumulado_pagos=0
                lista_totales_acumulados=[]
                try:
                    j=0  
                    k=0 
                    #guardamos la primera fraccion para tener algo con que comparar en el for
                    fraccion_actual=object_list[0].lote.manzana.fraccion_id
                    for i in object_list:
                        #contador general de registros
                        k+=1
                         
                        if(fraccion_actual==i.lote.manzana.fraccion_id):
                            monto_total_cuotas[j]+=int(i.total_de_cuotas)
                            monto_total_mora[j]+=int(i.total_de_mora)
                            monto_total_pagos[j]+=int(i.total_de_pago)
                            
                            #acumulamos los totales para una lista de totales generales
                            total_acumulado_cuotas+=int(i.total_de_cuotas)
                            total_acumulado_mora+=int(i.total_de_mora)
                            total_acumulado_pagos+=int(i.total_de_pago)
                        else:
                            #al cambiar de fraccion se guarda la posicion del cambio en la lista de cambios
                            lista_cambios.append(k-1)
                            #cambiamos de fraccion
                            fraccion_actual= i.lote.manzana.fraccion_id
                            
                            #agregamos a la lista los totales acumulados
                            monto_total_cuotas[j]=str('{:,}'.format(monto_total_cuotas[j])).replace(",", ".")
                            monto_total_mora[j]=str('{:,}'.format(monto_total_mora[j])).replace(",", ".")
                            monto_total_pagos[j]=str('{:,}'.format(monto_total_pagos[j])).replace(",", ".")
                    

                            lista_total_cuotas.append(monto_total_cuotas[j])
                            lista_total_mora.append(monto_total_mora[j])
                            lista_total_pagos.append(monto_total_pagos[j])
                            
                            #...y sumamos a los totales generales
                            total_acumulado_cuotas+=int(i.total_de_cuotas)
                            total_acumulado_mora+=int(i.total_de_mora)
                            total_acumulado_pagos+=int(i.total_de_pago)
                            #contador de los montos totales pertenecientes a una misma fraccion
                            j+=1
                            
                            #agregamos a la lista de la nueva fraccion los totales acumulados
                            monto_total_cuotas.append(int(i.total_de_cuotas))
                            monto_total_mora.append(int(i.total_de_mora))
                            monto_total_pagos.append(int(i.total_de_pago))
                            
                                         
                        i.fecha_de_pago=i.fecha_de_pago.strftime("%d/%m/%Y")
                        i.total_de_cuotas=str('{:,}'.format(i.total_de_cuotas)).replace(",", ".")
                        i.total_de_mora=str('{:,}'.format(i.total_de_mora)).replace(",", ".")
                        i.total_de_pago=str('{:,}'.format(i.total_de_pago)).replace(",", ".")
                    
                    #guardamos la posicion del ultimo cambio
                    lista_cambios.append(k)
                    
                    
                    #agregamos a la lista de totales los totales acumulados
                    lista_total_cuotas.append(monto_total_cuotas[j])
                    lista_total_mora.append(monto_total_mora[j])
                    lista_total_pagos.append(monto_total_pagos[j])

                    #parseamos los datos
                    total_acumulado_cuotas=str('{:,}'.format(total_acumulado_cuotas)).replace(",", ".")
                    total_acumulado_mora=str('{:,}'.format(total_acumulado_mora)).replace(",", ".")
                    total_acumulado_pagos=str('{:,}'.format(total_acumulado_pagos)).replace(",", ".")
                    
                    lista_totales_acumulados.append(total_acumulado_cuotas)
                    lista_totales_acumulados.append(total_acumulado_mora)
                    lista_totales_acumulados.append(total_acumulado_pagos)
                    
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
                        'lista_total_cuotas': lista_total_cuotas,
                        'lista_total_mora': lista_total_mora,
                        'lista_total_pagos': lista_total_pagos,
                        'lista_cambios': lista_cambios,
                        'lista_totales_acumulados':lista_totales_acumulados,
                    })
                    return HttpResponse(t.render(c))
                except Exception, error:
                    print error
        except:   
            return HttpResponseServerError("No se pudo obtener el Listado de Pagos de Lotes.")

def informe_movimientos(request):
    if request.method=='GET':
            if request.user.is_authenticated():
                t = loader.get_template('informes/informe_movimientos.html')
                c = RequestContext(request, {
                    'object_list': [],
                })
                return HttpResponse(t.render(c))                
            else:
                return HttpResponseRedirect("/login") 
    else:
        
        if request.user.is_authenticated():
            t = loader.get_template('informes/informe_movimientos.html')                
        else:
            return HttpResponseRedirect("/login") 
    
        try:
            print "op"
            lote=request.POST['lote_id']
            x=str(lote)
            fraccion_int = int(x[0:3])
            manzana_int =int(x[4:7])
            lote_int = int(x[8:])
            manzana= Manzana.objects.get(fraccion_id= fraccion_int, nro_manzana= manzana_int)
            lote = Lote.objects.get(manzana=manzana.id, nro_lote=lote_int)
        
            fecha_ini=request.POST['fecha_ini']
            fecha_fin=request.POST['fecha_fin']
            
            if not (fecha_ini and fecha_fin):
                lista_pagos=PagoDeCuotas.objects.filter(lote_id=lote.id)
                lista_ventas=Venta.objects.filter(lote_id=lote_int)
                lista_reservas=Reserva.objects.filter(lote_id=lote_int)
                lista_cambios=CambioDeLotes.objects.filter(lote_nuevo_id=lote_int)
                lista_recuperaciones=RecuperacionDeLotes.objects.filter(lote_id=lote_int)
                lista_transferencias=TransferenciaDeLotes.objects.filter(lote_id=lote_int)
            else:
                fecha_ini_parsed = datetime.strptime(fecha_ini, "%d/%m/%Y").date()
                fecha_fin_parsed = datetime.strptime(fecha_fin, "%d/%m/%Y").date()
                lista_pagos=PagoDeCuotas.objects.filter(lote_id=lote.id,fecha_de_pago__range=(fecha_ini_parsed,fecha_fin_parsed))
                lista_ventas=Venta.objects.filter(lote_id=lote_int,fecha_de_venta__range=(fecha_ini_parsed,fecha_fin_parsed))
                lista_reservas=Reserva.objects.filter(lote_id=lote_int,fecha_de_reserva__range=(fecha_ini_parsed,fecha_fin_parsed))
                lista_cambios=CambioDeLotes.objects.filter(lote_nuevo_id=lote_int,fecha_de_cambio__range=(fecha_ini_parsed,fecha_fin_parsed))
                lista_recuperaciones=RecuperacionDeLotes.objects.filter(lote_id=lote_int,fecha_de_recuperacion__range=(fecha_ini_parsed,fecha_fin_parsed))
                lista_transferencias=TransferenciaDeLotes.objects.filter(lote_id=lote_int,fecha_de_transferencia__range=(fecha_ini_parsed,fecha_fin_parsed))
                
            lista_aux=[]
            lista_aux.append(lista_pagos)
            paginator=Paginator(lista_pagos,15)
            page=request.GET.get('page')
            try:
                lista=paginator.page(page)
            except PageNotAnInteger:
                lista=paginator.page(1)
            except EmptyPage:
                lista=paginator.page(paginator.num_pages)
            
            
            if(lista_ventas):
                lista_aux.append(lista_ventas)
            
            if(lista_reservas):
                lista_aux.append(lista_reservas)
            
            if(lista_cambios):
                lista_aux.append(lista_cambios)
            
            if(lista_recuperaciones):
                lista_aux.append(lista_recuperaciones)
            
            if(lista_transferencias):
                lista_aux.append(lista_transferencias)
              
            if(lista_aux):
                lista_aux.append(lista_aux)
            
            paginator=Paginator(lista_aux,6)
            page=request.GET.get('page')
            try:
                listaP=paginator.page(page)
            except PageNotAnInteger:
                listaP=paginator.page(1)
            except EmptyPage:
                listaP=paginator.page(paginator.num_pages)
                   
            c = RequestContext(request, {
                'lista_pagos': lista_pagos,
                'lista': lista,
                'listaP': listaP,
                'lista_ventas': lista_ventas,
                'lista_reservas': lista_reservas,
                'lista_cambios': lista_cambios,
                'lista_recuperaciones': lista_recuperaciones,
                'lista_transferencias': lista_transferencias,
             })
                
        except Exception, error:
            print error
            c = RequestContext(request, {
                    'lista_pagos': [],
                    'lista': [],
                    'listaP': [],
                    'lista_ventas': [],
                    'lista_reservas': [],
                    'lista_cambios': [],
                    'lista_recuperaciones': [],
                    'lista_transferencias': [],
                })
        return HttpResponse(t.render(c))
 
def liquidacion_propietarios(request):
    if request.method=='GET':
        if request.user.is_authenticated():
            t = loader.get_template('informes/liquidacion_propietarios.html')                
            c = RequestContext(request, {
                'object_list': [],
            })
            return HttpResponse(t.render(c))
        else:
            return HttpResponseRedirect("/login")
            
    else:
        try:  
            if request.user.is_authenticated():
                fecha_ini=request.POST['fecha_ini']
                fecha_fin=request.POST['fecha_fin']
                fecha_ini_parsed = datetime.strptime(fecha_ini, "%d/%m/%Y").date()
                fecha_fin_parsed = datetime.strptime(fecha_fin, "%d/%m/%Y").date()
                tipo_busqueda=request.POST['tipo_busqueda']
                lista_fila=[]
                lista_pagos=[]
                lista_totales=[]
                pagos_list=[]
                fracciones_list=[]
                if tipo_busqueda == "fraccion":
                    fraccion_id=request.POST['busqueda']
                    fraccion=Fraccion.objects.get(pk=fraccion_id)
                                
                    print('Fraccion: '+fraccion.nombre+'\n')
                    manzana_list =  Manzana.objects.filter(fraccion_id= fraccion_id)
                    lista_lotes=[]
                    pagos_list=[]
                    total_monto_pagado=0
                    total_monto_inm=0
                    total_monto_prop=0
                    for m in manzana_list:
                        lotes_list=Lote.objects.filter(manzana_id=m.id)
                        for l in lotes_list:
                            lista_lotes.append(l)
                            pago=PagoDeCuotas.objects.filter(lote_id= l.id ,fecha_de_pago__range= [fecha_ini_parsed, fecha_fin_parsed])
                            if pago:
                                pagos_list.append(pago)
                    
                    #print('Lotes:' +str(len(lista_lotes)))
                    #print('FECHA'+'\t\t'+'LOTE ID'+'\t'+'CUOTA NRO'+'\t'+'MONTO PAG.'+'PLAN DE PAGO'+'\t'+'MONTO INMOBILIARIA'+'\t'+'MONTO PROPIETARIO')
                    for i in pagos_list:
                        cant_cuotas=0
                        for pago in i:
                            cant_cuotas+=1
                            if(cant_cuotas%2!=0 ): 
                                if cant_cuotas<20:
                                    monto_inmobiliaria=pago.total_de_cuotas
                                    monto_propietario=0
                                    total_monto_pagado+=pago.total_de_cuotas
                                    total_monto_inm+=monto_inmobiliaria
                                else:
                                    if pago.plan_de_pago.porcentaje_cuotas_inmobiliaria!=0:
                                        monto_inmobiliaria=pago.total_de_cuotas*int(pago.plan_de_pago.porcentaje_cuotas_inmobiliaria/100)
                                        monto_propietario=pago.total_de_cuotas-monto_inmobiliaria
                                        total_monto_inm+=monto_inmobiliaria
                                        total_monto_prop+=monto_propietario
                            try:
                                lista_fila.append(pago.fecha_de_pago)
                                lista_fila.append(pago.lote)
                                lista_fila.append(pago.cliente)
                                lista_fila.append(str(cant_cuotas)+'/'+str(pago.plan_de_pago.cantidad_de_cuotas))
                                lista_fila.append(str('{:,}'.format(pago.total_de_cuotas)).replace(",", "."))
                                lista_fila.append(str('{:,}'.format(monto_inmobiliaria)).replace(",", "."))
                                lista_fila.append(str('{:,}'.format(monto_propietario)).replace(",", "."))                    
                                #lista_fila.zip()
                                lista_pagos.append(lista_fila)
                                #lista_pagos=zip(lista_fila)
                                lista_fila=[]
                            except Exception, error:
                                print error
                    
                    if pagos_list:
                        lista_totales.append(total_monto_pagado)
                        lista_totales.append(total_monto_inm)
                        lista_totales.append(total_monto_prop)
                        print('aca estoy')
                            #print (str(pago.fecha_de_pago)+'\t'+str(pago.lote_id)+'\t'+str(cant_cuotas)+'/'+str(pago.plan_de_pago.cantidad_de_cuotas)+'\t'+str(pago.plan_de_pago_id)+'\t\t'+str(pago.total_de_cuotas)+'\t\t'+str(monto_inmobiliaria)+'\t\t'+str(monto_propietario)+'\n')
                            
                                                                
                else:
                    try:
                        propietario=request.POST['busqueda']    
                        propietario_id=Propietario.objects.get(nombres__icontains=propietario)
                        fracciones_list=Fraccion.objects.filter(propietario_id=propietario_id)
                        
                        for f in fracciones_list:
                            manzana_list =  Manzana.objects.filter(fraccion_id= f.id)
                            lista_lotes=[]
                            pagos_list=[]
                            monto_propietario=0
                            for m in manzana_list:
                                lotes_list=Lote.objects.filter(manzana_id=m.id)
                                for l in lotes_list:
                                    lista_lotes.append(l)
                                    pago=PagoDeCuotas.objects.filter(lote_id= l.id ,fecha_de_pago__range= [fecha_ini_parsed, fecha_fin_parsed])
                                    if pago:
                                        pagos_list.append(pago)
                                    
                                    #print('Lotes:' +str(len(lista_lotes)))
                                    
                                    for i in pagos_list:
                                        cant_cuotas=0
                                        for pago in i:
                                            cant_cuotas+=1
                                            if(cant_cuotas%2!=0): 
                                                if cant_cuotas<20:
                                                    monto_inmobiliaria=pago.total_de_cuotas
                                                    monto_propietario=0
                                                else:
                                                    if pago.plan_de_pago.porcentaje_cuotas_inmobiliaria!=0:
                                                        monto_inmobiliaria=pago.total_de_cuotas*int(pago.plan_de_pago.porcentaje_cuotas_inmobiliaria/100)
                                                        monto_propietario=pago.total_de_cuotas-monto_inmobiliaria
                                            #print (str(pago.fecha_de_pago)+'\t'+str(pago.lote_id)+'\t'+str(cant_cuotas)+'/'+str(pago.plan_de_pago.cantidad_de_cuotas)+'\t'+str(pago.plan_de_pago_id)+'\t\t'+str(pago.total_de_cuotas)+'\t\t'+str(monto_inmobiliaria)+'\t\t'+str(monto_propietario)+'\n')    
                                            try:
                                                lista_fila.append(pago.fecha_de_pago)
                                                lista_fila.append(pago.lote)
                                                lista_fila.append(pago.cliente)
                                                lista_fila.append(str(cant_cuotas)+'/'+str(pago.plan_de_pago.cantidad_de_cuotas))
                                                lista_fila.append(str('{:,}'.format(pago.total_de_cuotas)).replace(",", "."))
                                                lista_fila.append(str('{:,}'.format(monto_inmobiliaria)).replace(",", "."))
                                                lista_fila.append(str('{:,}'.format(monto_propietario)).replace(",", "."))                    
                                                #lista_fila.zip()
                                                lista_pagos.append(lista_fila)
                                                #lista_pagos=zip(lista_fila)
                                                lista_fila=[]
                                            except Exception, error:
                                                print error
                            if pagos_list:
                                lista_totales.append(total_monto_pagado)
                                lista_totales.append(total_monto_inm)
                                lista_totales.append(total_monto_prop)
                                print('aca estoy')                    
                    except:
                        lista_pagos=[]
                
                t = loader.get_template('informes/liquidacion_propietarios.html')
                c = RequestContext(request, {
                    'object_list': lista_pagos,
                    'lista_totales' : lista_totales
                })
                return HttpResponse(t.render(c))
            else:
                return HttpResponseRedirect("/login") 
        
        except Exception, error:
                print error
                          

        
def liquidacion_vendedores(request):
    if request.method=='GET':
        if request.user.is_authenticated():
            t = loader.get_template('informes/liquidacion_vendedores.html')
            c = RequestContext(request, {
                'object_list': [],
            })
            return HttpResponse(t.render(c))                
        else:
            return HttpResponseRedirect("/login") 

    if request.method=='GET':
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
            #'pagos_list': pagos_list,
            #'lista_totales_vendedor': lista_totales_vendedor,
        })
        return HttpResponse(t.render(c))
                
def liquidacion_gerentes(request):
    if request.method=='GET':
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
    if request.method=='GET':
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

        

    
