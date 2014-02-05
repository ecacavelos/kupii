from django.http import HttpResponse
from django.http import HttpResponseServerError, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden
from django.core.urlresolvers import reverse, resolve
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.template import RequestContext, loader
from django.utils import simplejson as json
from principal.models import Fraccion, Manzana, Venta, PagoDeCuotas, Propietario

@require_http_methods(["GET"])
def get_propietario_id_by_name(request):
    if request.method == 'GET':
        #data = request.GET
        try:
            
            name_propietario = request.GET['term']
            print("term ->" + name_propietario);
            object_list = Propietario.objects.filter(nombres__icontains= name_propietario)
#    object_list = PlanDePago.objects.filter(plan_id=plan_id)
            results = [ob.as_json() for ob in object_list]

            return HttpResponse(json.dumps(results), mimetype='application/json')
        except:
            return HttpResponseServerError('No se pudo procesar el pedido')
            #return (e)   

@require_http_methods(["GET"])
def get_propietario_name_by_id(request):
    if request.method == 'GET':
        #data = request.GET
        try:
            
            id_propietario = request.GET['propietario_id']
            print("id ->" + id_propietario);
            object_list = Propietario.objects.filter(id= id_propietario)
#    object_list = PlanDePago.objects.filter(plan_id=plan_id)
            results = [ob.as_json() for ob in object_list]

            return HttpResponse(json.dumps(results), mimetype='application/json')
        except:
            return HttpResponseServerError('No se pudo procesar el pedido')
            #return (e)  

@require_http_methods(["GET"])
def get_propietario_lastId(request):
    
#     callback = request.GET['callback']
    if request.method == 'GET':
        #data = request.GET
        try:
#     callback = request.GET['callback']
#    plan_id = request.GET['id_plan_pago']
#    print("id_plan_pago ->" + plan_id);
            #object_list = Propietario.objects.all().order_by("-id")[0]
            id = Propietario.objects.latest('id').id
            
#    object_list = PlanDePago.objects.filter(plan_id=plan_id)

            results = [{"id": id}]

            return HttpResponse(json.dumps(results), mimetype='application/json')
        except:
            return HttpResponseServerError('No se pudo procesar el pedido')
            #return (e)   
    



@require_http_methods(["GET"])
def get_fracciones_by_name(request):
    
#     callback = request.GET['callback']
    nombre_fraccion = request.GET['term']
    print("term ->" + nombre_fraccion);
    object_list = Fraccion.objects.filter(nombre__icontains=nombre_fraccion)
    results = [ob.as_json() for ob in object_list]

    return HttpResponse(json.dumps(results), mimetype='application/json')

@require_http_methods(["GET"])
def get_manzanas_by_fraccion(request):
    
#     callback = request.GET['callback']
    fraccion_id = request.GET['fraccion_id']
    print("fraccion_id ->" + fraccion_id);
#     object_list = Manzana.objects.all()
    object_list = Manzana.objects.filter(fraccion_id=fraccion_id)
    results = [ob.as_json() for ob in object_list]

    return HttpResponse(json.dumps(results), mimetype='application/json')

@require_http_methods(["GET"])
def get_ventas_by_lote(request):

    lote_id = request.GET['lote_id']
    print("lote_id ->" + lote_id);

#     object_list = Manzana.objects.all()
    object_list = Venta.objects.filter(lote=lote_id)
    results = [ob.as_json() for ob in object_list]
    json.dumps(results)
    return HttpResponse(json.dumps(results), mimetype='application/json')

@require_http_methods(["GET"])
def get_ventas_by_cliente(request):

    cliente_id = request.GET['cliente']
    print("cliente_id ->" + cliente_id);

#     object_list = Manzana.objects.all()
    object_list = Venta.objects.filter(cliente=cliente_id)
    results = [ob.as_json() for ob in object_list]
    json.dumps(results)
    return HttpResponse(json.dumps(results), mimetype='application/json')

@require_http_methods(["GET"])
def get_pagos_by_venta(request):

    venta_id = request.GET['venta_id']
    print("venta_id ->" + venta_id);

    object_list = PagoDeCuotas.objects.filter(venta=venta_id)
    results = [ob.as_json() for ob in object_list]
    json.dumps(results)
    return HttpResponse(json.dumps(results), mimetype='application/json')
