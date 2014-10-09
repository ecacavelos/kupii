from django.http import HttpResponse
from django.http import HttpResponseServerError, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden
from django.core.urlresolvers import reverse, resolve
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.template import RequestContext, loader
from django.utils import simplejson as json
from principal.models import Fraccion, Manzana, Venta, PagoDeCuotas, Propietario, Lote, Cliente, Vendedor, PlanDePago, PlanDePagoVendedor
from principal.common_functions import get_cuotas_detail_by_lote, get_nro_cuota
from datetime import datetime

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
def get_vendedor_name_id_by_cedula(request):
    if request.method == 'GET':
        #data = request.GET
        try:            
            cedula_vendedor = request.GET['term']
            print("term ->" + cedula_vendedor);
            object_list = Vendedor.objects.filter(cedula__icontains= cedula_vendedor)
#    object_list = PlanDePago.objects.filter(plan_id=plan_id)
            results = [ob.as_json() for ob in object_list]

            return HttpResponse(json.dumps(results), mimetype='application/json')
        except:
            return HttpResponseServerError('No se pudo procesar el pedido')
            #return (e) 
            
@require_http_methods(["GET"])
def get_propietario_name_id_by_cedula(request):
    if request.method == 'GET':
        #data = request.GET
        try:
            
            cedula_propietario = request.GET['term']
            print("term ->" + cedula_propietario);
            object_list = Propietario.objects.filter(cedula__icontains= cedula_propietario)
#    object_list = PlanDePago.objects.filter(plan_id=plan_id)
            results = [ob.as_json() for ob in object_list]

            return HttpResponse(json.dumps(results), mimetype='application/json')
        except:
            return HttpResponseServerError('No se pudo procesar el pedido')
            #return (e)                  

@require_http_methods(["GET"])
def get_cliente_name_id_by_cedula(request):
    if request.method == 'GET':
        #data = request.GET
        try:
            
            cedula_cliente = request.GET['term']
            print("term ->" + cedula_cliente);
            object_list = Cliente.objects.filter(cedula__icontains= cedula_cliente)
#    object_list = PlanDePago.objects.filter(plan_id=plan_id)
            results = [ob.as_json() for ob in object_list]

            return HttpResponse(json.dumps(results), mimetype='application/json')
        except:
            return HttpResponseServerError('No se pudo procesar el pedido')
            #return (e)   

def get_cliente_id_by_name(request):
    if request.method == 'GET':
        #data = request.GET
        try:
            
            name_cliente = request.GET['term']
            print("term ->" + name_cliente);
            object_list = Cliente.objects.filter(nombres__icontains= name_cliente)
#    object_list = PlanDePago.objects.filter(plan_id=plan_id)
            results = [ob.as_json() for ob in object_list]

            return HttpResponse(json.dumps(results), mimetype='application/json')
        except:
            return HttpResponseServerError('No se pudo procesar el pedido')
            #return (e)   

def get_vendedor_id_by_name(request):
    if request.method == 'GET':
        #data = request.GET
        try:
            
            name_vendedor = request.GET['term']
            print("term ->" + name_vendedor);
            object_list = Vendedor.objects.filter(nombres__icontains= name_vendedor)
#    object_list = PlanDePago.objects.filter(plan_id=plan_id)
            results = [ob.as_json() for ob in object_list]

            return HttpResponse(json.dumps(results), mimetype='application/json')
        except:
            return HttpResponseServerError('No se pudo procesar el pedido')
            #return (e)     
 
@require_http_methods(["GET"])
def get_lotes_a_cargar_by_manzana(request):
    if request.method == 'GET':
        #data = request.GET
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
#    object_list = PlanDePago.objects.filter(plan_id=plan_id)
                #results = [ob.as_json() for ob in object_list2]
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
            #object_list = PlanDePago.objects.filter(plan_id=plan_id)
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
    object_list = Venta.objects.filter(lote=lote_id).order_by('-id')[:1]
    venta = [ob.as_json() for ob in object_list]
    cuotas_details = get_cuotas_detail_by_lote(lote_id)
    json_response = json.dumps({
                                'venta': venta,
                                'cuotas_details': cuotas_details,
    })
    print(json_response)
    return HttpResponse(json_response, mimetype='application/json')

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

@require_http_methods(["GET"])
def get_plan_pago(request):
    if request.method == 'GET':
        #data = request.GET
        try:            
            nombre_plan = request.GET['term']
            print("term ->" + nombre_plan);
            object_list = PlanDePago.objects.filter(nombre_del_plan__icontains= nombre_plan)
#    object_list = PlanDePago.objects.filter(plan_id=plan_id)
            results = [ob.as_json() for ob in object_list]

            return HttpResponse(json.dumps(results), mimetype='application/json')
        except:
            return HttpResponseServerError('No se pudo procesar el pedido')
            #return (e) 
            
