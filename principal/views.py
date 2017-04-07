from django.db.models import Count, Min, Sum, Avg
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.template import RequestContext, loader
from principal.models import Lote, Cliente, Vendedor, PlanDePago, Fraccion, Manzana, Venta, Propietario, PlanDePagoVendedor, PagoDeCuotas
from django.core import serializers
from django.core.urlresolvers import reverse, resolve
from datetime import datetime
from django.contrib import auth
import common_functions
import json
from principal import permisos
from principal.common_functions import verificar_permisos

def logout(request):
    auth.logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect("/account/loggedout/")
                                
# vista principal de la plataforma PROPAR
def index(request):
    if request.user.is_authenticated():
        t = loader.get_template('index2.html')
        grupo= request.user.groups.get().name
        c = RequestContext(request, {
            'grupo': grupo
                                     })
        return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))

def retrieve_cedula_cliente(request):
    if request.method == 'GET':
        data = request.GET
        cedula_busqueda=data.get('cedula', '')
        try:
            cliente=Cliente.objects.get(cedula=cedula_busqueda)        
            if cliente:
                data=serializers.serialize('json',list(cliente)) 
                return HttpResponseServerError(data,content_type="application/json")                
        except:
            return HttpResponse(json.dumps("Valido"), content_type="application/json")           
            return HttpResponse(data,content_type="application/json")
                        
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
            response_data['superficie'] = u'%s' %(r.superficie)
            response_data['lote_id'] = r.id
            response_data['lote_tag'] = u'%s' %(r)
            response_data['precio_contado'] = r.precio_contado
            response_data['precio_credito'] = r.precio_credito
            
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            return HttpResponseServerError("No se encontraron lotes.")

    return HttpResponseServerError("No valido.")

def retrieve_fraccion(request):
    if request.user.is_authenticated():
        if request.method == 'GET':
            data = request.GET
            fraccion_int = int(data.get('fraccion', ''))
            myfraccion = Fraccion.objects.get(id=fraccion_int)
            response_data = {}
            response_data['fraccion_id']=myfraccion.id
            response_data['nombre']=myfraccion.nombre

            return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        return HttpResponseRedirect(reverse('login'))
        
def retrieve_lote_venta(request):
    if request.method == 'GET':
        data = request.GET

        fraccion_int = int(data.get('fraccion', ''))
        manzana_int = int(data.get('manzana', ''))
        lote_int = int(data.get('lote', ''))

        myfraccion = Fraccion.objects.get(id=fraccion_int)
        fraccion_manzanas = Manzana.objects.filter(fraccion=myfraccion)
        for manzana in fraccion_manzanas:
            if manzana.nro_manzana == manzana_int:
                mymanzana = manzana
        object_list = Lote.objects.filter(manzana_id=mymanzana.id, nro_lote=lote_int) | Lote.objects.filter(manzana_id=mymanzana.id, nro_lote=lote_int)
        
        r = object_list
        if r:
            #r = r[0]
            # Creamos una cadena JSON para enviar la respuesta al request AJAX POST.
            response_data = {}
            response_data['superficie'] = u'%s' %(r[0].superficie)
            response_data['lote_id'] = r[0].id
            response_data['lote_tag'] = u'%s' %(r[0])
            response_data['precio_contado'] = r[0].precio_contado
            response_data['precio_credito'] = r[0].precio_credito
            response_data['estado_lote'] = r[0].estado
            
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            response_data = {}
            response_data['estado'] = "0"
            return HttpResponse(json.dumps(response_data), content_type="application/json")

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
            response_data['superficie'] = u'%s' %(r[0].superficie)
            response_data['lote_id'] = r[0].id
            response_data['lote_tag'] = u'%s' %(r[0])
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
        #obs_int = str(data.get('obs', ''))
        #object_list = Lote.objects.get(fraccion=fraccion_int, manzana=manzana_int, nro_lote=lote_int)
        myfraccion = Fraccion.objects.get(id=fraccion_int)
        fraccion_manzanas = Manzana.objects.filter(fraccion=myfraccion)
        for manzana in fraccion_manzanas:
            if manzana.nro_manzana == manzana_int:
                mymanzana = manzana
        #object_list = Lote.objects.get(manzana_nro_manzana=mymanzana.nro_manzana, nro_lote=lote_int)
        
        object_list = Lote.objects.get(manzana_id=mymanzana.id, nro_lote=lote_int, estado="3", )
        #object_list_venta = Venta.objects.latest('fecha_de_venta')       
        r = object_list
        if r:
            #r = r[0]
            # Creamos una cadena JSON para enviar la respuesta al request AJAX POST.
            response_data = {}
            response_data['superficie'] = u'%s' %(r.superficie)
            response_data['lote_id'] = r.id
            response_data['lote_tag'] = u'%s' %(r)
            response_data['precio_contado'] = r.precio_contado
            response_data['precio_credito'] = r.precio_credito
            response_data['obs'] = r.comentarios

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
            response_data['superficie'] = u'%s' %(r[0].superficie)
            response_data['lote_id'] = r[0].id
            response_data['lote_tag'] = u'%s' %(r[0])
            response_data['precio_contado'] = r[0].precio_contado
            response_data['precio_credito'] = r[0].precio_credito
            
            ultima_venta = Venta.objects.filter(lote_id = r[0].id ).latest('fecha_de_venta')
            try:
                ultimo_pago = PagoDeCuotas.objects.filter(venta_id = ultima_venta.id).latest('fecha_de_pago')
                response_data['fecha_ultimo_pago'] = ultimo_pago.fecha_de_pago.strftime("%d/%m/%Y")
            except:
                response_data['fecha_ultimo_pago'] = ultima_venta.fecha_de_venta.strftime("%d/%m/%Y")
            
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

