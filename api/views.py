import traceback
from django.contrib.auth import authenticate
from django.http import HttpResponseServerError, HttpResponseBadRequest
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from principal.common_functions import *
from principal.models import *
import pytz
import logging
from django.db.models import Q


# Ejemplo nuevo esquema de serializacion:
# all_objects = list(Restaurant.objects.all()) + list(Place.objects.all())
# data = serializers.serialize('xml', all_objects)
# data = serializers.serialize('json', list(objectQuerySet), fields=('fileName','id'))


@require_http_methods(["GET"])
def consulta(request, codigo_consulta):
    codigo_base_error_consulta = 'c'
    # tipo_consulta = 'cliente'
    tipo_consulta = 'codigo_lote'
    error = {}
    if request.method == 'GET':
        try:
            username = request.GET['username']
            password = request.GET['password']

            # 1. Autenticacion
            user = authenticate(username=username, password=password)
            if user is not None:
                # the password verified for the user
                if user.is_active:
                    print("User is valid, active and authenticated")

                    if tipo_consulta == 'cliente':
                        print("cedula de identidad ->" + codigo_consulta)
                        # 2. Se obtiene cliente
                        cliente = Cliente.objects.get(cedula=codigo_consulta)
                        if not cliente:
                            error_msg = 'Cliente no encontrado'
                            print error_msg
                            error['codigo'] = codigo_base_error_consulta + '31'
                            error['mensaje'] = error_msg
                            return HttpResponse(json.dumps(error), status=404, content_type="application/json")
                        else:
                            # cliente_serialized = serializers.serialize('python', cliente)
                            # 2. Se obtienen las ventas de dicho cliente
                            ventas_list = Venta.objects.filter(cliente=cliente, lote__estado=3)
                            if not ventas_list:
                                error_msg = 'Cliente no tiene compras actuales'
                                print error_msg
                                error['codigo'] = codigo_base_error_consulta + '32'
                                error['mensaje'] = error_msg
                                return HttpResponse(json.dumps(error), status=404, content_type="application/json")
                            else:
                                items = []  # Aqui se almacena la lista de ventas disponibles para el pago.
                                respuesta = []
                                transaccion = Transaccion()
                                transaccion.estado = 'Consultado'
                                transaccion.cliente = cliente
                                transaccion.updated = datetime.datetime.now(pytz.utc)
                                transaccion.save()
                                # mas abajo se loggea

                                cabecera = {'id_transaccion': transaccion.pk, 'codigo': '100'}
                                respuesta.append(cabecera)
                                lote = []
                                for venta in ventas_list:
                                    # 3. Por cada venta se va generando la informacion necesaria para cada venta que
                                    # requiere pago.
                                    item = {}
                                    lote = Lote.objects.filter(id=venta.lote_id)
                                    lote_serialized = serializers.serialize('python', lote)
                                    detalle_cuotas = get_cuotas_detail_by_lote(unicode(lote_serialized[0]['pk']))
                                    cuota_detalle = get_cuota_information_by_lote(unicode(lote_serialized[0]['pk']), 1)
                                    item['codigo_lote'] = lote_serialized[0]['fields']['codigo_paralot']
                                    item['cuotas_pagadas'] = detalle_cuotas['cant_cuotas_pagadas']
                                    item['total_cuotas'] = detalle_cuotas['cantidad_total_cuotas']
                                    item['numero_cuota_a_pagar'] = cuota_detalle[0]['nro_cuota'].split('/')[0]
                                    item['fecha_vencimiento'] = detalle_cuotas['proximo_vencimiento']
                                    hoy = date.today()
                                    cuotas_a_pagar_detalle = obtener_cuotas_a_pagar(venta, hoy, detalle_cuotas)
                                    # cuotas_a_pagar_detalle = obtener_cuotas_
                                    # a_pagar(venta,date(2015,4,12),detalle_cuotas)
                                    item['detalle_cuotas'] = cuotas_a_pagar_detalle
                                    items.append(item)
                                respuesta.append(items)

                                # Se loguea la accion en el log de usuarios
                                id_objeto = transaccion.id
                                codigo_lote = lote.codigo_paralot
                                loggear_accion(request.user, "Agregar", "Transaccion", id_objeto, codigo_lote)
                                print "Consulta de transaccion id: " + unicode(id_objeto) + " finalizada."

                                return HttpResponse(json.dumps(respuesta), content_type="application/json")
                                # ------------------------- CODIGO DE LOTE ----------------------------
                    elif tipo_consulta == 'codigo_lote':
                        codigo_consulta = codigo_consulta.replace("-", "/")
                        print("codigo de lote ->" + codigo_consulta)
                        # 2. Se obtiene el lote
                        lote = Lote.objects.get(codigo_paralot=codigo_consulta)
                        if not lote:
                            error_msg = 'Lote no encontrado'
                            print error_msg
                            error['codigo'] = codigo_base_error_consulta + '31'
                            error['mensaje'] = error_msg
                            return HttpResponse(json.dumps(error), status=404, content_type="application/json")
                        else:
                            # cliente_serialized = serializers.serialize('python', cliente)
                            # 2. Se obtienen las ventas de dicho lote
                            ventas_list = Venta.objects.filter(
                                Q(lote=lote, recuperado=None) | Q(lote=lote, recuperado=False))
                            if not ventas_list:
                                error_msg = 'Lote no tiene ventas actuales'
                                print error_msg
                                error['codigo'] = codigo_base_error_consulta + '32'
                                error['mensaje'] = error_msg
                                return HttpResponse(json.dumps(error), status=404, content_type="application/json")
                            else:
                                items = []  # Aqui se almacena la lista de ventas disponibles para el pago.
                                respuesta = []
                                transaccion = Transaccion()
                                transaccion.estado = 'Consultado'
                                transaccion.cliente = ventas_list[0].cliente
                                transaccion.save()
                                # mas abajo se loggea

                                cabecera = {'id_transaccion': transaccion.pk, 'codigo': '100'}
                                respuesta.append(cabecera)
                                lote_log = []
                                for venta in ventas_list:
                                    # 3. Por cada venta se va generando la informacion
                                    # necesaria para cada venta que requiere pago.
                                    item = {}
                                    lote = Lote.objects.filter(id=venta.lote_id)
                                    lote_log = Lote.objects.get(id=venta.lote_id)
                                    lote_serialized = serializers.serialize('python', lote)
                                    detalle_cuotas = get_cuotas_detail_by_lote(unicode(lote_serialized[0]['pk']))
                                    cuota_detalle = get_cuota_information_by_lote(unicode(lote_serialized[0]['pk']), 1)
                                    item['codigo_lote'] = lote_serialized[0]['fields']['codigo_paralot']
                                    item['cuotas_pagadas'] = detalle_cuotas['cant_cuotas_pagadas']
                                    item['total_cuotas'] = detalle_cuotas['cantidad_total_cuotas']
                                    item['numero_cuota_a_pagar'] = cuota_detalle[0]['nro_cuota'].split('/')[0]
                                    item['fecha_vencimiento'] = detalle_cuotas['proximo_vencimiento']
                                    hoy = date.today()
                                    # Esta linea comentada sirve para probar la consulta en una fecha (anho, mes, dia)
                                    # hoy = datetime.date(2016, 12, 14)
                                    cuotas_a_pagar_detalle = obtener_cuotas_a_pagar_full(
                                        venta, hoy, detalle_cuotas, 500
                                    )
                                    # cuotas_a_pagar_detalle = obtener_cuotas_a_pagar(
                                    # venta,date(2015,4,12),detalle_cuotas)
                                    item['detalle_cuotas'] = cuotas_a_pagar_detalle

                                    fecha_primer_vencimiento = venta.fecha_primer_vencimiento
                                    cantidad_ideal_cuotas = monthdelta(fecha_primer_vencimiento, hoy)
                                    # Y obtenemos las cuotas atrasadas
                                    if cantidad_ideal_cuotas > 0:
                                        cuotas_atrasadas = cantidad_ideal_cuotas - int(
                                            detalle_cuotas['cant_cuotas_pagadas'])
                                    else:
                                        cuotas_atrasadas = 0

                                    item['cuotas_atrasadas'] = cuotas_atrasadas
                                    items.append(item)
                                respuesta.append(items)

                                # Se loguea la accion en el log de usuarios
                                id_objeto = transaccion.id
                                codigo_lote = lote_log.codigo_paralot
                                loggear_accion(user, "Agregar", "Transaccion", id_objeto, codigo_lote)
                                print "Consulta de transaccion id: " + unicode(id_objeto) + " finalizada."

                                return HttpResponse(json.dumps(respuesta), content_type="application/json")

                else:
                    error_msg = 'Cuenta deshabilitada'
                    print error_msg
                    error['codigo'] = '22'
                    error['mensaje'] = error_msg
                    return HttpResponse(json.dumps(error), status=401, content_type="application/json")
            else:
                # the authentication system was unable to verify the username and password
                error_msg = 'Usuario o password incorrecto'
                print error_msg
                error['codigo'] = '21'
                error['mensaje'] = error_msg
                return HttpResponse(json.dumps(error), status=401, content_type="application/json")
        except MultiValueDictKeyError:
            traceback.format_exc()
            error_msg = 'Sintaxis del request incorrecta'
            print error_msg
            error['codigo'] = '11'
            error['mensaje'] = error_msg
            return HttpResponseBadRequest(json.dumps(error), content_type="application/json")
        except Exception as e:
            logging.error('Failed.', exc_info=e)
            error = {}
            traceback.format_exc()
            error_msg = 'Error en el servidor'
            print error_msg
            error['codigo'] = '00'
            error['mensaje'] = error_msg
            return HttpResponseServerError(json.dumps(error), content_type="application/json")


