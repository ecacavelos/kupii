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

def listar_busqueda_lotes(request):
    
    if request.user.is_authenticated():
        t = loader.get_template('informes/lotes_libres.html')
    else:
        return HttpResponseRedirect("/login") 
    
    busqueda=request.POST['busqueda']
    if busqueda:
        x=str(busqueda)
        fraccion_int = int(x[0:3])
        manzana_int =int(x[4:7])
        lote_int = int(x[8:])
        manzana= Manzana.objects.get(fraccion_id= fraccion_int, nro_manzana= manzana_int)
        lote = Lote.objects.get(manzana=manzana.id, nro_lote=lote_int)
        object_list = Lote.objects.filter(pk=lote.id,estado="1").order_by('manzana', 'nro_lote')
    
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
        c = RequestContext(request, {
            #'object_list': lista,
            #'fraccion': f,
        })
        return HttpResponse(t.render(c))    

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
            #print "op"
            lote=request.POST['lote_id']
            x=str(lote)
            fraccion_int = int(x[0:3])
            manzana_int =int(x[4:7])
            lote_int = int(x[8:])
            manzana= Manzana.objects.get(fraccion_id= fraccion_int, nro_manzana= manzana_int)
            lote = Lote.objects.get(manzana=manzana.id, nro_lote=lote_int)
        
            fecha_ini=request.POST['fecha_ini']
            fecha_fin=request.POST['fecha_fin']
            total_cuotas=0
            total_pagos=0            
            total_mora=0
            lista_totales=[]
            #pagos_list=[]
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
            for pago in lista_pagos:
                total_cuotas+=pago.total_de_cuotas
                total_pagos+=pago.total_de_pago
                total_mora+=pago.total_de_mora
                cuota_nro=get_nro_cuota(pago)
                pago.cuota = str(cuota_nro)+'/'+str(pago.plan_de_pago.cantidad_de_cuotas)
                #pagos_list.append(str(cuota_nro)+'/'+str(pago.plan_de_pago.cantidad_de_cuotas))
                pago.total_de_cuotas=str('{:,}'.format(pago.total_de_cuotas)).replace(",", ".")
                pago.total_de_mora=str('{:,}'.format(pago.total_de_mora)).replace(",", ".")
                pago.total_de_pago=str('{:,}'.format(pago.total_de_pago)).replace(",", ".")
                    
            lista_totales.append((str('{:,}'.format(total_cuotas)).replace(",", ".")))
            lista_totales.append((str('{:,}'.format(total_mora)).replace(",", ".")))
            lista_totales.append((str('{:,}'.format(total_pagos)).replace(",", ".")))    
            print "hola"
            '''    
            paginator=Paginator(lista_pagos,15)
            page=request.GET.get('page')
            try:
                lista=paginator.page(page)
            except PageNotAnInteger:
                lista=paginator.page(1)
            except EmptyPage:
                lista=paginator.page(paginator.num_pages)
            '''
            lista_aux=[]
            if(lista_pagos):                
                lista_aux.append(lista_pagos)
            
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
            '''
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
            '''       
            c = RequestContext(request, {
                'lista_pagos': lista_pagos,
                'lista_totales': lista_totales,
                #'lista': lista,
                #'listaP': listaP,
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
                        lista_totales.append(str('{:,}'.format(total_monto_pagado)).replace(",", "."))
                        lista_totales.append(str('{:,}'.format(total_monto_inm)).replace(",", "."))
                        lista_totales.append(str('{:,}'.format(total_monto_prop)).replace(",", "."))
                        #print('aca estoy')
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
                

def lotes_libres_reporte_excel(request):
    
    #at = request.session.get('at', None)
    #TODO: Danilo, utiliza este template para poner tu logi
    if request.method=='GET':
        print ('Ejemplo de uso de parametros --> Parametro1' + request.GET['parametro1'])        
        book = xlwt.Workbook(encoding='utf8')
        sheet1 = book.add_sheet('Sheet 1')
        book.add_sheet('Sheet 2')
        
        sheet1.write(0,0,'A1')
        sheet1.write(0,1,'B1')
        row1 = sheet1.row(1)
        row1.write(0,'A2')
        row1.write(1,'B2')
        sheet1.col(0).width = 10000
        
        sheet2 = book.get_sheet(1)
        sheet2.row(0).write(0,'Sheet 2 A1')
        sheet2.row(0).write(1,'Sheet 2 B1')
        sheet2.flush_row_data()
        sheet2.write(1,0,'Sheet 2 A3')
        sheet2.col(0).width = 5000
        sheet2.col(0).hidden = True
        
    
        response = HttpResponse(content_type='application/vnd.ms-excel')
        # Crear un nombre intuitivo         
        response['Content-Disposition'] = 'attachment; filename=' + 'test.xls'
        book.save(response)
        return response

        

    
