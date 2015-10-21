# -*- encoding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseServerError, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden
from django.core.urlresolvers import reverse, resolve
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.template import RequestContext, loader
from django.core import serializers
from principal.models import Fraccion, Manzana, Venta, PagoDeCuotas, Propietario, Lote, Cliente, Vendedor, PlanDePago, PlanDePagoVendedor,Timbrado, RecuperacionDeLotes, Factura, TimbradoRangoFacturaUsuario, RangoFactura, ConceptoFactura
from django.core.urlresolvers import reverse, resolve
from principal.common_functions import *
from django.core.serializers.json import DjangoJSONEncoder
import json
import traceback
from django.db.models import Count, Min, Sum, Avg
from principal.monthdelta import MonthDelta
from calendar import monthrange
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.units import mm
from num2words import num2words
import base64
import ast

#Ejemplo nuevo esquema de serializacion:
# all_objects = list(Restaurant.objects.all()) + list(Place.objects.all())
# data = serializers.serialize('xml', all_objects)
#data = serializers.serialize('json', list(objectQuerySet), fields=('fileName','id'))

@require_http_methods(["GET"])
def get_propietario_id_by_name(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                name_propietario = request.GET['term']
                print("term ->" + name_propietario)
                object_list = Propietario.objects.filter(nombres__icontains = name_propietario)
                labels=["nombres","apellidos"]
                return HttpResponse(json.dumps(custom_json(object_list,labels), cls=DjangoJSONEncoder), content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login'))
        
@require_http_methods(["GET"])
def get_concepto_factura_by_name(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                name_concepto_factura = request.GET['term']
                print("term ->" + name_concepto_factura)
                object_list = ConceptoFactura.objects.filter(descripcion__icontains = name_concepto_factura)
                labels=["descripcion"]
                return HttpResponse(json.dumps(custom_json(object_list,labels), cls=DjangoJSONEncoder), content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login'))  

@require_http_methods(["GET"])
def get_vendedor_name_id_by_cedula(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                cedula_vendedor = request.GET['term']
                print("term ->" + cedula_vendedor);
                object_list = Vendedor.objects.filter(cedula__icontains= cedula_vendedor)
                labels=["nombres","apellidos"]
                return HttpResponse(json.dumps(custom_json(object_list,labels), cls=DjangoJSONEncoder), content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 
        
@require_http_methods(["GET"])
def get_propietario_name_id_by_cedula(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:
                cedula_propietario = request.GET['term']
                print("term ->" + cedula_propietario);
                object_list = Propietario.objects.filter(cedula__icontains= cedula_propietario)
                data=serializers.serialize('json',list(object_list))
                return HttpResponse(data,content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 


@require_http_methods(["GET"])
def get_cliente_name_id_by_cedula(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                cedula_cliente = request.GET['term']
                print("term ->" + cedula_cliente);
                object_list = Cliente.objects.filter(cedula__icontains= cedula_cliente)
                #labels=["nombres","apellidos","cedula"]
                #return HttpResponse(json.dumps(custom_json(object_list,labels), cls=DjangoJSONEncoder), content_type="application/json")
                data=serializers.serialize('json',list(object_list))
                return HttpResponse(data,content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 

def get_cliente_id_by_name(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                name_cliente = request.GET['term']
                print("term ->" + name_cliente);
                print Cliente.objects.filter(nombres__icontains= name_cliente).query
                object_list = Cliente.objects.filter(nombres__icontains= name_cliente)
                labels=["nombres","apellidos"]
                return HttpResponse(json.dumps(custom_json(object_list,labels), cls=DjangoJSONEncoder), content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 

def get_vendedor_id_by_name(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                name_vendedor = request.GET['term']
                print("term ->" + name_vendedor);
                object_list = Vendedor.objects.filter(nombres__icontains= name_vendedor)
                labels=["nombres","apellidos"]
                return HttpResponse(json.dumps(custom_json(object_list,labels), cls=DjangoJSONEncoder), content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 
 
@require_http_methods(["GET"])
def get_lotes_a_cargar_by_manzana(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                id_manzana = request.GET['id_manzana']
                id_fraccion = request.GET['id_fraccion']
                print("id_manzana ->" + id_manzana);
                print("id_fraccion ->" + id_fraccion);
                object_list = Manzana.objects.filter(pk= id_manzana, fraccion=id_fraccion)
                id_manzana = object_list[0].id
                total_lotes = object_list[0].cantidad_lotes
                object_list2= Lote.objects.filter(manzana_id = id_manzana)
                cantidad_encontrada = len(object_list2)
                print("cantidad_encontrada ->" + unicode(cantidad_encontrada));
                diferencia = total_lotes - cantidad_encontrada
                results =[]
                if (diferencia == 0):
                    results = [{"id": 0, "label": "No quedan Lotes disponibles en esta manzana"}]
                else:
                    if (cantidad_encontrada == 0):
                        for i in range(1, total_lotes+1):
                            record = {"id": i, "label": i}
                            results.append(record)
                    else:
                        encontrados = []
                        for i in range(1, total_lotes+2):
                            encontrados.append(0)
                            
                        for j in range(1, cantidad_encontrada +1):
                            nro_lote_encontrado = object_list2[j-1].nro_lote
                            for i in range(1,total_lotes+1): 
                                if (i == object_list2[j-1].nro_lote):
                                    encontrados[nro_lote_encontrado]= nro_lote_encontrado                        
                            
                        for i in range(1, total_lotes+1):
                            if (i != encontrados[i]):
                                record = {"id": i, "label": i}
                                results.append(record)                 
                
                return HttpResponse(json.dumps(results), content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 
 

@require_http_methods(["GET"])
def get_propietario_name_by_id(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                id_propietario = request.GET['propietario_id']
                print("id ->" + id_propietario);
                object_list = Propietario.objects.filter(id= id_propietario)
                data=serializers.serialize('json',list(object_list)) 
                return HttpResponse(data,content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 


@require_http_methods(["GET"])
def get_propietario_lastId(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:
                #callback = request.GET['callback']
                #plan_id = request.GET['id_plan_pago']
                #print("id_plan_pago ->" + plan_id);
                id = Propietario.objects.latest('id').id                
                results = [{"id": id}]
                return HttpResponse(json.dumps(results), content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login'))    
    



@require_http_methods(["GET"])
def get_fracciones_by_name(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:   
                nombre_fraccion = request.GET['term']
                print("term ->" + nombre_fraccion);
                object_list = Fraccion.objects.filter(nombre__icontains=nombre_fraccion)
                labels=["nombre"]         
                json_object_list = custom_json(object_list,labels)       
                return HttpResponse(json.dumps(json_object_list, cls=DjangoJSONEncoder),content_type="application/json")
            except Exception, error:
                print error
        else:
            return HttpResponseRedirect(reverse('login'))
  
@require_http_methods(["GET"])
def get_fracciones_by_id(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:    
                id_fraccion = request.GET['term']
                print("term ->" + id_fraccion);
                object_list = Fraccion.objects.filter(id__icontains=id_fraccion).order_by('id')
                labels=["nombre"]         
                json_object_list = custom_json(object_list,labels)       
                return HttpResponse(json.dumps(json_object_list, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception, error:
                print error
                print traceback.format_exc()
        else:
            return HttpResponseRedirect(reverse('login')) 

@require_http_methods(["GET"])
def get_manzanas_by_fraccion(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:
                fraccion_id = request.GET['fraccion_id']
                print("fraccion_id ->" + fraccion_id);
                object_list = Manzana.objects.filter(fraccion_id=fraccion_id)
                data=serializers.serialize('json',list(object_list)) 
                return HttpResponse(data,content_type="application/json")
            except Exception, error:
                print error
        else:
            return HttpResponseRedirect(reverse('login'))

@require_http_methods(["GET"])
def get_ventas_by_lote(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:
                lote_id = request.GET['lote_id']
                print("lote_id ->" + lote_id)
                #venta = Venta.objects.filter(lote=lote_id).order_by('-id')[:1]
                venta = [get_ultima_venta(lote_id)]
                print venta
                object_list = [ob.as_json() for ob in venta]
                cuotas_details = get_cuotas_detail_by_lote(lote_id)
                response = {
                    'venta': object_list,
                    'cuotas_details': cuotas_details,
                }
                return HttpResponse(json.dumps(response), content_type="application/json")
            except Exception, error:
                print error
        else:
            return HttpResponseRedirect(reverse('login')) 

@require_http_methods(["GET"])
def get_ventas_by_cliente(request):
    try:
        cliente_id = request.GET['cliente']
        print("cliente_id ->" + cliente_id);
        object_list = Venta.objects.filter(cliente=cliente_id)
        data=serializers.serialize('json',list(object_list)) 
        return HttpResponse(data,content_type="application/json")
    except Exception, error:
        print error

@require_http_methods(["GET"])
def get_pagos_by_venta(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:
                venta_id = request.GET['venta_id']
                print("venta_id ->" + venta_id);
                object_list = PagoDeCuotas.objects.filter(venta=venta_id)
                data=serializers.serialize('json',list(object_list)) 
                return HttpResponse(data,content_type="application/json")
            except Exception, error:
                print error
        else:
            return HttpResponseRedirect(reverse('login')) 

@require_http_methods(["GET"])
def get_plan_pago(request):
    if request.method == 'GET':
        if request.method == 'GET':
            if request.user.is_authenticated():
                try:              
                    nombre_plan = request.GET['term']
                    print("term ->" + nombre_plan);
                    object_list = PlanDePago.objects.filter(nombre_del_plan__icontains= nombre_plan)
                    labels=["nombre_del_plan"]
                    return HttpResponse(json.dumps(custom_json(object_list,labels), cls=DjangoJSONEncoder), content_type="application/json")     
                except Exception, error:
                    print error
                    #return HttpResponseServerError('No se pudo procesar el pedido')
            else:
                return HttpResponseRedirect(reverse('login'))

@require_http_methods(["GET"])
def get_plan_pago_vendedor(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:                                
                nombre_plan = request.GET['term']
                print("term ->" + nombre_plan);
                object_list = PlanDePagoVendedor.objects.filter(nombre__icontains= nombre_plan)
                labels=["nombre"]
                return HttpResponse(json.dumps(custom_json(object_list,labels), cls=DjangoJSONEncoder), content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login'))

def get_timbrado_by_numero(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                numero_timbrado = unicode(request.GET['term'])
                print("term ->" + numero_timbrado);
                object_list = Timbrado.objects.filter(numero__icontains= numero_timbrado)
                data=serializers.serialize('json',list(object_list)) 
                return HttpResponse(data,content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login'))

def get_cliente_id_by_name_or_ruc(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                name_cliente = request.GET['term']
                print("term ->" + name_cliente);
                term = name_cliente.split()
                if len(term) > 1:
                    object_list = Cliente.objects.filter(nombres__icontains= term[0], apellidos__icontains= term[1])
                else:
                    object_list = Cliente.objects.filter(nombres__icontains= term[0])
                data=serializers.serialize('json',list(object_list)) 
                return HttpResponse(data,content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 
        
def get_vendedor_id_by_name_or_cedula(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                name_vendedor = request.GET['term']
                print("term ->" + name_vendedor);
                object_list = Vendedor.objects.filter(nombres__icontains= name_vendedor)
                labels=["nombres","apellidos"]
                return HttpResponse(json.dumps(custom_json(object_list,labels), cls=DjangoJSONEncoder), content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 
        
def get_propietario_id_by_name_or_cedula(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                name_cliente = request.GET['term']
                print("term ->" + name_cliente);
                object_list = Cliente.objects.filter(nombres__icontains= name_cliente)
                data=serializers.serialize('json',list(object_list)) 
                return HttpResponse(data,content_type="application/json")
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 
                
@require_http_methods(["GET"])
def get_mes_pagado_by_id_lote(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:                
                lote_id = request.GET['lote_id']
                cuotas_pag = request.GET['cant_cuotas']
                cuotas_detalles = get_cuota_information_by_lote(lote_id,cuotas_pag)
                data = json.dumps({
                    'cuotas_a_pagar': cuotas_detalles})
                return HttpResponse(data,content_type="application/json")
            except Exception, error:
                print error
        else:
            return HttpResponseRedirect(reverse('login'))
        
def get_pago_cuotas_by_lote_cliente(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:  
                codigo= request.GET.get('lote_id')
                cedula_cli= request.GET.get('cliente_id')
                nombre= request.GET.get('nombre')
                lote =  Lote.objects.get(codigo_paralot= codigo)
                cliente = Cliente.objects.get(cedula=cedula_cli)
                venta = Venta.objects.get(lote_id= lote.id, cliente_id=cliente.id)
                object_list=get_pago_cuotas(venta, None, None)
                labels=["nro_cuota_y_total","nro_cuota"]
                return HttpResponse(json.dumps(object_list, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception, error:
                print error
        else:
            return HttpResponseRedirect(reverse('login'))
        
def get_detalles_factura(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:
                codigo= request.GET.get('lote_id')
                cedula_cli= request.GET.get('cliente_id')
                nro_cuota_desde = request.GET.get('nro_cuota_desde').split("/")
                nro_cuota_hasta = request.GET.get('nro_cuota_hasta').split("/")
                num_desde = int(nro_cuota_desde[0])
                num_hasta = int(nro_cuota_hasta[0])
                lote =  Lote.objects.get(codigo_paralot= codigo)
                cliente = Cliente.objects.get(cedula=cedula_cli)
                venta = Venta.objects.get(lote_id= lote.id, cliente_id=cliente.id)
                object_list=get_pago_cuotas(venta, None, None)
                gestion_cobranza = []
                interes_moratorio = 0   
                suma_gestion = 0                     
                detalles=[]
                detalle={}
                ok =False
                cantidad = num_hasta - (num_desde -1)
                detalle['cantidad'] = cantidad
                detalle['precio_unitario']= venta.precio_de_cuota
                
                detalle['iva5']= int( ( (cantidad * venta.precio_de_cuota) * 31.5) / 101.5) 
                
                detalle['exentas'] = int( (cantidad * venta.precio_de_cuota) - detalle['iva5']) 
                
                detalles.append(detalle)
                '''
                    Se trae los pagos que se van a facturar y se iteran para traer el interes de cada cuota.
                    Tambien se acumula la gestion de cobranza que hay en las cuotas
                '''
                cantidad = 0
                for x in xrange(num_desde -1 ,num_hasta):
                    pago = PagoDeCuotas.objects.get(id= object_list[x]['id'])
                    if pago.detalle != None:
                        detalle = ast.literal_eval(pago.detalle)
                        for y in xrange(0, len(detalle)-1):
                            if detalle['item' + str(y)]['nro_cuota'] == (x+1):
                                interes_moratorio += int(detalle['item' + str(y)]['intereses'])
                                cantidad +=1
                                break
                    if len(gestion_cobranza) == 0:
                        gestion_cobranza.append(pago)
                    else:
                        for x in xrange(0,len(gestion_cobranza) -1):
                            if gestion_cobranza[x].id == pago.id:
                                ok = True
                                break
                            else:
                                ok = False
                        if ok == False:
                            gestion_cobranza.append(pago)
                if interes_moratorio != 0:
                    detalle={}
                    detalle['cantidad'] = 1
                    detalle['precio_unitario']= interes_moratorio
                    detalle['exentas'] = 0
                    detalle['iva5']= 0
                    detalle['iva10'] = interes_moratorio
                    detalles.append(detalle)
                
                for x in xrange(0 ,len(gestion_cobranza)):
                    if gestion_cobranza[x].detalle != None:
                        detalle= ast.literal_eval(gestion_cobranza[x].detalle)
                        if detalle['item' + str(len(detalle) -1)]['gestion_cobranza'] != "0":
                            suma_gestion += detalle['item' + str(len(detalle) -1)]['gestion_cobranza']
                if suma_gestion != 0:
                    detalle={}
                    detalle['cantidad'] = 1
                    detalle['precio_unitario']= suma_gestion
                    detalle['exentas'] = 0
                    detalle['iva5']= 0
                    detalle['iva10'] = suma_gestion
                    detalles.append(detalle)
                return HttpResponse(json.dumps(detalles, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception, error:
                print error
        else:
            return HttpResponse(json.dumps(object_list, cls=DjangoJSONEncoder), content_type="application/json")

def get_pagos_by_ventas(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:
                data = request.GET
                id= int(data.get('venta_id'))
                pagos = PagoDeCuotas.objects.filter(venta_id=id)
                data=serializers.serialize('json',list(pagos))
                return HttpResponse(data,content_type="application/json")
                #return HttpResponse(json.dumps(pagos, cls=DjangoJSONEncoder), content_type="application/json")
            except Exception, error:
                print error
        else:
            return HttpResponseRedirect(reverse('login'))
        
def facturar(request):    
    if request.user.is_authenticated():
        if request.method == 'POST': 
            print 'POST'          
            #Obtener el cliente
            cliente_id = request.POST.get('cliente','')
            
            #Obtener el Lote
            lote_id = request.POST.get('lote','')
            
            x = unicode(lote_id)
            fraccion_int = int(x[0:3])
            manzana_int = int(x[4:7])
            lote_int = int(x[8:])
            manzana = Manzana.objects.get(fraccion_id=fraccion_int, nro_manzana=manzana_int)
            lote_id = Lote.objects.get(manzana=manzana.id, nro_lote=lote_int)
            
            #Obtener el TIMBRADO
            timbrado_id = request.POST.get('id_timbrado','')
            
            #Obtener el NUMERO
            numero = request.POST.get('nro_factura','')
            
            #Obtener fecha
            #fecha = datetime.datetime.strptime(request.POST.get('fecha', ''), "%Y-%m-%d")
            fecha = datetime.strptime(request.POST.get('fecha', ''), "%d/%m/%Y")
            
            #Obtener Tipo (Contado - Credito)
            tipo = request.POST.get('tipo','')
            
            #Obtener el detalle
            detalle = request.POST.get('detalle','')
            
            
            #Crear un objeto Factura y guardar            
            nueva_factura = Factura()
            nueva_factura.fecha = fecha
            trfu = TimbradoRangoFacturaUsuario.objects.get(usuario_id = request.user, timbrado_id = timbrado_id )
            nueva_factura.rango_factura = trfu.rango_factura
            nueva_factura.numero = numero
            nueva_factura.cliente = Cliente.objects.get(pk=cliente_id)
            nueva_factura.tipo = tipo
            nueva_factura.detalle = detalle
            nueva_factura.lote = lote_id 
            nueva_factura.save()
            
            #Se logea la accion del usuario
            id_objeto = nueva_factura.id
            codigo_lote = request.POST.get('lote','')
            loggear_accion(request.user, "Agregar", "Factura", id_objeto, codigo_lote)
            
            #obtener numero de cuotas
            numero_cuota_desde = request.POST.get('nro_cuota_desde','')
            numero_cuota_hasta= request.POST.get('nro_cuota_hasta','')
            if numero_cuota_desde != '' and numero_cuota_hasta !='':
                numero_cuota_desde = request.POST.get('nro_cuota_desde','').split("/") 
                numero_cuota_hasta= request.POST.get('nro_cuota_hasta','').split("/")
                num_desde = int(numero_cuota_desde[0])
                num_hasta = int(numero_cuota_hasta[0])
                
                venta = Venta.objects.get(cliente_id= nueva_factura.cliente.id, lote_id= lote_id.id)
                object_list= get_pago_cuotas(venta, None, None)
                for x in xrange(0,len(object_list)):
                    if num_desde <= int(object_list[x]['nro_cuota']) <= num_hasta:
                        pago = PagoDeCuotas.objects.get(pk=object_list[x]['id'])
                        pago.factura = nueva_factura
                        pago.save() 
            response = HttpResponse(content_type='application/pdf')
            
            nombre_factura = "factura-" + nueva_factura.numero + ".pdf"
            response['Content-Disposition'] = 'attachment; filename=factura'+str(nueva_factura.id)+'.pdf'
            p = canvas.Canvas(response)
            p.setPageSize((210*mm, 297*mm))
            p.setFont("Helvetica",  7)
            
            # INICIO PRIMERA IMPRESION
            y_1ra_imp = float(14.8)
            p.drawString(4.4*cm, float(y_1ra_imp+11)*cm, unicode(request.POST.get('fecha', '')))
            if nueva_factura.tipo == 'co':
                p.drawString(12.55*cm, float(y_1ra_imp+11)*cm, "X")
            else:
                p.drawString(14.1*cm, float(y_1ra_imp+11)*cm, "X")
            
            p.drawString(16.6*cm, float(y_1ra_imp+11)*cm, unicode(manzana.fraccion.nombre))
            #Solo se imprime el primer nombre y apellido-- Faltaaa
            nombre_ape = nueva_factura.cliente.nombres + " " + nueva_factura.cliente.apellidos
            p.drawString(5.3*cm, float(y_1ra_imp+10.3)*cm, unicode(nombre_ape))
            p.drawString(16.4*cm, float(y_1ra_imp+10.4)*cm, unicode(manzana.nro_manzana))
            p.drawString(18.7*cm, float(y_1ra_imp+10.4)*cm, unicode(lote_id.nro_lote))
            
            
            if nueva_factura.cliente.ruc == None:
                nueva_factura.cliente.ruc = ""                
            p.drawString(2.3*cm, float(y_1ra_imp+9.7)*cm, unicode(nueva_factura.cliente.ruc))
            p.drawString(16.7*cm, float(y_1ra_imp+9.7)*cm, unicode(nueva_factura.cliente.telefono_laboral))
            
            p.drawString(3*cm, float(y_1ra_imp+9.1)*cm, unicode(nueva_factura.cliente.direccion_cobro))
            p.drawString(13.1*cm, float(y_1ra_imp+9.1)*cm, unicode(lote_id.superficie)+ "  mts2")
            p.drawString(17.6*cm, float(y_1ra_imp+9.1)*cm, unicode(lote_id.cuenta_corriente_catastral))
            
            #Se obtienen la lista de los detalles
            lista_detalles=json.loads(nueva_factura.detalle)
            detalles=[]
            pos_y = float(y_1ra_imp+7.5)
            exentas = 0
            iva10 =0
            iva5 = 0
            total_iva_10 = 0
            total_iva_5 = 0
            total_iva = 0           
            total_gral = 0
            total_venta = 0
            for key, value in lista_detalles.iteritems():
                detalle={}
                detalle['item']=key
                detalle['cantidad']=value['cantidad']
                p.drawString(1.7*cm, float(pos_y - 0.5)*cm, unicode(detalle['cantidad']))
                detalle['concepto']=value['concepto']
                p.drawString(5*cm, float(pos_y - 0.5)*cm, unicode(detalle['concepto']))
                detalle['precio_unitario']=int(value['precio_unitario'])
                p.drawString(11.2*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['precio_unitario']).replace(",", ".")))
                total_venta +=  int(detalle['cantidad']) * int(detalle['precio_unitario'])
                detalle['exentas']=int(value['exentas'])
                p.drawString(13.5*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['exentas']).replace(",", ".")))
                if detalle['exentas'] != '':
                    exentas += int(detalle['exentas'])
                detalle['iva_5']=int(value['iva_5'])
                p.drawString(15.8*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['iva_5']).replace(",", ".")))
                if detalle['iva_5'] != '':
                    iva5 += int(detalle['iva_5'])
                detalle['iva_10']=int(value['iva_10'])
                p.drawString(18.6*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['iva_10']).replace(",", ".")))
                if detalle['iva_10'] != '':
                    iva10 += int(detalle['iva_10'])
                pos_y -= 0.5
                detalles.append(detalle)
            cantidad =  4 - len(detalles)
            pos_y -= (0.5 * cantidad)
            p.drawString(13.5*cm, float(y_1ra_imp+3.8)*cm, unicode('{:,}'.format(exentas).replace(",", "."))) 
            p.drawString(15.7*cm, float(y_1ra_imp+3.8)*cm, unicode('{:,}'.format(iva5).replace(",", ".")))   
            p.drawString(18*cm, float(y_1ra_imp+3.8)*cm, unicode('{:,}'.format(iva10).replace(",", ".")))
            pos_y -= 0.5
            p.drawString(18*cm, float(y_1ra_imp+3.2)*cm, unicode('{:,}'.format(total_venta).replace(",", ".")))
            pos_y -= 1
            numalet= num2words(int(total_venta), lang='es')
            p.drawString(6.5*cm, float(pos_y - 1.5)*cm, unicode(numalet))
            p.drawString(18*cm, float(pos_y - 1.5)*cm, unicode('{:,}'.format(total_venta).replace(",", ".")))
            total_iva_10 = int(iva10/11)
            total_iva_5 = int(iva5/21)
            total_iva = total_iva_10 + total_iva_5
            pos_y -= 0.5
            p.drawString(5.2*cm, float(pos_y - 1.6)*cm, unicode('{:,}'.format(total_iva_5).replace(",", ".")))
            p.drawString(8.5*cm, float(pos_y - 1.6)*cm, unicode('{:,}'.format(total_iva_10).replace(",", ".")))
            p.drawString(13*cm, float(pos_y - 1.6)*cm, unicode('{:,}'.format(total_iva).replace(",", ".")))
            # FIN PRIMERA IMPRESION
            ######################################################################################################################################
            # INICIO SEGUNDA IMPRESION
            p.drawString(4.4*cm, 12.1*cm, unicode(request.POST.get('fecha', '')))
            if nueva_factura.tipo == 'co':
                p.drawString(12.55*cm, 12.1*cm, "X")
            else:
                p.drawString(14.1*cm, 12.1*cm, "X")
            
            p.drawString(16.6*cm, 12.1*cm, unicode(manzana.fraccion.nombre))
            #Solo se imprime el primer nombre y apellido-- Faltaaa
            nombre_ape = nueva_factura.cliente.nombres + " " + nueva_factura.cliente.apellidos
            p.drawString(5.3*cm, 11.5*cm, unicode(nombre_ape))
            p.drawString(16.4*cm, 11.5*cm, unicode(manzana.nro_manzana))
            p.drawString(18.7*cm, 11.5*cm, unicode(lote_id.nro_lote))
            if nueva_factura.cliente.ruc == None:
                nueva_factura.cliente.ruc = ""                
            p.drawString(2.3*cm, 10.8*cm, unicode(nueva_factura.cliente.ruc))
            p.drawString(16.7*cm, 10.8*cm, unicode(nueva_factura.cliente.telefono_laboral))
            
            p.drawString(3*cm, 10.2*cm, unicode(nueva_factura.cliente.direccion_cobro))
            p.drawString(13.1*cm, 10.2*cm, unicode(lote_id.superficie)+ "  mts2")
            p.drawString(17.6*cm, 10.2*cm, unicode(lote_id.cuenta_corriente_catastral))
            
            #Se obtienen la lista de los detalles
            lista_detalles=json.loads(nueva_factura.detalle)
            detalles=[]
            pos_y = float(8.6)
            exentas = 0
            iva10 =0
            iva5 = 0
            total_iva_10 = 0
            total_iva_5 = 0
            total_iva = 0           
            total_gral = 0
            total_venta = 0
            for key, value in lista_detalles.iteritems():
                detalle={}
                detalle['item']=key
                detalle['cantidad']=value['cantidad']
                p.drawString(1.7*cm, float(pos_y - 0.5)*cm, unicode(detalle['cantidad']))
                detalle['concepto']=value['concepto']
                p.drawString(5*cm, float(pos_y - 0.5)*cm, unicode(detalle['concepto']))
                detalle['precio_unitario']=int(value['precio_unitario'])
                p.drawString(11.2*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['precio_unitario']).replace(",", ".")))
                total_venta +=  int(detalle['cantidad']) * int(detalle['precio_unitario'])
                detalle['exentas']=int(value['exentas'])
                p.drawString(13.5*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['exentas']).replace(",", ".")))
                if detalle['exentas'] != '':
                    exentas += int(detalle['exentas'])
                detalle['iva_5']=int(value['iva_5'])
                p.drawString(15.8*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['iva_5']).replace(",", ".")))
                if detalle['iva_5'] != '':
                    iva5 += int(detalle['iva_5'])
                detalle['iva_10']=int(value['iva_10'])
                p.drawString(18.6*cm, float(pos_y - 0.5)*cm, unicode('{:,}'.format(detalle['iva_10']).replace(",", ".")))
                if detalle['iva_10'] != '':
                    iva10 += int(detalle['iva_10'])
                pos_y -= 0.5
                detalles.append(detalle)
            cantidad =  4 - len(detalles)
            pos_y -= (0.5 * cantidad)
            p.drawString(13.5*cm, 4.8*cm, unicode('{:,}'.format(exentas).replace(",", "."))) 
            p.drawString(15.7*cm, 4.8*cm, unicode('{:,}'.format(iva5).replace(",", ".")))   
            p.drawString(18*cm, 4.8*cm, unicode('{:,}'.format(iva10).replace(",", ".")))
            pos_y -= 0.5
            p.drawString(18*cm, 4.2*cm, unicode('{:,}'.format(total_venta).replace(",", ".")))
            pos_y -= 1
            numalet= num2words(int(total_venta), lang='es')
            p.drawString(6.5*cm, float(pos_y - 1.5)*cm, unicode(numalet))
            p.drawString(18*cm, float(pos_y - 1.5)*cm, unicode('{:,}'.format(total_venta).replace(",", "."))) 
            total_iva_10 = int(iva10/11)
            total_iva_5 = int(iva5/21)
            total_iva = total_iva_10 + total_iva_5
            pos_y -= 0.5
            p.drawString(5.2*cm, float(pos_y - 1.6)*cm, unicode('{:,}'.format(total_iva_5).replace(",", ".")))
            p.drawString(8.5*cm, float(pos_y - 1.6)*cm, unicode('{:,}'.format(total_iva_10).replace(",", ".")))
            p.drawString(13*cm, float(pos_y - 1.6)*cm, unicode('{:,}'.format(total_iva).replace(",", ".")))
            # FIN SEGUNDA IMPRESION
            
            p.showPage()
            p.save()
            response = base64.b64encode(response.content)
            
            return HttpResponse(response);
    else:
        return HttpResponseRedirect(reverse('login')) 