@require_http_methods(["POST", "GET"])
@csrf_exempt
def pago(request):
    error = {}
    tipo_metodo = 'post'
    # tipo_metodo = 'json_post'
    codigo_base_error_pago = 'p'
    if request.method == 'POST':
        if tipo_metodo == 'json_post':
            try:
                username = request.GET['username']
                password = request.GET['password']
                transaccion_id = request.GET['transaccion_id']
                print 'Pago para transaccion id: ' + transaccion_id
                detalle_pago_json = request.body
                print 'JSON recibido: ' + detalle_pago_json
                if not detalle_pago_json:
                    print('Error en los parametros del request')
                    error['codigo'] = '12'
                    error['mensaje'] = 'Request sin datos en el cuerpo'
                    return HttpResponseBadRequest(json.dumps(error), content_type="application/json")
                else:
                    # 1. Autenticacion
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        # the password verified for the user
                        if user.is_active:
                            # 2. Se obtiene la transaccion
                            transaccion = Transaccion.objects.get(Q(id=transaccion_id))
                            # transaccion_tmstmp = transaccion.created.replace(tzinfo=None)
                            if not transaccion:
                                error_msg = 'Transaccion no encontrada'
                                print error_msg
                                error['codigo'] = codigo_base_error_pago + '31'
                                error['mensaje'] = error_msg
                                return HttpResponse(json.dumps(error), status=404, content_type="application/json")
                            else:
                                if transaccion.estado != 'Consultado':
                                    error_msg = 'Transaccion con estado invalido'
                                    print error_msg
                                    error['codigo'] = codigo_base_error_pago + '32'
                                    error['mensaje'] = error_msg
                                    return HttpResponse(json.dumps(error), status=404, content_type="application/json")
                                else:  # Estado valido
                                    if (datetime.datetime.now(
                                            pytz.utc) - transaccion.created).seconds / 60 > 30:  # TIMEOUT
                                        error_msg = 'Timeout'
                                        print error_msg
                                        error['codigo'] = codigo_base_error_pago + '33'
                                        error['mensaje'] = error_msg
                                        if transaccion.estado != 'Pagado':
                                            transaccion.estado = 'Expirado'
                                            transaccion.updated = datetime.datetime.now(pytz.utc)
                                            transaccion.save()

                                            # Se logea la accion del usuario
                                            id_objeto = transaccion.id
                                            codigo_lote = ''
                                            loggear_accion(request.user, "Actualizar Estado", "Transaccion", id_objeto,
                                                           codigo_lote)

                                        return HttpResponse(json.dumps(error), status=404,
                                                            content_type="application/json")
                                    else:
                                        detalle_pago = json.loads(detalle_pago_json)
                                        lote = Lote.objects.get(codigo_paralot=detalle_pago['codigo_lote'])
                                        venta = Venta.objects.get(Q(lote=lote), Q(cliente=transaccion.cliente))
                                        detalle_cuotas = get_cuotas_detail_by_lote(unicode(lote.id))
                                        hoy = date.today()
                                        cuotas_a_pagar_detalle = obtener_cuotas_a_pagar(venta, hoy, detalle_cuotas)
                                        if not cuotas_a_pagar_detalle:
                                            error_msg = 'Cuota a pagar no encontrada'
                                            print error_msg
                                            error['codigo'] = codigo_base_error_pago + '34'
                                            error['mensaje'] = error_msg
                                            return HttpResponse(json.dumps(error), status=404,
                                                                content_type="application/json")
                                        else:
                                            if unicode(
                                                    cuotas_a_pagar_detalle[0]['numero_cuota']) \
                                                    != detalle_pago['cuota_a_pagar']:
                                                error_msg = 'Numero de cuota a pagar incorrecta, se espera: ' + unicode(
                                                    cuotas_a_pagar_detalle[0]['numero_cuota'])
                                                print error_msg
                                                error['codigo'] = codigo_base_error_pago + '35'
                                                error['mensaje'] = error_msg
                                                return HttpResponse(json.dumps(error), status=404,
                                                                    content_type="application/json")
                                            elif float(detalle_pago['monto_total']) \
                                                    != cuotas_a_pagar_detalle[0]['monto_cuota']:
                                                error_msg = 'Monto de la cuota incorrecto, se espera: ' + unicode(
                                                    cuotas_a_pagar_detalle[0]['monto_cuota'])
                                                print error_msg
                                                error['codigo'] = codigo_base_error_pago + '44'
                                                error['mensaje'] = error_msg
                                                return HttpResponse(json.dumps(error), status=404,
                                                                    content_type="application/json")
                                            else:  # Parametros totalmente correctos, emitir el pago
                                                nuevo_pago = PagoDeCuotas()
                                                nuevo_pago.venta = venta
                                                nuevo_pago.lote = lote
                                                nuevo_pago.transaccion = transaccion
                                                nuevo_pago.fecha_de_pago = hoy
                                                nuevo_pago.nro_cuotas_a_pagar = 1
                                                nuevo_pago.cliente = transaccion.cliente
                                                nuevo_pago.plan_de_pago = venta.plan_de_pago
                                                nuevo_pago.plan_de_pago_vendedores = venta.plan_de_pago_vendedor
                                                nuevo_pago.vendedor = venta.vendedor
                                                nuevo_pago.total_de_cuotas = venta.precio_de_cuota
                                                nuevo_pago.total_de_pago = cuotas_a_pagar_detalle[0]['monto_cuota']
                                                nuevo_pago.total_de_mora = cuotas_a_pagar_detalle[0][
                                                                               'monto_cuota'] - venta.precio_de_cuota
                                                nuevo_pago.save()

                                                # Se loggea la accion del usuario
                                                id_objeto = nuevo_pago.id
                                                codigo_lote = detalle_pago['codigo_lote']
                                                loggear_accion(user, "Agregar", "Pago de cuota", id_objeto, codigo_lote)

                                                transaccion.estado = 'Pagado'
                                                transaccion.updated = datetime.datetime.now(pytz.utc)
                                                transaccion.save()

                                                # Se loggea la accion del usuario
                                                id_objeto = transaccion.id
                                                loggear_accion(user, "Actualizar estado", "Transaccion", id_objeto,
                                                               codigo_lote)

                                                respuesta = {'mensaje': 'Operacion Exitosa', 'codigo': '200'}

                                                print "Pago de transaccion id: " + unicode(id_objeto) + " finalizada."

                                                return HttpResponse(json.dumps(respuesta),
                                                                    content_type="application/json")
                        else:
                            error_msg = 'Cuenta deshabilitada'
                            print error_msg
                            error['codigo'] = '22'
                            error['mensaje'] = error_msg
                            return HttpResponse(json.dumps(error), status=401, content_type="application/json")
                    else:
                        # the authentication system was unable to verify the username and password
                        error_msg = 'Usuario o password incorrecto'
                        print error_msg
                        error['codigo'] = '21'
                        error['mensaje'] = error_msg
                        return HttpResponse(json.dumps(error), status=401, content_type="application/json")
            except MultiValueDictKeyError:
                error_msg = 'Sintaxis del request incorrecta'
                print error_msg
                error['codigo'] = '11'
                error['mensaje'] = error_msg
                return HttpResponseBadRequest(json.dumps(error), content_type="application/json")
            except Exception, error2:
                print error2
                if error2.message == 'Transaccion matching query does not exist.':
                    error_msg = 'Transaccion no encontrada'
                    print error_msg
                    error['codigo'] = codigo_base_error_pago + '46'
                    error['mensaje'] = error_msg
                    return HttpResponse(json.dumps(error), status=404, content_type="application/json")
                elif error2.message == 'Venta matching query does not exist.':
                    error_msg = 'No se encontro la venta'
                    print error_msg
                    error['codigo'] = codigo_base_error_pago + '48'
                    error['mensaje'] = error_msg
                    return HttpResponse(json.dumps(error), status=404, content_type="application/json")
                error['codigo'] = '00'
                error['mensaje'] = 'Error en el servidor'
        else:  # -------------------------------------------  P O S T ---------------------------------------------
            try:
                detalle_pago_post = request.POST
                if not detalle_pago_post:
                    respuesta = {}
                    print "Post de pago sin parametros para prueba de conexion"
                    print unicode(request.POST)
                    respuesta['mensaje'] = 'Conexion Exitosa'
                    respuesta['codigo'] = '200'
                    return HttpResponse(json.dumps(respuesta), content_type="application/json")
                else:
                    print 'POST recibido: ' + unicode(detalle_pago_post)
                    username = request.POST['username']
                    password = request.POST['password']
                    transaccion_id = request.POST['transaccion_id']
                    print 'Pago para transaccion id: ' + transaccion_id
                    transaccion_externa_id = request.POST['id_transaccion_externa']

                    # 1. Autenticacion
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        # the password verified for the user
                        if user.is_active:
                            # 2. Se obtiene la transaccion
                            transaccion = Transaccion.objects.get(Q(id=transaccion_id))
                            # transaccion_tmstmp = transaccion.created.replace(tzinfo=None)
                            if not transaccion:
                                error_msg = 'Transaccion no encontrada'
                                print error_msg
                                error['codigo'] = codigo_base_error_pago + '31'
                                error['mensaje'] = error_msg
                                return HttpResponse(json.dumps(error), status=404, content_type="application/json")
                            else:
                                if transaccion.estado != 'Consultado':
                                    error_msg = 'Transaccion con estado invalido'
                                    print error_msg
                                    error['codigo'] = codigo_base_error_pago + '32'
                                    error['mensaje'] = error_msg
                                    return HttpResponse(json.dumps(error), status=404, content_type="application/json")
                                else:  # Estado valido
                                    if (datetime.datetime.now(
                                            pytz.utc) - transaccion.created).seconds / 60 > 30:  # TIMEOUT
                                        error_msg = 'Timeout'
                                        print error_msg
                                        error['codigo'] = codigo_base_error_pago + '33'
                                        error['mensaje'] = error_msg
                                        if transaccion.estado != 'Pagado':
                                            transaccion.estado = 'Expirado'
                                            transaccion.updated = datetime.datetime.now(pytz.utc)
                                            transaccion.save()

                                            # Se logea la accion del usuario
                                            id_objeto = transaccion.id
                                            codigo_lote = ''
                                            loggear_accion(request.user, "Actualizar estado", "Transaccion", id_objeto,
                                                           codigo_lote)

                                            print "Pago de transaccion id: " + unicode(id_objeto) + " finalizado."

                                        return HttpResponse(json.dumps(error), status=404,
                                                            content_type="application/json")
                                    else:
                                        detalle_pago = detalle_pago_post
                                        lote = Lote.objects.get(codigo_paralot=detalle_pago['codigo_lote'])
                                        venta = Venta.objects.filter(lote=lote, cliente=transaccion.cliente).latest(
                                            'id')
                                        detalle_cuotas = get_cuotas_detail_by_lote(unicode(lote.id))
                                        hoy = date.today()
                                        # ahora = datetime.datetime.now()
                                        cuotas_a_pagar_detalle = obtener_cuotas_a_pagar(venta, hoy, detalle_cuotas)
                                        if not cuotas_a_pagar_detalle:
                                            error_msg = 'Cuota a pagar no encontrada'
                                            print error_msg
                                            error['codigo'] = codigo_base_error_pago + '34'
                                            error['mensaje'] = error_msg
                                            return HttpResponse(json.dumps(error), status=404,
                                                                content_type="application/json")
                                        else:
                                            if not unicode(detalle_pago['cantidad_cuotas']).isdigit():
                                                error_msg = 'Numero de cuotas a pagar incorrecta.'
                                                print error_msg
                                                error['codigo'] = codigo_base_error_pago + '35'
                                                error['mensaje'] = error_msg
                                                return HttpResponse(json.dumps(error), status=404,
                                                                    content_type="application/json")
                                            elif not unicode(detalle_pago['monto_total']).isdigit():
                                                error_msg = 'Monto total a pagar incorrecto.'
                                                print error_msg
                                                error['codigo'] = codigo_base_error_pago + '36'
                                                error['mensaje'] = error_msg
                                                return HttpResponse(json.dumps(error), status=404,
                                                                    content_type="application/json")
                                            elif not unicode(detalle_pago['id_transaccion_externa']).isdigit():
                                                error_msg = 'Id Transaccion externa incorrecta.'
                                                print error_msg
                                                error['codigo'] = codigo_base_error_pago + '37'
                                                error['mensaje'] = error_msg
                                                return HttpResponse(json.dumps(error), status=404,
                                                                    content_type="application/json")
                                            else:  # Parametros totalmente correctos, emitir el pago

                                                detalle_cuotas = get_cuotas_detail_by_lote(unicode(lote.id))
                                                # cuota_detalle = get_cuota_information_by_lote(unicode(lote.id), 1)

                                                vencimiento = detalle_cuotas['proximo_vencimiento']

                                                proximo_vencimiento_parsed = datetime.datetime.strptime(
                                                    vencimiento, "%d/%m/%Y").date()

                                                detalles = obtener_detalle_interes_lote(
                                                    lote.id, hoy, proximo_vencimiento_parsed,
                                                    int(
                                                        detalle_pago['cantidad_cuotas']
                                                    )
                                                )

                                                lista_detalles_json = []
                                                detalles_json = {}
                                                item = 0
                                                for detalle in detalles:
                                                    detalles_json['item' + unicode(item)] = detalle
                                                    lista_detalles_json.append(detalles_json)
                                                    item += 1

                                                lista_detalles_json = json.dumps(detalles_json)

                                                nuevo_pago = PagoDeCuotas()
                                                nuevo_pago.venta = venta
                                                nuevo_pago.lote = lote
                                                nuevo_pago.transaccion = transaccion
                                                nuevo_pago.fecha_de_pago = hoy
                                                nuevo_pago.nro_cuotas_a_pagar = int(detalle_pago['cantidad_cuotas'])
                                                nuevo_pago.cliente = transaccion.cliente
                                                nuevo_pago.plan_de_pago = venta.plan_de_pago
                                                nuevo_pago.plan_de_pago_vendedores = venta.plan_de_pago_vendedor
                                                nuevo_pago.vendedor = venta.vendedor
                                                nuevo_pago.total_de_cuotas = venta.precio_de_cuota
                                                nuevo_pago.total_de_pago = int(detalle_pago['monto_total'])
                                                nuevo_pago.total_de_mora = int(
                                                    detalle_pago['monto_total']) - venta.precio_de_cuota
                                                nuevo_pago.detalle = lista_detalles_json
                                                nuevo_pago.save()

                                                venta.pagos_realizados += nuevo_pago.nro_cuotas_a_pagar
                                                venta.save()
                                                # Se loggea la accion del usuario
                                                id_objeto = nuevo_pago.id
                                                codigo_lote = detalle_pago['codigo_lote']
                                                loggear_accion(user, "Agregar", "Pago de cuota", id_objeto, codigo_lote)

                                                transaccion.estado = 'Pagado'
                                                transaccion.id_transaccion_externa = transaccion_externa_id
                                                transaccion.updated = datetime.datetime.now(pytz.utc)
                                                transaccion.save()

                                                # Se loggea la accion del usuario
                                                id_objeto = transaccion.id
                                                loggear_accion(user, "Actualizar estado", "Transaccion", id_objeto,
                                                               codigo_lote)

                                                respuesta = {'mensaje': 'Operacion Exitosa', 'codigo': '200'}

                                                print "Pago de transaccion id: " + unicode(id_objeto) + " finalizado."

                                                return HttpResponse(json.dumps(respuesta),
                                                                    content_type="application/json")
                        else:
                            error_msg = 'Cuenta deshabilitada'
                            print error_msg
                            error['codigo'] = '22'
                            error['mensaje'] = error_msg
                            return HttpResponse(json.dumps(error), status=401, content_type="application/json")
                    else:
                        # the authentication system was unable to verify the username and password
                        error_msg = 'Usuario o password incorrecto'
                        print error_msg
                        error['codigo'] = '21'
                        error['mensaje'] = error_msg
                        return HttpResponse(json.dumps(error), status=401, content_type="application/json")
            except MultiValueDictKeyError:
                error_msg = 'Sintaxis del request incorrecta'
                print error_msg
                error['codigo'] = '11'
                error['mensaje'] = error_msg
                return HttpResponseBadRequest(json.dumps(error), content_type="application/json")
            except Exception, error2:
                print error2
                if error2.message == 'Transaccion matching query does not exist.':
                    error_msg = 'Transaccion no encontrada'
                    print error_msg
                    error['codigo'] = codigo_base_error_pago + '46'
                    error['mensaje'] = error_msg
                    return HttpResponse(json.dumps(error), status=404, content_type="application/json")
                elif error2.message == 'Venta matching query does not exist.':
                    error_msg = 'No se encontro la venta'
                    print error_msg
                    error['codigo'] = codigo_base_error_pago + '48'
                    error['mensaje'] = error_msg
                    return HttpResponse(json.dumps(error), status=404, content_type="application/json")
                error['codigo'] = '00'
                error['mensaje'] = 'Error en el servidor'

                return HttpResponseServerError(json.dumps(error), content_type="application/json")
    else:
        respuesta = {'mensaje': 'Conexion Exitosa', 'codigo': '200'}
        return HttpResponse(json.dumps(respuesta), content_type="application/json")