def get_all_planes(request):
    if request.method == 'GET':
        data = request.GET
        try:
#     callback = request.GET['callback']
            nombre_plan = request.GET['term']
#    print("id_plan_pago ->" + plan_id);

            #object_list = PlanDePago.objects.filter()
            object_list = PlanDePago.objects.filter(nombre_del_plan__icontains=nombre_plan)
            data=serializers.serialize('json',list(object_list)) 
            return HttpResponseServerError(data,content_type="application/json")           
        except:
            return HttpResponseServerError('No se pudo procesar el pedido')
            #return (e)
            
def get_all_planes_vendedores(request):
    if request.method == 'GET':
        data = request.GET
        try:
#     callback = request.GET['callback']
#            plan_id = request.GET['id_plan_pago']
#    print("id_plan_pago ->" + plan_id);
            nombre_plan = request.GET['term']
            object_list = PlanDePagoVendedor.objects.filter(nombre__icontains=nombre_plan)
#    object_list = PlanDePago.objects.filter(plan_id=plan_id)
            data=serializers.serialize('json',list(object_list)) 
            return HttpResponseServerError(data,content_type="application/json")   
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
            data=serializers.serialize('json',list(object_list)) 
            return HttpResponseServerError(data,content_type="application/json")   
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

def retrieve_plan_pago(request):
    if request.method == 'GET':
        data = request.GET

        try:
            datos_plan = PlanDePago.objects.get(pk=data.get('plan_pago', ''))
            # Creamos la respuesta al request.
            response_data = {}
            response_data['nombre_del_plan'] = u'%s' %(datos_plan.nombre_del_plan)            
            response_data['credito'] = datos_plan.tipo_de_plan
            response_data['cantidad_cuotas'] = datos_plan.cantidad_de_cuotas
            
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except Exception, error:
            print error
            return HttpResponseServerError("No se encontraron planes de pago.")

def retrieve_plan_pago_vendedores(request):
    if request.method == 'GET':
        data = request.GET

        try:
            datos_plan = PlanDePagoVendedor.objects.get(pk=data.get('plan_pago_vendedor', ''))
            # Creamos la respuesta al request.
            response_data = {}
            # TODO: setear todo lo que necesites para tu vista.            
            response_data['nombre_del_plan'] = u'%s' %(datos_plan.nombre)
            response_data['credito'] = datos_plan.tipo
            response_data['cantidad_cuotas'] = datos_plan.cantidad_cuotas
            
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        except:
            return HttpResponseServerError("No se encontraron planes de pago.")



def get_cuotas_lotes_detalles(request):

    if request.method == 'GET':
        lote_id = request.GET['lote_id']
        print("buscando pagos del lote --> " + lote_id);
        datos = common_functions.get_cuotas_detail_by_lote(lote_id)
        return HttpResponse(json.dumps(datos), content_type="application/json")




