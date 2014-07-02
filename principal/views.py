from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.template import RequestContext, loader
from principal.models import Lote, Cliente, Vendedor, PlanDePago, Fraccion, Manzana, Venta, Propietario, PlanDePagoVendedor
from django.utils import simplejson as json
from datetime import datetime
from django.contrib import auth

def logout(request):
    auth.logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect("/account/loggedout/")
                                
# vista principal de la plataforma PROPAR
def index(request):
    if request.user.is_authenticated():
        t = loader.get_template('index2.html')
        c = RequestContext(request, {
                                     #'nombre': 'profe'
                                     })
        return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login")

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
        
        object_list = Lote.objects.get(manzana_id=mymanzana.id, nro_lote=lote_int, estado="1")
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

def retrieve_lote_venta(request):
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
        object_list = Lote.objects.filter(manzana_id=mymanzana.id, nro_lote=lote_int, estado="1") | Lote.objects.filter(manzana_id=mymanzana.id, nro_lote=lote_int, estado="2")
        
        #object_list = Lote.objects.get(manzana_id=mymanzana.id, nro_lote=lote_int, estado="1")
        r = object_list
        if r:
            #r = r[0]
            # Creamos una cadena JSON para enviar la respuesta al request AJAX POST.
            response_data = {}
            response_data['superficie'] = str(r[0].superficie)
            response_data['lote_id'] = r[0].id
            response_data['lote_tag'] = str(r[0])
            response_data['precio_contado'] = r[0].precio_contado
            response_data['precio_credito'] = r[0].precio_credito
            response_data['estado_lote'] = r[0].estado
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            return HttpResponseServerError("No se encontraron lotes.")

    return HttpResponseServerError("No valido.")

def retrieve_lote_cambio(request):
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
        
        object_list = Lote.objects.filter(manzana_id=mymanzana.id, nro_lote=lote_int).exclude(estado= "1")
        r = object_list
        if r:
            #r = r[0]
            # Creamos una cadena JSON para enviar la respuesta al request AJAX POST.
            response_data = {}
            response_data['superficie'] = str(r[0].superficie)
            response_data['lote_id'] = r[0].id
            response_data['lote_tag'] = str(r[0])
            response_data['precio_contado'] = r[0].precio_contado
            response_data['precio_credito'] = r[0].precio_credito
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            return HttpResponseServerError("No se encontraron lotes.")

    return HttpResponseServerError("No valido.")

def retrieve_lote_pago_cuotas(request):
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
        
        object_list = Lote.objects.get(manzana_id=mymanzana.id, nro_lote=lote_int, estado="3")
        #object_list_venta = Venta.objects.latest('fecha_de_venta')       
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

def retrieve_lote_recuperacion(request):
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
        object_list = Lote.objects.filter(manzana_id=mymanzana.id, nro_lote=lote_int, estado="3") | Lote.objects.filter(manzana_id=mymanzana.id, nro_lote=lote_int, estado="2")

        #object_list = Lote.objects.get(manzana_id=mymanzana.id, nro_lote=lote_int, estado="3")
        #object_list_venta = Venta.objects.latest('fecha_de_venta')       
        r = object_list
        if r:
            #r = r[0]
            # Creamos una cadena JSON para enviar la respuesta al request AJAX POST.
            response_data = {}
            response_data['superficie'] = str(r[0].superficie)
            response_data['lote_id'] = r[0].id
            response_data['lote_tag'] = str(r[0])
            response_data['precio_contado'] = r[0].precio_contado
            response_data['precio_credito'] = r[0].precio_credito
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
     

def get_all_planes(request):
    if request.method == 'GET':
        #data = request.GET
        try:
#     callback = request.GET['callback']
#    plan_id = request.GET['id_plan_pago']
#    print("id_plan_pago ->" + plan_id);
            object_list = PlanDePago.objects.all()
#    object_list = PlanDePago.objects.filter(plan_id=plan_id)
            results = [ob.as_json() for ob in object_list]

            return HttpResponse(json.dumps(results), mimetype='application/json')
        except:
            return HttpResponseServerError('No se pudo procesar el pedido')
            #return (e)
            
def get_all_planes_vendedores(request):
    if request.method == 'GET':
        #data = request.GET
        try:
#     callback = request.GET['callback']
#    plan_id = request.GET['id_plan_pago']
#    print("id_plan_pago ->" + plan_id);
            object_list = PlanDePagoVendedor.objects.all()
#    object_list = PlanDePago.objects.filter(plan_id=plan_id)
            results = [ob.as_json() for ob in object_list]

            return HttpResponse(json.dumps(results), mimetype='application/json')
        except:
            return HttpResponseServerError('No se pudo procesar el pedido')
            #return (e)         

def get_propietario_id_by_name(request):
    if request.method == 'GET':
        #data = request.GET
        try:
            callback = request.GET['callback']
            id_propietario = request.GET['id_propietario']
            print("id_propietario ->" + id_propietario);
            object_list = Propietario.objects.filter(id_propietario= id_propietario)
#    object_list = PlanDePago.objects.filter(plan_id=plan_id)
            results = [ob.as_json() for ob in object_list]

            return HttpResponse(json.dumps(results), mimetype='application/json')
        except:
            return HttpResponseServerError('No se pudo procesar el pedido')
            #return (e)     

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
            response_data['fecha_venta'] = datos_venta.fecha_de_venta
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except:
            return HttpResponseServerError("No se encontro la venta.")

    return HttpResponseServerError("No valido.")

def retrieve_plan_pago_vendedores(request):
    if request.method == 'GET':
        data = request.GET

        try:
            datos_plan = PlanDePagoVendedor.objects.get(pk=data.get('plan_pago_vendedor', ''))
            # Creamos la respuesta al request.
            response_data = {}
            # TODO: setear todo lo que necesites para tu vista.
            
#             response_data['nombre_del_plan'] = str(datos_plan.nombre_del_plan)
#             response_data['credito'] = datos_plan.tipo_de_plan
#             response_data['cantidad_cuotas'] = datos_plan.cantidad_de_cuotas
            
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except:
            return HttpResponseServerError("No se encontraron planes de pago.")
