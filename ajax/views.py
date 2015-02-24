from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseServerError, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden
from django.core.urlresolvers import reverse, resolve
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.template import RequestContext, loader
from django.core import serializers
from principal.models import Fraccion, Manzana, Venta, PagoDeCuotas, Propietario, Lote, Cliente, Vendedor, PlanDePago, PlanDePagoVendedor,Timbrado
from django.core.urlresolvers import reverse, resolve
from principal.common_functions import get_cuotas_detail_by_lote, get_nro_cuota
from datetime import datetime
#from principal.reports import reporte_lotes_libres, reporte_general_pagos, reporte_liquidacion_vendedores,reporte_liquidacion_gerentes

@require_http_methods(["GET"])
def get_propietario_id_by_name(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                name_propietario = request.GET['term']
                print("term ->" + name_propietario);
                object_list = Propietario.objects.filter(nombres__icontains= name_propietario)
                results = [ob.as_json() for ob in object_list]    
                return HttpResponse(json.dumps(results), mimetype='application/json')
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
                results = [ob.as_json() for ob in object_list]
                return HttpResponse(json.dumps(results), mimetype='application/json')
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
                results = [ob.as_json() for ob in object_list]
                return HttpResponse(json.dumps(results), mimetype='application/json')
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
                results = [ob.as_json() for ob in object_list]
                return HttpResponse(json.dumps(results), mimetype='application/json')
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
                object_list = Cliente.objects.filter(nombres__icontains= name_cliente)
                results = [ob.as_json() for ob in object_list]
                return HttpResponse(json.dumps(results), mimetype='application/json')
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
                results = [ob.as_json() for ob in object_list]
                return HttpResponse(json.dumps(results), mimetype='application/json')
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
                print("cantidad_encontrada ->" + str(cantidad_encontrada));
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
                            
                return HttpResponse(json.dumps(results), mimetype='application/json')
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
                results = [ob.as_json() for ob in object_list]
                return HttpResponse(json.dumps(results), mimetype='application/json')
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 


@require_http_methods(["GET"])
def get_propietario_lastId(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            #data = request.GET
            try:
                #callback = request.GET['callback']
                #plan_id = request.GET['id_plan_pago']
                #print("id_plan_pago ->" + plan_id);
                #object_list = Propietario.objects.all().order_by("-id")[0]
                id = Propietario.objects.latest('id').id                
                #object_list = PlanDePago.objects.filter(plan_id=plan_id)
                results = [{"id": id}]
                return HttpResponse(json.dumps(results), mimetype='application/json')
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
                results = [ob.as_json() for ob in object_list]
                return HttpResponse(json.dumps(results), mimetype='application/json')
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
                results = [ob.as_json() for ob in object_list]
                return HttpResponse(json.dumps(results), mimetype='application/json')
            except Exception, error:
                print error
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
                results = [ob.as_json() for ob in object_list]
                return HttpResponse(json.dumps(results), mimetype='application/json')
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
                object_list = Venta.objects.filter(lote=lote_id).order_by('-id')[:1]
                venta = [ob.as_json() for ob in object_list]
                cuotas_details = get_cuotas_detail_by_lote(lote_id)
                json_response = json.dumps({
                    'venta': venta,
                    'cuotas_details': cuotas_details,
                })
                print(json_response)
                return HttpResponse(json_response, mimetype='application/json')
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
        results = [ob.as_json() for ob in object_list]
        json.dumps(results)
        return HttpResponse(json.dumps(results), mimetype='application/json')
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
                results = [ob.as_json() for ob in object_list]
                json.dumps(results)
                return HttpResponse(json.dumps(results), mimetype='application/json')
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
                    results = [ob.as_json() for ob in object_list]
                    return HttpResponse(json.dumps(results), mimetype='application/json')
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
                results = [ob.as_json() for ob in object_list]
                return HttpResponse(json.dumps(results), mimetype='application/json')
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login'))

def get_timbrado_by_numero(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:            
                numero_timbrado = request.GET['term']
                print("term ->" + numero_timbrado);
                object_list = Timbrado.objects.filter(numero__icontains= numero_timbrado)
                results = [ob.as_json() for ob in object_list]
                return HttpResponse(json.dumps(results), mimetype='application/json')
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
                object_list = Cliente.objects.filter(nombres__icontains= name_cliente)
                results = [ob.as_json() for ob in object_list]
                return HttpResponse(json.dumps(results), mimetype='application/json')
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
                results = [ob.as_json() for ob in object_list]
                return HttpResponse(json.dumps(results), mimetype='application/json')
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
                results = [ob.as_json() for ob in object_list]
                return HttpResponse(json.dumps(results), mimetype='application/json')
            except Exception, error:
                print error
                #return HttpResponseServerError('No se pudo procesar el pedido')
        else:
            return HttpResponseRedirect(reverse('login')) 