@require_http_methods(["GET"])
def get_plan_pago_vendedor(request):
    if request.method == 'GET':
        #data = request.GET
        try:            
            nombre_plan = request.GET['term']
            print("term ->" + nombre_plan);
            object_list = PlanDePagoVendedor.objects.filter(nombre__icontains= nombre_plan)
#    object_list = PlanDePago.objects.filter(plan_id=plan_id)
            results = [ob.as_json() for ob in object_list]

            return HttpResponse(json.dumps(results), mimetype='application/json')
        except:
            return HttpResponseServerError('No se pudo procesar el pedido')
            #return (e) 


@require_http_methods(["GET"])
def get_lista_pagos(request):
    
    #vendedor_id = request.GET['busqueda']
    #print("vendedor_id ->" + vendedor_id);
    fecha_ini=request.GET['fecha_ini']
    fecha_fin=request.GET['fecha_fin']
    tipo_busqueda=request.GET['tipo_busqueda']
    if(tipo_busqueda=='vendedor_id'):
        vendedor_id=request.GET['busqueda']
        print("vendedor_id ->" + vendedor_id)
    if(tipo_busqueda=='nombre'):
        nombre_vendedor=request.GET['busqueda']
        print("nombre_vendedor ->" + nombre_vendedor)
        vendedor=Vendedor.objects.get(nombres__icontains=nombre_vendedor)
        vendedor_id=str(vendedor.id)
    query=(
    '''
    select pc.* from principal_pagodecuotas pc, principal_lote l, principal_manzana m, principal_fraccion f
    where pc.fecha_de_pago >= \''''+ fecha_ini +               
    '''\' and pc.fecha_de_pago <= \'''' + fecha_fin +
    '''\' and pc.vendedor_id=''' + vendedor_id +                
    ''' 
    and (pc.lote_id = l.id and l.manzana_id=m.id and m.fraccion_id=f.id) order by f.id,pc.fecha_de_pago
    '''
    )
        
        
    object_list=list(PagoDeCuotas.objects.raw(query))
    cuotas=[]
    for i in object_list:
        nro_cuota=get_nro_cuota(i)
        if(nro_cuota%2!=0 and nro_cuota<10):
            cuota={}            
            cuota['fraccion_id']=i.lote.manzana.fraccion.id
            cuota['fraccion']=str(i.lote.manzana.fraccion)
            cuota['cliente']=str(i.cliente)
            cuota['lote']=str(i.lote)
            cuota['cuota_nro']=str(nro_cuota)+'/'+str(i.plan_de_pago.cantidad_de_cuotas)
            cuota['fecha_pago']=str(i.fecha_de_pago)
            cuota['importe']=i.total_de_cuotas
            cuota['comision']=int(i.total_de_cuotas*(i.plan_de_pago_vendedores.porcentaje_de_cuotas/100))
            cuotas.append(cuota)
    #print 'hola'
    return HttpResponse(json.dumps(cuotas), mimetype='application/json')
    
@require_http_methods(["GET"])
def get_informe_general(request):
   
    fecha_ini=request.GET['fecha_ini']
    fecha_fin=request.GET['fecha_fin']
    fecha_ini_parsed = datetime.strptime(fecha_ini, "%d/%m/%Y").date()
    fecha_fin_parsed = datetime.strptime(fecha_fin, "%d/%m/%Y").date()
    fraccion_ini=request.GET['fraccion_ini']
    fraccion_fin=request.GET['fraccion_fin']
    query=(
    '''
    select pc.* from principal_pagodecuotas pc, principal_lote l, principal_manzana m, principal_fraccion f
    where pc.fecha_de_pago >= \''''+ str(fecha_ini_parsed) +               
    '''\' and pc.fecha_de_pago <= \'''' + str(fecha_fin_parsed) +
    '''\' and f.id>=''' + fraccion_ini +
    '''
    and f.id<=''' + fraccion_fin +
    '''
    and (pc.lote_id = l.id and l.manzana_id=m.id and m.fraccion_id=f.id) order by f.id,pc.fecha_de_pago
    '''
    )
         
    print query
 
    object_list=list(PagoDeCuotas.objects.raw(query))
 
    cuotas=[]
    for i in object_list:
        nro_cuota=get_nro_cuota(i)
        cuota={}            
        cuota['fraccion_id']=i.lote.manzana.fraccion.id
        cuota['fraccion']=str(i.lote.manzana.fraccion)
        cuota['lote']=str(i.lote)
        cuota['cliente']=str(i.cliente)
        cuota['cuota_nro']=str(nro_cuota)+'/'+str(i.plan_de_pago.cantidad_de_cuotas)
        cuota['plan_de_pago']=i.plan_de_pago.nombre_del_plan
        cuota['fecha_pago']=str(i.fecha_de_pago)
        cuota['total_de_cuotas']=i.total_de_cuotas
        cuota['total_de_mora']=i.total_de_mora
        cuota['total_de_pago']=i.total_de_pago
        cuotas.append(cuota)
    
    #print 'hola'
    return HttpResponse(json.dumps(cuotas), mimetype='application/json')
            
   
    
    
    
    
    
    
