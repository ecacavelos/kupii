from django.http import HttpResponse
from django.http import HttpResponseServerError, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden
from django.core.urlresolvers import reverse, resolve
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.template import RequestContext, loader
from django.utils import simplejson as json
from principal.models import Fraccion, Manzana, Venta, PagoDeCuotas


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
