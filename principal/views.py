from django.http import HttpResponse, HttpResponseServerError
from django.template import RequestContext, loader
from principal.models import Lote, Cliente, Vendedor, PlanDeVendedores, PlanDePagos
from django.utils import simplejson as json
from datetime import datetime

# vista principal de la plataforma PROPAR
def index(request):
    t = loader.get_template('index.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))

def retrieve_lote(request):
    if request.method == 'GET':
        data = request.GET

        fraccion_int = int(data.get('fraccion', ''))
        manzana_int = int(data.get('manzana', ''))
        lote_int = int(data.get('lote', ''))

        object_list = Lote.objects.filter(fraccion=fraccion_int, manzana=manzana_int, nro_lote=lote_int)
        r = list(object_list[:1])
        if r:
            r = r[0]
            # Creamos una cadena JSON para enviar la respuesta al request AJAX POST.
            response_data = {}
            response_data['superficie'] = str(r.superficie)
            response_data['lote_id'] = r.id
            response_data['lote_tag'] = str(r)
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            return HttpResponseServerError("No se encontraron lotes.")

    return HttpResponseServerError("No valido.")

def retrieve_cliente(request):
    if request.method == 'GET':
        data = request.GET

        try:
            object_list = Cliente.objects.get(pk=data.get('cliente', ''))
            # Creamos la respuesta al request.
            response = HttpResponse()
            response.write(object_list.nombres)
            response.write(" ")
            response.write(object_list.apellidos)
            return response
        except:
            return HttpResponseServerError("No se encontraron clientes.")

def retrieve_vendedor(request):
    if request.method == 'GET':
        data = request.GET

        try:
            object_list = Vendedor.objects.get(pk=data.get('vendedor', ''))
            # Creamos la respuesta al request.
            response = HttpResponse()
            response.write(object_list.nombres)
            response.write(" ")
            response.write(object_list.apellidos)
            return response
        except:
            return HttpResponseServerError("No se encontraron vendedores.")

def retrieve_plan_vendedor(request):
    if request.method == 'GET':
        data = request.GET

        try:
            object_list = PlanDeVendedores.objects.get(pk=data.get('plan_vendedor', ''))
            # Creamos la respuesta al request.
            response = HttpResponse()
            response.write(object_list.nombre_del_plan)
            return response
        except:
            return HttpResponseServerError("No se encontraron planes de vendedores.")

def retrieve_plan_pagos(request):
    if request.method == 'GET':
        data = request.GET

        try:
            datos_plan = PlanDePagos.objects.get(pk=data.get('plan_pago', ''))
            # lote_id = data.get('lote', '')
            # datos_lote = Lote.objects.get(pk=lote_id)
            fraccion_int = int(data.get('plan_pago_fraccion', ''))
            manzana_int = int(data.get('plan_pago_manzana', ''))
            lote_int = int(data.get('plan_pago_lote', ''))
            datos_lote = Lote.objects.get(fraccion=fraccion_int, manzana=manzana_int, nro_lote=lote_int)
            # Creamos la respuesta al request.
            response_data = {}
            response_data['nombre_del_plan'] = str(datos_plan.nombre_del_plan)
            response_data['credito'] = datos_plan.tipo_de_plan
            response_data['cantidad_cuotas'] = datos_plan.cantidad_de_cuotas
            if datos_plan.tipo_de_plan == True:
                response_data['precio_del_lote'] = datos_lote.precio_credito
            else:
                response_data['precio_del_lote'] = datos_lote.precio_contado
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except:
            return HttpResponseServerError("No se encontraron planes de pago.")
