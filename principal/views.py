from django.http import HttpResponse, HttpResponseServerError
from django.template import RequestContext, loader
from principal.models import Lote, Cliente, Vendedor, PlanDePago, Fraccion, Manzana, Venta
from django.utils import simplejson as json
from datetime import datetime

# vista principal de la plataforma PROPAR
def index(request):
    t = loader.get_template('index2.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))

def retrieve_lote(request):
    if request.method == 'GET':
        data = request.GET

        fraccion_int = int(data.get('fraccion', ''))
        manzana_int = int(data.get('manzana', ''))
        lote_int = int(data.get('lote', ''))

        #object_list = Lote.objects.get(fraccion=fraccion_int, manzana=manzana_int, nro_lote=lote_int)
        myfraccion = Fraccion.objects.get(id=fraccion_int)
        fraccion_manzanas = Manzana.objects.filter(fraccion=myfraccion)
        for manzana in fraccion_manzanas:
            if manzana.nro_manzana == manzana_int:
                mymanzana = manzana
        #object_list = Lote.objects.get(manzana_nro_manzana=mymanzana.nro_manzana, nro_lote=lote_int)
        
        object_list = Lote.objects.get(manzana_id=mymanzana.id, nro_lote=lote_int)
        r = object_list
        if r:
            #r = r[0]
            # Creamos una cadena JSON para enviar la respuesta al request AJAX POST.
            response_data = {}
            response_data['superficie'] = str(r.superficie)
            response_data['lote_id'] = r.id
            response_data['lote_tag'] = str(r)
            response_data['precio_contado'] = r.precio_contado
            response_data['precio_credito'] = r.precio_credito
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

def retrieve_plan_pago(request):
    if request.method == 'GET':
        data = request.GET

        try:
            datos_plan = PlanDePago.objects.get(pk=data.get('plan_pago', ''))
            # Creamos la respuesta al request.
            response_data = {}
            response_data['nombre_del_plan'] = str(datos_plan.nombre_del_plan)
            response_data['credito'] = datos_plan.tipo_de_plan
            response_data['cantidad_cuotas'] = datos_plan.cantidad_de_cuotas
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except:
            return HttpResponseServerError("No se encontraron planes de pago.")

def retrieve_venta(request):
    if request.method == 'GET':
        data = request.GET
        try:
            my_lote_id = int(data.get('lote_id'))
        except:
            return HttpResponseServerError('No se pudo leer el parametro id_lote')    

        try:
            datos_venta = Venta.objects.get(lote_id=my_lote_id)
            response_data = {}
            response_data['cliente'] = datos_venta.cliente
            response_data['vendedor'] = datos_venta.vendedor
            response_data['plan_de_pago'] = datos_venta.plan_de_pago
            response_data['precio_de_cuota'] = datos_venta.precio_de_cuota
            response_data['fecha_primer_vencimiento'] = datos_venta.fecha_primer_vencimiento
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except:
            return HttpResponseServerError("No se encontro la venta.")

    return HttpResponseServerError("No valido.")