@require_http_methods(["POST", "GET"])
@csrf_exempt
def reversion(request):
    error = {}
    codigo_base_error_reversion = 'r'
    if request.method == 'POST':
        try:
            detalle_reversion_post = request.POST
            if not detalle_reversion_post:
                respuesta = {}
                print "Post de reversion sin parametros para prueba de conexion"
                print unicode(request.POST)
                respuesta['mensaje'] = 'Conexion Exitosa'
                respuesta['codigo'] = '200'
                return HttpResponse(json.dumps(respuesta), content_type="application/json")
            else:
                print 'POST recibido: ' + unicode(detalle_reversion_post)
                username = request.POST['username']
                password = request.POST['password']
                # transaccion_id = request.POST['transaccion_id']
                transaccion_externa_id = request.POST['id_transaccion_externa']
                print 'Reversion para id transaccion externa: ' + transaccion_externa_id

                # 1. Autenticacion
                user = authenticate(username=username, password=password)
                if user is not None:
                    # the password verified for the user
                    if user.is_active:
                        # 2. Se obtiene la transaccion
                        # transaccion = Transaccion.objects.get(
                        # id = transaccion_id, id_transaccion_externa=transaccion_externa_id
                        # )
                        transaccion = Transaccion.objects.get(id_transaccion_externa=transaccion_externa_id)
                        # transaccion_tmstmp = transaccion.created.replace(tzinfo=None)
                        if not transaccion:
                            error_msg = 'Transaccion no encontrada'
                            print error_msg
                            error['codigo'] = codigo_base_error_reversion + '31'
                            error['mensaje'] = error_msg
                            return HttpResponse(json.dumps(error), status=404, content_type="application/json")
                        else:
                            if transaccion.estado != 'Pagado':
                                error_msg = 'Transaccion con estado invalido'
                                print error_msg
                                error['codigo'] = codigo_base_error_reversion + '32'
                                error['mensaje'] = error_msg
                                return HttpResponse(json.dumps(error), status=404, content_type="application/json")
                            else:  # Estado valido
                                if (datetime.datetime.now(pytz.utc) - transaccion.created).seconds / 60 > 30:  # TIMEOUT
                                    error_msg = 'Timeout'
                                    print error_msg
                                    error['codigo'] = codigo_base_error_reversion + '33'
                                    error['mensaje'] = error_msg
                                    return HttpResponse(json.dumps(error), status=404, content_type="application/json")
                                else:
                                    # detalle_reversion = detalle_reversion_post
                                    # hoy = date.today()
                                    try:
                                        pago_de_transaccion = PagoDeCuotas.objects.get(transaccion_id=transaccion.id)
                                    except Exception as e:
                                        logging.error('Failed.', exc_info=e)
                                        pago_de_transaccion = ''

                                    if pago_de_transaccion == '':
                                        error_msg = 'No se encuentra el pago asociado a la transaccion.'
                                        print error_msg
                                        error['codigo'] = codigo_base_error_reversion + '35'
                                        error['mensaje'] = error_msg
                                        return HttpResponse(json.dumps(error), status=404,
                                                            content_type="application/json")
                                    else:  # Parametros totalmente correctos, emitir el pago

                                        venta = pago_de_transaccion.venta
                                        nro_cuotas_pagadas = pago_de_transaccion.nro_cuotas_a_pagar
                                        id_objeto = pago_de_transaccion.id
                                        pago_de_transaccion.delete()
                                        # Se loggea la accion del usuario
                                        codigo_lote = venta.lote.codigo_paralot
                                        loggear_accion(user, "Eliminar (Reversion)", "Pago de cuota", id_objeto,
                                                       codigo_lote)

                                        venta.pagos_realizados = venta.pagos_realizados - nro_cuotas_pagadas
                                        id_objeto = venta.id
                                        venta.save()
                                        loggear_accion(user, "Actualizacion de cuotas pagadas (Reversion)", "Venta",
                                                       id_objeto, codigo_lote)

                                        transaccion.estado = 'Revertido'
                                        transaccion.updated = datetime.datetime.now(pytz.utc)
                                        transaccion.save()

                                        # Se loggea la accion del usuario
                                        id_objeto = transaccion.id
                                        loggear_accion(user, "Actualizar estado (Reversion)", "Transaccion", id_objeto,
                                                       codigo_lote)

                                        respuesta = {'mensaje': 'Operacion Exitosa', 'codigo': '200'}

                                        print "Reversion de transaccion id: " + unicode(id_objeto) + " finalizada."

                                        return HttpResponse(json.dumps(respuesta), content_type="application/json")
                    else:
                        error_msg = 'Cuenta deshabilitada'
                        print error_msg
                        error['codigo'] = '22'
                        error['mensaje'] = error_msg
                        return HttpResponse(json.dumps(error), status=401, content_type="application/json")
                else:
                    # the authentication system was unable to verify the username and password
                    error_msg = 'Usuario o password incorrecto'
                    print error_msg
                    error['codigo'] = '21'
                    error['mensaje'] = error_msg
                    return HttpResponse(json.dumps(error), status=401, content_type="application/json")
        except MultiValueDictKeyError:
            error_msg = 'Sintaxis del request incorrecta'
            print error_msg
            error['codigo'] = '11'
            error['mensaje'] = error_msg
            return HttpResponseBadRequest(json.dumps(error), content_type="application/json")
        except Exception, error2:
            print error2
            if error2.message == 'Transaccion matching query does not exist.':
                error_msg = 'Transaccion no encontrada'
                print error_msg
                error['codigo'] = codigo_base_error_reversion + '46'
                error['mensaje'] = error_msg
                return HttpResponse(json.dumps(error), status=404, content_type="application/json")
            elif error2.message == 'Venta matching query does not exist.':
                error_msg = 'No se encontro la venta'
                print error_msg
                error['codigo'] = codigo_base_error_reversion + '48'
                error['mensaje'] = error_msg
                return HttpResponse(json.dumps(error), status=404, content_type="application/json")
            error['codigo'] = '00'
            error['mensaje'] = 'Error en el servidor'

            return HttpResponseServerError(json.dumps(error), content_type="application/json")
    else:
        respuesta = {'mensaje': 'Conexion Exitosa', 'codigo': '200'}
        return HttpResponse(json.dumps(respuesta), content_type="application/json")
