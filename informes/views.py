# -*- encoding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template import RequestContext, loader
from principal.models import Propietario, Fraccion, Lote, Manzana, PagoDeCuotas, Venta, Reserva, CambioDeLotes, \
    RecuperacionDeLotes, TransferenciaDeLotes, Factura, Transaccion, Vendedor
from operator import itemgetter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from datetime import datetime, timedelta, date
from datetime import datetime, timedelta, date
from django.core.urlresolvers import reverse, resolve
from calendar import monthrange
from principal.common_functions import get_nro_cuota
import json
from django.db import connection
import xlwt
import math
from principal.common_functions import *
from principal.excel_styles import *
from principal import permisos
from operator import itemgetter, attrgetter
from django.utils.datastructures import MultiValueDictKeyError
# Funcion principal del modulo de lotes.
from sucursal.models import Sucursal
import calendar
from django.utils import timezone


def informes(request):
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_OPCIONES):
            t = loader.get_template('informes/index.html')
            c = RequestContext(request, {})
            return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo = request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))


def lotes_libres(request):
    if request.method == 'GET':
        if request.user.is_authenticated():  # AUTENTICACION
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):  # PERMISOS DEL USUARIO
                sucursales = Sucursal.objects.all()
                t = loader.get_template('informes/lotes_libres.html')

                if (filtros_establecidos(request.GET, 'lotes_libres') == False):
                    c = RequestContext(request, {
                        'object_list': [],
                        'sucursales': sucursales
                    })
                    return HttpResponse(t.render(c))
                else:
                    # PARAMETROS SETEADOS, REALIZAMOS LA BUSQUEDA
                    # SE OBTIENEN LOS PARAMETROS
                    sucursal_id = request.GET['sucursal']
                    fracciones_a_exluir = request.GET.getlist('fracciones_excluir')
                    order_by = request.GET['order_by']
                    # SUCURSAL A BUSCAR
                    sucursal = Sucursal.objects.get(pk=sucursal_id)

                    lista_lotes_libres = obtener_lotes_disponbiles(sucursal, order_by, fracciones_a_exluir)
                    # SE OBTIENE LA LISTA DE OBJETOS A MOSTRAR

                    if (request.GET['formato_reporte'] == "pantalla"):

                        # TODO: Paginacion y ordenamiento

                        c = RequestContext(request, {
                            'sucursal': sucursal,
                            'lista_lotes': lista_lotes_libres,
                            'sucursales': sucursales,
                            'fracciones_excluidas': fracciones_a_exluir,
                            'fracciones_excluidas_json': json.dumps(fracciones_a_exluir)
                        })
                        return HttpResponse(t.render(c))

                    elif request.GET['formato_reporte'] == "excel":

                        wb = xlwt.Workbook(encoding='utf-8')
                        sheet = wb.add_sheet('Lotes_libres', cell_overwrite_ok=True)
                        sheet.paper_size_code = 1

                        usuario = unicode(request.user)
                        sheet.header_str = (
                            u"&L&8Fecha: &D Hora: &T \nUsuario: " + usuario + " "
                                                                              u"&C&8PROPAR S.R.L.\n LOTES LIBRES "
                                                                              u"&R&8Sucursal: " + sucursal.nombre + " \nPage &P of &N"
                        )
                        sheet.footer_str = ''  # sheet.footer_str = 'things'

                        c = 0
                        sheet.write_merge(c, c, 0, 7, "Lotes Libres", style_titulo_resumen_centrado)
                        # contador de filas

                        for lote in lista_lotes_libres:
                            c += 1
                            try:
                                if lote['total_importe_cuotas'] and lote['ultimo_lote'] == False:
                                    c += 1
                                    sheet.write_merge(c, c, 0, 4, "Cantidad de Lotes libres de la fraccion: " + unicode(
                                        lote['total_lotes']), style_normal)
                            except Exception, error:
                                print error
                                pass

                            try:
                                lote['misma_fraccion']
                                if lote['misma_fraccion'] == False:
                                    sheet.write_merge(c, c, 0, 4, "Fraccion: " + unicode(lote['fraccion']),
                                                      style_titulos_columna_resaltados_centrados)
                                    c += 1
                                    sheet.write(c, 0, "Lote Nro.", style_normal)
                                    sheet.write(c, 1, "Superficie", style_normal)
                                    sheet.write(c, 2, "Precio Contado", style_normal)
                                    sheet.write(c, 3, "Precio Credito", style_normal)
                                    sheet.write(c, 4, "Precio Cuota", style_normal)
                                    c += 1
                            except Exception, error:
                                print error
                                pass

                            sheet.write(c, 0, lote['lote'], style_normal)
                            sheet.write(c, 1, unicode(lote['superficie']) + ' mts2', style_normal)
                            sheet.write(c, 2, lote['precio_contado'], style_normal)
                            sheet.write(c, 3, lote['precio_credito'], style_normal)
                            sheet.write(c, 4, lote['importe_cuota'], style_normal)

                            try:
                                if lote['ultimo_lote'] == True:
                                    c += 1
                                    sheet.write_merge(c, c, 0, 4, "Cantidad de Lotes libres de la fraccion: " + unicode(
                                        lote['total_lotes']), style_normal)
                                    '''
                                    sheet.write(c, 3, lote['total_superficie_fraccion'], style2)
                                    sheet.write(c, 4, lote['total_contado_fraccion'], style2)
                                    sheet.write(c, 5, lote['total_credito_fraccion'], style2)
                                    sheet.write(c, 6, lote['total_importe_cuotas'], style2)
                                    '''
                                if lote['total_general_cuotas']:
                                    c += 1
                                    sheet.write_merge(c, c, 0, 4, "Cantidad total de Lotes libres: " + unicode(
                                        lote['total_general_lotes']), style_normal)
                                    '''
                                    sheet.write(c, 3, lote['total_general_superficie'], style2)
                                    sheet.write(c, 4, lote['total_general_contado'], style2)
                                    sheet.write(c, 5, lote['total_general_credito'], style2)
                                    sheet.write(c, 6, lote['total_general_cuotas'], style2)
                                    '''
                            except Exception, error:
                                print error
                                pass
                        response = HttpResponse(content_type='application/vnd.ms-excel')
                        # Crear un nombre intuitivo
                        fecha_actual = datetime.datetime.now().date()
                        fecha_str = unicode(fecha_actual)
                        fecha = unicode(datetime.datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                        response[
                            'Content-Disposition'] = 'attachment; filename=' + 'lotes_libres_sucursal' + sucursal.nombre + '_' + fecha + '.xls'
                        wb.save(response)
                        return response
                        #
            else:
                t = loader.get_template('index2.html')
                grupo = request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))
        else:
            return HttpResponseRedirect(reverse('login'))

    else:
        t = loader.get_template('informes/lotes_libres.html')
        c = RequestContext(request, {
            # 'object_list': lista,
            # 'fraccion': f,
        })
        return HttpResponse(t.render(c))


# def lotes_libres(request):
#     if request.method == 'GET':
#         if request.user.is_authenticated():
#             if verificar_permisos(request.user.id, permisos.VER_INFORMES):
#                 sucursales = Sucursal.objects.all()
#                 if (filtros_establecidos(request.GET, 'lotes_libres') == False):
#                     t = loader.get_template('informes/lotes_libres.html')
#                     c = RequestContext(request, {
#                         'object_list': [],
#                         'sucursales': sucursales
#                     })
#                     return HttpResponse(t.render(c))
#                 else:  # Parametros seteados
#                     tipo_busqueda = request.GET['tipo_busqueda']
#                     t = loader.get_template('informes/lotes_libres.html')
#                     fraccion_ini = request.GET['frac1']
#                     fraccion_fin = request.GET['frac2']
#                     f1 = request.GET['fraccion_ini']
#                     f2 = request.GET['fraccion_fin']
#                     ultimo = "&tipo_busqueda=" + tipo_busqueda + "&fraccion_ini=" + f1 + "&frac1=" + fraccion_ini + "&fraccion_fin=" + f2 + "&frac2=" + fraccion_fin
#                     object_list = []  # lista de lotes
#                     if fraccion_ini and fraccion_fin:
#                         manzanas = Manzana.objects.filter(fraccion_id__range=(fraccion_ini, fraccion_fin)).order_by(
#                             'fraccion', 'nro_manzana')
#                         for m in manzanas:
#                             lotes = Lote.objects.filter(manzana=m.id, estado="1").order_by('nro_lote')
#                             for l in lotes:
#                                 object_list.append(l)
#                     else:
#                         object_list = Lote.objects.filter(estado="1").order_by('nro_lote')
#
#                     lotes = []
#                     total_importe_cuotas = 0
#                     total_contado_fraccion = 0
#                     total_credito_fraccion = 0
#                     total_superficie_fraccion = 0
#                     total_lotes_fraccion = 0
#                     total_general_lotes = 0
#                     misma_fraccion = True
#                     for index, lote_item in enumerate(object_list):
#                         lote = {}
#                         # Se setean los datos de cada fila
#                         if misma_fraccion == True:
#                             misma_fraccion = False
#                             lote['misma_fraccion'] = misma_fraccion
#                         precio_cuota = int(math.ceil(lote_item.precio_credito / 130))
#                         lote['fraccion_id'] = unicode(lote_item.manzana.fraccion.id)
#                         lote['fraccion'] = unicode(lote_item.manzana.fraccion)
#                         lote['lote'] = unicode(lote_item.manzana).zfill(3) + "/" + unicode(lote_item.nro_lote).zfill(4)
#                         lote['superficie'] = lote_item.superficie
#                         lote['precio_contado'] = unicode('{:,}'.format(lote_item.precio_contado)).replace(",", ".")
#                         lote['precio_credito'] = unicode('{:,}'.format(lote_item.precio_credito)).replace(",", ".")
#                         lote['importe_cuota'] = unicode('{:,}'.format(precio_cuota)).replace(",", ".")
#                         lote['id'] = lote_item.id
#                         lote['ultimo_registro'] = False
#                         # ESTEEE
#                         # Se suman los TOTALES por FRACCION
#                         total_superficie_fraccion += lote_item.superficie
#                         total_contado_fraccion += lote_item.precio_contado
#                         total_credito_fraccion += lote_item.precio_credito
#                         total_importe_cuotas += precio_cuota
#                         total_lotes_fraccion += 1
#                         total_general_lotes += 1
#                         # Es el ultimo lote, cerrar totales de fraccion
#                         if (len(object_list) - 1 == index):
#                             lote['total_importe_cuotas'] = unicode('{:,}'.format(total_importe_cuotas)).replace(",",
#                                                                                                                 ".")
#                             lote['total_credito_fraccion'] = unicode('{:,}'.format(total_credito_fraccion)).replace(",",
#                                                                                                                     ".")
#                             lote['total_contado_fraccion'] = unicode('{:,}'.format(total_contado_fraccion)).replace(",",
#                                                                                                                     ".")
#                             lote['total_superficie_fraccion'] = unicode(
#                                 '{:,}'.format(total_superficie_fraccion)).replace(",", ".")
#                             lote['total_lotes'] = unicode('{:,}'.format(total_lotes_fraccion)).replace(",", ".")
#                             lote['total_general_lotes'] = unicode('{:,}'.format(total_general_lotes)).replace(",", ".")
#                             lote['ultimo_registro'] = True
#
#                             # Hay cambio de fraccion pero NO es el ultimo elemento todavia
#                         elif (lote_item.manzana.fraccion.id != object_list[index + 1].manzana.fraccion.id):
#                             lote['total_importe_cuotas'] = unicode('{:,}'.format(total_importe_cuotas)).replace(",",
#                                                                                                                 ".")
#                             lote['total_credito_fraccion'] = unicode('{:,}'.format(total_credito_fraccion)).replace(",",
#                                                                                                                     ".")
#                             lote['total_contado_fraccion'] = unicode('{:,}'.format(total_contado_fraccion)).replace(",",
#                                                                                                                     ".")
#                             lote['total_superficie_fraccion'] = unicode(
#                                 '{:,}'.format(total_superficie_fraccion)).replace(",", ".")
#                             lote['total_lotes'] = unicode('{:,}'.format(total_lotes_fraccion)).replace(",", ".")
#                             # Se CERAN  los TOTALES por FRACCION
#                             total_importe_cuotas = 0
#                             total_contado_fraccion = 0
#                             total_credito_fraccion = 0
#                             total_superficie_fraccion = 0
#                             total_lotes_fraccion = 0
#                             misma_fraccion = True
#
#                         lotes.append(lote)
#                     # sin paginacion
#                     lista = lotes
#                     # cantidad de registros a mostrar, determinada por el usuario
#                     #                     try:
#                     #                         cant_reg = request.GET['cant_reg']
#                     #                         if cant_reg=='todos':
#                     #                             paginator = Paginator(lotes, len(lotes))
#                     #                         else:
#                     #                             p=range(int(cant_reg))
#                     #                             paginator = Paginator(lotes, len(p))
#                     #                     except:
#                     #                         cant_reg=25
#                     #                         paginator = Paginator(lotes, 25)
#                     #
#                     #                     page = request.GET.get('page')
#                     #                     try:
#                     #                         lista = paginator.page(page)
#                     #                     except PageNotAnInteger:
#                     #                         lista = paginator.page(1)
#                     #                     except EmptyPage:
#                     #                         lista = paginator.page(paginator.num_pages)
#
#                     c = RequestContext(request, {
#                         'tipo_busqueda': tipo_busqueda,
#                         'fraccion_ini': fraccion_ini,
#                         'fraccion_fin': fraccion_fin,
#                         'ultimo': ultimo,
#                         'lista_lotes': lista,
#                         # 'cant_reg':cant_reg,
#                         'frac1': f1,
#                         'frac2': f2,
#                         'sucursales': sucursales
#                     })
#                     return HttpResponse(t.render(c))
#             else:
#                 t = loader.get_template('index2.html')
#                 grupo = request.user.groups.get().id
#                 c = RequestContext(request, {
#                     'grupo': grupo
#                 })
#                 return HttpResponse(t.render(c))
#         else:
#             return HttpResponseRedirect(reverse('login'))
#
#     else:
#         t = loader.get_template('informes/lotes_libres.html')
#         c = RequestContext(request, {
#             # 'object_list': lista,
#             # 'fraccion': f,
#         })
#         return HttpResponse(t.render(c))

def listar_busqueda_lotes(request):
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_INFORMES):
            t = loader.get_template('informes/lotes_libres.html')
        else:
            t = loader.get_template('index2.html')
            grupo = request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))

    busqueda = request.POST['busqueda']
    if busqueda:
        x = unicode(busqueda)
        fraccion_int = int(x[0:3])
        manzana_int = int(x[4:7])
        lote_int = int(x[8:])
        manzana = Manzana.objects.get(fraccion_id=fraccion_int, nro_manzana=manzana_int)
        lote = Lote.objects.get(manzana=manzana.id, nro_lote=lote_int)
        object_list = Lote.objects.filter(pk=lote.id, estado="1").order_by('manzana', 'nro_lote')

    paginator = Paginator(object_list, 15)
    page = request.GET.get('page')
    try:
        lista = paginator.page(page)
    except PageNotAnInteger:
        lista = paginator.page(1)
    except EmptyPage:
        lista = paginator.page(paginator.num_pages)

    c = RequestContext(request, {
        'object_list': lista,
    })
    return HttpResponse(t.render(c))


def listar_clientes_atrasados(request):
    venta = request.GET['venta_id']
    cliente = request.GET['cliente_id']

    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_INFORMES):
            t = loader.get_template('informes/detalle_pagos_cliente.html')
        else:
            t = loader.get_template('index2.html')
            grupo = request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))

    if venta != '' and cliente != '':
        object_list = PagoDeCuotas.objects.filter(venta_id=venta, cliente_id=cliente).order_by('fecha_de_pago')
        a = len(object_list)
        if a > 0:
            for i in object_list:
                i.fecha_de_pago = i.fecha_de_pago.strftime("%d/%m/%Y")
                i.total_de_cuotas = unicode('{:,}'.format(i.total_de_cuotas)).replace(",", ".")
                i.total_de_mora = unicode('{:,}'.format(i.total_de_mora)).replace(",", ".")
                i.total_de_pago = unicode('{:,}'.format(i.total_de_pago)).replace(",", ".")

            paginator = Paginator(object_list, 15)
            page = request.GET.get('page')
            try:
                lista = paginator.page(page)
            except PageNotAnInteger:
                lista = paginator.page(1)
            except EmptyPage:
                lista = paginator.page(paginator.num_pages)
            c = RequestContext(request, {
                'object_list': lista,
            })
            return HttpResponse(t.render(c))
        else:
            c = RequestContext(request, {
                'object_list': object_list,
            })
            return HttpResponse(t.render(c))
    else:
        # return HttpResponseRedirect("/informes/clientes_atrasados")
        return HttpResponseRedirect(reverse('frontend_clientes_atrasados'))


def obtener_clientes_con_lotes_por_vencer(fraccion, fecha_inicio, fecha_fin):

    # OBJETO QUE SE UTILIZA PARA CARGAR TODOS LOS CLIENTES QUE TENGAN LOTES POR VENCER
    listado_clientes = []

    formato_fecha = "%d/%m/%Y"
    fecha_inicial = datetime.datetime.strptime(fecha_inicio, formato_fecha)
    fecha_final = datetime.datetime.strptime(fecha_fin,
                                             formato_fecha)

    # QUERY PARA TRAER TODOS LOS LOTES DE LA FRACCION EN CUESTION
    query = (
        '''
        SELECT lote.* FROM principal_fraccion fraccion, principal_manzana manzana, principal_lote lote WHERE manzana.id = lote.manzana_id AND manzana.fraccion_id = fraccion.id
        '''
    )

    # FILTROS:
    #     NI FRACCION NI MESES DE ATRASO SETEADOS
    #          RETURN 0
    #     FRACCION SETEADA PERO MESES DE ATRASO NO
    #         RETURN 1
    #     FRACCION NO SETEADA PERO SI MESES DE ATRASO
    #         return 2
    #     AMBOS SETEADOS
    #         RETURN 3

    if fraccion != '':
        query += " AND  fraccion.id =  %s "
        query += " ORDER BY codigo_paralot "
        cursor = connection.cursor()
        cursor.execute(query, [fraccion])

        # Por ultimo, traemos ordenados los registros por el CODIGO DE LOTE
    #    query += " ORDER BY codigo_paralot "

    # try:
    results = cursor.fetchall()  # LOTES

    for r in results:  # RECORREMOS TODOS LOS LOTES DE LA FRACCION

        cliente_atrasado = {}

        cuotas_a_pagar = []
        # OBTENER LA ULTIMA VENTA Y SU DETALLE
        ultima_venta = get_ultima_venta_no_recuperada(r[0])

        # SE TRATAN LOS CASOS EN DONDE NO SE ENCUENTRA VENTA PARA ALGUN LOTE.
        if ultima_venta != None:
            #obtenemos el detalle
            #detalle = get_cuotas_detail_by_lote2(unicode(str(r[0])), fecha_inicio, fecha_fin)
            detalle_cuotas = get_cuotas_detail_by_lote(unicode(str(r[0])))
            #obtenemos la fecha de vencimiento

            hoy = date.today()
            try:
                cuotas_a_pagar = obtener_cuotas_a_pagar_full(ultima_venta, hoy, detalle_cuotas,
                                                             500)  # Maximo atraso = 500 para tener un parametro maximo de atraso en las cuotas.
            except Exception, e:
                print e

            #obtenemos del proximo vencimiento
            venc = datetime.datetime.strptime(detalle_cuotas['proximo_vencimiento'], formato_fecha)

            #hacemos la comparacion para saber si la proxima fecha de vencimiento
            #se encuentra en el rango
            if ( (fecha_inicial)<=(venc)):
                if( (venc) <= (fecha_final)):

                    # cuotas_atrasadas = detalle_cuotas['cantidad_total_cuotas'] - detalle_cuotas['cant_cuotas_pagadas'];  # CUOTAS ATRASADAS
                    if len(cuotas_a_pagar) > 1:
                        cuotas_atrasadas = len(cuotas_a_pagar) - 1
                    else:
                        cuotas_atrasadas = len(cuotas_a_pagar)

                    cantidad_cuotas_pagadas = detalle_cuotas['cant_cuotas_pagadas'];  # CUOTAS PAGADAS

                    # DATOS DEL CLIENTE
                    cliente_atrasado['cliente'] = ultima_venta.cliente.nombres + ' ' + ultima_venta.cliente.apellidos
                    cliente_atrasado['direccion_particular'] = ultima_venta.cliente.direccion_particular
                    cliente_atrasado['direccion_cobro'] = ultima_venta.cliente.direccion_cobro
                    cliente_atrasado['telefono_particular'] = ultima_venta.cliente.telefono_particular
                    cliente_atrasado['telefono_laboral'] = ultima_venta.cliente.telefono_laboral
                    cliente_atrasado['celular_1'] = ultima_venta.cliente.celular_1
                    cliente_atrasado['celular_2'] = ultima_venta.cliente.celular_2

                    # FECHA ULTIMO PAGO
                    if (len(PagoDeCuotas.objects.filter(venta_id=ultima_venta.id).order_by('-fecha_de_pago')) > 0):
                            fecha_ultimo_pago = \
                            PagoDeCuotas.objects.filter(venta_id=ultima_venta.id).order_by('-fecha_de_pago')[0].fecha_de_pago

                            cliente_atrasado['fecha_ultimo_pago'] = fecha_ultimo_pago.strftime(formato_fecha)
                    else:
                        cliente_atrasado['fecha_ultimo_pago'] = 'Dato no disponible'

                    cliente_atrasado['proximo_vencimiento'] = detalle_cuotas['proximo_vencimiento']

                    cliente_atrasado['lote'] = ultima_venta.lote.codigo_paralot

                    # IMPORTE CUOTA
                    cliente_atrasado['importe_cuota'] = unicode('{:,}'.format(ultima_venta.precio_de_cuota)).replace(",", ".")

                    # CUOTAS ATRASADAS
                    cliente_atrasado['cuotas_atrasadas'] = unicode('{:,}'.format(cuotas_atrasadas)).replace(",", ".")

                    # TOTAL ATRASO
                    total_atrasado = cuotas_atrasadas * ultima_venta.precio_de_cuota;
                    cliente_atrasado['total_atrasado'] = unicode('{:,}'.format(total_atrasado)).replace(",", ".")

                    # CUOTAS PAGADAS
                    cuotas_pagadas = unicode('{:,}'.format(cantidad_cuotas_pagadas)).replace(",", ".") + '/' + unicode(
                        '{:,}'.format(detalle_cuotas['cantidad_total_cuotas'])).replace(",", ".")
                    cliente_atrasado['cuotas_pagadas'] = cuotas_pagadas

                    # TOTAL PAGADO
                    total_pagado = cantidad_cuotas_pagadas * ultima_venta.precio_de_cuota;
                    cliente_atrasado['total_pagado'] = unicode('{:,}'.format(total_pagado)).replace(",", ".")

                    if(detalle_cuotas['cantidad_total_cuotas'] == 0):
                        porcentaje_pagado = 0
                    else:
                        porcentaje_pagado = round(
                            (float(cantidad_cuotas_pagadas) / float(detalle_cuotas['cantidad_total_cuotas'])) * 100);

                    cliente_atrasado['porc_pagado'] = unicode('{:,}'.format(int(porcentaje_pagado))).replace(",", ".") + '%'

                    proximo_vencimiento_parsed = datetime.datetime.strptime(detalle_cuotas['proximo_vencimiento'],
                                                                            "%d/%m/%Y").date()
                    detalles = obtener_detalle_interes_lote(unicode(ultima_venta.lote_id), hoy, proximo_vencimiento_parsed,
                                                            cuotas_atrasadas)
                    total_interes = 0
                    total_cobranza = 0
                    for detalle in detalles:
                        if 'intereses' in detalle:
                            total_interes += detalle['intereses']
                        if 'gestion_cobranza' in detalle:
                            total_cobranza = detalle['gestion_cobranza']
                    cliente_atrasado['intereses'] = unicode('{:,}'.format(total_interes)).replace(",", ".")
                    cliente_atrasado['gestion_cobranza'] = unicode('{:,}'.format(total_cobranza)).replace(",", ".")
                    listado_clientes.append(cliente_atrasado)

    return listado_clientes


def obtener_clientes_atrasados(filtros, fraccion, meses_peticion):
    # OBJETO QUE SE UTILIZA PARA CARGAR TODOS LOS CLIENTES ATRASADOS A MOSTRAR
    clientes_atrasados = []

    # QUERY PARA TRAER TODOS LOS LOTES DE LA FRACCION EN CUESTION
    query = (
        '''
        SELECT lote.* FROM principal_fraccion fraccion, principal_manzana manzana, principal_lote lote WHERE manzana.id = lote.manzana_id AND manzana.fraccion_id = fraccion.id
        '''
    )

    # FILTROS:
    #     NI FRACCION NI MESES DE ATRASO SETEADOS
    #          RETURN 0
    #     FRACCION SETEADA PERO MESES DE ATRASO NO
    #         RETURN 1
    #     FRACCION NO SETEADA PERO SI MESES DE ATRASO
    #         return 2
    #     AMBOS SETEADOS
    #         RETURN 3

    if filtros == 0:
        return []
    elif filtros == 1:
        query += " AND  fraccion.id =  %s "
        query += " ORDER BY codigo_paralot "
        cursor = connection.cursor()
        cursor.execute(query, [fraccion])
    elif filtros == 2:
        query += " ORDER BY codigo_paralot "
        cursor = connection.cursor()
        cursor.execute(query, [meses_peticion])
    else:
        query += " AND fraccion.id =  %s"
        query += " ORDER BY codigo_paralot "
        cursor = connection.cursor()
        cursor.execute(query, [fraccion])

        # Por ultimo, traemos ordenados los registros por el CODIGO DE LOTE
    #    query += " ORDER BY codigo_paralot "

    # try:
    results = cursor.fetchall()  # LOTES

    for r in results:  # RECORREMOS TODOS LOS LOTES DE LA FRACCION

        cliente_atrasado = {}

        formato_fecha = "%d/%m/%Y"

        cuotas_a_pagar = []
        # OBTENER LA ULTIMA VENTA Y SU DETALLE
        ultima_venta = get_ultima_venta_no_recuperada(r[0])

        # SE TRATAN LOS CASOS EN DONDE NO SE ENCUENTRA VENTA PARA ALGUN LOTE.
        if ultima_venta != None:
            detalle_cuotas = get_cuotas_detail_by_lote(unicode(str(r[0])))
            hoy = date.today()
            try:
                cuotas_a_pagar = obtener_cuotas_a_pagar_full(ultima_venta, hoy, detalle_cuotas,
                                                         500)  # Maximo atraso = 500 para tener un parametro maximo de atraso en las cuotas.
            except Exception, e:
                print e


        if (len(cuotas_a_pagar) >= meses_peticion + 1):

            # cuotas_atrasadas = detalle_cuotas['cantidad_total_cuotas'] - detalle_cuotas['cant_cuotas_pagadas'];  # CUOTAS ATRASADAS
            if len(cuotas_a_pagar) > 1:
                cuotas_atrasadas = len(cuotas_a_pagar) - 1
            else:
                cuotas_atrasadas = len(cuotas_a_pagar)
                
            cantidad_cuotas_pagadas = detalle_cuotas['cant_cuotas_pagadas'];  # CUOTAS PAGADAS

            # DATOS DEL CLIENTE
            cliente_atrasado['cliente'] = ultima_venta.cliente.nombres + ' ' + ultima_venta.cliente.apellidos
            cliente_atrasado['direccion_particular'] = ultima_venta.cliente.direccion_particular
            cliente_atrasado['direccion_cobro'] = ultima_venta.cliente.direccion_cobro
            cliente_atrasado['telefono_particular'] = ultima_venta.cliente.telefono_particular
            cliente_atrasado['telefono_laboral'] = ultima_venta.cliente.telefono_laboral
            cliente_atrasado['celular_1'] = ultima_venta.cliente.celular_1
            cliente_atrasado['celular_2'] = ultima_venta.cliente.celular_2

            # FECHA ULTIMO PAGO
            if (len(PagoDeCuotas.objects.filter(venta_id=ultima_venta.id).order_by('-fecha_de_pago')) > 0):
                fecha_ultimo_pago = \
                    PagoDeCuotas.objects.filter(venta_id=ultima_venta.id).order_by('-fecha_de_pago')[0].fecha_de_pago

                cliente_atrasado['fecha_ultimo_pago'] = fecha_ultimo_pago.strftime(formato_fecha)
            else:
                cliente_atrasado['fecha_ultimo_pago'] = 'Dato no disponible'

            cliente_atrasado['lote'] = ultima_venta.lote.codigo_paralot

            cliente_atrasado['codigo_lote'] = ultima_venta.lote.id

            if ultima_venta.lote.mejora != None:
                cliente_atrasado['lote_mejora'] = ultima_venta.lote.mejora.descripcion
            else:
               cliente_atrasado['lote_mejora'] = "NO"

            if ultima_venta.lote.demanda != None:
                cliente_atrasado['lote_demanda'] = ultima_venta.lote.demanda
            else:
                cliente_atrasado['lote_demanda'] = "NO"

            # IMPORTE CUOTA
            cliente_atrasado['importe_cuota'] = unicode('{:,}'.format(ultima_venta.precio_de_cuota)).replace(",", ".")

            # CUOTAS ATRASADAS
            cliente_atrasado['cuotas_atrasadas'] = unicode('{:,}'.format(cuotas_atrasadas)).replace(",", ".")

            # TOTAL ATRASO
            total_atrasado = cuotas_atrasadas * ultima_venta.precio_de_cuota;
            cliente_atrasado['total_atrasado'] = unicode('{:,}'.format(total_atrasado)).replace(",", ".")

            # CUOTAS PAGADAS
            cuotas_pagadas = unicode('{:,}'.format(cantidad_cuotas_pagadas)).replace(",", ".") + '/' + unicode(
                '{:,}'.format(detalle_cuotas['cantidad_total_cuotas'])).replace(",", ".")
            cliente_atrasado['cuotas_pagadas'] = cuotas_pagadas

            # TOTAL PAGADO
            total_pagado = cantidad_cuotas_pagadas * ultima_venta.precio_de_cuota;
            cliente_atrasado['total_pagado'] = unicode('{:,}'.format(total_pagado)).replace(",", ".")

            porcentaje_pagado = round(
                (float(cantidad_cuotas_pagadas) / float(detalle_cuotas['cantidad_total_cuotas'])) * 100);
            cliente_atrasado['porc_pagado'] = unicode('{:,}'.format(int(porcentaje_pagado))).replace(",", ".") + '%'

            proximo_vencimiento_parsed = datetime.datetime.strptime(detalle_cuotas['proximo_vencimiento'],
                                                                    "%d/%m/%Y").date()
            detalles = obtener_detalle_interes_lote(unicode(ultima_venta.lote_id), hoy, proximo_vencimiento_parsed,
                                                    cuotas_atrasadas)
            total_interes = 0
            total_cobranza = 0
            for detalle in detalles:
                if 'intereses' in detalle:
                    total_interes += detalle['intereses']
                if 'gestion_cobranza' in detalle:
                    total_cobranza = detalle['gestion_cobranza']
            cliente_atrasado['intereses'] = unicode('{:,}'.format(total_interes)).replace(",", ".")
            cliente_atrasado['gestion_cobranza'] = unicode('{:,}'.format(total_cobranza)).replace(",", ".")
            clientes_atrasados.append(cliente_atrasado)

    return clientes_atrasados


def obtener_deudores_por_venta(filtros, fraccion, meses_peticion):
    # OBJETO QUE SE UTILIZA PARA CARGAR TODOS LOS CLIENTES ATRASADOS A MOSTRAR
    deudores_por_venta = []

    # QUERY PARA TRAER TODOS LOS LOTES DE LA FRACCION EN CUESTION
    query = (
        '''
        SELECT lote.* FROM principal_fraccion fraccion, principal_manzana manzana, principal_lote lote WHERE manzana.id = lote.manzana_id AND manzana.fraccion_id = fraccion.id
        '''
    )

    query += " AND  fraccion.id =  %s "
    query += " ORDER BY codigo_paralot "
    cursor = connection.cursor()
    cursor.execute(query, [fraccion])
    ventas_al_contado = 0

    # Por ultimo, traemos ordenados los registros por el CODIGO DE LOTE
    # query += " ORDER BY codigo_paralot "

    # try:
    results = cursor.fetchall()  # LOTES

    for r in results:  # RECORREMOS TODOS LOS LOTES DE LA FRACCION

        deudor_por_venta = {}
        deudor_por_venta['cuotas_devengadas'] = 0

        # OBTENER LA ULTIMA VENTA Y SU DETALLE
        ultima_venta = get_ultima_venta_no_recuperada(r[0])

        # SE TRATAN LOS CASOS EN DONDE NO SE ENCUENTRA VENTA PARA ALGUN LOTE.
        if ultima_venta != None:
            detalle_cuotas = get_cuotas_detail_by_lote(unicode(str(r[0])))
            hoy = date.today()
            cuotas_a_pagar = obtener_cuotas_a_pagar_full(ultima_venta, hoy, detalle_cuotas,
                                                         500)  # Maximo atraso = 500 para tener un parametro maximo de atraso en las cuotas.
            if len(cuotas_a_pagar) == 0:
                ventas_al_contado += 1
            # aqui para saber cuanto esta debiendo por cuotas atrasadas, vamos a recorrer las cuotas que faltan por pagar, e ir preguntando si la prox fecha de vto, mes
            # a mes todavia es menor a la fecha actual, si es asi, vamos aumentado la cuota
            if detalle_cuotas != None:
                if detalle_cuotas['cant_cuotas_pagadas'] != detalle_cuotas['cantidad_total_cuotas']:
                    prox_vto_date_parsed = datetime.datetime.strptime(unicode(detalle_cuotas['proximo_vencimiento']),
                                                                      '%d/%m/%Y').date()
                    for x in xrange(detalle_cuotas['cantidad_total_cuotas'] - detalle_cuotas['cant_cuotas_pagadas']):
                        if prox_vto_date_parsed < datetime.datetime.now().date():
                            deudor_por_venta['cuotas_devengadas'] = deudor_por_venta[
                                                                        'cuotas_devengadas'] + ultima_venta.precio_de_cuota
                        prox_vto_date_parsed = add_months(prox_vto_date_parsed, 1)


        else:
            cuotas_a_pagar = []

        deudor_por_venta['cuotas_devengadas'] = unicode('{:,}'.format(deudor_por_venta['cuotas_devengadas'])).replace(
            ",", ".")
        if (len(cuotas_a_pagar) >= meses_peticion + 1):

            cuotas_atrasadas = detalle_cuotas['cantidad_total_cuotas'] - detalle_cuotas[
                'cant_cuotas_pagadas'];  # CUOTAS ATRASADAS
            cantidad_cuotas_pagadas = detalle_cuotas['cant_cuotas_pagadas'];  # CUOTAS PAGADAS

            # DATOS DEL CLIENTE
            deudor_por_venta['cliente'] = ultima_venta.cliente.nombres + ' ' + ultima_venta.cliente.apellidos
            deudor_por_venta['direccion_particular'] = ultima_venta.cliente.direccion_particular
            deudor_por_venta['direccion_cobro'] = ultima_venta.cliente.direccion_cobro
            deudor_por_venta['telefono_particular'] = ultima_venta.cliente.telefono_particular
            deudor_por_venta['telefono_laboral'] = ultima_venta.cliente.telefono_laboral
            deudor_por_venta['celular_1'] = ultima_venta.cliente.celular_1
            deudor_por_venta['celular_2'] = ultima_venta.cliente.celular_2

            deudor_por_venta['lote'] = ultima_venta.lote.codigo_paralot

            # FECHA VENTA
            if (ultima_venta.fecha_de_venta != None):
                deudor_por_venta['fecha_venta'] = ultima_venta.fecha_de_venta
            else:
                deudor_por_venta['fecha_venta'] = 'Dato no disponible'

            deudor_por_venta['lote'] = ultima_venta.lote.codigo_paralot

            # IMPORTE CUOTA
            deudor_por_venta['importe_cuota'] = unicode('{:,}'.format(ultima_venta.precio_de_cuota)).replace(",", ".")

            # CUOTAS ATRASADAS
            deudor_por_venta['cuotas_atrasadas'] = unicode('{:,}'.format(cuotas_atrasadas)).replace(",", ".")

            # TOTAL ATRASO
            total_atrasado = cuotas_atrasadas * ultima_venta.precio_de_cuota;
            deudor_por_venta['total_atrasado'] = unicode('{:,}'.format(total_atrasado)).replace(",", ".")

            # CUOTAS PAGADAS
            cuotas_pagadas = unicode('{:,}'.format(cantidad_cuotas_pagadas)).replace(",", ".") + '/' + unicode(
                '{:,}'.format(detalle_cuotas['cantidad_total_cuotas'])).replace(",", ".")
            deudor_por_venta['cuotas_pagadas'] = cuotas_pagadas

            # TOTAL PAGADO
            total_pagado = cantidad_cuotas_pagadas * ultima_venta.precio_de_cuota;
            deudor_por_venta['total_pagado'] = unicode('{:,}'.format(total_pagado)).replace(",", ".")
            deudores_por_venta.append(deudor_por_venta)
        if ultima_venta != None:
            if ultima_venta.plan_de_pago.tipo_de_plan == "contado":

                # DATOS DEL CLIENTE
                deudor_por_venta['cliente'] = ultima_venta.cliente.nombres + ' ' + ultima_venta.cliente.apellidos
                deudor_por_venta['direccion_particular'] = ultima_venta.cliente.direccion_particular
                deudor_por_venta['direccion_cobro'] = ultima_venta.cliente.direccion_cobro
                deudor_por_venta['telefono_particular'] = ultima_venta.cliente.telefono_particular
                deudor_por_venta['telefono_laboral'] = ultima_venta.cliente.telefono_laboral
                deudor_por_venta['celular_1'] = ultima_venta.cliente.celular_1
                deudor_por_venta['celular_2'] = ultima_venta.cliente.celular_2

                deudor_por_venta['lote'] = ultima_venta.lote.codigo_paralot

                # FECHA VENTA
                if (ultima_venta.fecha_de_venta != None):
                    deudor_por_venta['fecha_venta'] = ultima_venta.fecha_de_venta
                else:
                    deudor_por_venta['fecha_venta'] = 'Dato no disponible'

                deudor_por_venta['lote'] = ultima_venta.lote.codigo_paralot

                # IMPORTE CUOTA
                deudor_por_venta['importe_cuota'] = "0"

                # CUOTAS ATRASADAS
                deudor_por_venta['cuotas_atrasadas'] = "0"

                # TOTAL ATRASO
                deudor_por_venta['total_atrasado'] = "0"

                # CUOTAS PAGADAS
                deudor_por_venta['cuotas_pagadas'] = "Contado"

                # TOTAL PAGADO
                total_pagado = ultima_venta.precio_final_de_venta;
                deudor_por_venta['total_pagado'] = unicode('{:,}'.format(total_pagado)).replace(",", ".")
                deudores_por_venta.append(deudor_por_venta)

    print "ventas al contado:" + unicode(ventas_al_contado)
    return deudores_por_venta


def obtener_clientes_atrasados_del_dia():
    # OBJETO QUE SE UTILIZA PARA CARGAR TODOS LOS CLIENTES ATRASADOS EN LA FECHA ACTUAL A MOSTRAR
    clientes_atrasados = []

    # QUERY PARA TRAER TODOS LOS LOTES DE LA FRACCION EN CUESTION
    query = (
        '''
        SELECT lote.* FROM principal_fraccion fraccion, principal_manzana manzana, principal_lote lote WHERE manzana.id = lote.manzana_id AND manzana.fraccion_id = fraccion.id
        '''
    )

    query += " ORDER BY codigo_paralot "
    cursor = connection.cursor()
    cursor.execute(query)

    # try:
    results = cursor.fetchall()  # LOTES

    for r in results:  # RECORREMOS TODOS LOS LOTES DE LA FRACCION

        cliente_atrasado = {}

        # OBTENER LA ULTIMA VENTA Y SU DETALLE
        ultima_venta = get_ultima_venta_no_recuperada(r[0])

        # SE TRATAN LOS CASOS EN DONDE NO SE ENCUENTRA VENTA PARA ALGUN LOTE.
        if ultima_venta != None:
            detalle_cuotas = get_cuotas_detail_by_lote(unicode(str(r[0])))
            hoy = date.today()
            cuotas_a_pagar = obtener_cuotas_a_pagar_full(ultima_venta, hoy, detalle_cuotas,
                                                         500)  # Maximo atraso = 500 para tener un parametro maximo de atraso en las cuotas.
        else:
            cuotas_a_pagar = []

        if (len(cuotas_a_pagar) >= 0 + 1):

            cuotas_atrasadas = len(cuotas_a_pagar);  # CUOTAS ATRASADAS
            cantidad_cuotas_pagadas = detalle_cuotas['cant_cuotas_pagadas'];  # CUOTAS PAGADAS

            fecha_actual = datetime.datetime.now().date()
            fecha_str = unicode(fecha_actual)
            fecha = unicode(datetime.datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y"))

            if detalle_cuotas['proximo_vencimiento'] == fecha:
                # DATOS DEL CLIENTE
                cliente_atrasado['cliente'] = ultima_venta.cliente.nombres + ' ' + ultima_venta.cliente.apellidos
                cliente_atrasado['direccion_particular'] = ultima_venta.cliente.direccion_particular
                cliente_atrasado['direccion_cobro'] = ultima_venta.cliente.direccion_cobro
                cliente_atrasado['telefono_particular'] = ultima_venta.cliente.telefono_particular
                cliente_atrasado['celular_1'] = ultima_venta.cliente.celular_1

                # FECHA ULTIMO PAGO
                if (len(PagoDeCuotas.objects.filter(venta_id=ultima_venta.id).order_by('-fecha_de_pago')) > 0):
                    cliente_atrasado['fecha_ultimo_pago'] = \
                        PagoDeCuotas.objects.filter(venta_id=ultima_venta.id).order_by('-fecha_de_pago')[
                            0].fecha_de_pago
                else:
                    cliente_atrasado['fecha_ultimo_pago'] = 'Dato no disponible'

                cliente_atrasado['lote'] = ultima_venta.lote.codigo_paralot

                # IMPORTE CUOTA
                cliente_atrasado['importe_cuota'] = unicode('{:,}'.format(ultima_venta.precio_de_cuota)).replace(",",
                                                                                                                 ".")

                # CUOTAS ATRASADAS
                cliente_atrasado['cuotas_atrasadas'] = unicode('{:,}'.format(cuotas_atrasadas)).replace(",", ".")

                # TOTAL ATRASO
                total_atrasado = cuotas_atrasadas * ultima_venta.precio_de_cuota;
                cliente_atrasado['total_atrasado'] = unicode('{:,}'.format(total_atrasado)).replace(",", ".")

                # CUOTAS PAGADAS
                cuotas_pagadas = unicode('{:,}'.format(cantidad_cuotas_pagadas)).replace(",", ".") + '/' + unicode(
                    '{:,}'.format(detalle_cuotas['cantidad_total_cuotas'])).replace(",", ".")
                cliente_atrasado['cuotas_pagadas'] = cuotas_pagadas

                # TOTAL PAGADO
                total_pagado = cantidad_cuotas_pagadas * ultima_venta.precio_de_cuota;
                cliente_atrasado['total_pagado'] = unicode('{:,}'.format(total_pagado)).replace(",", ".")

                porcentaje_pagado = round(
                    (float(cantidad_cuotas_pagadas) / float(detalle_cuotas['cantidad_total_cuotas'])) * 100);
                cliente_atrasado['porc_pagado'] = unicode('{:,}'.format(int(porcentaje_pagado))).replace(",", ".") + '%'

                clientes_atrasados.append(cliente_atrasado)

    return clientes_atrasados


def proximos_vencimientos(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
                sucursales = Sucursal.objects.all()
                # TEMPLATE A CARGAR
                t = loader.get_template('informes/proximos_vencimientos.html')



                filtros = filtros_establecidos(request.GET, 'proximos_vencimientos')

                # OBJETO QUE SE UTILIZA PARA CARGAR TODOS LOS CLIENTES ATRASADOS A MOSTRAR
                clientes_atrasados = []

                # PARAMETROS
                meses_peticion = 1
                fraccion = ''
                fraccion_nombre = ''
                tipo_busqueda = ''


                # QUERY PARA TRAER TODOS LOS LOTES DE LA FRACCION EN CUESTION
                query = (
                    '''
                SELECT lote.* FROM principal_fraccion fraccion, principal_manzana manzana, principal_lote lote WHERE manzana.id = lote.manzana_id AND manzana.fraccion_id = fraccion.id
                '''
                )
                if filtros == 2:
                    c = RequestContext(request, {
                        'object_list': [],
                    })
                    return HttpResponse(t.render(c))

                else:

                    if filtros == 0:
                        fraccion = ''
                    else:
                        fecha_inicio = request.GET['fecha_ini']
                        fecha_fin = request.GET['fecha_fin']
                        fraccion = request.GET['fraccion']
                        fraccion_nombre = request.GET['fraccion_nombre']

                    clientes_con_lotes_a_vencer = obtener_clientes_con_lotes_por_vencer(fraccion, fecha_inicio, fecha_fin)

                a = len(clientes_con_lotes_a_vencer)
                if a > 0:
                    ultimo = "&fraccion=" + unicode(fraccion) +"&fraccion_nombre=" + unicode(fraccion_nombre) + "&meses_atraso=" + unicode(123)
                    lista = clientes_con_lotes_a_vencer
                    c = RequestContext(request, {
                        'fraccion': fraccion,
                        'fraccion_nombre': fraccion_nombre,
                        'fecha_inicio': fecha_inicio,
                        'fecha_fin': fecha_fin,
                        'ultimo': ultimo,
                        'object_list': lista,
                        # 'cant_reg':cant_reg,
                        'clientes_atrasados': clientes_con_lotes_a_vencer
                    })
                    return HttpResponse(t.render(c))
                else:
                    ultimo = "&fraccion=" + unicode(fraccion) +"&fraccion_nombre=" + unicode(fraccion_nombre) + "&meses_atraso=" + unicode(123)
                    c = RequestContext(request, {
                        'fraccion': fraccion,
                        'fraccion_nombre': fraccion_nombre,
                        'meses_atraso': 1,
                        'ultimo': ultimo,
                        'object_list': clientes_con_lotes_a_vencer
                    })
                    return HttpResponse(t.render(c))
                    # except Exception, error:
                    #     print error
                    # return HttpResponseServerError("No se pudo obtener el Listado de Clientes Atrasados.")
            else:
                t = loader.get_template('index2.html')
                grupo = request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))
        else:
            return HttpResponseRedirect(reverse('login'))


def clientes_atrasados(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):

                # TEMPLATE A CARGAR
                t = loader.get_template('informes/clientes_atrasados.html')
                fecha_actual = datetime.datetime.now()

                # FILTROS DISPONIBLES
                #obtiene un valor de acuerdo a los parametros que recibe.
                #si recibe la fraccion retorna 1
                filtros = filtros_establecidos(request.GET, 'clientes_atrasados')

                # OBJETO QUE SE UTILIZA PARA CARGAR TODOS LOS CLIENTES ATRASADOS A MOSTRAR
                clientes_atrasados = []

                # PARAMETROS
                meses_peticion = 1
                fraccion = ''
                fraccion_nombre = ''
                tipo_busqueda = ''

                try:
                    if request.GET['tipo_busqueda'] == 'fecha':
                        filtros = 5
                except MultiValueDictKeyError:
                    fraccion = ''

                # QUERY PARA TRAER TODOS LOS LOTES DE LA FRACCION EN CUESTION
                query = (
                    '''
                SELECT lote.* FROM principal_fraccion fraccion, principal_manzana manzana, principal_lote lote WHERE manzana.id = lote.manzana_id AND manzana.fraccion_id = fraccion.id
                '''
                )

                # FILTROS:
                #     NI FRACCION NI MESES DE ATRASO SETEADOS
                #          RETURN 0
                #     FRACCION SETEADA PERO MESES DE ATRASO NO
                #         RETURN 1
                #     FRACCION NO SETEADA PERO SI MESES DE ATRASO
                #         return 2
                #     AMBOS SETEADOS
                #         RETURN 3

                if filtros == 0:
                    c = RequestContext(request, {
                        'object_list': [],
                    })
                    return HttpResponse(t.render(c))
                elif filtros == 1:
                    fraccion = request.GET['fraccion']
                    fraccion_nombre = request.GET['fraccion_nombre']
                elif filtros == 2:
                    meses_peticion = int(request.GET['meses_atraso'])
                else:
                    if filtros != 5:
                        fraccion = request.GET['fraccion']
                        fraccion_nombre = request.GET['fraccion_nombre']
                        meses_peticion = int(request.GET['meses_atraso'])

                if filtros != 5:
                    clientes_atrasados = obtener_clientes_atrasados(filtros, fraccion, meses_peticion)
                else:
                    clientes_atrasados = obtener_clientes_atrasados_del_dia()

                if meses_peticion == 0:
                    meses_peticion = ''

                a = len(clientes_atrasados)
                if a > 0:
                    ultimo = "&fraccion=" + unicode(fraccion) +"&fraccion_nombre=" + unicode(fraccion_nombre) + "&meses_atraso=" + unicode(meses_peticion)
                    lista = clientes_atrasados
                    c = RequestContext(request, {
                        'fraccion': fraccion,
                        'fraccion_nombre': fraccion_nombre,
                        'meses_atraso': meses_peticion,
                        'ultimo': ultimo,
                        'object_list': lista,
                        # 'cant_reg':cant_reg,
                        'clientes_atrasados': clientes_atrasados
                    })
                    return HttpResponse(t.render(c))
                else:
                    ultimo = "&fraccion=" + unicode(fraccion) +"&fraccion_nombre=" + unicode(fraccion_nombre) + "&meses_atraso=" + unicode(meses_peticion)
                    c = RequestContext(request, {
                        'fraccion': fraccion,
                        'fraccion_nombre': fraccion_nombre,
                        'meses_atraso': meses_peticion,
                        'ultimo': ultimo,
                        'object_list': clientes_atrasados
                    })
                    return HttpResponse(t.render(c))
                    # except Exception, error:
                    #     print error
                    # return HttpResponseServerError("No se pudo obtener el Listado de Clientes Atrasados.")
            else:
                t = loader.get_template('index2.html')
                grupo = request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))
        else:
            return HttpResponseRedirect(reverse('login'))


def clientes_atrasados_2(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
                t = loader.get_template('informes/clientes_atrasados.html')
                fecha_actual = datetime.datetime.now()
                filtros = filtros_establecidos(request.GET, 'clientes_atrasados')
                cliente_atrasado = {}
                clientes_atrasados = []
                meses_peticion = 0
                fraccion = ''
                query = (
                    '''
                SELECT pm.nro_manzana manzana, pl.nro_lote lote, pl.id lote_id, pc.id, pc.nombres || ' ' || apellidos cliente, (pp.cantidad_de_cuotas - pv.pagos_realizados) cuotas_atrasadas,
                pv.pagos_realizados cuotas_pagadas, pv.precio_de_cuota importe_cuota,
                (pv.pagos_realizados * pv.precio_de_cuota) total_pagado, pp.cantidad_de_cuotas * pv.precio_de_cuota valor_total_lote,
                (pv.pagos_realizados*100/pp.cantidad_de_cuotas) porc_pagado
                FROM principal_lote pl, principal_cliente pc, principal_venta pv, principal_manzana pm, principal_plandepago pp
                WHERE pv.plan_de_pago_id = pp.id AND pv.lote_id = pl.id AND pv.cliente_id = pc.id
                AND (pp.cantidad_de_cuotas - pv.pagos_realizados) > 0 AND pl.manzana_id = pm.id AND pp.tipo_de_plan='credito'
                '''
                )
                if filtros == 0:
                    meses_peticion = 0
                    c = RequestContext(request, {
                        'object_list': [],
                    })
                    return HttpResponse(t.render(c))
                elif filtros == 1:
                    fraccion = request.GET['fraccion']
                    query += "AND  pm.fraccion_id =  %s"
                    cursor = connection.cursor()
                    cursor.execute(query, [fraccion])
                elif filtros == 2:
                    meses_peticion = int(request.GET['meses_atraso'])
                    query += "AND (pp.cantidad_de_cuotas - pv.pagos_realizados) = %s"
                    cursor = connection.cursor()
                    cursor.execute(query, [meses_peticion])
                else:
                    fraccion = request.GET['fraccion']
                    meses_peticion = int(request.GET['meses_atraso'])
                    query += "AND pm.fraccion_id =  %s"
                    cursor = connection.cursor()
                    cursor.execute(query, [fraccion])

                try:
                    dias = meses_peticion * 30
                    results = cursor.fetchall()
                    desc = cursor.description
                    for r in results:
                        i = 0
                        cliente_atrasado = {}
                        while i < len(desc):
                            cliente_atrasado[desc[i][0]] = r[i]
                            i = i + 1
                        try:
                            ultimo_pago = PagoDeCuotas.objects.filter(cliente_id=cliente_atrasado['id']).order_by(
                                '-fecha_de_pago')[:1].get()
                            cliente_persona = Cliente.objects.get(pk=cliente_atrasado['id'])
                        except PagoDeCuotas.DoesNotExist:
                            ultimo_pago = None

                        if ultimo_pago != None:
                            fecha_ultimo_pago = ultimo_pago.fecha_de_pago

                        f1 = fecha_actual.date()
                        f2 = fecha_ultimo_pago
                        diferencia = (f1 - f2).days
                        meses_diferencia = int(diferencia / 30)
                        # En el caso de que las cuotas que debe son menores a la diferencia de meses de la fecha de ultimo pago y la actual
                        if meses_diferencia > cliente_atrasado['cuotas_atrasadas']:
                            meses_diferencia = cliente_atrasado['cuotas_atrasadas']

                        if meses_diferencia >= meses_peticion:
                            cliente_atrasado['cuotas_atrasadas'] = meses_diferencia
                            clientes_atrasados.append(cliente_atrasado)
                            print ("Venta agregada")
                            print (" ")
                        else:
                            print ("Venta no agregada")
                            print (" ")

                        # Seteamos los campos restantes
                        total_atrasado = meses_diferencia * cliente_atrasado['importe_cuota']
                        cliente_atrasado['fecha_ultimo_pago'] = fecha_ultimo_pago.strftime("%d/%m/%Y")
                        cliente_atrasado['lote'] = (
                            unicode(cliente_atrasado['manzana']).zfill(3) + "/" + unicode(
                                cliente_atrasado['lote']).zfill(
                                4))
                        cliente_atrasado['total_atrasado'] = unicode('{:,}'.format(total_atrasado)).replace(",", ".")
                        cliente_atrasado['importe_cuota'] = unicode(
                            '{:,}'.format(cliente_atrasado['importe_cuota'])).replace(",", ".")
                        cliente_atrasado['total_pagado'] = unicode(
                            '{:,}'.format(cliente_atrasado['total_pagado'])).replace(",", ".")
                        cliente_atrasado['valor_total_lote'] = unicode(
                            '{:,}'.format(cliente_atrasado['valor_total_lote'])).replace(",", ".")
                        cliente_atrasado['direccion_particular'] = unicode(cliente_persona.direccion_particular)
                        cliente_atrasado['direccion_cobro'] = unicode(cliente_persona.direccion_cobro)
                        cliente_atrasado['telefono_particular'] = unicode(cliente_persona.telefono_particular)
                        cliente_atrasado['celular_1'] = unicode(cliente_persona.celular_1)
                    if meses_peticion == 0:
                        meses_peticion = ''
                    a = len(clientes_atrasados)
                    if a > 0:
                        ultimo = "&fraccion=" + unicode(fraccion) + "&meses_atraso=" + unicode(meses_peticion)
                        lista = clientes_atrasados
                        # cantidad de registros a mostrar, determinada por el usuario
                        #                         try:
                        #                             cant_reg = request.GET['cant_reg']
                        #                             if cant_reg=='todos':
                        #                                 paginator = Paginator(clientes_atrasados, len(clientes_atrasados))
                        #                             else:
                        #                                 p=range(int(cant_reg))
                        #                                 paginator = Paginator(clientes_atrasados, len(p))
                        #                         except:
                        #                             cant_reg=25
                        #                             paginator = Paginator(clientes_atrasados, 25)
                        #
                        #                         page = request.GET.get('page')
                        #                         try:
                        #                             lista = paginator.page(page)
                        #                         except PageNotAnInteger:
                        #                             lista = paginator.page(1)
                        #                         except EmptyPage:
                        #                             lista = paginator.page(paginator.num_pages)

                        c = RequestContext(request, {
                            'fraccion': fraccion,
                            'meses_atraso': meses_peticion,
                            'ultimo': ultimo,
                            'object_list': lista,
                            # 'cant_reg':cant_reg,
                            'clientes_atrasados': clientes_atrasados
                        })
                        return HttpResponse(t.render(c))
                    else:
                        ultimo = "&fraccion=" + unicode(fraccion) + "&meses_atraso=" + unicode(meses_peticion)
                        c = RequestContext(request, {
                            'fraccion': fraccion,
                            'meses_atraso': meses_peticion,
                            'ultimo': ultimo,
                            'object_list': clientes_atrasados
                        })
                        return HttpResponse(t.render(c))
                except Exception, error:
                    print error
                    # return HttpResponseServerError("No se pudo obtener el Listado de Clientes Atrasados.")
            else:
                t = loader.get_template('index2.html')
                grupo = request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))
        else:
            return HttpResponseRedirect(reverse('login'))


def deudores_por_venta(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
                # TEMPLATE A CARGAR
                t = loader.get_template('informes/deudores_por_venta.html')
                fraccion = ''
                if (filtros_establecidos(request.GET, 'deudores_por_venta') == False):
                    c = RequestContext(request, {
                        'object_list': [],
                    })
                    return HttpResponse(t.render(c))
                else:
                    fraccion = request.GET['fraccion']
                    fraccion_label = request.GET.get('fraccion_nombre', '')

                    # OBJETO QUE SE UTILIZA PARA CARGAR TODOS LOS CLIENTES ATRASADOS A MOSTRAR
                    deudores_por_venta = obtener_deudores_por_venta(1, fraccion, 0)
                    a = len(deudores_por_venta)
                    totales_total_pagado = 0
                    totales_total_atrasado = 0
                    totales_total_cuotas_devengadas = 0
                    if a > 0:
                        ultimo = "&fraccion=" + unicode(fraccion)
                        lista = deudores_por_venta
                        for deudor in lista:
                            # acumulamos los totales
                            totales_total_pagado += int(deudor['total_pagado'].replace(".", ""))
                            totales_total_atrasado += int(deudor['total_atrasado'].replace(".", ""))
                            totales_total_cuotas_devengadas += int(deudor['cuotas_devengadas'].replace(".", ""))

                        c = RequestContext(request, {
                            'fraccion': fraccion,
                            'fraccion_label': fraccion_label,
                            'ultimo': ultimo,
                            'object_list': lista,
                            'deudores_por_venta': deudores_por_venta,
                            'totales_total_pagado': unicode('{:,}'.format(totales_total_pagado)).replace(",", "."),
                            'totales_total_atrasado': unicode('{:,}'.format(totales_total_atrasado)).replace(",", "."),
                            'totales_total_cuotas_devengadas': unicode(
                                '{:,}'.format(totales_total_cuotas_devengadas)).replace(",", ".")
                        })
                        return HttpResponse(t.render(c))
                    else:
                        ultimo = "&fraccion=" + unicode(fraccion)
                        c = RequestContext(request, {
                            'fraccion': fraccion,
                            'fraccion_label': fraccion_label,
                            'ultimo': ultimo,
                            'object_list': deudores_por_venta
                        })
                        return HttpResponse(t.render(c))
            else:
                t = loader.get_template('index2.html')
                grupo = request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))
        else:
            return HttpResponseRedirect(reverse('login'))


def informe_general(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
                if (filtros_establecidos(request.GET, 'informe_general') == False):
                    t = loader.get_template('informes/informe_general.html')
                    c = RequestContext(request, {
                        'object_list': [],
                    })
                    return HttpResponse(t.render(c))
                else:  # Parametros seteados
                    t = loader.get_template('informes/informe_general.html')
                    tipo_busqueda = request.GET['tipo_busqueda']
                    fecha_ini = request.GET['fecha_ini']
                    fecha_fin = request.GET['fecha_fin']

                    fraccion_ini = request.GET['frac1']
                    fraccion_fin = request.GET['frac2']
                    f1 = request.GET['fraccion_ini']
                    f2 = request.GET['fraccion_fin']
                    filas_fraccion = []
                    ultimo = "&tipo_busqueda=" + tipo_busqueda + "&fraccion_ini=" + f1 + "&frac1=" + fraccion_ini + "&fraccion_fin=" + f2 + "&frac2=" + fraccion_fin + "&fecha_ini=" + fecha_ini + "&fecha_fin=" + fecha_fin
                    g_fraccion = ''
                    if fecha_ini == '' and fecha_fin == '':
                        query = (
                            '''
                        SELECT pc.* FROM principal_pagodecuotas pc, principal_lote l, principal_manzana m, principal_fraccion f
                        WHERE f.id>=''' + fraccion_ini +
                            '''
                        AND f.id<=''' + fraccion_fin +
                            '''
                        AND (pc.lote_id = l.id AND l.manzana_id=m.id AND m.fraccion_id=f.id) ORDER BY f.id
                        '''
                        )
                    else:
                        fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date()
                        fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date()
                        query = (
                            '''
                        SELECT pc.* FROM principal_pagodecuotas pc, principal_lote l, principal_manzana m, principal_fraccion f
                        WHERE pc.fecha_de_pago >= \'''' + unicode(fecha_ini_parsed) +
                            '''\' AND pc.fecha_de_pago <= \'''' + unicode(fecha_fin_parsed) +
                            '''\' AND f.id >= ''' + fraccion_ini +
                            '''
                        AND f.id <= ''' + fraccion_fin +
                            '''
                        AND (pc.lote_id = l.id AND l.manzana_id=m.id AND m.fraccion_id=f.id) ORDER BY f.id,pc.fecha_de_pago
                        '''
                        )

                    object_list = list(PagoDeCuotas.objects.raw(query))

                    cuotas = []
                    total_cuotas = 0
                    total_mora = 0
                    total_pagos = 0

                    total_general_cuotas = 0
                    total_general_mora = 0
                    total_general_pagos = 0
                    # ver esto
                    for i, cuota_item in enumerate(object_list):
                        # Se setean los datos de cada fila
                        cuota = {}
                        cuota['misma_fraccion'] = True
                        nro_cuota = get_nro_cuota(cuota_item)
                        if g_fraccion == '':
                            g_fraccion = cuota_item.lote.manzana.fraccion.id
                            cuota['misma_fraccion'] = False
                        if g_fraccion != cuota_item.lote.manzana.fraccion.id:

                            filas_fraccion[0]['misma_fraccion'] = False
                            cuotas.extend(filas_fraccion)
                            filas_fraccion = []

                            g_fraccion = cuota_item.lote.manzana.fraccion.id

                            cuota = {}
                            # cuota['misma_fraccion'] = False
                            cuota['total_cuotas'] = unicode('{:,}'.format(total_cuotas)).replace(",", ".")
                            cuota['total_mora'] = unicode('{:,}'.format(total_mora)).replace(",", ".")
                            cuota['total_pago'] = unicode('{:,}'.format(total_pagos)).replace(",", ".")
                            cuota['ultimo_pago'] = True
                            cuotas.append(cuota)

                            total_cuotas = 0
                            total_mora = 0
                            total_pagos = 0

                            cuota = {}
                            cuota['misma_fraccion'] = False
                            cuota['ultimo_pago'] = False
                            cuota['fraccion_id'] = unicode(cuota_item.lote.manzana.fraccion.id)
                            cuota['fraccion'] = unicode(cuota_item.lote.manzana.fraccion)
                            cuota['lote'] = unicode(cuota_item.lote)
                            cuota['cliente'] = unicode(cuota_item.cliente)
                            cuota['cuota_nro'] = unicode(nro_cuota) + '/' + unicode(
                                cuota_item.plan_de_pago.cantidad_de_cuotas)
                            cuota['plan_de_pago'] = cuota_item.plan_de_pago.nombre_del_plan
                            cuota['fecha_pago'] = unicode(cuota_item.fecha_de_pago.strftime("%d/%m/%Y"))
                            cuota['total_de_cuotas'] = unicode('{:,}'.format(cuota_item.total_de_cuotas)).replace(",",
                                                                                                                  ".")
                            cuota['total_de_mora'] = unicode('{:,}'.format(cuota_item.total_de_mora)).replace(",", ".")
                            cuota['total_de_pago'] = unicode('{:,}'.format(cuota_item.total_de_pago)).replace(",", ".")
                            # Se suman los totales por fraccion
                            total_cuotas += cuota_item.total_de_cuotas
                            total_mora += cuota_item.total_de_mora
                            total_pagos += cuota_item.total_de_pago

                            total_general_cuotas += cuota_item.total_de_cuotas
                            total_general_mora += cuota_item.total_de_mora
                            total_general_pagos += cuota_item.total_de_pago

                            filas_fraccion.append(cuota)

                        else:
                            cuota['ultimo_pago'] = False
                            cuota['misma_fraccion'] = True
                            cuota['fraccion_id'] = unicode(cuota_item.lote.manzana.fraccion.id)
                            cuota['fraccion'] = unicode(cuota_item.lote.manzana.fraccion)
                            cuota['lote'] = unicode(cuota_item.lote)
                            cuota['cliente'] = unicode(cuota_item.cliente)
                            cuota['cuota_nro'] = unicode(nro_cuota) + '/' + unicode(
                                cuota_item.plan_de_pago.cantidad_de_cuotas)
                            cuota['plan_de_pago'] = cuota_item.plan_de_pago.nombre_del_plan
                            cuota['fecha_pago'] = unicode(cuota_item.fecha_de_pago.strftime("%d/%m/%Y"))
                            cuota['total_de_cuotas'] = unicode('{:,}'.format(cuota_item.total_de_cuotas)).replace(",",
                                                                                                                  ".")
                            cuota['total_de_mora'] = unicode('{:,}'.format(cuota_item.total_de_mora)).replace(",", ".")
                            cuota['total_de_pago'] = unicode('{:,}'.format(cuota_item.total_de_pago)).replace(",", ".")
                            # Se suman los totales por fraccion
                            total_cuotas += cuota_item.total_de_cuotas
                            total_mora += cuota_item.total_de_mora
                            total_pagos += cuota_item.total_de_pago

                            total_general_cuotas += cuota_item.total_de_cuotas
                            total_general_mora += cuota_item.total_de_mora
                            total_general_pagos += cuota_item.total_de_pago

                            filas_fraccion.append(cuota)

                    cuotas.extend(filas_fraccion)
                    cuota = {}
                    cuota['total_cuotas'] = unicode('{:,}'.format(total_cuotas)).replace(",", ".")
                    cuota['total_mora'] = unicode('{:,}'.format(total_mora)).replace(",", ".")
                    cuota['total_pago'] = unicode('{:,}'.format(total_pagos)).replace(",", ".")
                    cuota['ultimo_pago'] = True
                    cuotas.append(cuota)
                    cuota = {}
                    cuota['total_general_cuotas'] = unicode('{:,}'.format(total_general_cuotas)).replace(",", ".")
                    cuota['total_general_mora'] = unicode('{:,}'.format(total_general_mora)).replace(",", ".")
                    cuota['total_general_pago'] = unicode('{:,}'.format(total_general_pagos)).replace(",", ".")
                    cuotas.append(cuota)
                    lista = cuotas
                    #                     #cantidad de registros a mostrar, determinada por el usuario
                    #                     try:
                    #                         cant_reg = request.GET['cant_reg']
                    #                         if cant_reg=='todos':
                    #                             paginator = Paginator(cuotas, len(cuotas))
                    #                         else:
                    #                             p=range(int(cant_reg))
                    #                             paginator = Paginator(cuotas, len(p))
                    #                     except:
                    #                         cant_reg=25
                    #                         paginator = Paginator(cuotas, 25)
                    #
                    #
                    #                     page = request.GET.get('page')
                    #                     try:
                    #                         lista = paginator.page(page)
                    #                     except PageNotAnInteger:
                    #                         lista = paginator.page(1)
                    #                     except EmptyPage:
                    #                         lista = paginator.page(paginator.num_pages)
                    c = RequestContext(request, {
                        'tipo_busqueda': tipo_busqueda,
                        # 'cant_reg': cant_reg,
                        'fraccion_ini': fraccion_ini,
                        'fraccion_fin': fraccion_fin,
                        'fecha_ini': fecha_ini,
                        'fecha_fin': fecha_fin,
                        'lista_cuotas': lista,
                        'ultimo': ultimo,
                        'frac1': f1,
                        'frac2': f2
                    })
                    return HttpResponse(t.render(c))
            else:
                t = loader.get_template('index2.html')
                grupo = request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))
        else:
            return HttpResponseRedirect(reverse('login'))


def informe_cuotas_por_cobrar(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
                t = loader.get_template('informes/informe_cuotas_por_cobrar.html')
            else:
                t = loader.get_template('index2.html')
                grupo = request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))
        else:
            return HttpResponseRedirect(reverse('login'))

        if (filtros_establecidos(request.GET, 'informe_cuotas_por_cobrar') == False):
            # t = loader.get_template('informes/informe_cuotas_por_cobrar.html')
            c = RequestContext(request, {
                'object_list': [],
            })
            return HttpResponse(t.render(c))
        else:  # Parametros seteados
            fraccion_ini = request.GET['frac1']
            f1 = request.GET['fraccion_ini']
            tipo_busqueda = request.GET['tipo_busqueda']
            ultimo = "&tipo_busqueda=" + tipo_busqueda + "&frac1=" + fraccion_ini + "&fraccion_ini=" + f1
            # obtiene la lista que buscamos
            lista = obtener_informe_cuotas_por_cobrar(fraccion_ini)
            # si es para visualizar
            if request.GET['formato-reporte'] == 'pantalla':
                t = loader.get_template('informes/informe_cuotas_por_cobrar.html')
                c = RequestContext(request, {
                    'tipo_busqueda': tipo_busqueda,
                    # 'cant_reg': cant_reg,
                    'fraccion_ini': fraccion_ini,
                    # 'fraccion_fin': fraccion_fin,
                    'lista_cuotas': lista,
                    'ultimo': ultimo,
                    'frac1': f1,
                })
                return HttpResponse(t.render(c))
            # o si es para descargar
            else:
                response = informe_cuotas_por_cobrar_excel(lista)
                return response


# Funcion que devuelve la lista de pagos de para liquidacion de propietarios.
#
def obtener_pagos_liquidacion(entidad_id, tipo_busqueda, fecha_ini, fecha_fin, order_by, ley_param=None,
                              impuesto_renta_param=None, iva_comision_param=None):
    lista_ordenada = []
    filas = []

    if tipo_busqueda == "fraccion":
        lotes = []
        # Totales por FRACCION
        total_monto_pagado = 0
        total_monto_inm = 0
        total_monto_prop = 0

        # Totales GENERALES
        total_general_pagado = 0
        total_general_inm = 0
        total_general_prop = 0

        monto_inmobiliaria = 0
        monto_propietario = 0
        # lista_totales = []
        lista_pagos = []

        try:
            fila = {}
            ok = True
            pagos = []
            fraccion = Fraccion.objects.get(pk=entidad_id)
            # ventas = Venta.objects.filter(lote__manzana__fraccion =fraccion_id).order_by('lote_id')

            query = ('''
                SELECT
                  "principal_lote"."codigo_paralot",
                  "principal_venta"."id",
                  "principal_venta"."lote_id",
                  "principal_venta"."fecha_de_venta",
                  "principal_venta"."cliente_id",
                  "principal_venta"."vendedor_id",
                  "principal_venta"."plan_de_pago_id",
                  "principal_venta"."entrega_inicial",
                  "principal_venta"."precio_de_cuota",
                  "principal_venta"."precio_final_de_venta",
                  "principal_venta"."fecha_primer_vencimiento",
                  "principal_venta"."pagos_realizados",
                  "principal_venta"."importacion_paralot",
                  "principal_venta"."plan_de_pago_vendedor_id",
                  "principal_venta"."monto_cuota_refuerzo",
                  "principal_venta"."recuperado"
                FROM "principal_venta"
                  INNER JOIN "principal_lote" ON ("principal_venta"."lote_id" = "principal_lote"."id")
                  INNER JOIN "principal_manzana" ON ("principal_lote"."manzana_id" = "principal_manzana"."id")
                WHERE "principal_manzana"."fraccion_id" = %s
            ''')

            cursor = connection.cursor()
            cursor.execute(query, [entidad_id])
            ventas = cursor.fetchall()

            for venta_obtenida in ventas:

                venta = Venta.objects.get(pk=venta_obtenida[1])

                if venta.plan_de_pago.tipo_de_plan == "contado":
                    if venta.fecha_de_venta >= fecha_ini and venta.fecha_de_venta <= fecha_fin:
                        montos = calculo_montos_liquidacion_propietarios_contado(venta)
                        monto_inmobiliaria = montos['monto_inmobiliaria']
                        monto_propietario = montos['monto_propietario']
                        total_de_cuotas = int(venta.precio_final_de_venta)
                        fecha_pago_str = unicode(venta.fecha_de_venta)
                        fecha_pago = unicode(
                            datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                        fecha_pago_order = datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y")
                        # Se setean los datos de cada fila
                        fila = {}
                        fila['misma_fraccion'] = True
                        fila['fraccion'] = unicode(fraccion)
                        fila['fecha_de_pago'] = fecha_pago
                        fila['fecha_de_pago_order'] = fecha_pago_order
                        fila['lote'] = unicode(venta.lote)
                        fila['cliente'] = unicode(venta.cliente)
                        fila['nro_cuota'] = "Venta Contado"
                        fila['total_de_cuotas'] = unicode('{:,}'.format(total_de_cuotas)).replace(",", ".")
                        fila['monto_inmobiliaria'] = unicode('{:,}'.format(monto_inmobiliaria)).replace(",", ".")
                        fila['monto_propietario'] = unicode('{:,}'.format(monto_propietario)).replace(",", ".")

                        monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov",
                                      "Dic"];
                        fecha_1 = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                        parts_1 = fecha_1.split("/")
                        year_1 = parts_1[2];
                        mes_1 = int(parts_1[1]) - 1;
                        mes_year = monthNames[mes_1] + "/" + year_1;
                        fila['mes'] = mes_year
                        # Se suman los TOTALES por FRACCION
                        # total_monto_inm += int(monto_inmobiliaria)
                        # total_monto_prop += int(monto_propietario)
                        # total_monto_pagado += int(venta.precio_final_de_venta)

                        filas.append(fila)
                        # Acumulamos para los TOTALES GENERALES
                        total_general_pagado += int(venta.precio_final_de_venta)
                        total_general_inm += int(monto_inmobiliaria)
                        total_general_prop += int(monto_propietario)

                if venta.entrega_inicial != 0:
                    if venta.fecha_de_venta >= fecha_ini and venta.fecha_de_venta <= fecha_fin:
                        montos = calculo_montos_liquidacion_propietarios_entrega_inicial(venta)
                        monto_inmobiliaria = montos['monto_inmobiliaria']
                        monto_propietario = montos['monto_propietario']
                        total_de_cuotas = int(venta.entrega_inicial)
                        fecha_pago_str = unicode(venta.fecha_de_venta)
                        fecha_pago = unicode(
                            datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                        fecha_pago_order = datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y")
                        # Se setean los datos de cada fila
                        fila = {}
                        fila['misma_fraccion'] = True
                        fila['fraccion'] = unicode(fraccion)
                        fila['fecha_de_pago'] = fecha_pago
                        fila['fecha_de_pago_order'] = fecha_pago_order
                        fila['lote'] = unicode(venta.lote)
                        fila['cliente'] = unicode(venta.cliente)
                        fila['nro_cuota'] = "Entrega Inicial"
                        fila['total_de_cuotas'] = unicode('{:,}'.format(total_de_cuotas)).replace(",", ".")
                        fila['monto_inmobiliaria'] = unicode('{:,}'.format(monto_inmobiliaria)).replace(",", ".")
                        fila['monto_propietario'] = unicode('{:,}'.format(monto_propietario)).replace(",", ".")

                        monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov",
                                      "Dic"];
                        fecha_1 = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                        parts_1 = fecha_1.split("/")
                        year_1 = parts_1[2];
                        mes_1 = int(parts_1[1]) - 1;
                        mes_year = monthNames[mes_1] + "/" + year_1;
                        fila['mes'] = mes_year
                        # Se suman los TOTALES por FRACCION
                        # total_monto_inm += int(monto_inmobiliaria)
                        # total_monto_prop += int(monto_propietario)
                        # total_monto_pagado += int(venta.precio_final_de_venta)

                        filas.append(fila)
                        # Acumulamos para los TOTALES GENERALES
                        total_general_pagado += int(venta.entrega_inicial)
                        total_general_inm += int(monto_inmobiliaria)
                        total_general_prop += int(monto_propietario)

                pagos = get_pago_cuotas(venta, fecha_ini, fecha_fin)
                lista_cuotas_inm = []
                lista_cuotas_inm.append(venta.plan_de_pago.inicio_cuotas_inmobiliaria)
                numero_cuota = venta.plan_de_pago.inicio_cuotas_inmobiliaria
                for i in range(venta.plan_de_pago.cantidad_cuotas_inmobiliaria - 1):
                    numero_cuota += venta.plan_de_pago.intervalos_cuotas_inmobiliaria
                    lista_cuotas_inm.append(numero_cuota)

                for pago in pagos:
                    if pago['id'] == 1859897:
                        print "Este es el pago"
                    #if pago['cuota_obsequio']:
                     #   print "Es una cuota obsequio"
                    # try:
                    montos = calculo_montos_liquidacion_propietarios(pago, venta, lista_cuotas_inm)
                    monto_inmobiliaria = montos['monto_inmobiliaria']
                    monto_propietario = montos['monto_propietario']
                    total_de_cuotas = int(pago['monto'])
                    fecha_pago_str = unicode(pago['fecha_de_pago'])
                    fecha_pago = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"))
                    fecha_pago_order = datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")
                    # Se setean los datos de cada fila
                    fila = {}
                    fila['pago_id'] = pago['id']
                    fila['cuota_obsequio'] = pago['cuota_obsequio']
                    fila['misma_fraccion'] = True
                    fila['fraccion'] = unicode(fraccion)
                    fila['fecha_de_pago'] = fecha_pago
                    fila['fecha_de_pago_order'] = fecha_pago_order
                    fila['lote'] = unicode(pago['lote'])
                    fila['cliente'] = unicode(venta.cliente)

                    cuotas_detalles = get_cuota_information_by_lote(pago['lote'].id, int(pago['nro_cuota']), True, True,venta)

                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                    fecha_1 = cuotas_detalles[0]['fecha']
                    parts_1 = fecha_1.split("/")
                    year_1 = parts_1[2];
                    mes_1 = int(parts_1[1]) - 1;
                    mes_year = monthNames[mes_1] + "/" + year_1;
                    fila['nro_cuota'] = unicode(pago['nro_cuota_y_total'])
                    fila['mes'] = mes_year
                    fila['total_de_cuotas'] = unicode('{:,}'.format(total_de_cuotas)).replace(",", ".")
                    if pago['cuota_obsequio'] == True:
    #Si la cuota es obsequio se le asigna cero a las columnas monto_inm monto_prop y monto_pagado
                        fila['total_de_cuotas'] = unicode('{:,}'.format(0)).replace(",", ".")
                        fila['monto_inmobiliaria'] = unicode('{:,}'.format(0)).replace(",", ".")
                        fila['monto_propietario'] = unicode('{:,}'.format(0)).replace(",", ".")
                        # Se suman los TOTALES por FRACCION
                        total_monto_inm += int(0)
                        total_monto_prop += int(0)
                        total_monto_pagado += int(0)
                        filas.append(fila)
                        # Acumulamos para los TOTALES GENERALES
                        total_general_pagado += int(0)
                        total_general_inm += int(0)
                        total_general_prop += int(0)
                    else:
    #si no es cuota obsequio se acumulan los totales por fraccion
                        fila['total_de_cuotas'] = unicode('{:,}'.format(total_de_cuotas)).replace(",", ".")
                        fila['monto_inmobiliaria'] = unicode('{:,}'.format(monto_inmobiliaria)).replace(",", ".")
                        fila['monto_propietario'] = unicode('{:,}'.format(monto_propietario)).replace(",", ".")
                        # Se suman los TOTALES por FRACCION
                        total_monto_inm += int(monto_inmobiliaria)
                        total_monto_prop += int(monto_propietario)
                        total_monto_pagado += int(pago['monto'])
                        filas.append(fila)
                        # Acumulamos para los TOTALES GENERALES
                        total_general_pagado += int(pago['monto'])
                        total_general_inm += int(monto_inmobiliaria)
                        total_general_prop += int(monto_propietario)

            # ORDENAMIENTO
            if order_by == "fecha":
                lista_ordenada = sorted(filas, key=lambda k: k['fecha_de_pago'])
            if order_by == "codigo":
                lista_ordenada = sorted(filas, key=lambda k: k['lote'])

            lista_ordenada[0]['misma_fraccion'] = False
            fila = {}
            fila['total_general_pagado'] = unicode('{:,}'.format(total_general_pagado)).replace(",", ".")
            fila['total_general_inmobiliaria'] = unicode('{:,}'.format(total_general_inm)).replace(",", ".")
            fila['total_general_propietario'] = unicode('{:,}'.format(total_general_prop)).replace(",", ".")

            # LEY
            if ley_param == None:
                ley = int(round(total_general_pagado * 0.015))
            else:
                ley = ley_param

            fila['ley'] = unicode('{:,}'.format(ley)).replace(",", ".")

            # IMPUESTO A LA RENTA
            if impuesto_renta_param == None:
                impuesto_renta = int(round((total_general_pagado - ley) * 0.045))
            else:
                impuesto_renta = impuesto_renta_param

            fila['impuesto_renta'] = unicode('{:,}'.format(impuesto_renta)).replace(",", ".")

            # IVA
            if iva_comision_param == None:
                iva_comision = int(round(total_general_inm * 0.1))
            else:
                iva_comision = iva_comision_param

            fila['iva_comision'] = unicode('{:,}'.format(iva_comision)).replace(",", ".")
            fila['total_a_cobrar'] = unicode(
                '{:,}'.format(total_general_prop - (ley + impuesto_renta + iva_comision))).replace(",", ".")
            lista_ordenada.append(fila)

        except Exception, error:
            print error

    elif tipo_busqueda == "propietario":

        try:
            # fila={}
            propietario_id = entidad_id  # liquidacion_propietario_por_propietario
            # Se CERAN  los TOTALES por FRACCION
            total_monto_pagado = 0
            total_monto_inm = 0
            total_monto_prop = 0

            # Totales GENERALES
            total_general_pagado = 0
            total_general_inm = 0
            total_general_prop = 0
            ok = True
            filas_fraccion = []

            ventas = Venta.objects.filter(lote__manzana__fraccion__propietario=propietario_id).order_by(
                'lote__manzana__fraccion').select_related()
            ventas_id = []

            for venta in ventas:
                ventas_id.append(venta.id)

            pagos_de_cuotas_ventas = PagoDeCuotas.objects.filter(venta__in=ventas_id, fecha_de_pago__range=(
                fecha_ini, fecha_fin)).order_by('fecha_de_pago').prefetch_related('venta',
                                                                                  'venta__plan_de_pago',
                                                                                  'venta__lote__manzana__fraccion')
            cant_cuotas_pagadas_ventas = PagoDeCuotas.objects.filter(venta__in=ventas_id,
                                                                     fecha_de_pago__lt=fecha_ini).values(
                'venta_id').annotate(Sum('nro_cuotas_a_pagar')).prefetch_related('venta_id')

            no_recu = None
            g_fraccion = ""
            cambio = 0
            fila = {}
            for venta in ventas:
                if venta.fecha_de_venta >= fecha_ini and venta.fecha_de_venta <= fecha_fin:
                    if venta.plan_de_pago.tipo_de_plan == "contado":

                        if g_fraccion == "":
                            g_fraccion = venta.lote.manzana.fraccion

                        if venta.lote.manzana.fraccion != g_fraccion:
                            # Totales por FRACCION
                            try:
                                filas_fraccion = sorted(filas_fraccion, key=lambda f: (f['fecha_de_pago_order']))
                            except Exception, error:
                                print error + ": " + fecha_pago_str

                            filas_fraccion[0]['misma_fraccion'] = False
                            filas.extend(filas_fraccion)
                            filas_fraccion = []
                            fila = {}
                            fila['total_monto_pagado'] = unicode('{:,}'.format(total_monto_pagado)).replace(",", ".")
                            fila['total_monto_inmobiliaria'] = unicode('{:,}'.format(total_monto_inm)).replace(",", ".")
                            fila['total_monto_propietario'] = unicode('{:,}'.format(total_monto_prop)).replace(",", ".")

                            total_monto_inm = 0
                            total_monto_prop = 0
                            total_monto_pagado = 0

                            fila['ultimo_pago'] = True
                            filas.append(fila)
                            g_fraccion = venta.lote.manzana.fraccion
                            ok = True
                        else:

                            montos = calculo_montos_liquidacion_propietarios_contado(venta)
                            monto_inmobiliaria = montos['monto_inmobiliaria']
                            monto_propietario = montos['monto_propietario']
                            total_de_cuotas = int(venta.precio_final_de_venta)
                            fecha_pago_str = unicode(venta.fecha_de_venta)
                            fecha_pago = unicode(
                                datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                            fecha_pago_order = venta.fecha_de_venta
                            # Se setean los datos de cada fila
                            fila = {}
                            fila['misma_fraccion'] = True
                            fila['fraccion'] = unicode(venta.lote.manzana.fraccion)
                            fila['fecha_de_pago'] = fecha_pago
                            fila['fecha_de_pago_order'] = fecha_pago_order
                            fila['lote'] = unicode(venta.lote)
                            fila['cliente'] = unicode(venta.cliente)
                            fila['nro_cuota'] = "Venta Contado"
                            fila['total_de_cuotas'] = unicode('{:,}'.format(total_de_cuotas)).replace(",", ".")
                            fila['monto_inmobiliaria'] = unicode('{:,}'.format(monto_inmobiliaria)).replace(",", ".")
                            fila['monto_propietario'] = unicode('{:,}'.format(monto_propietario)).replace(",", ".")

                            monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov",
                                          "Dic"];
                            fecha_1 = unicode(
                                datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                            parts_1 = fecha_1.split("/")
                            year_1 = parts_1[2];
                            mes_1 = int(parts_1[1]) - 1;
                            mes_year = monthNames[mes_1] + "/" + year_1;
                            fila['mes'] = mes_year
                            # Se suman los TOTALES por FRACCION
                            total_monto_inm += int(monto_inmobiliaria)
                            total_monto_prop += int(monto_propietario)
                            total_monto_pagado += int(venta.precio_final_de_venta)

                            # filas.append(fila)
                            # Acumulamos para los TOTALES GENERALES
                            total_general_pagado += int(venta.precio_final_de_venta)
                            total_general_inm += int(monto_inmobiliaria)
                            total_general_prop += int(monto_propietario)
                            filas_fraccion.append(fila)

                    if venta.entrega_inicial != 0:

                        if g_fraccion == "":
                            g_fraccion = venta.lote.manzana.fraccion

                        if venta.lote.manzana.fraccion != g_fraccion:
                            # Totales por FRACCION
                            try:
                                filas_fraccion = sorted(filas_fraccion, key=lambda f: (f['fecha_de_pago_order']))
                            except Exception, error:
                                print error + ": " + fecha_pago_str

                            filas_fraccion[0]['misma_fraccion'] = False
                            filas.extend(filas_fraccion)
                            filas_fraccion = []
                            fila = {}
                            fila['total_monto_pagado'] = unicode('{:,}'.format(total_monto_pagado)).replace(",", ".")
                            fila['total_monto_inmobiliaria'] = unicode('{:,}'.format(total_monto_inm)).replace(",", ".")
                            fila['total_monto_propietario'] = unicode('{:,}'.format(total_monto_prop)).replace(",", ".")

                            total_monto_inm = 0
                            total_monto_prop = 0
                            total_monto_pagado = 0

                            fila['ultimo_pago'] = True
                            filas.append(fila)
                            g_fraccion = venta.lote.manzana.fraccion
                            ok = True

                        else:

                            montos = calculo_montos_liquidacion_propietarios_entrega_inicial(venta)
                            monto_inmobiliaria = montos['monto_inmobiliaria']
                            monto_propietario = montos['monto_propietario']
                            total_de_cuotas = int(venta.entrega_inicial)
                            fecha_pago_str = unicode(venta.fecha_de_venta)
                            fecha_pago = unicode(
                                datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                            fecha_pago_order = venta.fecha_de_venta
                            # Se setean los datos de cada fila
                            fila = {}
                            fila['misma_fraccion'] = True
                            fila['fraccion'] = unicode(venta.lote.manzana.fraccion)
                            fila['fecha_de_pago'] = fecha_pago
                            fila['fecha_de_pago_order'] = fecha_pago_order
                            fila['lote'] = unicode(venta.lote)
                            fila['cliente'] = unicode(venta.cliente)
                            fila['nro_cuota'] = "Entrega Inicial"
                            fila['total_de_cuotas'] = unicode('{:,}'.format(total_de_cuotas)).replace(",", ".")
                            fila['monto_inmobiliaria'] = unicode('{:,}'.format(monto_inmobiliaria)).replace(",", ".")
                            fila['monto_propietario'] = unicode('{:,}'.format(monto_propietario)).replace(",", ".")

                            monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov",
                                          "Dic"];
                            fecha_1 = unicode(
                                datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                            parts_1 = fecha_1.split("/")
                            year_1 = parts_1[2];
                            mes_1 = int(parts_1[1]) - 1;
                            mes_year = monthNames[mes_1] + "/" + year_1;
                            fila['mes'] = mes_year

                            # Se suman los TOTALES por FRACCION
                            total_monto_inm += int(monto_inmobiliaria)
                            total_monto_prop += int(monto_propietario)
                            total_monto_pagado += int(venta.entrega_inicial)

                            # filas.append(fila)
                            # Acumulamos para los TOTALES GENERALES
                            total_general_pagado += int(venta.entrega_inicial)
                            total_general_inm += int(monto_inmobiliaria)
                            total_general_prop += int(monto_propietario)

                            filas_fraccion.append(fila)

                # print 'se encontro la venta no recuperada, la venta actual'
                pagos = []
                # pagos = get_pago_cuotas(venta, fecha_ini_parsed,fecha_fin_parsed)
                pagos = get_pago_cuotas(venta, fecha_ini, fecha_fin, pagos_de_cuotas_ventas,
                                        cant_cuotas_pagadas_ventas)
                lista_cuotas_inm = []
                lista_cuotas_inm.append(venta.plan_de_pago.inicio_cuotas_inmobiliaria)
                numero_cuota = venta.plan_de_pago.inicio_cuotas_inmobiliaria
                for i in range(venta.plan_de_pago.cantidad_cuotas_inmobiliaria - 1):
                    numero_cuota += venta.plan_de_pago.intervalos_cuotas_inmobiliaria
                    lista_cuotas_inm.append(numero_cuota)
                if pagos:
                    for pago in pagos:
                        # if pago['id'] == 1841840:
                        # print "este es"
                        try:

                            if g_fraccion == "":
                                g_fraccion = venta.lote.manzana.fraccion

                            if pago['fraccion'] != g_fraccion:
                                # Totales por FRACCION
                                try:
                                    filas_fraccion = sorted(filas_fraccion, key=lambda f: (f['fecha_de_pago_order']))
                                except Exception, error:
                                    print error + ": " + fecha_pago_str

                                filas_fraccion[0]['misma_fraccion'] = False
                                filas.extend(filas_fraccion)
                                filas_fraccion = []
                                fila = {}
                                fila['total_monto_pagado'] = unicode('{:,}'.format(total_monto_pagado)).replace(",",
                                                                                                                ".")
                                fila['total_monto_inmobiliaria'] = unicode('{:,}'.format(total_monto_inm)).replace(",",
                                                                                                                   ".")
                                fila['total_monto_propietario'] = unicode('{:,}'.format(total_monto_prop)).replace(",",
                                                                                                                   ".")

                                total_monto_inm = 0
                                total_monto_prop = 0
                                total_monto_pagado = 0

                                fila['ultimo_pago'] = True
                                filas.append(fila)
                                g_fraccion = pago['fraccion']
                                ok = True

                                montos = calculo_montos_liquidacion_propietarios(pago, venta, lista_cuotas_inm)
                                monto_inmobiliaria = montos['monto_inmobiliaria']
                                monto_propietario = montos['monto_propietario']
                                fecha_pago_str = unicode(pago['fecha_de_pago'])
                                try:
                                    fecha_pago = unicode(
                                        datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                except Exception, error:
                                    print error + ": " + fecha_pago_str

                                # Se setean los datos de cada fila
                                fila = {}
                                fila['cuota_obsequio'] = pago['cuota_obsequio']
                                fila['misma_fraccion'] = True
                                fila['fraccion'] = unicode(venta.lote.manzana.fraccion)
                                fila['fecha_de_pago'] = fecha_pago
                                fila['fecha_de_pago_order'] = pago['fecha_de_pago']
                                fila['lote'] = unicode(pago['lote'])
                                fila['cliente'] = unicode(venta.cliente)
                                fila['nro_cuota'] = unicode(pago['nro_cuota_y_total'])
                                if pago['cuota_obsequio'] == True:
                                    fila['total_de_cuotas'] = unicode('{:,}'.format(0)).replace(",", ".")
                                    fila['monto_inmobiliaria'] = unicode('{:,}'.format(0)).replace(",", ".")
                                    fila['monto_propietario'] = unicode('{:,}'.format(0)).replace(",", ".")
                                    # Se suman los TOTALES por FRACCION
                                    total_monto_inm += int(0)
                                    total_monto_prop += int(0)
                                    total_monto_pagado += int(0)
                                    # Acumulamos para los TOTALES GENERALES
                                    total_general_pagado += int(0)
                                    total_general_inm += int(0)
                                    total_general_prop += int(0)
                                else:
                                    fila['total_de_cuotas'] = unicode('{:,}'.format(int(pago['monto']))).replace(",",
                                                                                                                 ".")
                                    fila['monto_inmobiliaria'] = unicode('{:,}'.format(monto_inmobiliaria)).replace(",",
                                                                                                                    ".")
                                    fila['monto_propietario'] = unicode('{:,}'.format(monto_propietario)).replace(",",
                                                                                                                  ".")
                                    # Se suman los TOTALES por FRACCION
                                    total_monto_inm += int(monto_inmobiliaria)
                                    total_monto_prop += int(monto_propietario)
                                    total_monto_pagado += int(pago['monto'])
                                    # Acumulamos para los TOTALES GENERALES
                                    total_general_pagado += int(pago['monto'])
                                    total_general_inm += int(monto_inmobiliaria)
                                    total_general_prop += int(monto_propietario)

                                cuotas_detalles = get_cuota_information_by_lote(pago['lote'].id, int(pago['nro_cuota']),
                                                                                True, True, venta)
                                monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct",
                                              "Nov", "Dic"];
                                fecha_1 = cuotas_detalles[0]['fecha']
                                parts_1 = fecha_1.split("/")
                                year_1 = parts_1[2];
                                mes_1 = int(parts_1[1]) - 1;
                                mes_year = monthNames[mes_1] + "/" + year_1;
                                fila['mes'] = mes_year

                                # if venta.lote.manzana.fraccion != g_fraccion:
                                ok = False

                                filas_fraccion.append(fila)

                            else:

                                montos = calculo_montos_liquidacion_propietarios(pago, venta, lista_cuotas_inm)
                                monto_inmobiliaria = montos['monto_inmobiliaria']
                                monto_propietario = montos['monto_propietario']
                                fecha_pago_str = unicode(pago['fecha_de_pago'])
                                try:
                                    fecha_pago = unicode(
                                        datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"))
                                except Exception, error:
                                    print error + ": " + fecha_pago_str

                                # Se setean los datos de cada fila
                                fila = {}
                                fila['cuota_obsequio'] = pago['cuota_obsequio']
                                fila['misma_fraccion'] = True
                                fila['fraccion'] = unicode(venta.lote.manzana.fraccion)
                                fila['fecha_de_pago'] = fecha_pago
                                fila['fecha_de_pago_order'] = pago['fecha_de_pago']
                                fila['lote'] = unicode(pago['lote'])
                                fila['cliente'] = unicode(venta.cliente)
                                fila['nro_cuota'] = unicode(pago['nro_cuota_y_total'])
                                if pago['cuota_obsequio'] == True:
                                    fila['total_de_cuotas'] = unicode('{:,}'.format(0)).replace(",", ".")
                                    fila['monto_inmobiliaria'] = unicode('{:,}'.format(0)).replace(",", ".")
                                    fila['monto_propietario'] = unicode('{:,}'.format(0)).replace(",", ".")
                                    # Se suman los TOTALES por FRACCION
                                    total_monto_inm += int(0)
                                    total_monto_prop += int(0)
                                    total_monto_pagado += int(0)
                                    # Acumulamos para los TOTALES GENERALES
                                    total_general_pagado += int(0)
                                    total_general_inm += int(0)
                                    total_general_prop += int(0)

                                else:
                                    fila['total_de_cuotas'] = unicode('{:,}'.format(int(pago['monto']))).replace(",",
                                                                                                                 ".")
                                    fila['monto_inmobiliaria'] = unicode('{:,}'.format(monto_inmobiliaria)).replace(",",
                                                                                                                    ".")
                                    fila['monto_propietario'] = unicode('{:,}'.format(monto_propietario)).replace(",",
                                                                                                                  ".")
                                    # Se suman los TOTALES por FRACCION
                                    total_monto_inm += int(monto_inmobiliaria)
                                    total_monto_prop += int(monto_propietario)
                                    total_monto_pagado += int(pago['monto'])
                                    # Acumulamos para los TOTALES GENERALES
                                    total_general_pagado += int(pago['monto'])
                                    total_general_inm += int(monto_inmobiliaria)
                                    total_general_prop += int(monto_propietario)

                                cuotas_detalles = get_cuota_information_by_lote(pago['lote'].id, int(pago['nro_cuota']),
                                                                                True, True, venta)
                                monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct",
                                              "Nov", "Dic"];
                                fecha_1 = cuotas_detalles[0]['fecha']
                                parts_1 = fecha_1.split("/")
                                year_1 = parts_1[2];
                                mes_1 = int(parts_1[1]) - 1;
                                mes_year = monthNames[mes_1] + "/" + year_1;
                                fila['mes'] = mes_year

                                # if venta.lote.manzana.fraccion != g_fraccion:
                                ok = False

                                filas_fraccion.append(fila)

                        except Exception, error:
                            print "Error: " + unicode(error) + ", Id Pago: " + unicode(
                                pago['id']) + ", Fraccion: " + unicode(pago['fraccion']) + ", lote: " + unicode(
                                pago['lote']) + " Nro cuota: " + unicode(unicode(pago['nro_cuota_y_total']))

            # ORDENAMIENTO
            if order_by == "fecha":
                lista_ordenada = sorted(filas_fraccion, key=lambda k: k['fecha_de_pago'])
            if order_by == "codigo":
                lista_ordenada = sorted(filas_fraccion, key=lambda k: k['lote'])

            # Totales GENERALES
            # filas = sorted(filas, key=lambda f: f['fecha_de_pago'])
            if filas_fraccion != []:
                filas_fraccion = sorted(filas_fraccion, key=lambda f: (f['fecha_de_pago_order']))
                filas_fraccion[0]['misma_fraccion'] = False
                filas.extend(filas_fraccion)

                fila = {}
                fila['total_monto_pagado'] = unicode('{:,}'.format(total_monto_pagado)).replace(",", ".")
                fila['total_monto_inmobiliaria'] = unicode('{:,}'.format(total_monto_inm)).replace(",", ".")
                fila['total_monto_propietario'] = unicode('{:,}'.format(total_monto_prop)).replace(",", ".")
                total_monto_inm = 0
                total_monto_prop = 0
                total_monto_pagado = 0
                fila['ultimo_pago'] = True
                filas.append(fila)

            fila = {}
            fila['total_general_pagado'] = unicode('{:,}'.format(total_general_pagado)).replace(",", ".")
            fila['total_general_inmobiliaria'] = unicode('{:,}'.format(total_general_inm)).replace(",", ".")
            fila['total_general_propietario'] = unicode('{:,}'.format(total_general_prop)).replace(",", ".")
            ley = int(round(total_general_pagado * 0.015))
            fila['ley'] = unicode('{:,}'.format(ley)).replace(",", ".")
            impuesto_renta = int(round((total_general_pagado - ley) * 0.045))
            fila['impuesto_renta'] = unicode('{:,}'.format(impuesto_renta)).replace(",", ".")
            iva_comision = int(round(total_general_inm * 0.1))
            fila['iva_comision'] = unicode('{:,}'.format(iva_comision)).replace(",", ".")
            fila['total_a_cobrar'] = unicode(
                '{:,}'.format(total_general_prop - (ley + impuesto_renta + iva_comision))).replace(",", ".")
            filas.append(fila)
            filas[0]['misma_fraccion'] = False

        except Exception, error:
            print error

    return lista_ordenada


def liquidacion_propietarios(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
                if (filtros_establecidos(request.GET, 'liquidacion_propietarios') == False):
                    t = loader.get_template('informes/liquidacion_propietarios.html')
                    c = RequestContext(request, {
                        'object_list': [],
                    })
                    return HttpResponse(t.render(c))
                else:  # Parametros SETEADOS
                    t = loader.get_template('informes/liquidacion_propietarios.html')
                    try:

                        # PARAMETROS RECIBIDOS
                        fecha_ini = request.GET['fecha_ini']
                        #fecha_ini_con_hora = fecha_ini + ' ' +'00:00:00'
                        fecha_fin = request.GET['fecha_fin']
                        #fecha_fin_con_hora  = fecha_fin + ' ' +'00:00:00'

                        fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date()
                        #fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y %H:%M:%S")
                        fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date()
                        #fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y %H:%M:%S")
                        tipo_busqueda = request.GET['tipo_busqueda']
                        order_by = request.GET['order_by']
                        busqueda_id = request.GET['busqueda']
                        busqueda_label = request.GET['busqueda_label']

                        # BUSQUEDA
                        lista_ordenada = obtener_pagos_liquidacion(busqueda_id, tipo_busqueda, fecha_ini_parsed,
                                                                   fecha_fin_parsed, order_by)

                        ultimo = "&tipo_busqueda=" + tipo_busqueda + "&busqueda=" + busqueda_id + "&busqueda_label=" \
                                 + busqueda_label + "&fecha_ini=" + fecha_ini + "&fecha_fin=" + fecha_fin \
                                 + "&order_by=" + order_by

                        lista = lista_ordenada
                        # PAGINADOR
                        # paginator = Paginator(filas, 25)
                        # page = request.GET.get('page')
                        # try:
                        #    lista = paginator.page(page)
                        # except PageNotAnInteger:
                        #    lista = paginator.page(1)
                        # except EmptyPage:
                        #    lista = paginator.page(paginator.num_pages)
                        c = RequestContext(request, {
                            'object_list': lista,
                            #'lista_totales' : lista_totales,
                            'fecha_ini': fecha_ini,
                            'fecha_fin': fecha_fin,
                            'tipo_busqueda': tipo_busqueda,
                            'busqueda': busqueda_id,
                            'busqueda_label': busqueda_label,
                            'order_by': order_by,
                            'ultimo': ultimo
                        })
                        return HttpResponse(t.render(c))
                    except Exception, error:
                        print error
            else:
                t = loader.get_template('index2.html')
                grupo = request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))
        else:
            return HttpResponseRedirect(reverse('login'))


def liquidacion_vendedores(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
                if (filtros_establecidos(request.GET, 'liquidacion_vendedores') == False):
                    t = loader.get_template('informes/liquidacion_vendedores.html')
                    c = RequestContext(request, {
                        'object_list': [],
                    })

                    return HttpResponse(t.render(c))
                else:  # Parametros seteados
                    t = loader.get_template('informes/liquidacion_vendedores.html')
                    fecha_ini = request.GET['fecha_ini']
                    fecha_fin = request.GET['fecha_fin']
                    fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date()
                    fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date()

                    fecha_final = fecha_fin_parsed+timedelta(days=1)
                    #fecha_finalizacion = datetime.datetime.strptime(un_dia_mas, "%d/%m/%Y").date()
                    busqueda_label = request.GET['busqueda_label']
                    vendedor_id = request.GET['busqueda']
                    print("vendedor_id ->" + vendedor_id)

                    # por alguna razon, no encuentra la venta en algunos casos con el select_related()
                    # ventas = Venta.objects.filter(vendedor_id = vendedor_id).order_by('lote__manzana__fraccion').select_related()
                    ventas = Venta.objects.filter(vendedor_id=vendedor_id).order_by('lote__manzana__fraccion')
                    ventas_id = []

                    for venta in ventas:
                        ventas_id.append(venta.id)

                    pagos_de_cuotas_ventas = PagoDeCuotas.objects.filter(venta__in=ventas_id, fecha_de_pago__range=(
                        fecha_ini_parsed, fecha_final)).order_by('fecha_de_pago').prefetch_related('venta',
                                                                                                        'venta__plan_de_pago_vendedor',
                                                                                                        'venta__lote__manzana__fraccion')
                    cant_cuotas_pagadas_ventas = PagoDeCuotas.objects.filter(venta__in=ventas_id,
                                                                             fecha_de_pago__lt=fecha_ini_parsed).values(
                        'venta_id').annotate(Sum('nro_cuotas_a_pagar')).prefetch_related('venta_id')

                    filas_fraccion = []
                    filas = []

                    total_fraccion_monto_pagado = 0
                    total_fraccion_monto_vendedor = 0

                    total_general_monto_pagado = 0
                    total_general_monto_vendedor = 0

                    fecha_pago_str = ''
                    # ACAAA
                    g_fraccion = ''
                    for venta in ventas:

                        if venta.fecha_de_venta >= fecha_ini_parsed and venta.fecha_de_venta <= fecha_fin_parsed:
                            # preguntar por el plan de pago de la venta con el vendedor, si el vendedor lleva un % de la venta total, un % de la entrega inicial

                            if venta.plan_de_pago_vendedor.tipo == 'contado':

                                if g_fraccion == '':
                                    g_fraccion = venta.lote.manzana.fraccion
                                if venta.lote.manzana.fraccion != g_fraccion:
                                    # Totales por FRACCION

                                    if filas_fraccion:
                                        try:
                                            filas_fraccion = sorted(filas_fraccion,
                                                                    key=lambda f: (f['fecha_de_pago_order']))
                                        except Exception, error:
                                            print unicode(error) + ": " + fecha_pago_str
                                        filas_fraccion[0]['misma_fraccion'] = False
                                        filas.extend(filas_fraccion)
                                        filas_fraccion = []
                                        fila = {}
                                        fila['total_monto_pagado'] = unicode(
                                            '{:,}'.format(total_fraccion_monto_pagado)).replace(",", ".")
                                        fila['total_monto_vendedor'] = unicode(
                                            '{:,}'.format(total_fraccion_monto_vendedor)).replace(",", ".")

                                        total_fraccion_monto_pagado = 0
                                        total_fraccion_monto_vendedor = 0

                                        fila['ultimo_pago'] = True
                                        filas.append(fila)
                                    else:
                                        montos = calculo_montos_liquidacion_vendedores_contado(venta)
                                        monto_vendedor = montos['monto_vendedor']
                                        fecha_pago_str = unicode(venta.fecha_de_venta)
                                        fecha_pago = unicode(
                                            datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                        fecha_pago_order = venta.fecha_de_venta

                                        # Fraccion    Lote    Fecha de Pago    Cliente    Cuota Nº    Mes    Monto Pag Monto Prop.
                                        fila = {}
                                        fila['fraccion'] = venta.lote.manzana.fraccion
                                        fila['plan'] = unicode(venta.plan_de_pago_vendedor)
                                        fila['lote'] = venta.lote.codigo_paralot
                                        fila['fecha_de_pago'] = fecha_pago
                                        fila['fecha_de_pago_order'] = fecha_pago_order
                                        fila['cliente'] = venta.cliente
                                        fila['nro_cuota'] = 'Venta al Contado'
                                        fila['monto_pagado'] = venta.precio_final_de_venta
                                        fila['monto_vendedor'] = monto_vendedor
                                        fila['misma_fraccion'] = True

                                        monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                                                      "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
                                        fecha_1 = unicode(
                                            datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                        parts_1 = fecha_1.split("/")
                                        year_1 = parts_1[2]
                                        mes_1 = int(parts_1[1]) - 1
                                        mes_year = monthNames[mes_1] + "/" + year_1
                                        fila['mes'] = "1/1"

                                        total_fraccion_monto_pagado += fila['monto_pagado']
                                        total_fraccion_monto_vendedor += fila['monto_vendedor']

                                        total_general_monto_pagado += fila['monto_pagado']
                                        total_general_monto_vendedor += fila['monto_vendedor']

                                        fila['monto_pagado'] = unicode(
                                            '{:,}'.format(fila['monto_pagado'])
                                        ).replace(",", ".")

                                        fila['monto_vendedor'] = unicode(
                                            '{:,}'.format(fila['monto_vendedor'])
                                        ).replace(",", ".")

                                        filas_fraccion.append(fila)

                                    g_fraccion = venta.lote.manzana.fraccion.nombre
                                    ok = True
                                else:
                                    montos = calculo_montos_liquidacion_vendedores_contado(venta)
                                    monto_vendedor = montos['monto_vendedor']
                                    fecha_pago_str = unicode(venta.fecha_de_venta)
                                    fecha_pago = unicode(
                                        datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                    fecha_pago_order = venta.fecha_de_venta

                                    # Fraccion    Lote    Fecha de Pago    Cliente    Cuota Nº    Mes    Monto Pag Monto Prop.
                                    fila = {}
                                    fila['fraccion'] = g_fraccion
                                    fila['plan'] = unicode(venta.plan_de_pago_vendedor)
                                    fila['lote'] = venta.lote.codigo_paralot
                                    fila['fecha_de_pago'] = fecha_pago
                                    fila['fecha_de_pago_order'] = fecha_pago_order
                                    fila['cliente'] = venta.cliente
                                    fila['nro_cuota'] = 'Venta al Contado'
                                    fila['monto_pagado'] = venta.precio_final_de_venta
                                    fila['monto_vendedor'] = monto_vendedor
                                    fila['misma_fraccion'] = True

                                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct",
                                                  "Nov", "Dic"]
                                    fecha_1 = unicode(
                                        datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                    parts_1 = fecha_1.split("/")
                                    year_1 = parts_1[2];
                                    mes_1 = int(parts_1[1]) - 1;
                                    mes_year = monthNames[mes_1] + "/" + year_1;
                                    fila['mes'] = mes_year

                                    total_fraccion_monto_pagado += fila['monto_pagado']
                                    total_fraccion_monto_vendedor += fila['monto_vendedor']

                                    total_general_monto_pagado += fila['monto_pagado']
                                    total_general_monto_vendedor += fila['monto_vendedor']

                                    fila['monto_pagado'] = unicode('{:,}'.format(fila['monto_pagado'])).replace(",",
                                                                                                                ".")
                                    fila['monto_vendedor'] = unicode('{:,}'.format(fila['monto_vendedor'])).replace(",",
                                                                                                                    ".")

                                    filas_fraccion.append(fila)

                            if venta.entrega_inicial > 0:
                                if g_fraccion == '':
                                    g_fraccion = venta.lote.manzana.fraccion
                                if venta.lote.manzana.fraccion != g_fraccion:
                                    # Totales por FRACCION
                                    if filas_fraccion:
                                        try:
                                            filas_fraccion = sorted(filas_fraccion,
                                                                    key=lambda f: (f['fecha_de_pago_order']))
                                        except Exception, error:
                                            print unicode(error) + ": " + fecha_pago_str
                                        filas_fraccion[0]['misma_fraccion'] = False
                                        filas.extend(filas_fraccion)
                                        filas_fraccion = []
                                        fila = {}
                                        fila['total_monto_pagado'] = unicode(
                                            '{:,}'.format(total_fraccion_monto_pagado)).replace(",", ".")
                                        fila['total_monto_vendedor'] = unicode(
                                            '{:,}'.format(total_fraccion_monto_vendedor)).replace(",", ".")

                                        total_fraccion_monto_pagado = 0
                                        total_fraccion_monto_vendedor = 0

                                        fila['ultimo_pago'] = True
                                        filas.append(fila).append(fila)
                                    g_fraccion = venta.lote.manzana.fraccion
                                    ok = True
                                else:

                                    montos = calculo_montos_liquidacion_vendedores_entrega_inicial(venta)
                                    monto_vendedor = montos['monto_vendedor']
                                    fecha_pago_str = unicode(venta.fecha_de_venta)
                                    fecha_pago = unicode(
                                        datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                    fecha_pago_order = venta.fecha_de_venta

                                    # Fraccion    Lote    Fecha de Pago    Cliente    Cuota Nº    Mes    Monto Pag Monto Prop.
                                    fila = {}
                                    fila['fraccion'] = g_fraccion
                                    fila['plan'] = unicode(venta.plan_de_pago_vendedor)
                                    fila['lote'] = venta.lote.codigo_paralot
                                    fila['fecha_de_pago'] = fecha_pago
                                    fila['fecha_de_pago_order'] = fecha_pago_order
                                    fila['cliente'] = venta.cliente
                                    fila['nro_cuota'] = 'Entrega Inicial'
                                    fila['monto_pagado'] = venta.entrega_inicial
                                    fila['monto_vendedor'] = monto_vendedor
                                    fila['misma_fraccion'] = True

                                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct",
                                                  "Nov", "Dic"];
                                    fecha_1 = unicode(
                                        datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                    parts_1 = fecha_1.split("/")
                                    year_1 = parts_1[2]
                                    mes_1 = int(parts_1[1]) - 1
                                    mes_year = monthNames[mes_1] + "/" + year_1;
                                    fila['mes'] = mes_year

                                    total_fraccion_monto_pagado += fila['monto_pagado']
                                    total_fraccion_monto_vendedor += fila['monto_vendedor']

                                    total_general_monto_pagado += fila['monto_pagado']
                                    total_general_monto_vendedor += fila['monto_vendedor']

                                    fila['monto_pagado'] = unicode('{:,}'.format(fila['monto_pagado'])).replace(",",
                                                                                                                ".")
                                    fila['monto_vendedor'] = unicode('{:,}'.format(fila['monto_vendedor'])).replace(",",
                                                                                                                    ".")

                                    filas_fraccion.append(fila)

                        pagos = []
                        pagos = get_pago_cuotas(venta, fecha_ini_parsed, fecha_fin_parsed, pagos_de_cuotas_ventas,
                                                cant_cuotas_pagadas_ventas)
                        lista_cuotas_ven = []
                        lista_cuotas_ven.append(venta.plan_de_pago_vendedor.cuota_inicial)
                        numero_cuota = venta.plan_de_pago_vendedor.cuota_inicial
                        for i in range(venta.plan_de_pago_vendedor.cantidad_cuotas - 1):
                            numero_cuota += venta.plan_de_pago_vendedor.intervalos
                            lista_cuotas_ven.append(numero_cuota)

                        for pago in pagos:
                            # preguntar por el plan de pago de la venta con el vendedor, si el vendedor lleva un % del pago de acuerdo al nro de cuota que se está pagando
                            try:

                                # if pago['id']== 1840987:
                                #    print "este es"

                                if venta.lote.manzana.fraccion.nombre == 'VISTA AL PARANA':
                                    print "este es"

                                if g_fraccion == "":
                                    g_fraccion = venta.lote.manzana.fraccion

                                if pago['fraccion'] != g_fraccion:
                                    # Totales por FRACCION
                                    if filas_fraccion:
                                        try:
                                            filas_fraccion = sorted(filas_fraccion,
                                                                    key=lambda f: (f['fecha_de_pago_order']))
                                        except Exception, error:
                                            print unicode(error) + ": " + fecha_pago_str
                                        filas_fraccion[0]['misma_fraccion'] = False
                                        filas.extend(filas_fraccion)
                                        filas_fraccion = []
                                        fila = {}
                                        fila['total_monto_pagado'] = unicode(
                                            '{:,}'.format(total_fraccion_monto_pagado)).replace(",", ".")
                                        fila['total_monto_vendedor'] = unicode(
                                            '{:,}'.format(total_fraccion_monto_vendedor)).replace(",", ".")

                                        total_fraccion_monto_pagado = 0
                                        total_fraccion_monto_vendedor = 0

                                        fila['ultimo_pago'] = True
                                        filas.append(fila)
                                    g_fraccion = pago['fraccion']
                                    ok = True

                                    montos = calculo_montos_liquidacion_vendedores(pago, venta, lista_cuotas_ven)
                                    monto_vendedor = montos['monto_vendedor']
                                    fecha_pago_str = unicode(pago['fecha_de_pago'])
                                    try:
                                        fecha_pago = unicode(
                                            datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"))
                                    except Exception, error:
                                        print unicode(error) + ": " + fecha_pago_str

                                    # Se setean los datos de cada fila
                                    fila = {}
                                    fila['misma_fraccion'] = True
                                    fila['fraccion'] = unicode(venta.lote.manzana.fraccion)
                                    fila['plan'] = unicode(venta.plan_de_pago_vendedor)
                                    fila['fecha_de_pago'] = fecha_pago
                                    fila['fecha_de_pago_order'] = pago['fecha_de_pago']
                                    fila['lote'] = unicode(pago['lote'])
                                    fila['cliente'] = unicode(venta.cliente)
                                    fila['nro_cuota'] = unicode(pago['nro_cuota_y_total'])
                                    fila['total_de_cuotas'] = unicode('{:,}'.format(int(pago['monto']))).replace(",",
                                                                                                                 ".")
                                    fila['monto_vendedor'] = unicode('{:,}'.format(monto_vendedor)).replace(",", ".")

                                    cuotas_detalles = get_cuota_information_by_lote(pago['lote'].id,
                                                                                    int(pago['nro_cuota']), True, True,
                                                                                    venta)
                                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct",
                                                  "Nov", "Dic"];
                                    fecha_1 = cuotas_detalles[0]['fecha']
                                    parts_1 = fecha_1.split("/")
                                    year_1 = parts_1[2];
                                    mes_1 = int(parts_1[1]) - 1;
                                    mes_year = monthNames[mes_1] + "/" + year_1;
                                    fila['mes'] = mes_year

                                    # if venta.lote.manzana.fraccion != g_fraccion:
                                    if monto_vendedor != 0:
                                        ok = False
                                        # Se suman los TOTALES por FRACCION
                                        total_fraccion_monto_vendedor += int(monto_vendedor)
                                        total_fraccion_monto_pagado += int(pago['monto'])

                                        # Acumulamos para los TOTALES GENERALES
                                        total_general_monto_pagado += int(pago['monto'])
                                        total_general_monto_vendedor += int(monto_vendedor)

                                        filas_fraccion.append(fila)

                                else:

                                    montos = calculo_montos_liquidacion_vendedores(pago, venta, lista_cuotas_ven)
                                    monto_vendedor = montos['monto_vendedor']
                                    fecha_pago_str = unicode(pago['fecha_de_pago'])
                                    try:
                                        fecha_pago = unicode(
                                            datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"))
                                    except Exception, error:
                                        print error + ": " + fecha_pago_str

                                    # Se setean los datos de cada fila
                                    fila = {}
                                    fila['misma_fraccion'] = True
                                    fila['fraccion'] = unicode(venta.lote.manzana.fraccion)
                                    fila['plan'] = unicode(venta.plan_de_pago_vendedor)
                                    fila['fecha_de_pago'] = fecha_pago
                                    fila['fecha_de_pago_order'] = pago['fecha_de_pago']
                                    fila['lote'] = unicode(pago['lote'])
                                    fila['cliente'] = unicode(venta.cliente)
                                    fila['nro_cuota'] = unicode(pago['nro_cuota_y_total'])
                                    fila['total_de_cuotas'] = unicode('{:,}'.format(int(pago['monto']))).replace(",",
                                                                                                                 ".")
                                    fila['monto_vendedor'] = unicode('{:,}'.format(monto_vendedor)).replace(",", ".")

                                    cuotas_detalles = get_cuota_information_by_lote(pago['lote'].id,
                                                                                    int(pago['nro_cuota']), True, True,
                                                                                    venta)
                                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct",
                                                  "Nov", "Dic"];
                                    fecha_1 = cuotas_detalles[0]['fecha']
                                    parts_1 = fecha_1.split("/")
                                    year_1 = parts_1[2];
                                    mes_1 = int(parts_1[1]) - 1;
                                    mes_year = monthNames[mes_1] + "/" + year_1;
                                    fila['mes'] = mes_year

                                    # if venta.lote.manzana.fraccion != g_fraccion:
                                    if monto_vendedor != 0:
                                        ok = False
                                        # Se suman los TOTALES por FRACCION
                                        total_fraccion_monto_vendedor += int(monto_vendedor)
                                        total_fraccion_monto_pagado += int(pago['monto'])

                                        # Acumulamos para los TOTALES GENERALES
                                        total_general_monto_pagado += int(pago['monto'])
                                        total_general_monto_vendedor += int(monto_vendedor)

                                        filas_fraccion.append(fila)





                            except Exception, error:
                                print "Error: " + unicode(error) + ", Id Pago: " + unicode(
                                    pago['id']) + ", Fraccion: " + unicode(pago['fraccion']) + ", lote: " + unicode(
                                    pago['lote']) + " Nro cuota: " + unicode(unicode(pago['nro_cuota_y_total']))

                # Totales GENERALES
                # filas = sorted(filas, key=lambda f: f['fecha_de_pago'])
                if filas_fraccion:
                    filas_fraccion = sorted(filas_fraccion, key=lambda f: (f['fecha_de_pago_order']))
                    filas_fraccion[0]['misma_fraccion'] = False
                    filas.extend(filas_fraccion)

                    fila = {}
                    fila['total_monto_pagado'] = unicode('{:,}'.format(total_fraccion_monto_pagado)).replace(",", ".")
                    fila['total_monto_vendedor'] = unicode('{:,}'.format(total_fraccion_monto_vendedor)).replace(",",
                                                                                                                 ".")
                    total_fraccion_monto_vendedor = 0
                    total_fraccion_monto_pagado = 0
                    fila['ultimo_pago'] = True
                    filas.append(fila)

                fila = {}
                fila['total_general_pagado'] = unicode('{:,}'.format(total_general_monto_pagado)).replace(",", ".")
                fila['total_general_vendedor'] = unicode('{:,}'.format(total_general_monto_vendedor)).replace(",", ".")
                ley = int(total_general_monto_pagado * 0.015)
                filas.append(fila)
                filas[0]['misma_fraccion'] = False

                ultimo = "&busqueda_label=" + busqueda_label + "&busqueda=" + vendedor_id + "&fecha_ini=" + fecha_ini + "&fecha_fin=" + fecha_fin

                lista = filas

                #                 paginator = Paginator(cuotas, 25)
                #                 page = request.GET.get('page')
                #                 try:
                #                     lista = paginator.page(page)
                #                 except PageNotAnInteger:
                #                     lista = paginator.page(1)
                #                 except EmptyPage:
                #                     lista = paginator.page(paginator.num_pages)
                c = RequestContext(request, {
                    'lista_cuotas': lista,
                    'fecha_ini': fecha_ini,
                    'fecha_fin': fecha_fin,
                    'busqueda': vendedor_id,
                    'busqueda_label': busqueda_label,
                    'ultimo': ultimo
                })
                return HttpResponse(t.render(c))
            else:
                t = loader.get_template('index2.html')
                grupo = request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))
        else:
            return HttpResponseRedirect(reverse('login'))


def liquidacion_general_vendedores(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
                if (filtros_establecidos(request.GET, 'liquidacion_general_vendedores') == False):
                    t = loader.get_template('informes/liquidacion_general_vendedores.html')
                    c = RequestContext(request, {
                        'object_list': [],
                    })
                    return HttpResponse(t.render(c))
                else:  # Parametros seteados
                    t = loader.get_template('informes/liquidacion_general_vendedores.html')
                    fecha_ini = request.GET['fecha_ini']
                    fecha_fin = request.GET['fecha_fin']
                    fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date()
                    fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date()
                    # busqueda_label = request.GET['busqueda_label']

                    # la funcion del select_related() no esta trayendo una venta en particular
                    # ventas = Venta.objects.filter().order_by('lote__manzana__fraccion').select_related()
                    ventas = Venta.objects.filter().order_by('vendedor')
                    # ventas.group_by = ['vendedor_id']
                    ventas_id = []


                    for venta in ventas:
                        ventas_id.append(venta.id)
                    #aumentamos en uno la fecha de final para consultar con el rango de fecha seleccionado incluido
                    fecha_final = fecha_fin_parsed + timedelta(days=1)

                    pagos_de_cuotas_ventas = PagoDeCuotas.objects.filter(venta__in=ventas_id, fecha_de_pago__range=(
                        fecha_ini_parsed, fecha_final)).order_by('fecha_de_pago').prefetch_related('venta',
                                                                                                        'venta__plan_de_pago_vendedor',
                                                                                                        'venta__lote__manzana__fraccion')

                    cant_cuotas_pagadas_ventas = PagoDeCuotas.objects.filter(venta__in=ventas_id,
                                                                             fecha_de_pago__lt=fecha_ini_parsed).values(
                        'venta_id').annotate(Sum('nro_cuotas_a_pagar')).prefetch_related('venta_id')

                    filas_vendedor = []
                    filas = []

                    total_vendedor_monto_pagado = 0
                    total_vendedor_monto_vendedor = 0

                    total_general_monto_pagado = 0
                    total_general_monto_vendedor = 0

                    fecha_pago_str = ''
                    # ACAAA
                    g_vendedor = ''
                    for venta in ventas:

                        if venta.fecha_de_venta >= fecha_ini_parsed and venta.fecha_de_venta <= fecha_fin_parsed:
                            # preguntar por el plan de pago de la venta con el vendedor, si el vendedor lleva un % de la venta total, un % de la entrega inicial

                            if venta.plan_de_pago_vendedor.tipo == 'contado':

                                if g_vendedor == '':
                                    # g_fraccion = venta.lote.manzana.fraccion
                                    g_vendedor = venta.vendedor
                                # if venta.lote.manzana.fraccion != g_fraccion:
                                if venta.vendedor != g_vendedor:
                                    # Totales por VENDEDOR

                                    if filas_vendedor:
                                        try:
                                            filas_vendedor = sorted(filas_vendedor,
                                                                    key=lambda f: (f['fecha_de_pago_order']))
                                        except Exception, error:
                                            print unicode(error) + ": " + fecha_pago_str
                                        filas_vendedor[0]['misma_vendedor'] = False
                                        filas.extend(filas_vendedor)
                                        filas_vendedor = []
                                        fila = {}
                                        fila['total_monto_pagado'] = unicode(
                                            '{:,}'.format(total_vendedor_monto_pagado)).replace(",", ".")
                                        fila['total_monto_vendedor'] = unicode(
                                            '{:,}'.format(total_vendedor_monto_vendedor)).replace(",", ".")

                                        total_vendedor_monto_pagado = 0
                                        total_vendedor_monto_vendedor = 0

                                        fila['ultimo_pago'] = True
                                        filas.append(fila)
                                    # g_fraccion = venta.lote.manzana.fraccion.nombre
                                    g_vendedor = venta.vendedor
                                    ok = True
                                else:
                                    montos = calculo_montos_liquidacion_vendedores_contado(venta)
                                    monto_vendedor = montos['monto_vendedor']
                                    fecha_pago_str = unicode(venta.fecha_de_venta)
                                    fecha_pago = unicode(
                                        datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                    fecha_pago_order = venta.fecha_de_venta

                                    # Fraccion    Lote    Fecha de Pago    Cliente    Cuota Nº    Mes    Monto Pag Monto Prop.
                                    fila = {}
                                    fila['vendedor'] = g_vendedor
                                    fila['plan'] = unicode(venta.plan_de_pago_vendedor)
                                    fila['lote'] = venta.lote.codigo_paralot
                                    fila['fecha_de_pago'] = fecha_pago
                                    fila['fecha_de_pago_order'] = fecha_pago_order
                                    fila['cliente'] = venta.cliente
                                    fila['nro_cuota'] = 'Venta al Contado'
                                    fila['monto_pagado'] = venta.precio_final_de_venta
                                    fila['monto_vendedor'] = monto_vendedor
                                    fila['mismo_vendedor'] = True

                                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct",
                                                  "Nov", "Dic"];
                                    fecha_1 = unicode(
                                        datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                    parts_1 = fecha_1.split("/")
                                    year_1 = parts_1[2];
                                    mes_1 = int(parts_1[1]) - 1;
                                    mes_year = monthNames[mes_1] + "/" + year_1;
                                    fila['mes'] = mes_year

                                    total_vendedor_monto_pagado += fila['monto_pagado']
                                    total_vendedor_monto_vendedor += fila['monto_vendedor']

                                    total_general_monto_pagado += fila['monto_pagado']
                                    total_general_monto_vendedor += fila['monto_vendedor']

                                    fila['monto_pagado'] = unicode('{:,}'.format(fila['monto_pagado'])).replace(",",
                                                                                                                ".")
                                    fila['monto_vendedor'] = unicode('{:,}'.format(fila['monto_vendedor'])).replace(",",
                                                                                                                    ".")

                                    filas_vendedor.append(fila)

                            if venta.entrega_inicial > 0:
                                if g_vendedor == '':
                                    # g_fraccion = venta.lote.manzana.fraccion
                                    g_vendedor = venta.vendedor
                                # if venta.lote.manzana.fraccion != g_fraccion:
                                if venta.vendedor != g_vendedor:
                                    # Totales por VENDEDOR
                                    if filas_vendedor:
                                        try:
                                            filas_vendedor = sorted(filas_vendedor,
                                                                    key=lambda f: (f['fecha_de_pago_order']))
                                        except Exception, error:
                                            print unicode(error) + ": " + fecha_pago_str
                                        filas_vendedor[0]['mismo_vendedor'] = False
                                        filas.extend(filas_vendedor)
                                        filas_vendedor = []
                                        fila = {}
                                        fila['total_monto_pagado'] = unicode(
                                            '{:,}'.format(total_vendedor_monto_pagado)).replace(",", ".")
                                        fila['total_monto_vendedor'] = unicode(
                                            '{:,}'.format(total_vendedor_monto_vendedor)).replace(",", ".")

                                        total_vendedor_monto_pagado = 0
                                        total_vendedor_monto_vendedor = 0

                                        fila['ultimo_pago'] = True
                                        filas.append(fila).append(fila)
                                    # g_fraccion = venta.lote.manzana.fraccion
                                    g_vendedor = venta.vendedor
                                    ok = True
                                else:

                                    montos = calculo_montos_liquidacion_vendedores_entrega_inicial(venta)
                                    monto_vendedor = montos['monto_vendedor']
                                    fecha_pago_str = unicode(venta.fecha_de_venta)
                                    fecha_pago = unicode(
                                        datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                    fecha_pago_order = venta.fecha_de_venta

                                    # Fraccion    Lote    Fecha de Pago    Cliente    Cuota Nº    Mes    Monto Pag Monto Prop.
                                    fila = {}
                                    fila['vendedor'] = g_vendedor
                                    fila['plan'] = unicode(venta.plan_de_pago_vendedor)
                                    fila['lote'] = venta.lote.codigo_paralot
                                    fila['fecha_de_pago'] = fecha_pago
                                    fila['fecha_de_pago_order'] = fecha_pago_order
                                    fila['cliente'] = venta.cliente
                                    fila['nro_cuota'] = 'Entrega Inicial'
                                    fila['monto_pagado'] = venta.entrega_inicial
                                    fila['monto_vendedor'] = monto_vendedor
                                    fila['misma_fraccion'] = True

                                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct",
                                                  "Nov", "Dic"];
                                    fecha_1 = unicode(
                                        datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                    parts_1 = fecha_1.split("/")
                                    year_1 = parts_1[2];
                                    mes_1 = int(parts_1[1]) - 1;
                                    mes_year = monthNames[mes_1] + "/" + year_1;
                                    fila['mes'] = mes_year

                                    total_vendedor_monto_pagado += fila['monto_pagado']
                                    total_vendedor_monto_vendedor += fila['monto_vendedor']

                                    total_general_monto_pagado += fila['monto_pagado']
                                    total_general_monto_vendedor += fila['monto_vendedor']

                                    fila['monto_pagado'] = unicode('{:,}'.format(fila['monto_pagado'])).replace(",",
                                                                                                                ".")
                                    fila['monto_vendedor'] = unicode('{:,}'.format(fila['monto_vendedor'])).replace(",",
                                                                                                                    ".")

                                    filas_vendedor.append(fila)

                        pagos = []
                        if venta.id == 2652:
                            print "este es"
                        pagos = get_pago_cuotas(venta, fecha_ini_parsed, fecha_fin_parsed, pagos_de_cuotas_ventas,
                                                cant_cuotas_pagadas_ventas)
                        lista_cuotas_ven = []
                        lista_cuotas_ven.append(venta.plan_de_pago_vendedor.cuota_inicial)
                        numero_cuota = venta.plan_de_pago_vendedor.cuota_inicial
                        for i in range(venta.plan_de_pago_vendedor.cantidad_cuotas - 1):
                            numero_cuota += venta.plan_de_pago_vendedor.intervalos
                            lista_cuotas_ven.append(numero_cuota)

                        for pago in pagos:
                            # preguntar por el plan de pago de la venta con el vendedor, si el vendedor lleva un % del pago de acuerdo al nro de cuota que se está pagando
                            try:

                                if pago['id']== 1858020:
                                    print "este es"

                                #if venta.lote.manzana.fraccion.nombre == 'VISTA AL PARANA':
                                #    print "este es"

                                if g_vendedor == "":
                                    g_vendedor = venta.vendedor

                                # if pago['vendedor'] != g_vendedor:
                                if venta.vendedor != g_vendedor:
                                    # Totales por VENDEDOR
                                    if filas_vendedor:
                                        try:
                                            filas_vendedor = sorted(filas_vendedor,
                                                                    key=lambda f: (f['fecha_de_pago_order']))
                                        except Exception, error:
                                            print unicode(error) + ": " + fecha_pago_str
                                        filas_vendedor[0]['mismo_vendedor'] = False
                                        filas.extend(filas_vendedor)
                                        filas_vendedor = []
                                        fila = {}
                                        fila['total_monto_pagado'] = unicode(
                                            '{:,}'.format(total_vendedor_monto_pagado)).replace(",", ".")
                                        fila['total_monto_vendedor'] = unicode(
                                            '{:,}'.format(total_vendedor_monto_vendedor)).replace(",", ".")

                                        total_vendedor_monto_pagado = 0
                                        total_vendedor_monto_vendedor = 0

                                        fila['ultimo_pago'] = True
                                        filas.append(fila)
                                    g_vendedor = venta.vendedor
                                    ok = True

                                    montos = calculo_montos_liquidacion_vendedores(pago, venta, lista_cuotas_ven)
                                    monto_vendedor = montos['monto_vendedor']
                                    fecha_pago_str = unicode(pago['fecha_de_pago'])
                                    try:
                                        fecha_pago = unicode(
                                            datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"))
                                    except Exception, error:
                                        print unicode(error) + ": " + fecha_pago_str

                                    # Se setean los datos de cada fila
                                    fila = {}
                                    fila['mismo_vendedor'] = True
                                    fila['vendedor'] = unicode(venta.vendedor)
                                    fila['plan'] = unicode(venta.plan_de_pago_vendedor)
                                    fila['fecha_de_pago'] = fecha_pago
                                    fila['fecha_de_pago_order'] = pago['fecha_de_pago']
                                    fila['lote'] = unicode(pago['lote'])
                                    fila['cliente'] = unicode(venta.cliente)
                                    fila['nro_cuota'] = unicode(pago['nro_cuota_y_total'])
                                    fila['total_de_cuotas'] = unicode('{:,}'.format(int(pago['monto']))).replace(",",
                                                                                                                 ".")
                                    fila['monto_vendedor'] = unicode('{:,}'.format(monto_vendedor)).replace(",", ".")

                                    cuotas_detalles = get_cuota_information_by_lote(pago['lote'].id,
                                                                                    int(pago['nro_cuota']), True, True,
                                                                                    venta)
                                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct",
                                                  "Nov", "Dic"];
                                    fecha_1 = cuotas_detalles[0]['fecha']
                                    parts_1 = fecha_1.split("/")
                                    year_1 = parts_1[2];
                                    mes_1 = int(parts_1[1]) - 1;
                                    mes_year = monthNames[mes_1] + "/" + year_1;
                                    fila['mes'] = mes_year

                                    # if venta.lote.manzana.fraccion != g_fraccion:
                                    if monto_vendedor != 0:
                                        ok = False
                                        # Se suman los TOTALES por VENDEDOR
                                        total_vendedor_monto_vendedor += int(monto_vendedor)
                                        total_vendedor_monto_pagado += int(pago['monto'])

                                        # Acumulamos para los TOTALES GENERALES
                                        total_general_monto_pagado += int(pago['monto'])
                                        total_general_monto_vendedor += int(monto_vendedor)

                                        filas_vendedor.append(fila)

                                else:
                                    montos = calculo_montos_liquidacion_vendedores(pago, venta, lista_cuotas_ven)
                                    monto_vendedor = montos['monto_vendedor']
                                    fecha_pago_str = unicode(pago['fecha_de_pago'])
                                    try:
                                        fecha_pago = unicode(
                                            datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"))
                                    except Exception, error:
                                        print error + ": " + fecha_pago_str

                                    # Se setean los datos de cada fila
                                    fila = {}
                                    fila['mismo_vendedor'] = True
                                    fila['vendedor'] = unicode(venta.vendedor)
                                    fila['plan'] = unicode(venta.plan_de_pago_vendedor)
                                    fila['fecha_de_pago'] = fecha_pago
                                    fila['fecha_de_pago_order'] = pago['fecha_de_pago']
                                    fila['lote'] = unicode(pago['lote'])
                                    fila['cliente'] = unicode(venta.cliente)
                                    fila['nro_cuota'] = unicode(pago['nro_cuota_y_total'])
                                    fila['total_de_cuotas'] = unicode('{:,}'.format(int(pago['monto']))).replace(",",
                                                                                                                 ".")
                                    fila['monto_vendedor'] = unicode('{:,}'.format(monto_vendedor)).replace(",", ".")

                                    cuotas_detalles = get_cuota_information_by_lote(pago['lote'].id,
                                                                                    int(pago['nro_cuota']), True, True,
                                                                                    venta)
                                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct",
                                                  "Nov", "Dic"];
                                    fecha_1 = cuotas_detalles[0]['fecha']
                                    parts_1 = fecha_1.split("/")
                                    year_1 = parts_1[2];
                                    mes_1 = int(parts_1[1]) - 1;
                                    mes_year = monthNames[mes_1] + "/" + year_1;
                                    fila['mes'] = mes_year

                                    # if venta.lote.manzana.fraccion != g_fraccion:
                                    if monto_vendedor != 0:
                                        ok = False
                                        # Se suman los TOTALES por VENDEDOR
                                        total_vendedor_monto_vendedor += int(monto_vendedor)
                                        total_vendedor_monto_pagado += int(pago['monto'])

                                        # Acumulamos para los TOTALES GENERALES
                                        total_general_monto_pagado += int(pago['monto'])
                                        total_general_monto_vendedor += int(monto_vendedor)

                                        filas_vendedor.append(fila)

                            except Exception, error:
                                print "Error: " + unicode(error) + ", Id Pago: " + unicode(
                                    pago['id']) + ", Fraccion: " + unicode(pago['fraccion']) + ", lote: " + unicode(
                                    pago['lote']) + " Nro cuota: " + unicode(unicode(pago['nro_cuota_y_total']))

                # Totales GENERALES
                # filas = sorted(filas, key=lambda f: f['fecha_de_pago'])
                if filas_vendedor:
                    filas_vendedor = sorted(filas_vendedor, key=lambda f: (f['fecha_de_pago_order']))
                    filas_vendedor[0]['mismo_vendedor'] = False
                    filas.extend(filas_vendedor)

                    fila = {}
                    fila['total_monto_pagado'] = unicode('{:,}'.format(total_vendedor_monto_pagado)).replace(",", ".")
                    fila['total_monto_vendedor'] = unicode('{:,}'.format(total_vendedor_monto_vendedor)).replace(",",
                                                                                                                 ".")
                    total_fraccion_monto_vendedor = 0
                    total_fraccion_monto_pagado = 0
                    fila['ultimo_pago'] = True
                    filas.append(fila)

                fila = {}
                fila['total_general_pagado'] = unicode('{:,}'.format(total_general_monto_pagado)).replace(",", ".")
                fila['total_general_vendedor'] = unicode('{:,}'.format(total_general_monto_vendedor)).replace(",", ".")
                ley = int(total_general_monto_pagado * 0.015)
                filas.append(fila)
                filas[0]['mismo_vendedor'] = False

                # ultimo="&busqueda_label="+busqueda_label+"&busqueda="+vendedor_id+"&fecha_ini="+fecha_ini+"&fecha_fin="+fecha_fin

                lista = filas

                #                 paginator = Paginator(cuotas, 25)
                #                 page = request.GET.get('page')
                #                 try:
                #                     lista = paginator.page(page)
                #                 except PageNotAnInteger:
                #                     lista = paginator.page(1)
                #                 except EmptyPage:
                #                     lista = paginator.page(paginator.num_pages)
                c = RequestContext(request, {
                    'lista_cuotas': lista,
                    'fecha_ini': fecha_ini,
                    'fecha_fin': fecha_fin,
                    # 'busqueda':vendedor_id,
                    # 'busqueda_label':busqueda_label,
                    # 'ultimo': ultimo
                })
                return HttpResponse(t.render(c))
            else:
                t = loader.get_template('index2.html')
                grupo = request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))
        else:
            return HttpResponseRedirect(reverse('login'))


def liquidacion_gerentes(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
                if (filtros_establecidos(request.GET, 'liquidacion_gerentes') == False):
                    t = loader.get_template('informes/liquidacion_gerentes.html')
                    c = RequestContext(request, {
                        'object_list': [],
                    })
                    return HttpResponse(t.render(c))
                else:  # Parametros seteados
                    t = loader.get_template('informes/liquidacion_gerentes.html')
                    fecha = request.GET['fecha']
                    tipo_liquidacion = request.GET['tipo_liquidacion']
                    fecha_ini = request.GET['fecha_ini']
                    fecha_fin = request.GET['fecha_fin']
                    fecha_ini_parsed = unicode(datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date())
                    fecha_fin_parsed = unicode(datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date())
                    query = (
                        '''
                    SELECT pc.* FROM principal_pagodecuotas pc, principal_lote l, principal_manzana m, principal_fraccion f
                    WHERE pc.fecha_de_pago >= \'''' + fecha_ini_parsed +
                        '''\' AND pc.fecha_de_pago <= \'''' + fecha_fin_parsed +
                        '''\'
                    AND (pc.lote_id = l.id AND l.manzana_id=m.id AND m.fraccion_id=f.id) ORDER BY pc.vendedor_id, f.id, pc.fecha_de_pago
                    '''
                    )

                    lista_pagos = list(PagoDeCuotas.objects.raw(query))

                    if tipo_liquidacion == 'gerente_ventas':
                        tipo_gerente = "Gerente de Ventas"
                    if tipo_liquidacion == 'gerente_admin':
                        tipo_gerente = "Gerente Administrativo"

                    # totales por vendedor
                    total_importe = 0
                    total_comision = 0

                    # totales generales
                    total_general_importe = 0
                    total_general_comision = 0
                    k = 0  # variable de control
                    cuotas = []
                    # Seteamos los datos de las filas
                    for i, cuota_item in enumerate(lista_pagos):
                        nro_cuota = get_nro_cuota(cuota_item)
                        cuota = {}
                        com = 0
                        # Esta es una regla de negocio, los vendedores cobran comisiones segun el numero de cuota, maximo hasta la cuota Nro 9.
                        # Si el plan de pago tiene hasta 12 cuotas, los vendedores cobran una comision sobre todas las cuotas.
                        cuotas_para_vendedor = ((cuota_item.plan_de_pago_vendedor.cantidad_cuotas) * (
                            cuota_item.plan_de_pago_vendedor.intervalos)) - cuota_item.plan_de_pago_vendedor.cuota_inicial
                        # A los vendedores le corresponde comision por las primeras 4 (maximo 5) cuotas impares.
                        if ((nro_cuota % 2 != 0 and nro_cuota <= cuotas_para_vendedor) or (
                                        cuota_item.plan_de_pago.cantidad_de_cuotas <= 12 and nro_cuota <= 12)):
                            if k == 0:
                                # Guardamos el vendedor asociado a la primera cuota que cumple con la condicion, para tener algo con que comparar.
                                vendedor_actual = cuota_item.vendedor.id
                                fraccion_actual = cuota_item.lote.manzana.fraccion
                            k += 1
                            # print k
                            if (
                                            cuota_item.vendedor.id == vendedor_actual and cuota_item.lote.manzana.fraccion == fraccion_actual):
                                # comision de las cuotas
                                com = int(cuota_item.total_de_cuotas * (
                                    float(cuota_item.plan_de_pago_vendedor.porcentaje_de_cuotas) / float(100)))
                                if (cuota_item.venta.entrega_inicial):
                                    # comision de la entrega inicial, si la hubiere
                                    com_inicial = int(cuota_item.venta.entrega_inicial * (
                                        float(cuota_item.plan_de_pago_vendedor.porcentaje_cuota_inicial) / float(100)))
                                    cuota['concepto'] = "Entrega Inicial"
                                    cuota['cuota_nro'] = unicode(0) + '/' + unicode(
                                        cuota_item.plan_de_pago.cantidad_de_cuotas)
                                    cuota['comision'] = unicode('{:,}'.format(com_inicial)).replace(",", ".")
                                else:
                                    cuota['concepto'] = "Pago de Cuota"
                                    cuota['cuota_nro'] = unicode(nro_cuota) + '/' + unicode(
                                        cuota_item.plan_de_pago.cantidad_de_cuotas)
                                    cuota['comision'] = unicode('{:,}'.format(com)).replace(",", ".")
                                cuota['fraccion'] = unicode(cuota_item.lote.manzana.fraccion)
                                cuota['vendedor'] = unicode(cuota_item.vendedor)
                                cuota['fraccion_id'] = cuota_item.lote.manzana.fraccion.id
                                cuota['lote'] = unicode(cuota_item.lote)
                                cuota['fecha_pago'] = unicode(cuota_item.fecha_de_pago)
                                cuota['importe'] = unicode('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".")

                                # Sumamos los totales por vendedor
                                total_importe += cuota_item.total_de_cuotas
                                total_comision += com
                                # Guardamos el ultimo lote que cumple la condicion en dos variables, por si se convierta en el ultimo lote para cerrar la fraccion
                                # actual, o por si sea el ultimo lote de la lista.
                                anterior = cuota
                                ultimo = cuota
                                # Hay cambio de lote pero NO es el ultimo elemento todavia
                            else:
                                com = int(cuota_item.total_de_cuotas * (
                                    float(cuota_item.plan_de_pago_vendedor.porcentaje_de_cuotas) / float(100)))
                                if (cuota_item.venta.entrega_inicial):
                                    # comision de la entrega inicial, si la hubiere
                                    com_inicial = int(cuota_item.venta.entrega_inicial * (
                                        float(cuota_item.plan_de_pago_vendedor.porcentaje_cuota_inicial) / float(100)))
                                    cuota['concepto'] = "Entrega Inicial"
                                    cuota['cuota_nro'] = unicode(0) + '/' + unicode(
                                        cuota_item.plan_de_pago.cantidad_de_cuotas)
                                    cuota['comision'] = unicode('{:,}'.format(com_inicial)).replace(",", ".")
                                else:
                                    cuota['concepto'] = "Pago de Cuota"
                                    cuota['cuota_nro'] = unicode(nro_cuota) + '/' + unicode(
                                        cuota_item.plan_de_pago.cantidad_de_cuotas)
                                    cuota['comision'] = unicode('{:,}'.format(com)).replace(",", ".")
                                cuota['fraccion'] = unicode(cuota_item.lote.manzana.fraccion)
                                cuota['vendedor'] = unicode(cuota_item.vendedor)
                                cuota['fraccion_id'] = cuota_item.lote.manzana.fraccion.id
                                cuota['lote'] = unicode(cuota_item.lote)
                                cuota['fecha_pago'] = unicode(cuota_item.fecha_de_pago)
                                cuota['importe'] = unicode('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".")
                                cuota['total_importe'] = unicode('{:,}'.format(total_importe)).replace(",", ".")
                                cuota['total_comision'] = unicode('{:,}'.format(total_comision)).replace(",", ".")

                                # Se CERAN  los TOTALES por VENDEDOR
                                total_importe = 0
                                total_comision = 0

                                # Sumamos los totales por fraccion
                                total_importe += cuota_item.total_de_cuotas
                                total_comision += com
                                vendedor_actual = cuota_item.vendedor.id
                                fraccion_actual = cuota_item.lote.manzana.fraccion
                                ultimo = cuota
                            total_general_importe += cuota_item.total_de_cuotas
                            total_general_comision += com
                            cuotas.append(cuota)
                            # Si es el ultimo lote, cerramos totales de fraccion
                        if (len(lista_pagos) - 1 == i):
                            try:
                                ultimo['total_importe'] = unicode('{:,}'.format(total_importe)).replace(",", ".")
                                ultimo['total_comision'] = unicode('{:,}'.format(total_comision)).replace(",", ".")
                                ultimo['total_general_importe'] = unicode('{:,}'.format(total_general_importe)).replace(
                                    ",", ".")
                                ultimo['total_general_comision'] = unicode(
                                    '{:,}'.format(total_general_comision)).replace(",", ".")
                            except Exception, error:
                                print error
                                pass

                    monto_calculado = int(math.ceil((float(total_general_importe) * float(0.1)) / float(2)))
                    monto_calculado = unicode('{:,}'.format(monto_calculado)).replace(",", ".")

                c = RequestContext(request, {
                    'monto_calculado': monto_calculado,
                    'cuotas': cuotas,
                    'fecha': fecha,
                    'fecha_ini': fecha_ini,
                    'fecha_fin': fecha_fin,
                    'tipo_liquidacion': tipo_liquidacion,
                    'tipo_gerente': tipo_gerente
                })
                return HttpResponse(t.render(c))
            else:
                t = loader.get_template('index2.html')
                grupo = request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))
        else:
            return HttpResponseRedirect(reverse('login'))


def informe_movimientos(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_FICHA_LOTE):
                if (filtros_establecidos(request.GET, 'informe_movimientos') == False):
                    t = loader.get_template('informes/informe_movimientos.html')
                    c = RequestContext(request, {
                        'object_list': [],
                    })
                    return HttpResponse(t.render(c))
                else:  # Parametros seteados
                    t = loader.get_template('informes/informe_movimientos.html')
                    lote_ini_orig = request.GET['lote_ini']
                    lote_fin_orig = request.GET['lote_fin']
                    fecha_ini = request.GET['fecha_ini']
                    fecha_fin = request.GET['fecha_fin']
                    lote_ini_parsed = unicode(lote_ini_orig)
                    lote_fin_parsed = unicode(lote_fin_orig)
                    fecha_ini_parsed = None
                    fecha_fin_parsed = None
                    lotes = []
                    lotes.append(lote_ini_parsed)
                    lotes.append(lote_fin_parsed)
                    # print lotes
                    rango_lotes_id = []
                    try:
                        for l in lotes:
                            fraccion_int = int(l[0:3])
                            manzana_int = int(l[4:7])
                            lote_int = int(l[8:])
                            manzana = Manzana.objects.get(fraccion_id=fraccion_int, nro_manzana=manzana_int)
                            lote = Lote.objects.get(manzana=manzana.id, nro_lote=lote_int)
                            rango_lotes_id.append(lote.id)
                        print rango_lotes_id
                    except Exception, error:
                        print error
                    lote_ini = str(rango_lotes_id[0])
                    lote_fin = str(rango_lotes_id[1])
                    lote = Lote.objects.get(id=int(lote_ini))
                    lista_movimientos = []
                    print 'lote inicial->' + unicode(lote_ini)
                    print 'lote final->' + unicode(lote_fin)
                    if fecha_ini != '' and fecha_fin != '':
                        fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date()
                        fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date()
                        try:
                            lista_ventas = Venta.objects.filter(lote_id__range=(lote_ini, lote_fin)).order_by(
                                'lote__nro_lote')
                            lista_reservas = Reserva.objects.filter(lote_id__range=(lote_ini, lote_fin),
                                                                    fecha_de_reserva__range=(
                                                                        fecha_ini_parsed, fecha_fin_parsed))
                            lista_cambios = CambioDeLotes.objects.filter(
                                Q(lote_nuevo_id__range=(lote_ini, lote_fin)) | Q(
                                    lote_a_cambiar__range=(lote_ini, lote_fin)),
                                fecha_de_cambio__range=(fecha_ini_parsed, fecha_fin_parsed))
                            lista_transferencias = TransferenciaDeLotes.objects.filter(
                                lote_id__range=(lote_ini, lote_fin),
                                fecha_de_transferencia__range=(fecha_ini_parsed, fecha_fin_parsed))
                        except Exception, error:
                            print error
                            lista_ventas = []
                            lista_reservas = []
                            lista_cambios = []
                            lista_transferencias = []
                            pass
                    else:
                        try:
                            lista_ventas = Venta.objects.filter(lote_id__range=(lote_ini, lote_fin)).order_by(
                                'lote__nro_lote')
                            lista_cambios = CambioDeLotes.objects.filter(
                                Q(lote_nuevo_id__range=(lote_ini, lote_fin)) | Q(
                                    lote_a_cambiar__range=(lote_ini, lote_fin)))
                            lista_reservas = Reserva.objects.filter(lote_id__range=(lote_ini, lote_fin))
                            lista_transferencias = TransferenciaDeLotes.objects.filter(
                                lote_id__range=(lote_ini, lote_fin))
                        except Exception, error:
                            print error
                            lista_ventas = []
                            lista_reservas = []
                            lista_cambios = []
                            lista_transferencias = []
                            pass

                    if lista_ventas:
                        print('Hay ventas asociadas a este lote')
                        lista_movimientos = []
                        # En este punto tenemos ventas asociadas a este lote
                        try:
                            for item_venta in lista_ventas:
                                try:
                                    resumen_venta = {}
                                    fecha_venta_str = unicode(item_venta.fecha_de_venta)
                                    resumen_venta['fecha_de_venta'] = unicode(
                                        datetime.datetime.strptime(fecha_venta_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                                    resumen_venta['lote'] = item_venta.lote
                                    resumen_venta['cliente'] = item_venta.cliente
                                    resumen_venta['cantidad_de_cuotas'] = item_venta.plan_de_pago.cantidad_de_cuotas
                                    resumen_venta['precio_final'] = unicode(
                                        '{:,}'.format(item_venta.precio_final_de_venta)).replace(",", ".")
                                    resumen_venta['entrega_inicial'] = unicode(
                                        '{:,}'.format(item_venta.entrega_inicial)).replace(",", ".")
                                    resumen_venta['tipo_de_venta'] = item_venta.plan_de_pago.tipo_de_plan
                                    RecuperacionDeLotes.objects.get(venta=item_venta.id)
                                    try:
                                        venta_pagos_query_set = get_pago_cuotas_2(item_venta, fecha_ini_parsed,
                                                                                  fecha_fin_parsed)
                                        resumen_venta['recuperacion'] = True
                                    except PagoDeCuotas.DoesNotExist:
                                        venta_pagos_query_set = []
                                except RecuperacionDeLotes.DoesNotExist:
                                    print 'se encontro la venta no recuperada, la venta actual'
                                    try:
                                        venta_pagos_query_set = get_pago_cuotas_2(item_venta, fecha_ini_parsed,
                                                                                  fecha_fin_parsed)
                                        resumen_venta['recuperacion'] = False
                                    except PagoDeCuotas.DoesNotExist:
                                        venta_pagos_query_set = []

                                ventas_pagos_list = []
                                ventas_pagos_list.insert(0,
                                                         resumen_venta)  # El primer elemento de la lista de pagos es el resumen de la venta
                                saldo_anterior = item_venta.precio_final_de_venta
                                monto = item_venta.entrega_inicial
                                saldo = saldo_anterior - monto
                                tipo_de_venta = item_venta.plan_de_pago.tipo_de_plan
                                for pago in venta_pagos_query_set:
                                    saldo_anterior = saldo
                                    monto = long(pago['monto'])
                                    saldo = saldo_anterior - monto
                                    cuota = {}
                                    cuota['vencimiento'] = ""
                                    cuota['tipo_de_venta'] = tipo_de_venta
                                    fecha_pago_str = unicode(pago['fecha_de_pago'])
                                    cuota['fecha_de_pago'] = unicode(
                                        datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"))
                                    cuota['id'] = pago['id']
                                    cuota['nro_cuota'] = pago['nro_cuota_y_total']

                                    cuotas_detalles = []
                                    cuotas_detalles = get_cuota_information_by_lote(pago['lote'].id,
                                                                                    int(pago['nro_cuota']), True, True,
                                                                                    item_venta)
                                    cuota['vencimiento'] = cuota['vencimiento'] + unicode(
                                        cuotas_detalles[0]['fecha']) + ' '

                                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct",
                                                  "Nov", "Dic"];
                                    fecha_1 = cuota['vencimiento']
                                    parts_1 = fecha_1.split("/")
                                    year_1 = parts_1[2];
                                    mes_1 = int(parts_1[1]) - 1;
                                    mes_year = monthNames[mes_1] + "/" + year_1;
                                    cuota['mes'] = mes_year

                                    cuota['saldo_anterior'] = unicode('{:,}'.format(int(saldo_anterior))).replace(",",
                                                                                                                  ".")
                                    cuota['monto'] = unicode('{:,}'.format(int(pago['monto']))).replace(",", ".")
                                    cuota['saldo'] = unicode('{:,}'.format(int(saldo))).replace(",", ".")
                                    ventas_pagos_list.append(cuota)
                                lista_movimientos.append(ventas_pagos_list)
                        except Exception, error:
                            print error

                    mostrar_transferencias = False
                    mostrar_mvtos = False
                    mostrar_reservas = False
                    mostrar_cambios = False

                    if lista_movimientos:
                        mostrar_mvtos = True
                    if lista_cambios:
                        mostrar_cambios = True
                    if lista_reservas:
                        mostrar_reservas = True
                    if lista_transferencias:
                        mostrar_transferencias = True

                    ultimo = "&lote_ini=" + lote_ini_orig + "&lote_fin=" + lote_fin_orig + "&fecha_ini=" + fecha_ini + "&fecha_fin=" + fecha_fin

                    lista = lista_movimientos
                    #                     paginator = Paginator(lista_movimientos, 25)
                    #                     page = request.GET.get('page')
                    #                     try:
                    #                         lista = paginator.page(page)
                    #                     except PageNotAnInteger:
                    #                         lista = paginator.page(1)
                    #                     except EmptyPage:
                    #                         lista = paginator.page(paginator.num_pages)

                    c = RequestContext(request, {
                        'lista_ventas': lista,
                        'lista_cambios': lista_cambios,
                        'lista_transferencias': lista_transferencias,
                        'lista_reservas': lista_reservas,
                        'mostrar_transferencias': mostrar_transferencias,
                        'mostrar_reservas': mostrar_reservas,
                        'mostrar_cambios': mostrar_cambios,
                        'mostrar_mvtos': mostrar_mvtos,
                        'lote_ini': lote_ini_orig,
                        'lote_fin': lote_fin_orig,
                        'fecha_ini': fecha_ini,
                        'fecha_fin': fecha_fin,
                        'ultimo': ultimo,
                        'comentarios': lote.comentarios
                    })
                    return HttpResponse(t.render(c))
            else:
                t = loader.get_template('index2.html')
                grupo = request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))
        else:
            return HttpResponseRedirect(reverse('login'))



            # def lotes_libres_reporte_excel(request):

            # # TODO: Danilo, utiliza este template para poner tu logi
            # fraccion_ini=request.GET['fraccion_ini']
            # fraccion_fin=request.GET['fraccion_fin']
            # object_list = []
            # if fraccion_ini and fraccion_fin:
            #     manzanas = Manzana.objects.filter(fraccion_id__range=(fraccion_ini, fraccion_fin)).order_by('fraccion', 'nro_manzana')
            #     for m in manzanas:
            #         lotes = Lote.objects.filter(manzana=m.id, estado="1").order_by('nro_lote')
            #         for l in lotes:
            #             object_list.append(l)
            # else:
            #     object_list = Lote.objects.filter(estado="1").order_by('nro_lote')
            #
            #
            # #Totales por FRACCION
            # total_importe_cuotas = 0
            # total_contado_fraccion = 0
            # total_credito_fraccion = 0
            # total_superficie_fraccion = 0
            # total_lotes = 0
            #
            # #Totales GENERALES
            # total_general_cuotas = 0
            # total_general_contado = 0
            # total_general_credito = 0
            # total_general_superficie = 0
            # total_general_lotes = 0
            #
            # g_fraccion = ''
            #
            # lotes = []
            # for index, lote_item in enumerate(object_list):
            #     lote={}
            #     # Se setean los datos de cada fila
            #     precio_cuota=int(math.ceil(lote_item.precio_credito/130))
            #     lote['fraccion_id']=unicode(lote_item.manzana.fraccion.id)
            #     lote['fraccion']=unicode(lote_item.manzana.fraccion)
            #     lote['lote']= lote_item.codigo_paralot
            #     lote['superficie']=lote_item.superficie
            #     lote['precio_contado']=unicode('{:,}'.format(lote_item.precio_contado)).replace(",", ".")
            #     lote['precio_credito']=unicode('{:,}'.format(lote_item.precio_credito)).replace(",", ".")
            #     lote['importe_cuota']=unicode('{:,}'.format(precio_cuota)).replace(",", ".")
            #     lote['misma_fraccion'] = True
            #     lote['ultimo_lote'] = False
            #     if g_fraccion == '':
            #         g_fraccion = lote_item.manzana.fraccion
            #
            #
            #
            #     # Se suman los TOTALES por FRACCION
            #     total_superficie_fraccion += lote_item.superficie
            #     total_contado_fraccion += lote_item.precio_contado
            #     total_credito_fraccion += lote_item.precio_credito
            #     total_importe_cuotas += precio_cuota
            #     total_lotes += 1
            #     #Esteee
            #
            #     # Se suman los TOTALES GENERALES
            #     total_general_cuotas += precio_cuota
            #     total_general_contado += lote_item.precio_contado
            #     total_general_credito += lote_item.precio_credito
            #     total_general_superficie += lote_item.superficie
            #     total_general_lotes += 1
            #
            #     #Es el ultimo lote, cerrar totales de fraccion
            #     if (len(object_list)-1 == index):
            #         lote['ultimo_lote'] = True
            #         lote['total_importe_cuotas'] = unicode('{:,}'.format(total_importe_cuotas)).replace(",", ".")
            #         lote['total_credito_fraccion'] =  unicode('{:,}'.format(total_credito_fraccion)).replace(",", ".")
            #         lote['total_contado_fraccion'] =  unicode('{:,}'.format(total_contado_fraccion)).replace(",", ".")
            #         lote['total_superficie_fraccion'] =  unicode('{:,}'.format(total_superficie_fraccion)).replace(",", ".")
            #         lote['total_lotes'] =  unicode('{:,}'.format(total_lotes)).replace(",", ".")
            #
            #         lote['total_general_cuotas'] = unicode('{:,}'.format(total_general_cuotas)).replace(",", ".")
            #         lote['total_general_credito'] =  unicode('{:,}'.format(total_general_credito)).replace(",", ".")
            #         lote['total_general_contado'] =  unicode('{:,}'.format(total_general_contado)).replace(",", ".")
            #         lote['total_general_superficie'] =  unicode('{:,}'.format(total_general_superficie)).replace(",", ".")
            #         lote['total_general_lotes'] =  unicode('{:,}'.format(total_general_lotes)).replace(",", ".")
            #
            #     #Hay cambio de lote pero NO es el ultimo elemento todavia
            #     elif (lote_item.manzana.fraccion.id != object_list[index+1].manzana.fraccion.id):
            #         lote['ultimo_lote'] = True
            #         lote['total_importe_cuotas'] = unicode('{:,}'.format(total_importe_cuotas)).replace(",", ".")
            #         lote['total_credito_fraccion'] =  unicode('{:,}'.format(total_credito_fraccion)).replace(",", ".")
            #         lote['total_contado_fraccion'] =  unicode('{:,}'.format(total_contado_fraccion)).replace(",", ".")
            #         lote['total_superficie_fraccion'] =  unicode('{:,}'.format(total_superficie_fraccion)).replace(",", ".")
            #         lote['total_lotes'] =  unicode('{:,}'.format(total_lotes)).replace(",", ".")
            #     # Se CERAN  los TOTALES por FRACCION
            #         total_importe_cuotas = 0
            #         total_contado_fraccion = 0
            #         total_credito_fraccion = 0
            #         total_superficie_fraccion = 0
            #         total_lotes = 0
            #
            #     if lote_item.manzana.fraccion != g_fraccion:
            #         g_fraccion = lote_item.manzana.fraccion
            #         lote['misma_fraccion'] = False
            #     lotes.append(lote)
            # lotes[0]['misma_fraccion'] = False
            # #esteee
            # wb = xlwt.Workbook(encoding='utf-8')
            # sheet = wb.add_sheet('test', cell_overwrite_ok=True)
            # sheet.paper_size_code = 1
            # style = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
            #                           'font: name Gill Sans MT Condensed, bold True; align: horiz center')
            # style2 = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
            #                      'font: name Gill Sans MT Condensed, bold True, height 160;')
            # style3 = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160 ; align: horiz center')
            # style4 = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160 ; align: horiz right')
            # style5 = xlwt.easyxf('pattern: pattern solid, fore_colour white;''font: name Gill Sans MT Condensed, bold True, height 160 ; align: horiz right')
            #
            # style_normal = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160;')
            # style_normal_centrado = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160; align: horiz center')
            #
            # style_fraccion = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
            #                           'font: name Gill Sans MT Condensed, bold True; align: horiz center')
            # #Titulo
            # #sheet.write_merge(0,0,0,7, 'PROPAR S.R.L.' ,style3)
            # #sheet.write_merge(1,1,1,7, 'Sistema de Control de Loteamiento' ,style3)
            #
            # #sheet.header_str = 'PROPAR S.R.L.'
            # periodo_1 = fraccion_ini
            # periodo_2 = fraccion_fin
            # usuario = unicode(request.user)
            # sheet.header_str = (
            #  u"&LFecha: &D Hora: &T \nUsuario: "+usuario+" "
            #  u"&CPROPAR S.R.L.\n LOTES LIBRES "
            #  u"&RFraccion del "+periodo_1+" al "+periodo_2+" \nPage &P of &N"
            #  )
            # #sheet.footer_str = 'things'
            #
            #
            #
            # c=0
            # sheet.write_merge(c,c,0,4, "Lotes Libres", style)
            # #contador de filas
            #
            # for lote in lotes:
            #     c+=1
            #     '''
            #     sheet.write(c, 0, lote['fraccion'])
            #     sheet.write(c, 1, lote['fraccion_id'])
            #     '''
            #     try:
            #         if lote['total_importe_cuotas'] and lote['ultimo_lote'] == False:
            #             c += 1
            #             sheet.write_merge(c,c,0,4, "Cantidad de Lotes libres de la fraccion: "+unicode(lote['total_lotes']), style2)
            #             '''
            #             sheet.write(c, 3, lote['total_superficie_fraccion'], style2)
            #             sheet.write(c, 4, lote['total_contado_fraccion'], style2)
            #             sheet.write(c, 5, lote['total_credito_fraccion'], style2)
            #             sheet.write(c, 6, lote['total_importe_cuotas'], style2)
            #             '''
            #     except Exception, error:
            #         print error
            #         pass
            #
            #     if lote['misma_fraccion'] == False:
            #         sheet.write_merge(c,c,0,4, "Fraccion: "+unicode(lote['fraccion']), style)
            #         c+=1
            #         sheet.write(c, 0, "Lote Nro.", style)
            #         sheet.write(c, 1, "Superficie", style)
            #         sheet.write(c, 2, "Precio Contado", style)
            #         sheet.write(c, 3, "Precio Credito", style)
            #         sheet.write(c, 4, "Precio Cuota", style)
            #         c+=1
            #
            #     sheet.write(c, 0, lote['lote'], style_normal_centrado)
            #     sheet.write(c, 1, unicode(lote['superficie']) + ' mts2', style_normal_centrado)
            #     sheet.write(c, 2, lote['precio_contado'], style4)
            #     sheet.write(c, 3, lote['precio_credito'], style4)
            #     sheet.write(c, 4, lote['importe_cuota'], style4)
            #     try:
            #         if lote['ultimo_lote'] == True:
            #             c += 1
            #             sheet.write_merge(c,c,0,4, "Cantidad de Lotes libres de la fraccion: "+unicode(lote['total_lotes']), style2)
            #             '''
            #             sheet.write(c, 3, lote['total_superficie_fraccion'], style2)
            #             sheet.write(c, 4, lote['total_contado_fraccion'], style2)
            #             sheet.write(c, 5, lote['total_credito_fraccion'], style2)
            #             sheet.write(c, 6, lote['total_importe_cuotas'], style2)
            #             '''
            #         if lote['total_general_cuotas']:
            #             c += 1
            #             sheet.write_merge(c,c,0,4, "Cantidad total de Lotes libres: "+unicode(lote['total_general_lotes']), style2)
            #             '''
            #             sheet.write(c, 3, lote['total_general_superficie'], style2)
            #             sheet.write(c, 4, lote['total_general_contado'], style2)
            #             sheet.write(c, 5, lote['total_general_credito'], style2)
            #             sheet.write(c, 6, lote['total_general_cuotas'], style2)
            #             '''
            #     except Exception, error:
            #         print error
            #         pass
            # response = HttpResponse(content_type='application/vnd.ms-excel')
            # # Crear un nombre intuitivo
            # fecha_actual= datetime.datetime.now().date()
            # fecha_str = unicode(fecha_actual)
            # fecha = unicode(datetime.datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
            # response['Content-Disposition'] = 'attachment; filename=' + 'lotes_libres_fraccion_del_'+periodo_1+'_a_'+periodo_2+'_'+fecha+'.xls'
            # wb.save(response)
            # return response


def informe_cuotas_devengadas(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_FICHA_LOTE):
                if (filtros_establecidos(request.GET, 'informe_cuotas_devengadas') == False):
                    t = loader.get_template('informes/informe_cuotas_devengadas.html')
                    c = RequestContext(request, {
                        'object_list': [],
                    })
                    return HttpResponse(t.render(c))
                else:  # Parametros seteados
                    t = loader.get_template('informes/informe_cuotas_devengadas.html')
                    fecha_ini = request.GET['fecha_ini']
                    fecha_fin = request.GET['fecha_fin']
                    fraccion = request.GET['fraccion']
                    fraccion_label = request.GET['fraccion_label']
                    fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date()
                    fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date()
                    lotes_ordenados = Lote.objects.all().order_by('manzana__fraccion', 'manzana__nro_manzana',
                                                                  'nro_lote')
                    lotes_ordenados2 = []
                    # for lote in lotes_ordenados:
                    #     detalle_lote = get_ultima_venta_no_recuperada_by_lote(unicode(lote.id))
                    #     if detalle_lote!=None:
                    #         if detalle_lote['cant_cuotas_pagadas'] != detalle_lote['cantidad_total_cuotas']:
                    #             prox_vto_date_parsed = datetime.datetime.strptime(unicode(detalle_lote['proximo_vencimiento']), '%d/%m/%Y').date()
                    #             if prox_vto_date_parsed >= fecha_ini_parsed and prox_vto_date_parsed <= fecha_fin_parsed:
                    #                 lotes_ordenados2.append(lote)

                    # esta forma es obtener RawWuerySet, es decir, los modelos del Django a partir de un query estático
                    if fraccion == '':
                        ventas = Venta.objects.raw(
                            '''SELECT * FROM "principal_venta" WHERE "principal_venta"."lote_id" IN (SELECT "id" FROM "principal_lote") AND "principal_venta"."id" NOT IN (SELECT "venta_id" FROM "principal_recuperaciondelotes") ORDER BY lote_id''')
                    else:
                        ventas = Venta.objects.raw(
                            '''SELECT * FROM "principal_venta" WHERE "principal_venta"."lote_id" IN (SELECT id FROM principal_lote WHERE manzana_id IN (SELECT id FROM principal_manzana WHERE fraccion_id = %s)) AND "principal_venta"."id" NOT IN (SELECT "venta_id" FROM "principal_recuperaciondelotes") ORDER BY lote_id''',
                            [fraccion])
                    for venta in ventas:
                        # detalle_lote = get_ultima_venta_no_recuperada_by_lote(unicode(venta.lote_id))
                        detalle_lote = get_cuotas_details_by_lote(unicode(venta.lote_id))
                        if detalle_lote != None:
                            if detalle_lote['cant_cuotas_pagadas'] != detalle_lote['cantidad_total_cuotas']:
                                prox_vto_date_parsed = datetime.datetime.strptime(
                                    unicode(detalle_lote['proximo_vencimiento']), '%d/%m/%Y').date()
                                if prox_vto_date_parsed >= fecha_ini_parsed and prox_vto_date_parsed <= fecha_fin_parsed:
                                    lote = Lote.objects.get(id=venta.lote_id)
                                    lote.boleto_nro = prox_vto_date_parsed
                                    lote.casa_edificada = unicode('{:,}'.format(venta.precio_de_cuota)).replace(",",
                                                                                                                ".")
                                    lote.comentarios = detalle_lote['cant_cuotas_pagadas'] + 1
                                    lotes_ordenados2.append(lote)

                    if request.GET.get('formato-reporte', '') == 'pantalla':
                        ultima_busqueda = "&fecha_ini=" + fecha_ini + "&fecha_fin=" + fecha_fin
                        object_list = lotes_ordenados2

                        c = RequestContext(request, {
                            'object_list': object_list,
                            'ultima_busqueda': ultima_busqueda,
                            'fecha_ini': fecha_ini,
                            'fecha_fin': fecha_fin,
                            'fraccion': fraccion,
                            'fraccion_label': fraccion_label,
                        })
                        return HttpResponse(t.render(c))

                    else:
                        response = listado_lotes_excel(lotes_ordenados)
                        return response

        else:
            return HttpResponseRedirect(reverse('login'))


def informe_cuotas_devengadas_reporte_excel(request):
    fecha_ini = request.GET['fecha_ini']
    fecha_fin = request.GET['fecha_fin']
    fraccion = request.GET['fraccion']
    fraccion_label = request.GET['fraccion_label']
    fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date()
    fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date()
    lotes_ordenados = []
    if fraccion == '':
        ventas = Venta.objects.raw(
            '''SELECT * FROM "principal_venta" WHERE "principal_venta"."lote_id" IN (SELECT "id" FROM "principal_lote") AND "principal_venta"."id" NOT IN (SELECT "venta_id" FROM "principal_recuperaciondelotes") ORDER BY lote_id''')
    else:
        ventas = Venta.objects.raw(
            '''SELECT * FROM "principal_venta" WHERE "principal_venta"."lote_id" IN (SELECT id FROM principal_lote WHERE manzana_id IN (SELECT id FROM principal_manzana WHERE fraccion_id = %s)) AND "principal_venta"."id" NOT IN (SELECT "venta_id" FROM "principal_recuperaciondelotes") ORDER BY lote_id''',
            [fraccion])
    for venta in ventas:
        detalle_lote = get_cuotas_details_by_lote(unicode(venta.lote_id))
        if detalle_lote != None:
            if detalle_lote['cant_cuotas_pagadas'] != detalle_lote['cantidad_total_cuotas']:
                prox_vto_date_parsed = datetime.datetime.strptime(unicode(detalle_lote['proximo_vencimiento']),
                                                                  '%d/%m/%Y').date()
                if prox_vto_date_parsed >= fecha_ini_parsed and prox_vto_date_parsed <= fecha_fin_parsed:
                    lote = Lote.objects.get(id=venta.lote_id)
                    lote.boleto_nro = prox_vto_date_parsed
                    lote.casa_edificada = unicode('{:,}'.format(venta.precio_de_cuota)).replace(",", ".")
                    lote.comentarios = detalle_lote['cant_cuotas_pagadas'] + 1
                    lotes_ordenados.append(lote)

    ultimo = "&fecha_ini=" + fecha_ini + "&fecha_fin=" + fecha_fin + "&fraccion_label=" + fraccion_label + "&fraccion=" + fraccion

    lista = lotes_ordenados

    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    sheet.paper_size_code = 1
    style = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                        'font: name Calibri, bold True, height 200; align: horiz center')
    style2 = xlwt.easyxf('font: name Calibri, height 200;')

    style3 = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz right')

    style4 = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz center')

    # Este estilo pidio Ivan para pulir el informe en una forma visual mas agradable, antes usaba el style4 que es en negrita
    style_titulos_columna_resaltados_centrados = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                                                             'font: name Calibri; align: horiz center')

    # BORDES PARA las columnas de titulos
    borders = xlwt.Borders()
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.DOUBLE
    style_titulos_columna_resaltados_centrados.borders = borders
    usuario = unicode(request.user)

    if fraccion == '':
        sheet.write_merge(0, 0, 0, 4, "CUOTAS DEVENGADAS del " + fecha_ini + " al " + fecha_fin, style)
    else:
        sheet.write_merge(0, 0, 0, 4,
                          "CUOTAS DEVENGADAS de la fraccion " + fraccion_label + " del " + fecha_ini + " al " + fecha_fin,
                          style)

    c = 1

    sheet.write(c, 0, "Lote Nro", style)
    sheet.write(c, 1, "Nombre Fraccion", style)
    sheet.write(c, 2, "Fecha Vto", style)
    sheet.write(c, 3, "Monto Cuota", style)
    sheet.write(c, 4, "Nro Cuota", style)

    c = c + 1

    for lote in lista:
        sheet.write(c, 0, unicode(lote.codigo_paralot), style3)
        sheet.write(c, 1, unicode(lote.manzana.fraccion), style3)
        sheet.write(c, 2, unicode(lote.boleto_nro), style3)
        sheet.write(c, 3, unicode(lote.casa_edificada), style3)
        sheet.write(c, 4, unicode(lote.comentarios), style4)
        c = c + 1

    # Ancho de la columna Lote
    col_lote = sheet.col(0)
    col_lote.width = 256 * 15  # 15 characters wide

    # Ancho de la columna Fraccion
    col_fraccion = sheet.col(1)
    col_fraccion.width = 256 * 26  # 26 characters wide

    # Ancho de la columna Fecha Vto
    col_fecha_vto = sheet.col(2)
    col_fecha_vto.width = 256 * 12  # 12 characters wide

    # Ancho de la columna Monto Cuota
    col_monto_cuota = sheet.col(3)
    col_monto_cuota.width = 256 * 12  # 10 characters wide

    # Ancho de la columna Nro Cuota
    col_nro_cuota = sheet.col(4)
    col_nro_cuota.width = 256 * 12  # 12 characters wide

    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo
    if fraccion == '':
        response[
            'Content-Disposition'] = 'attachment; filename=' + 'informe_cuotas_devengadas' + '_' + fecha_ini + '_al_' + fecha_fin + '.xls'
    else:
        response[
            'Content-Disposition'] = 'attachment; filename=' + 'informe_cuotas_devengadas' + '_' + fraccion_label + '_del_' + fecha_ini + '_al_' + fecha_fin + '.xls'
    wb.save(response)
    return response
def proximos_vencimientos_reporte_excel(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):

                fecha_actual = datetime.datetime.now()

                # FILTROS DISPONIBLES
                filtros = filtros_establecidos(request.GET, 'proximos_vencimientos')

                # OBJETO QUE SE UTILIZA PARA CARGAR TODOS LOS CLIENTES ATRASADOS A MOSTRAR
                clientes_atrasados = []

                # PARAMETROS
                meses_peticion = 1
                fraccion = ''


                fraccion = request.GET['fraccion']
                fecha_inicio = request.GET['fecha_inicio']
                fecha_fin = request.GET['fecha_fin']

            clientes_atrasados = obtener_clientes_con_lotes_por_vencer(fraccion, fecha_inicio, fecha_fin)
            #clientes_atrasados = obtener_clientes_atrasados(filtros, fraccion, meses_peticion)

            if clientes_atrasados:

                wb = xlwt.Workbook(encoding='utf-8')
                sheet = wb.add_sheet('test', cell_overwrite_ok=True)
                sheet.paper_size_code = 1
                # style = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                #                   'font: name Gill Sans MT Condensed, bold True, height 160; align: horiz center')
                # style2 = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160;')
                #
                # style3 = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160 ; align: horiz right')
                #
                # style4 = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160 ; align: horiz center')

                style = xlwt.easyxf('font: name Calibri, bold True; align: horiz center')
                style2 = xlwt.easyxf(
                    'pattern: pattern solid, fore_colour white; font: name Calibri; align: horiz right')
                style3 = xlwt.easyxf('font: name Calibri, height 200; align: horiz left')
                # style4 = xlwt.easyxf('pattern: pattern solid, fore_colour white; font: name Calibri')
                style4 = xlwt.easyxf('font: name Calibri, height 200; align: horiz center')

                nombre_fraccion = Fraccion.objects.get(id=fraccion)
                usuario = unicode(request.user)
                sheet.header_str = (
                    u"&LFecha: &D Hora: &T \nUsuario: " + usuario + " "
                                                                    u"&CPROPAR S.R.L.\n PROXIMOS VENCIMIENTOS " + unicode(
                        nombre_fraccion) + " "
                                           u"&Rango de Fecha: " + unicode(fecha_inicio)+" "u"al "+ unicode(fecha_fin) + " \nPage &P of &N"
                )
                sheet.write_merge(0, 0, 0, 10, "PROXIMOS VENCIMIENTOS " + unicode(nombre_fraccion), style)
                # BORDES PARA las columnas de titulos
                borders = xlwt.Borders()
                borders.top = xlwt.Borders.THIN
                borders.bottom = xlwt.Borders.DOUBLE
                style.borders = borders

                # sheet.write(0, 0, "Cliente", style)
                # sheet.write(0, 1, "Lote", style)
                # sheet.write(0, 2, "C.A.", style)
                # sheet.write(0, 3, "C.P.", style)
                # sheet.write(0, 4, "Importe C", style)
                # sheet.write(0, 5, "Total A.", style)
                # sheet.write(0, 6, "Total P.", style)
                # sheet.write(0, 7, "Total Lote", style)
                # sheet.write(0, 8, "% P.", style)
                # sheet.write(0, 9, "Fecha U.P.", style)

                sheet.write(1, 0, "Cliente", style)
                sheet.write(1, 1, "Telefono", style)
                sheet.write(1, 2, "Celular", style)
                sheet.write(1, 3, "Direccion", style)
                sheet.write(1, 4, "Cod Lote", style)
                sheet.write(1, 5, "Cuotas Atras.", style)
                sheet.write(1, 6, "Cuotas Pag.", style)
                sheet.write(1, 7, "Importe Cuota", style)
                sheet.write(1, 8, "Total Atras.", style)
                sheet.write(1, 9, "Total Pag.", style)
                sheet.write(1, 10, "% Pag.", style)
                sheet.write(1, 11, "Fec Ult.Pago.", style)
                sheet.write(1,12, "Prox Vencimiento", style)

                # Ancho de la columna Nombre
                col_nombre = sheet.col(0)
                col_nombre.width = 256 * 25  # 25 characters wide

                # Ancho de la columna Telefono
                col_lote = sheet.col(1)
                col_lote.width = 256 * 25  # 12 characters wide

                # Ancho de la columna Celular
                col_lote = sheet.col(2)
                col_lote.width = 256 * 26  # 12 characters wide

                # Ancho de la columna Direccion
                col_nro_cuota = sheet.col(3)
                col_nro_cuota.width = 256 * 40  # 6 characters wide

                # Ancho de la columna Lote
                col_nro_cuota = sheet.col(4)
                col_nro_cuota.width = 256 * 15  # 6 characters wide

                # Ancho de la columna Cuotas Atras.
                col_nro_cuota = sheet.col(5)
                col_nro_cuota.width = 256 * 12  # 6 characters wide

                # Ancho de la columna Cuotas Pag.
                col_mes = sheet.col(6)
                col_mes.width = 256 * 12  # 8 characters wide

                # Ancho de la columna Imp. Cuota"
                col_monto_pagado = sheet.col(7)
                col_monto_pagado.width = 256 * 11  # 11 characters wide

                # Ancho de la columna Total Atras
                col_monto_inmo = sheet.col(8)
                col_monto_inmo.width = 256 * 14  # 15 characters wide

                # Ancho de la columna Total Pag
                col_nombre = sheet.col(9)
                col_nombre.width = 256 * 14  # 15 characters wide

                # Ancho de la columna % Pag
                col_nombre = sheet.col(10)
                col_nombre.width = 256 * 6  # 5 characters wide

                # Ancho de la columna Fecha
                col_fecha = sheet.col(11)
                col_fecha.width = 256 * 20  # 12 characters wide

                #ancho de la columna proximo vencimiento
                col_prox_venc = sheet.col(12)
                col_prox_venc.width = 256*20

                i = 0
                c = 2
                # for i in range(len(clientes_atrasados)):
                # sheet.write(c, 0, clientes_atrasados[i]['cliente'],style2)
                # sheet.write(c, 1, unicode(clientes_atrasados[i]['lote']),style4)
                # sheet.write(c, 2, unicode(clientes_atrasados[i]['cuotas_atrasadas']),style4)
                # sheet.write(c, 3, unicode(clientes_atrasados[i]['cuotas_pagadas']),style4)
                # sheet.write(c, 4, unicode(clientes_atrasados[i]['importe_cuota']),style3)
                # sheet.write(c, 5, unicode(clientes_atrasados[i]['total_atrasado']),style3)
                # sheet.write(c, 6, unicode(clientes_atrasados[i]['total_pagado']),style3)
                # # sheet.write(c, 7, unicode(clientes_atrasados[i]['valor_total_lote']),style3)
                # sheet.write(c, 8, unicode(clientes_atrasados[i]['porc_pagado']),style4)
                # sheet.write(c, 9,unicode(clientes_atrasados[i]['fecha_ultimo_pago']),style2)
                # c += 1

                for i in range(len(clientes_atrasados)):
                    sheet.write(c, 0, clientes_atrasados[i]['cliente'], style3)
                    if clientes_atrasados[i]['telefono_laboral'] != '' and clientes_atrasados[i][
                        'telefono_laboral'] != None:
                        sheet.write(c, 1, unicode('tel1: ' + clientes_atrasados[i]['telefono_particular'] + '  tel2: ' +
                                                  clientes_atrasados[i]['telefono_laboral']), style4)
                    else:
                        sheet.write(c, 1, unicode(clientes_atrasados[i]['telefono_particular']), style4)
                    if (clientes_atrasados[i]['celular_1'] != '' and clientes_atrasados[i]['celular_1'] != None) or (
                                    clientes_atrasados[i]['celular_2'] != '' and clientes_atrasados[i][
                                'celular_2'] != None):
                        sheet.write(c, 2, unicode(
                            'cel1: ' + clientes_atrasados[i]['celular_1'] + '  cel2: ' + clientes_atrasados[i][
                                'celular_2']), style4)
                    elif clientes_atrasados[i]['celular_1'] != '' and clientes_atrasados[i]['celular_1'] != None:
                        sheet.write(c, 2, unicode('cel1: ' + clientes_atrasados[i]['celular_1']), style4)
                    elif clientes_atrasados[i]['celular_2'] != '' and clientes_atrasados[i]['celular_2'] != None:
                        sheet.write(c, 2, unicode('cel1: ' + clientes_atrasados[i]['celular_2']), style4)
                    sheet.write(c, 3, unicode(
                        'dir1: ' + clientes_atrasados[i]['direccion_particular'] + '  dir2: ' + clientes_atrasados[i][
                            'direccion_cobro']), style4)
                    sheet.write(c, 4, unicode(clientes_atrasados[i]['lote']), style4)
                    sheet.write(c, 5, unicode(clientes_atrasados[i]['cuotas_atrasadas']), style4)
                    sheet.write(c, 6, unicode(clientes_atrasados[i]['cuotas_pagadas']), style4)
                    sheet.write(c, 7, unicode(clientes_atrasados[i]['importe_cuota']), style4)
                    sheet.write(c, 8, unicode(clientes_atrasados[i]['total_atrasado']), style4)
                    sheet.write(c, 9, unicode(clientes_atrasados[i]['total_pagado']), style4)
                    sheet.write(c, 10, unicode(clientes_atrasados[i]['porc_pagado']), style4)
                    # formateamos la fecha
                    fecha_str = unicode(clientes_atrasados[i]['fecha_ultimo_pago'])
                    if clientes_atrasados[i]['fecha_ultimo_pago'] != 'Dato no disponible':
                        sheet.write(c, 11, unicode(fecha_str), style4)
                    else:
                        sheet.write(c, 11, unicode('Dato no disponible'), style4)

                    sheet.write(c, 12, unicode(clientes_atrasados[i]['proximo_vencimiento']), style4)
                    c += 1

            response = HttpResponse(content_type='application/vnd.ms-excel')
            # Crear un nombre intuitivo
            response['Content-Disposition'] = 'attachment; filename=' + 'proximos_vencimientos_' + unicode(
                nombre_fraccion) + '.xls'
            wb.save(response)
            return response


def clientes_atrasados_reporte_excel(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):

                fecha_actual = datetime.datetime.now()

                # FILTROS DISPONIBLES
                filtros = filtros_establecidos(request.GET, 'clientes_atrasados')

                # OBJETO QUE SE UTILIZA PARA CARGAR TODOS LOS CLIENTES ATRASADOS A MOSTRAR
                clientes_atrasados = []

                # PARAMETROS
                meses_peticion = 1
                fraccion = ''

                if filtros == 0:
                    meses_peticion = 0
                elif filtros == 1:
                    fraccion = request.GET['fraccion']
                elif filtros == 2:
                    meses_peticion = int(request.GET['meses_atraso'])
                else:
                    fraccion = request.GET['fraccion']
                    meses_peticion = int(request.GET['meses_atraso'])

                    # # Por ultimo, traemos ordenados los registros por el CODIGO DE LOTE
                    # query += " ORDER BY codigo_paralot "
                    #
                    # # try:
                    # results = cursor.fetchall()  # LOTES
                    #
                    # for r in results:  # RECORREMOS TODOS LOS LOTES DE LA FRACCION
                    #
                    #     cliente_atrasado = {}
                    #
                    #     # OBTENER LA ULTIMA VENTA Y SU DETALLE
                    #     ultima_venta = get_ultima_venta(r[0])
                    #
                    #     # SE TRATAN LOS CASOS EN DONDE NO SE ENCUENTRA VENTA PARA ALGUN LOTE.
                    #     if ultima_venta != None:
                    #         detalle_cuotas = get_cuotas_detail_by_lote(unicode(str(r[0])))
                    #         hoy = date.today()
                    #         cuotas_a_pagar = obtener_cuotas_a_pagar_full(ultima_venta, hoy, detalle_cuotas,
                    #                                                      500)  # Maximo atraso = 500 para tener un parametro maximo de atraso en las cuotas.
                    #     else:
                    #         cuotas_a_pagar = []
                    #
                    #     if (len(cuotas_a_pagar) >= meses_peticion + 1):
                    #
                    #         cliente_atrasado[
                    #             'cliente'] = ultima_venta.cliente.nombres + ' ' + ultima_venta.cliente.apellidos
                    #
                    #         if (len(PagoDeCuotas.objects.filter(venta_id=ultima_venta.id).order_by('-fecha_de_pago')) > 0):
                    #             cliente_atrasado['fecha_ultimo_pago'] = \
                    #             PagoDeCuotas.objects.filter(venta_id=ultima_venta.id).order_by('-fecha_de_pago')[
                    #                 0].fecha_de_pago
                    #         else:
                    #             cliente_atrasado['fecha_ultimo_pago'] = 'Dato no disponible'
                    #
                    #         cliente_atrasado['lote'] = ultima_venta.lote.codigo_paralot
                    #         cliente_atrasado['total_atrasado'] = unicode('{:,}'.format(cuotas_a_pagar[len(cuotas_a_pagar) - 1]['monto_sumatoria_cuotas'])).replace(",", ".")
                    #         cliente_atrasado['importe_cuota'] = unicode(
                    #             '{:,}'.format(ultima_venta.precio_de_cuota)).replace(",", ".")
                    #         cliente_atrasado['total_pagado'] = unicode('{:,}'.format(
                    #             detalle_cuotas['cant_cuotas_pagadas'] * ultima_venta.precio_de_cuota)).replace(",", ".")
                    #         cliente_atrasado['cuotas_atrasadas'] = unicode('{:,}'.format(len(cuotas_a_pagar) - 1)).replace(",", ".")
                    #         cuotas_pagadas = unicode('{:,}'.format(detalle_cuotas['cant_cuotas_pagadas'])).replace(",", ".") + '/' + unicode(
                    #             '{:,}'.format(detalle_cuotas['cantidad_total_cuotas'])).replace(",", ".")
                    #         cliente_atrasado['cuotas_pagadas'] = cuotas_pagadas
                    #         porcentaje_pagado = round((float(detalle_cuotas['cant_cuotas_pagadas']) / float(detalle_cuotas['cantidad_total_cuotas'])) * 100);
                    #         cliente_atrasado['porc_pagado'] = unicode('{:,}'.format(int(porcentaje_pagado))).replace(",", ".") + '%'
                    #         cliente_atrasado['direccion_particular'] = ultima_venta.cliente.direccion_particular
                    #         cliente_atrasado['direccion_cobro'] = ultima_venta.cliente.direccion_cobro
                    #         cliente_atrasado['telefono_particular'] = ultima_venta.cliente.telefono_particular
                    #         cliente_atrasado['celular_1'] = ultima_venta.cliente.celular_1
                    #         clientes_atrasados.append(cliente_atrasado)

                    # if meses_peticion == 0:
                    #     meses_peticion = ''
                    # a = len(clientes_atrasados)
            clientes_atrasados = obtener_clientes_atrasados(filtros, fraccion, meses_peticion)

            if clientes_atrasados:

                wb = xlwt.Workbook(encoding='utf-8')
                sheet = wb.add_sheet('test', cell_overwrite_ok=True)
                sheet.paper_size_code = 1
                # style = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                #                   'font: name Gill Sans MT Condensed, bold True, height 160; align: horiz center')
                # style2 = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160;')
                #
                # style3 = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160 ; align: horiz right')
                #
                # style4 = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160 ; align: horiz center')

                style = xlwt.easyxf('font: name Calibri, bold True; align: horiz center')
                style2 = xlwt.easyxf(
                    'pattern: pattern solid, fore_colour white; font: name Calibri; align: horiz right')
                style3 = xlwt.easyxf('font: name Calibri, height 200; align: horiz left')
                # style4 = xlwt.easyxf('pattern: pattern solid, fore_colour white; font: name Calibri')
                style4 = xlwt.easyxf('font: name Calibri, height 200; align: horiz center')

                nombre_fraccion = Fraccion.objects.get(id=fraccion)
                usuario = unicode(request.user)
                sheet.header_str = (
                    u"&LFecha: &D Hora: &T \nUsuario: " + usuario + " "
                                                                    u"&CPROPAR S.R.L.\n CLIENTES ATRASADOS DE LA FRACCION " + unicode(
                        nombre_fraccion) + " "
                                           u"&RMeses de Atraso: " + unicode(meses_peticion) + " \nPage &P of &N"
                )
                sheet.write_merge(0, 0, 0, 10, "CLIENTES ATRASADOS DE LA FRACCION " + unicode(nombre_fraccion), style)
                # BORDES PARA las columnas de titulos
                borders = xlwt.Borders()
                borders.top = xlwt.Borders.THIN
                borders.bottom = xlwt.Borders.DOUBLE
                style.borders = borders

                # sheet.write(0, 0, "Cliente", style)
                # sheet.write(0, 1, "Lote", style)
                # sheet.write(0, 2, "C.A.", style)
                # sheet.write(0, 3, "C.P.", style)
                # sheet.write(0, 4, "Importe C", style)
                # sheet.write(0, 5, "Total A.", style)
                # sheet.write(0, 6, "Total P.", style)
                # sheet.write(0, 7, "Total Lote", style)
                # sheet.write(0, 8, "% P.", style)
                # sheet.write(0, 9, "Fecha U.P.", style)

                sheet.write(1, 0, "Cliente", style)
                sheet.write(1, 1, "Telefono", style)
                sheet.write(1, 2, "Celular", style)
                sheet.write(1, 3, "Direccion", style)
                sheet.write(1, 4, "Cod Lote", style)
                sheet.write(1, 5, "Cuotas Atras.", style)
                sheet.write(1, 6, "Cuotas Pag.", style)
                sheet.write(1, 7, "Importe Cuota", style)
                sheet.write(1, 8, "Total Atras.", style)
                sheet.write(1, 9, "Total Pag.", style)
                sheet.write(1, 10, "% Pag.", style)
                sheet.write(1, 11, "Fec Ult.Pago.", style)
                sheet.write(1,12,"Mejora", style)
                sheet.write(1,13,"Demanda",style)

                # Ancho de la columna Nombre
                col_nombre = sheet.col(0)
                col_nombre.width = 256 * 25  # 25 characters wide

                # Ancho de la columna Telefono
                col_lote = sheet.col(1)
                col_lote.width = 256 * 25  # 12 characters wide

                # Ancho de la columna Celular
                col_lote = sheet.col(2)
                col_lote.width = 256 * 26  # 12 characters wide

                # Ancho de la columna Direccion
                col_nro_cuota = sheet.col(3)
                col_nro_cuota.width = 256 * 40  # 6 characters wide

                # Ancho de la columna Lote
                col_nro_cuota = sheet.col(4)
                col_nro_cuota.width = 256 * 15  # 6 characters wide

                # Ancho de la columna Cuotas Atras.
                col_nro_cuota = sheet.col(5)
                col_nro_cuota.width = 256 * 12  # 6 characters wide

                # Ancho de la columna Cuotas Pag.
                col_mes = sheet.col(6)
                col_mes.width = 256 * 12  # 8 characters wide

                # Ancho de la columna Imp. Cuota"
                col_monto_pagado = sheet.col(7)
                col_monto_pagado.width = 256 * 11  # 11 characters wide

                # Ancho de la columna Total Atras
                col_monto_inmo = sheet.col(8)
                col_monto_inmo.width = 256 * 14  # 15 characters wide

                # Ancho de la columna Total Pag
                col_nombre = sheet.col(9)
                col_nombre.width = 256 * 14  # 15 characters wide

                # Ancho de la columna % Pag
                col_nombre = sheet.col(10)
                col_nombre.width = 256 * 6  # 5 characters wide

                # Ancho de la columna Fecha
                col_fecha = sheet.col(11)
                col_fecha.width = 256 * 20  # 12 characters wide

                # Ancho de la columna  Mejora
                col_mejora = sheet.col(12)
                col_mejora.width = 256 * 14  # 5 characters wide

                # Ancho de la columna Demanda
                col_demanda = sheet.col(13)
                col_demanda.width = 256 * 10  # 5 characters wide

                i = 0
                c = 2
                # for i in range(len(clientes_atrasados)):
                # sheet.write(c, 0, clientes_atrasados[i]['cliente'],style2)
                # sheet.write(c, 1, unicode(clientes_atrasados[i]['lote']),style4)
                # sheet.write(c, 2, unicode(clientes_atrasados[i]['cuotas_atrasadas']),style4)
                # sheet.write(c, 3, unicode(clientes_atrasados[i]['cuotas_pagadas']),style4)
                # sheet.write(c, 4, unicode(clientes_atrasados[i]['importe_cuota']),style3)
                # sheet.write(c, 5, unicode(clientes_atrasados[i]['total_atrasado']),style3)
                # sheet.write(c, 6, unicode(clientes_atrasados[i]['total_pagado']),style3)
                # # sheet.write(c, 7, unicode(clientes_atrasados[i]['valor_total_lote']),style3)
                # sheet.write(c, 8, unicode(clientes_atrasados[i]['porc_pagado']),style4)
                # sheet.write(c, 9,unicode(clientes_atrasados[i]['fecha_ultimo_pago']),style2)
                # c += 1

                for i in range(len(clientes_atrasados)):
                    sheet.write(c, 0, clientes_atrasados[i]['cliente'], style3)
                    if clientes_atrasados[i]['telefono_laboral'] != '' and clientes_atrasados[i][
                        'telefono_laboral'] != None:
                        sheet.write(c, 1, unicode('tel1: ' + clientes_atrasados[i]['telefono_particular'] + '  tel2: ' +
                                                  clientes_atrasados[i]['telefono_laboral']), style4)
                    else:
                        sheet.write(c, 1, unicode(clientes_atrasados[i]['telefono_particular']), style4)
                    if (clientes_atrasados[i]['celular_1'] != '' and clientes_atrasados[i]['celular_1'] != None) or (
                                    clientes_atrasados[i]['celular_2'] != '' and clientes_atrasados[i][
                                'celular_2'] != None):
                        sheet.write(c, 2, unicode(
                            'cel1: ' + clientes_atrasados[i]['celular_1'] + '  cel2: ' + clientes_atrasados[i][
                                'celular_2']), style4)
                    elif clientes_atrasados[i]['celular_1'] != '' and clientes_atrasados[i]['celular_1'] != None:
                        sheet.write(c, 2, unicode('cel1: ' + clientes_atrasados[i]['celular_1']), style4)
                    elif clientes_atrasados[i]['celular_2'] != '' and clientes_atrasados[i]['celular_2'] != None:
                        sheet.write(c, 2, unicode('cel1: ' + clientes_atrasados[i]['celular_2']), style4)
                    sheet.write(c, 3, unicode(
                        'dir1: ' + clientes_atrasados[i]['direccion_particular'] + '  dir2: ' + clientes_atrasados[i][
                            'direccion_cobro']), style4)
                    sheet.write(c, 4, unicode(clientes_atrasados[i]['lote']), style4)
                    sheet.write(c, 5, unicode(clientes_atrasados[i]['cuotas_atrasadas']), style4)
                    sheet.write(c, 6, unicode(clientes_atrasados[i]['cuotas_pagadas']), style4)
                    sheet.write(c, 7, unicode(clientes_atrasados[i]['importe_cuota']), style4)
                    sheet.write(c, 8, unicode(clientes_atrasados[i]['total_atrasado']), style4)
                    sheet.write(c, 9, unicode(clientes_atrasados[i]['total_pagado']), style4)
                    sheet.write(c, 10, unicode(clientes_atrasados[i]['porc_pagado']), style4)
                    # formateamos la fecha
                    fecha_str = unicode(clientes_atrasados[i]['fecha_ultimo_pago'])
                    if clientes_atrasados[i]['fecha_ultimo_pago'] != 'Dato no disponible':

                        sheet.write(c, 11, unicode(fecha_str), style4)
                    else:
                        sheet.write(c, 11, unicode('Dato no disponible'), style4)
                    sheet.write(c, 12, unicode(clientes_atrasados[i]['lote_mejora']), style4)
                    sheet.write(c, 13, unicode(clientes_atrasados[i]['lote_demanda']), style4)
                    c += 1

            response = HttpResponse(content_type='application/vnd.ms-excel')
            # Crear un nombre intuitivo
            response['Content-Disposition'] = 'attachment; filename=' + 'clientes_atrasados_' + unicode(
                nombre_fraccion) + '.xls'
            wb.save(response)
            return response


def deudores_por_venta_reporte_excel(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
                # FILTROS DISPONIBLES
                filtros = filtros_establecidos(request.GET, 'deudores_por_venta')
                # PARAMETROS
                meses_peticion = 0
                fraccion = ''
                if filtros == 0:
                    meses_peticion = 0
                elif filtros == 1:
                    fraccion = request.GET['fraccion']
                elif filtros == 2:
                    meses_peticion = int(request.GET['meses_atraso'])
                else:
                    fraccion = request.GET['fraccion']
                    meses_peticion = int(request.GET['meses_atraso'])

            deudores_por_venta = obtener_deudores_por_venta(filtros, fraccion, meses_peticion)

            totales_total_pagado = 0
            totales_total_atrasado = 0
            totales_total_cuotas_devengadas = 0

            if deudores_por_venta:

                wb = xlwt.Workbook(encoding='utf-8')
                sheet = wb.add_sheet('test', cell_overwrite_ok=True)
                sheet.paper_size_code = 1

                style = xlwt.easyxf('font: name Calibri, bold True; align: horiz center')
                style2 = xlwt.easyxf(
                    'pattern: pattern solid, fore_colour white; font: name Calibri; align: horiz right')
                style3 = xlwt.easyxf('font: name Calibri, height 200; align: horiz left')
                style4 = xlwt.easyxf('font: name Calibri, height 200; align: horiz center')
                style5 = xlwt.easyxf('font: name Calibri, height 200; align: horiz right')
                style6 = xlwt.easyxf('font: name Calibri, bold True; align: horiz right')

                nombre_fraccion = Fraccion.objects.get(id=fraccion)
                usuario = unicode(request.user)
                sheet.header_str = (
                    u"&LFecha: &D Hora: &T \nUsuario: " + usuario + " "
                                                                    u"&CPROPAR S.R.L.\n DEUDORES POR VENTA DE LA FRACCION " + unicode(
                        nombre_fraccion) + " "
                                           u"&RMeses de Atraso: " + unicode(meses_peticion) + " \nPage &P of &N"
                )
                sheet.write_merge(0, 0, 0, 10, "DEUDORES POR VENTA DE LA FRACCION " + unicode(nombre_fraccion), style)
                # BORDES PARA las columnas de titulos
                borders = xlwt.Borders()
                borders.top = xlwt.Borders.THIN
                borders.bottom = xlwt.Borders.DOUBLE
                style.borders = borders

                sheet.write(1, 0, "Cod Lote", style)
                sheet.write(1, 1, "Fecha Vta", style)
                sheet.write(1, 2, "Cuotas Pag.", style)
                sheet.write(1, 3, "Importe Cuota", style)
                sheet.write(1, 4, "Total Cobrado", style)
                sheet.write(1, 5, "Saldo a Cobrar", style)
                sheet.write(1, 6, "Cuotas Devengadas", style)

                # Ancho de la columna Lote
                col_nro_cuota = sheet.col(0)
                col_nro_cuota.width = 256 * 15  # 6 characters wide

                # Ancho de la columna Fecha Vta
                col_fecha = sheet.col(1)
                col_fecha.width = 256 * 15  # 12 characters wide

                # Ancho de la columna Cuotas Pag.
                col_mes = sheet.col(2)
                col_mes.width = 256 * 12  # 8 characters wide

                # Ancho de la columna Imp. Cuota"
                col_monto_pagado = sheet.col(3)
                col_monto_pagado.width = 256 * 15  # 11 characters wide

                # Ancho de la columna Total Pag
                col_nombre = sheet.col(4)
                col_nombre.width = 256 * 14  # 15 characters wide

                # Ancho de la columna Total Atras
                col_monto_inmo = sheet.col(5)
                col_monto_inmo.width = 256 * 14  # 15 characters wide

                # Ancho de la columna Cuotas Devengadas
                col_monto_inmo = sheet.col(6)
                col_monto_inmo.width = 256 * 16  # 15 characters wide

                i = 0
                c = 2

                for i in range(len(deudores_por_venta)):
                    sheet.write(c, 0, unicode(deudores_por_venta[i]['lote']), style3)
                    if deudores_por_venta[i]['fecha_venta'] != 'Dato no disponible':
                        fecha_str = unicode(deudores_por_venta[i]['fecha_venta'])
                        fecha = unicode(datetime.datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                        sheet.write(c, 1, unicode(fecha), style4)
                    else:
                        sheet.write(c, 1, unicode('Dato no disponible'), style4)
                    sheet.write(c, 2, unicode(deudores_por_venta[i]['cuotas_pagadas']), style4)
                    sheet.write(c, 3, unicode(deudores_por_venta[i]['importe_cuota']), style5)
                    sheet.write(c, 4, unicode(deudores_por_venta[i]['total_pagado']), style5)
                    sheet.write(c, 5, unicode(deudores_por_venta[i]['total_atrasado']), style5)
                    sheet.write(c, 6, unicode(deudores_por_venta[i]['cuotas_devengadas']), style5)

                    # acumulamos los totales
                    totales_total_pagado += int(deudores_por_venta[i]['total_pagado'].replace(".", ""))
                    totales_total_atrasado += int(deudores_por_venta[i]['total_atrasado'].replace(".", ""))
                    totales_total_cuotas_devengadas += int(deudores_por_venta[i]['cuotas_devengadas'].replace(".", ""))

                    # formateamos la fecha
                    c += 1

            # sheet.write(c, 4, "Total Cobrado", style)
            # sheet.write(c, 5, "Saldo a Cobrar", style)
            # sheet.write(c, 6, "Cuotas Devengadas", style)

            c += 1
            sheet.write_merge(c, c, 0, 3, 'Totales:', style)
            sheet.write(c, 4, unicode('{:,}'.format(totales_total_pagado)).replace(",", "."), style6)
            sheet.write(c, 5, unicode('{:,}'.format(totales_total_atrasado)).replace(",", "."), style6)
            sheet.write(c, 6, unicode('{:,}'.format(totales_total_cuotas_devengadas)).replace(",", "."), style6)
            response = HttpResponse(content_type='application/vnd.ms-excel')
            # Crear un nombre intuitivo
            response['Content-Disposition'] = 'attachment; filename=' + 'deudores_por_venta_' + unicode(
                nombre_fraccion) + '.xls'
            wb.save(response)
            return response


def informe_general_reporte_excel(request):
    fecha_ini = request.GET['fecha_ini']
    fecha_fin = request.GET['fecha_fin']
    fraccion_ini = request.GET['fraccion_ini']
    fraccion_fin = request.GET['fraccion_fin']
    cuotas = []
    g_fraccion = ''
    filas_fraccion = []
    if fecha_ini == '' and fecha_fin == '':
        query = (
            '''
            SELECT pc.* FROM principal_pagodecuotas pc, principal_lote l, principal_manzana m, principal_fraccion f
            WHERE f.id>=''' + fraccion_ini +
            '''
            AND f.id<=''' + fraccion_fin +
            '''
            AND (pc.lote_id = l.id AND l.manzana_id=m.id AND m.fraccion_id=f.id) ORDER BY f.id
            '''
        )
    else:
        fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date()
        fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date()
        query = (
            '''
            SELECT pc.* FROM principal_pagodecuotas pc, principal_lote l, principal_manzana m, principal_fraccion f
            WHERE pc.fecha_de_pago >= \'''' + unicode(fecha_ini_parsed) +
            '''\' AND pc.fecha_de_pago <= \'''' + unicode(fecha_fin_parsed) +
            '''\' AND f.id>=''' + fraccion_ini +
            '''
            AND f.id<=''' + fraccion_fin +
            '''
            AND (pc.lote_id = l.id AND l.manzana_id=m.id AND m.fraccion_id=f.id) ORDER BY f.id,pc.fecha_de_pago
            '''
        )
    object_list = list(PagoDeCuotas.objects.raw(query))
    # Totales por FRACCION

    total_cuotas = 0
    total_mora = 0
    total_pagos = 0

    total_general_cuotas = 0
    total_general_mora = 0
    total_general_pagos = 0
    # ver esto
    for i, cuota_item in enumerate(object_list):
        # Se setean los datos de cada fila
        cuota = {}
        cuota['misma_fraccion'] = True
        nro_cuota = get_nro_cuota(cuota_item)
        if g_fraccion == '':
            g_fraccion = cuota_item.lote.manzana.fraccion.id
            cuota['misma_fraccion'] = False
        if g_fraccion != cuota_item.lote.manzana.fraccion.id:

            filas_fraccion[0]['misma_fraccion'] = False
            cuotas.extend(filas_fraccion)
            filas_fraccion = []

            g_fraccion = cuota_item.lote.manzana.fraccion.id

            cuota = {}
            # cuota['misma_fraccion'] = False
            cuota['total_cuotas'] = unicode('{:,}'.format(total_cuotas)).replace(",", ".")
            cuota['total_mora'] = unicode('{:,}'.format(total_mora)).replace(",", ".")
            cuota['total_pago'] = unicode('{:,}'.format(total_pagos)).replace(",", ".")
            cuota['ultimo_pago'] = True
            cuotas.append(cuota)

            total_cuotas = 0
            total_mora = 0
            total_pagos = 0

            cuota = {}
            cuota['misma_fraccion'] = False
            cuota['ultimo_pago'] = False
            cuota['fraccion_id'] = unicode(cuota_item.lote.manzana.fraccion.id)
            cuota['fraccion'] = unicode(cuota_item.lote.manzana.fraccion)
            cuota['lote'] = unicode(cuota_item.lote)
            cuota['cliente'] = unicode(cuota_item.cliente)
            cuota['cuota_nro'] = unicode(nro_cuota) + '/' + unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
            cuota['plan_de_pago'] = cuota_item.plan_de_pago.nombre_del_plan
            cuota['fecha_pago'] = unicode(cuota_item.fecha_de_pago.strftime("%d/%m/%Y"))
            cuota['total_de_cuotas'] = unicode('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".")
            cuota['total_de_mora'] = unicode('{:,}'.format(cuota_item.total_de_mora)).replace(",", ".")
            cuota['total_de_pago'] = unicode('{:,}'.format(cuota_item.total_de_pago)).replace(",", ".")
            # Se suman los totales por fraccion
            total_cuotas += cuota_item.total_de_cuotas
            total_mora += cuota_item.total_de_mora
            total_pagos += cuota_item.total_de_pago

            total_general_cuotas += cuota_item.total_de_cuotas
            total_general_mora += cuota_item.total_de_mora
            total_general_pagos += cuota_item.total_de_pago

            filas_fraccion.append(cuota)

        else:
            cuota['ultimo_pago'] = False
            cuota['misma_fraccion'] = True
            cuota['fraccion_id'] = unicode(cuota_item.lote.manzana.fraccion.id)
            cuota['fraccion'] = unicode(cuota_item.lote.manzana.fraccion)
            cuota['lote'] = unicode(cuota_item.lote)
            cuota['cliente'] = unicode(cuota_item.cliente)
            cuota['cuota_nro'] = unicode(nro_cuota) + '/' + unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
            cuota['plan_de_pago'] = cuota_item.plan_de_pago.nombre_del_plan
            cuota['fecha_pago'] = unicode(cuota_item.fecha_de_pago.strftime("%d/%m/%Y"))
            cuota['total_de_cuotas'] = unicode('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".")
            cuota['total_de_mora'] = unicode('{:,}'.format(cuota_item.total_de_mora)).replace(",", ".")
            cuota['total_de_pago'] = unicode('{:,}'.format(cuota_item.total_de_pago)).replace(",", ".")
            # Se suman los totales por fraccion
            total_cuotas += cuota_item.total_de_cuotas
            total_mora += cuota_item.total_de_mora
            total_pagos += cuota_item.total_de_pago

            total_general_cuotas += cuota_item.total_de_cuotas
            total_general_mora += cuota_item.total_de_mora
            total_general_pagos += cuota_item.total_de_pago

            filas_fraccion.append(cuota)

    cuotas.extend(filas_fraccion)
    cuota = {}
    cuota['total_cuotas'] = unicode('{:,}'.format(total_cuotas)).replace(",", ".")
    cuota['total_mora'] = unicode('{:,}'.format(total_mora)).replace(",", ".")
    cuota['total_pago'] = unicode('{:,}'.format(total_pagos)).replace(",", ".")
    cuota['ultimo_pago'] = True
    cuotas.append(cuota)
    cuota = {}
    cuota['total_general_cuotas'] = unicode('{:,}'.format(total_general_cuotas)).replace(",", ".")
    cuota['total_general_mora'] = unicode('{:,}'.format(total_general_mora)).replace(",", ".")
    cuota['total_general_pago'] = unicode('{:,}'.format(total_general_pagos)).replace(",", ".")
    cuotas.append(cuota)
    lista = cuotas

    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    sheet.paper_size_code = 1
    style = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                        'font: name Gill Sans MT Condensed, bold True; align: horiz center')
    style2 = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                         'font: name Gill Sans MT Condensed, bold True, height 160;')
    style3 = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160 ; align: horiz center')
    style4 = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160 ; align: horiz right')
    style5 = xlwt.easyxf(
        'pattern: pattern solid, fore_colour white;''font: name Gill Sans MT Condensed, bold True, height 160 ; align: horiz right')

    style_normal = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160;')
    style_normal_centrado = xlwt.easyxf('font: name Gill Sans MT Condensed, height 160; align: horiz center')

    style_fraccion = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                                 'font: name Gill Sans MT Condensed, bold True; align: horiz center')
    # Titulo
    # sheet.write_merge(0,0,0,7, 'PROPAR S.R.L.' ,style3)
    # sheet.write_merge(1,1,1,7, 'Sistema de Control de Loteamiento' ,style3)

    # sheet.header_str = 'PROPAR S.R.L.'
    periodo_1 = fecha_ini
    periodo_2 = fecha_fin
    usuario = unicode(request.user)
    sheet.header_str = (
        u"&LFecha: &D Hora: &T \nUsuario: " + usuario + " "
                                                        u"&CPROPAR S.R.L.\n INFORME GENERAL DE PAGOS  "
                                                        u"&RPeriodo del " + periodo_1 + " al " + periodo_2 + " \nPage &P of &N"
    )
    # cabeceras
    # sheet.write(0, 0, "Fraccion", style)

    # contador de filas
    c = 0
    for cuota in cuotas:
        try:

            if cuota['total_monto'] == True and cuota['ultimo_pago'] == False:
                c += 1
                sheet.write(c, 0, "Totales de Fraccion", style2)
                sheet.write(c, 5, cuota['total_cuotas'], style5)
                sheet.write(c, 6, cuota['total_mora'], style5)
                sheet.write(c, 7, cuota['total_pago'], style5)
        except Exception, error:
            # print error
            pass
        c += 1
        try:
            if cuota['misma_fraccion'] == False:
                sheet.write_merge(c, c, 0, 7, cuota['fraccion'], style_fraccion)
                c += 1

                sheet.write(c, 0, "Lote", style)
                sheet.write(c, 1, "Cliente", style)
                sheet.write(c, 2, "Cuota.", style)
                sheet.write(c, 3, "Plan de Pago", style)
                sheet.write(c, 4, "Fecha", style)
                sheet.write(c, 5, "Total Cuotas", style)
                sheet.write(c, 6, "Total Mora", style)
                sheet.write(c, 7, "Total Pago", style)
                c += 1

            sheet.write(c, 0, cuota['lote'], style_normal_centrado)
            sheet.write(c, 1, cuota['cliente'], style_normal)
            sheet.write(c, 2, cuota['cuota_nro'], style_normal_centrado)
            sheet.write(c, 3, cuota['plan_de_pago'], style_normal)
            sheet.write(c, 4, cuota['fecha_pago'], style_normal_centrado)
            sheet.write(c, 5, cuota['total_de_cuotas'], style4)
            sheet.write(c, 6, cuota['total_de_mora'], style4)
            sheet.write(c, 7, cuota['total_de_pago'], style4)

        except Exception, error:
            print error
            # pass

        try:
            if (cuota['ultimo_pago'] == True):
                c += 1
                sheet.write_merge(c, c, 0, 4, "Totales de Fraccion", style2)
                sheet.write(c, 5, cuota['total_cuotas'], style5)
                sheet.write(c, 6, cuota['total_mora'], style5)
                sheet.write(c, 7, cuota['total_pago'], style5)
        except Exception, error:
            # print error
            pass
        try:
            if cuota['total_general_cuotas']:
                c += 1
                sheet.write_merge(c, c, 0, 4, "Totales Generales", style2)
                sheet.write(c, 5, cuota['total_general_cuotas'], style5)
                sheet.write(c, 6, cuota['total_general_mora'], style5)
                sheet.write(c, 7, cuota['total_general_pago'], style5)
        except Exception, error:
            # print error
            pass
    # holaaa

    # Ancho de la columna Lote
    col_lote = sheet.col(0)
    col_lote.width = 256 * 8  # 12 characters wide

    # Ancho de la columna Fecha
    col_fecha = sheet.col(4)
    col_fecha.width = 256 * 10  # 10 characters wide

    # Ancho de la columna Nombre
    col_nombre = sheet.col(1)
    col_nombre.width = 256 * 25  # 25 characters wide

    # Ancho de la columna Nro cuota
    col_nro_cuota = sheet.col(2)
    col_nro_cuota.width = 256 * 6  # 6 characters wide

    # Ancho de la columna mes
    col_mes = sheet.col(3)
    col_mes.width = 256 * 20  # 8 characters wide

    # Ancho de la columna monto pagado
    col_monto_pagado = sheet.col(5)
    col_monto_pagado.width = 256 * 11  # 11 characters wide

    # Ancho de la columna monto inmobiliarioa
    col_monto_inmo = sheet.col(6)
    col_monto_inmo.width = 256 * 11  # 11 characters wide

    # Ancho de la columna monto propietario
    col_nombre = sheet.col(7)
    col_nombre.width = 256 * 11  # 11 characters wide

    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo
    response['Content-Disposition'] = 'attachment; filename=' + 'informe_general.xls'
    wb.save(response)
    return response


def liquidacion_propietarios_reporte_excel(request):
    if request.user.is_authenticated():

        fecha_ini = request.GET['fecha_ini']
        fecha_fin = request.GET['fecha_fin']
        fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date()
        fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date()
        tipo_busqueda = request.GET['tipo_busqueda']
        order_by = request.GET['order_by']
        busqueda_id = request.GET['busqueda']
        # busqueda_label = request.GET['busqueda_label']

        filas = []
        lista_pagos = []
        lista_totales = []
        lotes = []
        # Totales por FRACCION
        total_monto_pagado = 0
        total_monto_inm = 0
        total_monto_prop = 0

        # Totales GENERALES
        total_general_pagado = 0
        total_general_inm = 0
        total_general_prop = 0

        monto_inmobiliaria = 0
        monto_propietario = 0

        ley = request.GET['ley1']
        impuesto_renta = request.GET['impuesto_renta1']
        iva_comision = request.GET['iva_comision']
        cont = int(request.GET['cont'])
        descuentos = []
        descripcion_monto_descuento = {}
        cuotas_obsequios = []
        monto_total_descuento = 0
        for i in range(1, cont + 1, 1):
            descripcion_monto_descuento = {}
            if request.GET.get('descripcion_otros_descuentos' + unicode(i)) == '':
                descripcion = 'Sin otros descuentos'
            else:
                descripcion = request.GET.get('descripcion_otros_descuentos' + unicode(i), '')
            if request.GET.get('monto_otros_descuentos' + unicode(i)) == '':
                monto_descuento = 0
            else:
                monto_descuento = int(request.GET.get('monto_otros_descuentos' + unicode(i), 0).replace(".", ""))
            descripcion_monto_descuento['descripcion'] = descripcion
            descripcion_monto_descuento['monto_descuento'] = monto_descuento
            descuentos.append(descripcion_monto_descuento)
            if request.GET.get('monto_otros_descuentos' + unicode(i)) == '':
                monto_total_descuento = 0
            else:
                monto_total_descuento = monto_total_descuento + int(
                    request.GET.get('monto_otros_descuentos' + unicode(i), 0).replace(".", ""))
        total_descuentos = request.GET.get('total_descuentos', '')
        total_a_cobrar = request.GET['total_a_cobrar']

        # CONVERTIMOS TODOS LOS DATOS A INT PARA CHEQUEAR INTEGRIDAD
        total_descuentos_int = int(total_descuentos.replace(".", ""))
        iva_comision_int = int(iva_comision.replace(".", ""))
        impuesto_renta_int = int(impuesto_renta.replace(".", ""))
        # monto_descuento_int = int(monto_descuento.replace(".", ""))
        monto_total_descuento_int = monto_total_descuento
        ley_int = int(ley.replace(".", ""))

        # CHEQUEAMOS INTEGRIDAD DE LIQUIDACION
        if total_descuentos_int != (iva_comision_int + monto_total_descuento_int + ley_int + impuesto_renta_int):
            raise ValueError('El total de los descuentos no coincide con la sumatoria de descuentos')

        lista_ordenada = obtener_pagos_liquidacion(busqueda_id, tipo_busqueda, fecha_ini_parsed, fecha_fin_parsed,
                                                   order_by, ley_int, impuesto_renta_int, iva_comision_int)
        lista = lista_ordenada

        wb = xlwt.Workbook(encoding='utf-8')
        sheet = wb.add_sheet('Liquidacion', cell_overwrite_ok=True, )
        sheet.paper_size_code = 1

        # style_titulos_columna = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
        #                           'font: name Calibri; align: horiz center')
        #
        # style_titulos_columna_resaltados_centrados = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
        #                           'font: name Calibri; align: horiz center')
        # style_titulos_columna_resaltados= xlwt.easyxf('pattern: pattern solid, fore_colour white;'
        #                           'font: name Calibri')
        #
        #
        # style_titulo_resumen = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
        #                      'font: name Calibri, bold True, height 200;')
        #
        # style_datos_montos = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz right')
        # style_datos_montos_subrayado = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz right')
        # style_datos_montos_importante = xlwt.easyxf('font: name Calibri, bold True, height 200 ; align: horiz right')
        # # style_datos = xlwt.easyxf('pattern: pattern solid, fore_colour white;''font: name Calibri, height 200 ; align: horiz right')
        #
        # style_normal = xlwt.easyxf('font: name Calibri, height 200;')
        # style_normal_subrayado_palabra = xlwt.easyxf('font: name Calibri, height 200;')
        # style_subrayado_normal = xlwt.easyxf('font: name Calibri, height 200;')
        # style_subrayado_normal_titulo = xlwt.easyxf('font: name Calibri, height 200; align: horiz center')
        # style_doble_subrayado = xlwt.easyxf('font: name Calibri, height 200;')
        # style_datos_texto_lote = xlwt.easyxf('font: name Calibri, height 200; align: horiz center')
        # style_datos_texto = xlwt.easyxf('font: name Calibri, height 200; align: horiz center')
        #
        # style_fraccion = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
        #                           'font: name Calibri; align: horiz center')
        #
        # style_datos_montos_importante_doble_borde = xlwt.easyxf('font: name Calibri, bold True, height 200 ; align: horiz right')
        #
        # # BORDES PARA las columnas de titulos
        # borders = xlwt.Borders()
        # borders.top = xlwt.Borders.THIN
        # borders.bottom = xlwt.Borders.DOUBLE
        # style_titulos_columna_resaltados_centrados.borders = borders
        # style_datos_montos_importante_doble_borde.borders = borders
        # style_titulos_columna_resaltados.borders = borders
        #
        # # Subrayado normal
        # border_subrayado = xlwt.Borders()
        # border_subrayado.bottom = xlwt.Borders.THIN
        # style_subrayado_normal.borders = border_subrayado
        # style_datos_montos_subrayado.borders = border_subrayado
        # style_subrayado_normal_titulo.borders = border_subrayado
        #
        # # Doble Subrayado negritas
        # border_doble_subrayado = xlwt.Borders()
        # border_doble_subrayado.bottom = xlwt.Borders.THIN
        # style_doble_subrayado.borders = border_doble_subrayado
        #
        # # font
        # font = xlwt.Font()
        # font.underline = True
        # style_normal_subrayado_palabra.font = font



        # Titulo
        # sheet.write_merge(0,0,0,7, 'PROPAR S.R.L.' ,style3)
        # sheet.write_merge(1,1,1,7, 'Sistema de Control de Loteamiento' ,style3)

        # sheet.header_str = 'PROPAR S.R.L.'
        periodo_1 = fecha_ini
        periodo_2 = fecha_fin
        usuario = unicode(request.user)
        sheet.header_str = (
            u"&L&8Fecha: &D Hora: &T \nUsuario: " + usuario + " "
                                                              u"&C&8PROPAR S.R.L.\n LIQUIDACION DE PROPIETARIOS "
                                                              u"&R&8Periodo del " + periodo_1 + " al " + periodo_2 + " \nPage &P of &N"
        )
        sheet.footer_str = ''

        monto_cuota = 0
        c = 0
        for pago in lista:
            try:
                if pago['total_monto_pagado'] == True and pago['ultimo_pago'] == False:
                    c += 1
                    sheet.write_merge(c, c, 0, 4, "Liquidacion", style_titulo_resumen)

                    sheet.write(c, 5, pago['total_monto_pagado'], style_datos_montos)
                    sheet.write(c, 6, pago['total_monto_inmobiliaria'], style_datos_montos)
                    sheet.write(c, 7, pago['total_monto_propietario'], style_datos_montos)
            except Exception, error:
                print error
                pass

            c += 1
            try:
                if pago['misma_fraccion'] == False:
                    # sheet.write(c, 0, "Fraccion: " + pago['fraccion'],style2)
                    if tipo_busqueda == 'propietario':
                        propietario = Propietario.objects.get(pk=busqueda_id)
                        fraccion_str = pago['fraccion'] + ' (' + propietario.nombres + ' ' + propietario.apellidos + ')'
                    elif tipo_busqueda == 'fraccion':
                        fraccion = Fraccion.objects.get(pk=busqueda_id)
                        fraccion_str = pago[
                                           'fraccion'] + ' (' + fraccion.propietario.nombres + ' ' + fraccion.propietario.apellidos + ')'
                    sheet.write_merge(c, c, 0, 7, fraccion_str, style_fraccion)
                    c += 1
                    sheet.write(c, 0, 'Lote', style_titulos_columna_resaltados_centrados)
                    sheet.write(c, 1, 'Fecha de pago', style_titulos_columna_resaltados_centrados)
                    sheet.write(c, 2, 'Cliente', style_titulos_columna_resaltados_centrados)
                    sheet.write(c, 3, 'Nro cuota', style_titulos_columna_resaltados_centrados)
                    sheet.write(c, 4, 'Mes', style_titulos_columna_resaltados_centrados)
                    sheet.write(c, 5, 'Monto Pagado', style_titulos_columna_resaltados_centrados)
                    sheet.write(c, 6, 'Monto Inmob', style_titulos_columna_resaltados_centrados)
                    sheet.write(c, 7, 'Monto Prop', style_titulos_columna_resaltados_centrados)
                    c += 2

                sheet.write(c, 0, pago['lote'], style_datos_texto_lote)
                sheet.write(c, 1, pago['fecha_de_pago'][:10], style_datos_texto)
                sheet.write(c, 2, pago['cliente'], style_normal)
                sheet.write(c, 3, pago['nro_cuota'], style_datos_texto)
                sheet.write(c, 4, pago['mes'], style_datos_texto)
                sheet.write(c, 5, pago['total_de_cuotas'], style_datos_montos)
                if pago['total_de_cuotas'] == '0':
                    pago['monto_cuota'] = monto_cuota
                    cuotas_obsequios.append(pago)
                else:
                    monto_cuota = pago['total_de_cuotas']
                sheet.write(c, 6, pago['monto_inmobiliaria'], style_datos_montos)
                sheet.write(c, 7, pago['monto_propietario'], style_datos_montos)
            except Exception, error:
                print error

            try:
                if (pago['ultimo_pago'] == True):
                    c += 1
                    sheet.write_merge(c, c, 0, 4, "Liquidacion", style_titulo_resumen)
                    sheet.write(c, 5, pago['total_monto_pagado'], style_datos_montos)
                    sheet.write(c, 6, pago['total_monto_inmobiliaria'], style_datos_montos)
                    sheet.write(c, 7, pago['total_monto_propietario'], style_datos_montos)
            except Exception, error:
                print error
                pass

            try:
                if (pago['total_general_pagado']):
                    c += 1
                    sheet.write_merge(c, c, 0, 1, "Totales de la fracción: ", style_titulos_columna)
                    sheet.write(c, 5, pago['total_general_pagado'], style_datos_montos)
                    sheet.write(c, 6, pago['total_general_inmobiliaria'], style_datos_montos)
                    sheet.write(c, 7, pago['total_general_propietario'], style_datos_montos)
                    c += 1
                    sheet.write(c, 5, 'IVA', style_titulos_columna)
                    sheet.write(c, 6, pago['iva_comision'], style_datos_montos_subrayado)

                    iva_comision = int(pago['iva_comision'].replace(".", ""))
                    total_general_inmobiliaria = int(unicode(pago['total_general_inmobiliaria']).replace(".", ""))
                    general_inmobiliario_con_comision = iva_comision + total_general_inmobiliaria
                    general_inmobiliario_con_comision_txt = unicode(
                        '{:,}'.format(general_inmobiliario_con_comision)).replace(",", ".")

                    c += 1
                    sheet.write(c, 6, general_inmobiliario_con_comision_txt, style_datos_montos)

                    c += 2

                    if len(cuotas_obsequios) > 0:

                        sheet.write_merge(c, c, 1, 6, "Cuotas Obsequios", style_subrayado_normal_titulo)
                        c += 1
                        total_cuotas_obsequios = 0
                        for cuota in cuotas_obsequios:
                            sheet.write(c, 1, cuota['nro_cuota'], style_normal)
                            sheet.write(c, 6, cuota['monto_cuota'], style_datos_montos)
                            total_cuotas_obsequios += int(format(cuota['monto_cuota']).replace('.', ''))
                            c += 1
                        sheet.write(c, 1, "Total descuentos", style_titulos_columna_resaltados)
                        sheet.write(c, 6, unicode('{:,}'.format(total_cuotas_obsequios).replace(",", ".")),
                                    style_datos_montos_importante_doble_borde)
                        c += 1

                    sheet.write_merge(c, c, 1, 6, "RESUMEN IMPOSITIVO Y OTROS DESCUENTOS",
                                      style_subrayado_normal_titulo)
                    c += 1
                    sheet.write(c, 1, "Liquidacion Total", style_normal)
                    sheet.write(c, 6, pago['total_general_pagado'], style_datos_montos)
                    # sheet.write_merge(c,c,4,5, general_inmobiliario_con_comision, style_datos_montos)

                    c += 1
                    sheet.write(c, 1, "Monto Inmobiliaria", style_normal)
                    sheet.write(c, 5, general_inmobiliario_con_comision_txt, style_datos_montos)
                    # sheet.write_merge(c,c,3,4, pago['iva_comision'], style_datos_montos)
                    c += 1
                    sheet.write(c, 1, "Retención IVA", style_normal)
                    sheet.write(c, 5, pago['ley'], style_datos_montos)
                    # sheet.write_merge(c,c,3,4, pago['ley'], style_datos_montos)
                    c += 1
                    sheet.write(c, 1, "Imp Renta 4.5%", style_normal)
                    sheet.write(c, 5, pago['impuesto_renta'], style_datos_montos)
                    # sheet.write_merge(c,c,3,4, pago['impuesto_renta'], style_datos_montos)
                    c += 1
                    sheet.write(c, 1, "Detalle de Otros Descuentos", style_normal_subrayado_palabra)
                    sheet.write(c, 2, "", style_normal)
                    sheet.write(c, 5, '', style_datos_montos)
                    # sheet.write_merge(c,c,3,4,'', style_datos_montos)
                    c += 1
                    # if descripcion !='':
                    #     sheet.write(c,1, descripcion, style_normal)
                    #     sheet.write(c, 5, monto_descuento, style_datos_montos)
                    #     # sheet.write_merge(c,c,3,4, monto_descuento, style_datos_montos)
                    #     c+=1
                    # else:
                    #     sheet.write(c,1, "Sin otros descuentos", style_normal)
                    #     sheet.write(c, 5, "0", style_datos_montos_subrayado)
                    #     sheet.write(c, 6, "", style_datos_montos_subrayado)
                    #     # sheet.write_merge(c,c,3,4, "0", style_datos_montos)
                    #     c+=1
                    for i in range(0, cont, 1):
                        if descripcion != '':
                            sheet.write(c, 1, descuentos[i]['descripcion'], style_normal)
                            # sheet.write(c, 5, descuentos[i]['monto_descuento'], style_datos_montos)
                            sheet.write(c, 5,
                                        unicode('{:,}'.format(descuentos[i]['monto_descuento'])).replace(",", "."),
                                        style_datos_montos)
                            # sheet.write_merge(c,c,3,4, monto_descuento, style_datos_montos)
                            c += 1
                        else:
                            sheet.write(c, 1, "Sin otros descuentos", style_normal)
                            sheet.write(c, 5, "0", style_datos_montos_subrayado)
                            sheet.write(c, 6, "", style_datos_montos_subrayado)
                            # sheet.write_merge(c,c,3,4, "0", style_datos_montos)
                            c += 1

                    # total_descuentos = int(pago['ley'].replace(".", "")) + int(pago['impuesto_renta'].replace(".", ""))+general_inmobiliario_con_comision+int(monto_descuento.replace(".", ""))
                    total_descuentos = int(pago['ley'].replace(".", "")) + int(
                        pago['impuesto_renta'].replace(".", "")) + general_inmobiliario_con_comision + monto_descuento
                    total_descuentos_txt = unicode('{:,}'.format(total_descuentos)).replace(",", ".")
                    sheet.write(c, 1, "Total descuentos", style_normal)
                    sheet.write(c, 6, total_descuentos_txt, style_datos_montos)
                    # sheet.write_merge(c,c,3,4, total_descuentos, style_datos_montos)
                    c += 1
                    sheet.write(c, 1, "Total a cobrar por el propietario: ", style_titulos_columna_resaltados)
                    sheet.write(c, 2, "", style_titulos_columna_resaltados)
                    sheet.write(c, 3, "", style_titulos_columna_resaltados)
                    sheet.write(c, 4, "", style_titulos_columna_resaltados)
                    sheet.write(c, 5, "", style_titulos_columna_resaltados)
                    sheet.write(c, 6, total_a_cobrar, style_datos_montos_importante_doble_borde)
                    # sheet.write(c, 7, total_a_cobrar, style_datos_montos_importante)


            except Exception, error:
                print error
                pass

            # Ancho de la columna Lote
            col_lote = sheet.col(0)
            col_lote.width = 256 * 12  # 12 characters wide

            # Ancho de la columna Fecha
            col_fecha = sheet.col(1)
            col_fecha.width = 256 * 12  # 10 characters wide

            # Ancho de la columna Nombre
            col_nombre = sheet.col(2)
            col_nombre.width = 256 * 25  # 25 characters wide

            # Ancho de la columna Nro cuota
            col_nro_cuota = sheet.col(3)
            col_nro_cuota.width = 256 * 8  # 6 characters wide

            # Ancho de la columna mes
            col_mes = sheet.col(4)
            col_mes.width = 256 * 8  # 8 characters wide

            # Ancho de la columna monto pagado
            col_monto_pagado = sheet.col(5)
            col_monto_pagado.width = 256 * 12  # 11 characters wide

            # Ancho de la columna monto inmobiliarioa
            col_monto_inmo = sheet.col(6)
            col_monto_inmo.width = 256 * 11  # 11 characters wide

            # Ancho de la columna monto propietario
            col_nombre = sheet.col(7)
            col_nombre.width = 256 * 11  # 11 characters wide

        response = HttpResponse(content_type='application/vnd.ms-excel')
        # Crear un nombre intuitivo
        fecha_actual = datetime.datetime.now().date()
        fecha_str = unicode(fecha_actual)
        fecha = unicode(datetime.datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y"))

        if tipo_busqueda == 'fraccion':
            fraccion = Fraccion.objects.get(pk=busqueda_id)
            response[
                'Content-Disposition'] = 'attachment; filename=' + 'liq_prop_' + fraccion.nombre + '_' + fecha + '.xls'
        elif tipo_busqueda == 'propietario':
            propietario = Propietario.objects.get(pk=busqueda_id)
            response[
                'Content-Disposition'] = 'attachment; filename=' + 'liq_prop_' + propietario.nombres + '_' + propietario.apellidos + '_' + fecha + '.xls'
        else:
            response['Content-Disposition'] = 'attachment; filename=' + 'liquidacion_propietario_.xls'
        wb.save(response)
        return response
    else:
        return HttpResponseRedirect(reverse('login'))


def liquidacion_vendedores_reporte_excel(request):
    fecha_ini = request.GET['fecha_ini']
    fecha_fin = request.GET['fecha_fin']
    fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date()
    fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date()
    busqueda_label = request.GET['busqueda_label']
    vendedor_id = request.GET['busqueda']
    print("vendedor_id ->" + vendedor_id)

    ventas = Venta.objects.filter(vendedor_id=vendedor_id).order_by('lote__manzana__fraccion').select_related()
    ventas_id = []

    for venta in ventas:
        ventas_id.append(venta.id)

    #actualizamos a un dia mas para que busque tambien las que se encuentran en esa fecha de fin seleccionada
    fecha_final = fecha_fin_parsed + timedelta(days=1)

    pagos_de_cuotas_ventas = PagoDeCuotas.objects.filter(venta__in=ventas_id, fecha_de_pago__range=(
        fecha_ini_parsed, fecha_final)).order_by('fecha_de_pago').prefetch_related('venta',
                                                                                        'venta__plan_de_pago_vendedor',
                                                                                        'venta__lote__manzana__fraccion')
    cant_cuotas_pagadas_ventas = PagoDeCuotas.objects.filter(venta__in=ventas_id,
                                                             fecha_de_pago__lt=fecha_ini_parsed).values(
        'venta_id').annotate(Sum('nro_cuotas_a_pagar')).prefetch_related('venta_id')

    filas_fraccion = []
    filas = []

    total_fraccion_monto_pagado = 0
    total_fraccion_monto_vendedor = 0

    total_general_monto_pagado = 0
    total_general_monto_vendedor = 0

    b_fraccion = False
    b_vendedor = True

    vendedor = Vendedor.objects.get(pk=vendedor_id)

    g_nombre_fraccion = ''
    g_nombre_vendedor = vendedor.nombres + "_" + vendedor.apellidos

    fecha_pago_str = ''

    g_fraccion = ''
    for venta in ventas:

        if venta.fecha_de_venta >= fecha_ini_parsed and venta.fecha_de_venta <= fecha_fin_parsed:
            # preguntar por el plan de pago de la venta con el vendedor, si el vendedor lleva un % de la venta total, un % de la entrega inicial

            if venta.plan_de_pago_vendedor.tipo == 'contado':

                if g_fraccion == '':
                    g_fraccion = venta.lote.manzana.fraccion
                if venta.lote.manzana.fraccion != g_fraccion:
                    # Totales por FRACCION
                    try:
                        filas_fraccion = sorted(filas_fraccion, key=lambda f: (f['fecha_de_pago_order']))
                    except Exception, error:
                        print error + ": " + fecha_pago_str
                    if filas_fraccion:
                        filas_fraccion[0]['misma_fraccion'] = False
                        filas.extend(filas_fraccion)
                        filas_fraccion = []
                        fila = {}
                        fila['total_monto_pagado'] = unicode('{:,}'.format(total_fraccion_monto_pagado)).replace(",",
                                                                                                                 ".")
                        fila['total_monto_vendedor'] = unicode('{:,}'.format(total_fraccion_monto_vendedor)).replace(
                            ",", ".")

                        total_fraccion_monto_pagado = 0
                        total_fraccion_monto_vendedor = 0

                        fila['ultimo_pago'] = True
                        filas.append(fila)
                    else:
                        montos = calculo_montos_liquidacion_vendedores_contado(venta)
                        monto_vendedor = montos['monto_vendedor']
                        fecha_pago_str = unicode(venta.fecha_de_venta)
                        fecha_pago = unicode(
                            datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                        fecha_pago_order = venta.fecha_de_venta

                        # Fraccion    Lote    Fecha de Pago    Cliente    Cuota Nº    Mes    Monto Pag Monto Prop.
                        fila = {}
                        fila['fraccion'] = venta.lote.manzana.fraccion
                        fila['plan'] = unicode(venta.plan_de_pago_vendedor)
                        fila['lote'] = venta.lote.codigo_paralot
                        fila['fecha_de_pago'] = fecha_pago
                        fila['fecha_de_pago_order'] = fecha_pago_order
                        fila['cliente'] = venta.cliente
                        fila['nro_cuota'] = 'Venta al Contado'
                        fila['monto_pagado'] = venta.precio_final_de_venta
                        fila['monto_vendedor'] = monto_vendedor
                        fila['misma_fraccion'] = True

                        monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                                      "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
                        fecha_1 = unicode(
                            datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                        parts_1 = fecha_1.split("/")
                        year_1 = parts_1[2]
                        mes_1 = int(parts_1[1]) - 1
                        mes_year = monthNames[mes_1] + "/" + year_1
                        fila['mes'] = "1/1"

                        total_fraccion_monto_pagado += fila['monto_pagado']
                        total_fraccion_monto_vendedor += fila['monto_vendedor']

                        total_general_monto_pagado += fila['monto_pagado']
                        total_general_monto_vendedor += fila['monto_vendedor']

                        fila['monto_pagado'] = unicode(
                            '{:,}'.format(fila['monto_pagado'])
                        ).replace(",", ".")

                        fila['monto_vendedor'] = unicode(
                            '{:,}'.format(fila['monto_vendedor'])
                        ).replace(",", ".")

                        filas_fraccion.append(fila)

                    g_fraccion = venta.lote.manzana.fraccion.nombre
                    ok = True
                else:
                    montos = calculo_montos_liquidacion_vendedores_contado(venta)
                    monto_vendedor = montos['monto_vendedor']
                    fecha_pago_str = unicode(venta.fecha_de_venta)
                    fecha_pago = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                    fecha_pago_order = venta.fecha_de_venta

                    # Fraccion    Lote    Fecha de Pago    Cliente    Cuota Nº    Mes    Monto Pag Monto Prop.
                    fila = {}
                    fila['fraccion'] = g_fraccion
                    fila['plan'] = unicode(venta.plan_de_pago_vendedor)
                    fila['lote'] = venta.lote.codigo_paralot
                    fila['fecha_de_pago'] = fecha_pago
                    fila['fecha_de_pago_order'] = fecha_pago_order
                    fila['cliente'] = venta.cliente
                    fila['nro_cuota'] = 'Venta al Contado'
                    fila['monto_pagado'] = venta.precio_final_de_venta
                    fila['monto_vendedor'] = monto_vendedor
                    fila['misma_fraccion'] = True

                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                    fecha_1 = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                    parts_1 = fecha_1.split("/")
                    year_1 = parts_1[2];
                    mes_1 = int(parts_1[1]) - 1;
                    mes_year = monthNames[mes_1] + "/" + year_1;
                    fila['mes'] = mes_year

                    total_fraccion_monto_pagado += fila['monto_pagado']
                    total_fraccion_monto_vendedor += fila['monto_vendedor']

                    total_general_monto_pagado += fila['monto_pagado']
                    total_general_monto_vendedor += fila['monto_vendedor']

                    fila['monto_pagado'] = unicode('{:,}'.format(fila['monto_pagado'])).replace(",", ".")
                    fila['monto_vendedor'] = unicode('{:,}'.format(fila['monto_vendedor'])).replace(",", ".")

                    filas_fraccion.append(fila)

            if venta.entrega_inicial > 0:
                if g_fraccion == '':
                    g_fraccion = venta.lote.manzana.fraccion
                if venta.lote.manzana.fraccion != g_fraccion:
                    # Totales por FRACCION
                    try:
                        filas_fraccion = sorted(filas_fraccion, key=lambda f: (f['fecha_de_pago_order']))
                    except Exception, error:
                        print error + ": " + fecha_pago_str
                    if filas_fraccion:
                        filas_fraccion[0]['misma_fraccion'] = False
                        filas.extend(filas_fraccion)
                        filas_fraccion = []
                        fila = {}
                        fila['total_monto_pagado'] = unicode('{:,}'.format(total_fraccion_monto_pagado)).replace(",",
                                                                                                                 ".")
                        fila['total_monto_vendedor'] = unicode('{:,}'.format(total_fraccion_monto_vendedor)).replace(
                            ",", ".")

                        total_fraccion_monto_pagado = 0
                        total_fraccion_monto_vendedor = 0

                        fila['ultimo_pago'] = True
                        filas.append(fila)
                    g_fraccion = venta.lote.manzana.fraccion
                    ok = True
                else:

                    montos = calculo_montos_liquidacion_vendedores_entrega_inicial(venta)
                    monto_vendedor = montos['monto_vendedor']
                    fecha_pago_str = unicode(venta.fecha_de_venta)
                    fecha_pago = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                    fecha_pago_order = venta.fecha_de_venta

                    # Fraccion    Lote    Fecha de Pago    Cliente    Cuota Nº    Mes    Monto Pag Monto Prop.
                    fila = {}
                    fila['fraccion'] = g_fraccion
                    fila['plan'] = unicode(venta.plan_de_pago_vendedor)
                    fila['lote'] = venta.lote.codigo_paralot
                    fila['fecha_de_pago'] = fecha_pago
                    fila['fecha_de_pago_order'] = fecha_pago_order
                    fila['cliente'] = venta.cliente
                    fila['nro_cuota'] = 'Entrega Inicial'
                    fila['monto_pagado'] = venta.entrega_inicial
                    fila['monto_vendedor'] = monto_vendedor
                    fila['misma_fraccion'] = True

                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                    fecha_1 = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                    parts_1 = fecha_1.split("/")
                    year_1 = parts_1[2];
                    mes_1 = int(parts_1[1]) - 1;
                    mes_year = monthNames[mes_1] + "/" + year_1;
                    fila['mes'] = mes_year

                    total_fraccion_monto_pagado += fila['monto_pagado']
                    total_fraccion_monto_vendedor += fila['monto_vendedor']

                    total_general_monto_pagado += fila['monto_pagado']
                    total_general_monto_vendedor += fila['monto_vendedor']

                    fila['monto_pagado'] = unicode('{:,}'.format(fila['monto_pagado'])).replace(",", ".")
                    fila['monto_vendedor'] = unicode('{:,}'.format(fila['monto_vendedor'])).replace(",", ".")

                    filas_fraccion.append(fila)

        pagos = []
        pagos = get_pago_cuotas(venta, fecha_ini_parsed, fecha_fin_parsed, pagos_de_cuotas_ventas,
                                cant_cuotas_pagadas_ventas)
        lista_cuotas_ven = []
        lista_cuotas_ven.append(venta.plan_de_pago_vendedor.cuota_inicial)
        numero_cuota = venta.plan_de_pago_vendedor.cuota_inicial
        for i in range(venta.plan_de_pago_vendedor.cantidad_cuotas - 1):
            numero_cuota += venta.plan_de_pago_vendedor.intervalos
            lista_cuotas_ven.append(numero_cuota)

        for pago in pagos:
            # preguntar por el plan de pago de la venta con el vendedor, si el vendedor lleva un % del pago de acuerdo al nro de cuota que se está pagando
            try:

                if g_fraccion == "":
                    g_fraccion = venta.lote.manzana.fraccion

                if pago['fraccion'] != g_fraccion:
                    # Totales por FRACCION
                    try:
                        filas_fraccion = sorted(filas_fraccion, key=lambda f: (f['fecha_de_pago_order']))
                    except Exception, error:
                        print error + ": " + fecha_pago_str

                    if filas_fraccion:
                        filas_fraccion[0]['misma_fraccion'] = False
                        filas.extend(filas_fraccion)
                        filas_fraccion = []
                        fila = {}
                        fila['total_monto_pagado'] = unicode('{:,}'.format(total_fraccion_monto_pagado)).replace(",",
                                                                                                                 ".")
                        fila['total_monto_vendedor'] = unicode('{:,}'.format(total_fraccion_monto_vendedor)).replace(
                            ",", ".")

                        total_fraccion_monto_pagado = 0
                        total_fraccion_monto_vendedor = 0

                        fila['ultimo_pago'] = True
                        filas.append(fila)
                    g_fraccion = pago['fraccion']
                    ok = True

                    montos = calculo_montos_liquidacion_vendedores(pago, venta, lista_cuotas_ven)
                    monto_vendedor = montos['monto_vendedor']
                    fecha_pago_str = unicode(pago['fecha_de_pago'])
                    try:
                        fecha_pago = unicode(
                            datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"))
                    except Exception, error:
                        print error + ": " + fecha_pago_str

                    # Se setean los datos de cada fila
                    fila = {}
                    fila['misma_fraccion'] = True
                    fila['fraccion'] = unicode(venta.lote.manzana.fraccion)
                    fila['plan'] = unicode(venta.plan_de_pago_vendedor)
                    fila['fecha_de_pago'] = fecha_pago
                    fila['fecha_de_pago_order'] = pago['fecha_de_pago']
                    fila['lote'] = unicode(pago['lote'])
                    fila['cliente'] = unicode(venta.cliente)
                    fila['nro_cuota'] = unicode(pago['nro_cuota_y_total'])
                    fila['total_de_cuotas'] = unicode('{:,}'.format(int(pago['monto']))).replace(",", ".")
                    fila['monto_vendedor'] = unicode('{:,}'.format(monto_vendedor)).replace(",", ".")

                    cuotas_detalles = get_cuota_information_by_lote(pago['lote'].id, int(pago['nro_cuota']), True, True,
                                                                    venta)
                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                    fecha_1 = cuotas_detalles[0]['fecha']
                    parts_1 = fecha_1.split("/")
                    year_1 = parts_1[2];
                    mes_1 = int(parts_1[1]) - 1;
                    mes_year = monthNames[mes_1] + "/" + year_1;
                    fila['mes'] = mes_year

                    # if venta.lote.manzana.fraccion != g_fraccion:
                    if monto_vendedor != 0:
                        ok = False
                        # Se suman los TOTALES por FRACCION
                        total_fraccion_monto_vendedor += int(monto_vendedor)
                        total_fraccion_monto_pagado += int(pago['monto'])

                        # Acumulamos para los TOTALES GENERALES
                        total_general_monto_pagado += int(pago['monto'])
                        total_general_monto_vendedor += int(monto_vendedor)

                        filas_fraccion.append(fila)

                else:

                    montos = calculo_montos_liquidacion_vendedores(pago, venta, lista_cuotas_ven)
                    monto_vendedor = montos['monto_vendedor']
                    fecha_pago_str = unicode(pago['fecha_de_pago'])
                    try:
                        fecha_pago = unicode(
                            datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"))
                    except Exception, error:
                        print error + ": " + fecha_pago_str

                    # Se setean los datos de cada fila
                    fila = {}
                    fila['misma_fraccion'] = True
                    fila['fraccion'] = unicode(venta.lote.manzana.fraccion)
                    fila['plan'] = unicode(venta.plan_de_pago_vendedor)
                    fila['fecha_de_pago'] = fecha_pago
                    fila['fecha_de_pago_order'] = pago['fecha_de_pago']
                    fila['lote'] = unicode(pago['lote'])
                    fila['cliente'] = unicode(venta.cliente)
                    fila['nro_cuota'] = unicode(pago['nro_cuota_y_total'])
                    fila['total_de_cuotas'] = unicode('{:,}'.format(int(pago['monto']))).replace(",", ".")
                    fila['monto_vendedor'] = unicode('{:,}'.format(monto_vendedor)).replace(",", ".")

                    cuotas_detalles = get_cuota_information_by_lote(pago['lote'].id, int(pago['nro_cuota']), True, True,
                                                                    venta)
                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                    fecha_1 = cuotas_detalles[0]['fecha']
                    parts_1 = fecha_1.split("/")
                    year_1 = parts_1[2];
                    mes_1 = int(parts_1[1]) - 1;
                    mes_year = monthNames[mes_1] + "/" + year_1;
                    fila['mes'] = mes_year

                    # if venta.lote.manzana.fraccion != g_fraccion:
                    if monto_vendedor != 0:
                        ok = False
                        # Se suman los TOTALES por FRACCION
                        total_fraccion_monto_vendedor += int(monto_vendedor)
                        total_fraccion_monto_pagado += int(pago['monto'])

                        # Acumulamos para los TOTALES GENERALES
                        total_general_monto_pagado += int(pago['monto'])
                        total_general_monto_vendedor += int(monto_vendedor)

                        filas_fraccion.append(fila)





            except Exception, error:
                print "Error: " + unicode(error) + ", Id Pago: " + unicode(pago['id']) + ", Fraccion: " + unicode(
                    pago['fraccion']) + ", lote: " + unicode(pago['lote']) + " Nro cuota: " + unicode(
                    unicode(pago['nro_cuota_y_total']))

    # Totales GENERALES
    # filas = sorted(filas, key=lambda f: f['fecha_de_pago'])
    if filas_fraccion:
        filas_fraccion = sorted(filas_fraccion, key=lambda f: (f['fecha_de_pago_order']))
        filas_fraccion[0]['misma_fraccion'] = False
        filas.extend(filas_fraccion)

        fila = {}
        fila['total_monto_pagado'] = unicode('{:,}'.format(total_fraccion_monto_pagado)).replace(",", ".")
        fila['total_monto_vendedor'] = unicode('{:,}'.format(total_fraccion_monto_vendedor)).replace(",", ".")
        total_fraccion_monto_vendedor = 0
        total_fraccion_monto_pagado = 0
        fila['ultimo_pago'] = True
        filas.append(fila)

    fila = {}
    fila['total_general_pagado'] = unicode('{:,}'.format(total_general_monto_pagado)).replace(",", ".")
    fila['total_general_vendedor'] = unicode('{:,}'.format(total_general_monto_vendedor)).replace(",", ".")
    ley = int(total_general_monto_pagado * 0.015)
    filas.append(fila)
    filas[0]['misma_fraccion'] = False

    ultimo = "&busqueda_label=" + busqueda_label + "&busqueda=" + vendedor_id + "&fecha_ini=" + fecha_ini + "&fecha_fin=" + fecha_fin

    lista = filas
    # aquiiiii
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    sheet.paper_size_code = 1
    # sheet.set_portrait(False)
    sheet.fit_width_to_pages = 1
    style = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                        'font: name Calibri, bold True; align: horiz center')
    style2 = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                         'font: name Calibri, bold True, height 200;')
    style3 = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz center')
    style4 = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz right')
    style5 = xlwt.easyxf(
        'pattern: pattern solid, fore_colour white;''font: name Calibri, bold True, height 200 ; align: horiz right')

    style_normal = xlwt.easyxf('font: name Calibri, height 200;')
    style_normal_centrado = xlwt.easyxf('font: name Calibri, height 200; align: horiz center')

    style_fraccion = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                                 'font: name Calibri, bold True; align: horiz center')
    # Titulo
    # sheet.write_merge(0,0,0,7, 'PROPAR S.R.L.' ,style3)
    # sheet.write_merge(1,1,1,7, 'Sistema de Control de Loteamiento' ,style3)

    # sheet.header_str = 'PROPAR S.R.L.'
    periodo_1 = fecha_ini
    periodo_2 = fecha_fin
    usuario = unicode(request.user)
    sheet.header_str = (
        u"&LFecha: &D Hora: &T \nUsuario: " + usuario + " "
                                                        u"&CPROPAR S.R.L.\n LIQUIDACION DE VENDEDORES "
                                                        u"&RPeriodo del " + periodo_1 + " al " + periodo_2 + " \nPage &P of &N"
    )
    # sheet.footer_str = 'things'



    c = 0
    sheet.write_merge(c, c, 0, 6, "Liquidacion del Vendedor: " + busqueda_label, style)
    c += 1
    for pago in filas:
        try:
            if pago['total_monto_pagado'] == True and pago['ultimo_pago'] == False:
                c += 1
                sheet.write_merge(c, c, 0, 4, "Liquidacion", style2)

                sheet.write(c, 5, unicode(pago['total_monto_pagado']), style5)
                sheet.write(c, 6, unicode(pago['total_monto_vendedor']), style5)
        except Exception, error:
            print error
            pass

        c += 1
        try:
            if pago['misma_fraccion'] == False:
                # sheet.write(c, 0, "Fraccion: " + pago['fraccion'],style2)
                sheet.write_merge(c, c, 0, 7, unicode(pago['fraccion']), style_fraccion)
                c += 1
                sheet.write(c, 0, 'Lote', style)
                sheet.write(c, 1, 'Fecha de pago', style)
                sheet.write(c, 2, 'Cliente', style)
                sheet.write(c, 3, 'Nro cuota', style)
                sheet.write(c, 4, 'Mes', style)
                sheet.write(c, 5, 'Monto Pag.', style)
                sheet.write(c, 6, 'Vendedor', style)
                c += 1

            sheet.write(c, 0, unicode(pago['lote']), style_normal_centrado)
            sheet.write(c, 1, unicode(pago['fecha_de_pago']), style_normal_centrado)
            sheet.write(c, 2, unicode(pago['cliente']), style_normal)
            sheet.write(c, 3, unicode(pago['nro_cuota']), style_normal_centrado)
            sheet.write(c, 4, unicode(pago['mes']), style_normal_centrado)
            try:
                sheet.write(c, 5, unicode(pago['total_de_cuotas']), style4)
            except Exception, error:
                sheet.write(c, 5, unicode(pago['monto_pagado']), style4)

            sheet.write(c, 6, unicode(pago['monto_vendedor']), style4)
        except Exception, error:
            print error

        try:
            if (pago['ultimo_pago'] == True):
                c += 1
                sheet.write_merge(c, c, 0, 4, "Liquidacion", style2)
                sheet.write(c, 5, unicode(pago['total_monto_pagado']), style5)
                sheet.write(c, 6, unicode(pago['total_monto_vendedor']), style5)
        except Exception, error:
            print error
            pass

        try:
            if (pago['total_general_pagado']):
                c += 1
                sheet.write_merge(c, c, 0, 4, "Liquidacion Total", style2)
                sheet.write(c, 5, unicode(pago['total_general_pagado']), style5)
                sheet.write(c, 6, unicode(pago['total_general_vendedor']), style5)


        except Exception, error:
            print error
            pass

        # Ancho de la columna Lote
        col_lote = sheet.col(0)
        col_lote.width = 256 * 12  # 12 characters wide

        # Ancho de la columna Fecha
        col_fecha = sheet.col(1)
        col_fecha.width = 256 * 12  # 10 characters wide

        # Ancho de la columna Nombre
        col_nombre = sheet.col(2)
        col_nombre.width = 256 * 25  # 25 characters wide

        # Ancho de la columna Nro cuota
        col_nro_cuota = sheet.col(3)
        col_nro_cuota.width = 256 * 10  # 6 characters wide

        # Ancho de la columna mes
        col_mes = sheet.col(4)
        col_mes.width = 256 * 8  # 8 characters wide

        # Ancho de la columna monto pagado
        col_monto_pagado = sheet.col(5)
        col_monto_pagado.width = 256 * 10  # 12 characters wide

        # Ancho de la columna monto vendedor
        col_monto_inmo = sheet.col(6)
        col_monto_inmo.width = 256 * 12  # 15 characters wide

        # Ancho de la columna monto propietario
        col_nombre = sheet.col(7)
        col_nombre.width = 256 * 11  # 11 characters wide

    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo
    fecha_actual = datetime.datetime.now().date()
    fecha_str = unicode(fecha_actual)
    fecha = unicode(datetime.datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y"))

    if b_fraccion:
        response[
            'Content-Disposition'] = 'attachment; filename=' + 'liq_vend_' + g_nombre_fraccion + '_' + fecha + '.xls'
    elif b_vendedor:
        response[
            'Content-Disposition'] = 'attachment; filename=' + 'liq_vend_' + g_nombre_vendedor + '_' + fecha + '.xls'
    else:
        response['Content-Disposition'] = 'attachment; filename=' + 'liquidacion_vendedores_.xls'
    wb.save(response)
    return response


def liquidacion_general_vendedores_reporte_excel(request):
    fecha_ini = request.GET['fecha_ini']
    fecha_fin = request.GET['fecha_fin']

    fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date()
    fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date()

    # ventas = Venta.objects.filter(vendedor_id = vendedor_id).order_by('lote__manzana__fraccion').select_related()
    ventas = Venta.objects.filter().order_by('vendedor').select_related()
    ventas_id = []

    for venta in ventas:
        ventas_id.append(venta.id)

    #fecha_ini_str_with_time = fecha_ini + " 00:00:00"
    #fecha_fin_str_with_time = fecha_ini + " 00:00:00"

    #fecha_ini_parsed_with_time = datetime.datetime.strptime(fecha_ini_str_with_time, "%d/%m/%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    #fecha_fin_parsed_with_time = datetime.datetime.strptime(fecha_fin_str_with_time, "%d/%m/%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

    fecha_final = fecha_fin_parsed + timedelta(days=1)

    pagos_de_cuotas_ventas = PagoDeCuotas.objects.filter(venta__in=ventas_id, fecha_de_pago__range=(
        fecha_ini_parsed, fecha_final)).order_by('fecha_de_pago').prefetch_related('venta',
                                                                                        'venta__plan_de_pago_vendedor',
                                                                                        'venta__lote__manzana__fraccion')
    cant_cuotas_pagadas_ventas = PagoDeCuotas.objects.filter(venta__in=ventas_id,
                                                             fecha_de_pago__lt=fecha_ini_parsed).values(
        'venta_id').annotate(Sum('nro_cuotas_a_pagar')).prefetch_related('venta_id')

    filas_vendedor = []
    filas = []

    total_vendedor_monto_pagado = 0
    total_vendedor_monto_vendedor = 0

    total_general_monto_pagado = 0
    total_general_monto_vendedor = 0

    # b_fraccion = False
    # b_vendedor = True

    fecha_pago_str = ''

    g_vendedor = ''
    for venta in ventas:

        if venta.fecha_de_venta >= fecha_ini_parsed and venta.fecha_de_venta <= fecha_fin_parsed:
            # preguntar por el plan de pago de la venta con el vendedor, si el vendedor lleva un % de la venta total, un % de la entrega inicial

            if venta.plan_de_pago_vendedor.tipo == 'contado':

                if g_vendedor == '':
                    # g_fraccion = venta.lote.manzana.fraccion
                    g_venedor = venta.vendedor
                if venta.vendedor != g_vendedor:
                    # Totales por VENDEDOR
                    try:
                        filas_vendedor = sorted(filas_vendedor, key=lambda f: (f['fecha_de_pago_order']))
                    except Exception, error:
                        print error + ": " + fecha_pago_str
                    if filas_vendedor:
                        filas_vendedor[0]['mismo_vendedor'] = False
                        filas.extend(filas_vendedor)
                        filas_vendedor = []
                        fila = {}
                        fila['total_monto_pagado'] = unicode('{:,}'.format(total_vendedor_monto_pagado)).replace(",",
                                                                                                                 ".")
                        fila['total_monto_vendedor'] = unicode('{:,}'.format(total_vendedor_monto_vendedor)).replace(
                            ",", ".")

                        total_vendedor_monto_pagado = 0
                        total_vendedor_monto_vendedor = 0

                        fila['ultimo_pago'] = True
                        filas.append(fila)
                    g_vendedor = venta.vendedor
                    ok = True
                else:
                    montos = calculo_montos_liquidacion_vendedores_contado(venta)
                    monto_vendedor = montos['monto_vendedor']
                    fecha_pago_str = unicode(venta.fecha_de_venta)
                    fecha_pago = unicode(datetime.datetime.strptime(fecha_pago_str + " 00:00:00", "%Y-%m-%d  %H:%M:%S").strftime("%d/%m/%Y  %H:%M:%S"))
                    fecha_pago_order =  datetime.datetime.strptime(unicode(venta.fecha_de_venta) + " 00:00:00", "%Y-%m-%d  %H:%M:%S")

                    # Fraccion    Lote    Fecha de Pago    Cliente    Cuota Nº    Mes    Monto Pag Monto Prop.
                    fila = {}
                    fila['vendedor'] = g_vendedor
                    fila['plan'] = unicode(venta.plan_de_pago_vendedor)
                    fila['lote'] = venta.lote.codigo_paralot
                    fila['fecha_de_pago'] = fecha_pago
                    fila['fecha_de_pago_order'] = fecha_pago_order
                    fila['cliente'] = venta.cliente
                    fila['nro_cuota'] = 'Venta al Contado'
                    fila['monto_pagado'] = venta.precio_final_de_venta
                    fila['monto_vendedor'] = monto_vendedor
                    fila['mismo_vendedor'] = True

                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                    fecha_1 = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                    parts_1 = fecha_1.split("/")
                    year_1 = parts_1[2];
                    mes_1 = int(parts_1[1]) - 1;
                    mes_year = monthNames[mes_1] + "/" + year_1;
                    fila['mes'] = mes_year

                    total_vendedor_monto_pagado += fila['monto_pagado']
                    total_vendedor_monto_vendedor += fila['monto_vendedor']

                    total_general_monto_pagado += fila['monto_pagado']
                    total_general_monto_vendedor += fila['monto_vendedor']

                    fila['monto_pagado'] = unicode('{:,}'.format(fila['monto_pagado'])).replace(",", ".")
                    fila['monto_vendedor'] = unicode('{:,}'.format(fila['monto_vendedor'])).replace(",", ".")

                    filas_vendedor.append(fila)

            if venta.entrega_inicial > 0:
                if g_vendedor == '':
                    g_vendedor = venta.vendedor
                if venta.vendedor != g_vendedor:
                    # Totales por VENDEDOR
                    try:
                        filas_vendedor = sorted(filas_vendedor, key=lambda f: (f['fecha_de_pago_order']))
                    except Exception, error:
                        print unicode(error) + ": " + fecha_pago_str
                    if filas_vendedor:
                        filas_vendedor[0]['mismo_vendedor'] = False
                        filas.extend(filas_vendedor)
                        filas_vendedor = []
                        fila = {}
                        fila['total_monto_pagado'] = unicode('{:,}'.format(total_vendedor_monto_pagado)).replace(",",
                                                                                                                 ".")
                        fila['total_monto_vendedor'] = unicode('{:,}'.format(total_vendedor_monto_vendedor)).replace(
                            ",", ".")

                        total_vendedor_monto_pagado = 0
                        total_vendedor_monto_vendedor = 0

                        fila['ultimo_pago'] = True
                        filas.append(fila)
                    g_vendedor = venta.vendedor
                    ok = True
                else:

                    montos = calculo_montos_liquidacion_vendedores_entrega_inicial(venta)
                    monto_vendedor = montos['monto_vendedor']
                    fecha_pago_str = unicode(venta.fecha_de_venta)
                    fecha_pago = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                    fecha_pago_order = venta.fecha_de_venta

                    # Fraccion    Lote    Fecha de Pago    Cliente    Cuota Nº    Mes    Monto Pag Monto Prop.
                    fila = {}
                    fila['vendedor'] = g_vendedor
                    fila['plan'] = unicode(venta.plan_de_pago_vendedor)
                    fila['lote'] = venta.lote.codigo_paralot
                    fila['fecha_de_pago'] = fecha_pago
                    fila['fecha_de_pago_order'] = fecha_pago_order
                    fila['cliente'] = venta.cliente
                    fila['nro_cuota'] = 'Entrega Inicial'
                    fila['monto_pagado'] = venta.entrega_inicial
                    fila['monto_vendedor'] = monto_vendedor
                    fila['mismo_vendedor'] = True

                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                    fecha_1 = unicode(datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                    parts_1 = fecha_1.split("/")
                    year_1 = parts_1[2];
                    mes_1 = int(parts_1[1]) - 1;
                    mes_year = monthNames[mes_1] + "/" + year_1;
                    fila['mes'] = mes_year

                    total_vendedor_monto_pagado += fila['monto_pagado']
                    total_vendedor_monto_vendedor += fila['monto_vendedor']

                    total_general_monto_pagado += fila['monto_pagado']
                    total_general_monto_vendedor += fila['monto_vendedor']

                    fila['monto_pagado'] = unicode('{:,}'.format(fila['monto_pagado'])).replace(",", ".")
                    fila['monto_vendedor'] = unicode('{:,}'.format(fila['monto_vendedor'])).replace(",", ".")

                    filas_vendedor.append(fila)

        pagos = []
        pagos = get_pago_cuotas(venta, fecha_ini_parsed, fecha_fin_parsed, pagos_de_cuotas_ventas,
                                cant_cuotas_pagadas_ventas)
        lista_cuotas_ven = []
        lista_cuotas_ven.append(venta.plan_de_pago_vendedor.cuota_inicial)
        numero_cuota = venta.plan_de_pago_vendedor.cuota_inicial
        for i in range(venta.plan_de_pago_vendedor.cantidad_cuotas - 1):
            numero_cuota += venta.plan_de_pago_vendedor.intervalos
            lista_cuotas_ven.append(numero_cuota)

        for pago in pagos:
            # preguntar por el plan de pago de la venta con el vendedor, si el vendedor lleva un % del pago de acuerdo al nro de cuota que se está pagando
            try:

                if g_vendedor == "":
                    g_vendedor = venta.vendedor

                # if pago['vendedor'] != g_vendedor:
                if venta.vendedor != g_vendedor:
                    # Totales por VENDEDOR
                    try:
                        filas_vendedor = sorted(filas_vendedor, key=lambda f: ( f['fecha_de_pago_order'] ))
                    except Exception, error:
                        print unicode(error) + ": " + fecha_pago_str

                    if filas_vendedor:
                        filas_vendedor[0]['mismo_vendedor'] = False
                        filas.extend(filas_vendedor)
                        filas_vendedor = []
                        fila = {}
                        fila['total_monto_pagado'] = unicode('{:,}'.format(total_vendedor_monto_pagado)).replace(",",
                                                                                                                 ".")
                        fila['total_monto_vendedor'] = unicode('{:,}'.format(total_vendedor_monto_vendedor)).replace(
                            ",", ".")

                        total_vendedor_monto_pagado = 0
                        total_vendedor_monto_vendedor = 0

                        fila['ultimo_pago'] = True
                        filas.append(fila)
                    g_vendedor = venta.vendedor
                    ok = True

                    montos = calculo_montos_liquidacion_vendedores(pago, venta, lista_cuotas_ven)
                    monto_vendedor = montos['monto_vendedor']
                    fecha_pago_str = unicode(pago['fecha_de_pago'])
                    try:
                        fecha_pago = unicode(
                            datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"))
                    except Exception, error:
                        print error + ": " + fecha_pago_str

                    # Se setean los datos de cada fila
                    fila = {}
                    fila['mismo_vendedor'] = True
                    fila['vendedor'] = unicode(venta.vendedor)
                    fila['plan'] = unicode(venta.plan_de_pago_vendedor)
                    fila['fecha_de_pago'] = fecha_pago
                    fila['fecha_de_pago_order'] = pago['fecha_de_pago']
                    fila['lote'] = unicode(pago['lote'])
                    fila['cliente'] = unicode(venta.cliente)
                    fila['nro_cuota'] = unicode(pago['nro_cuota_y_total'])
                    fila['total_de_cuotas'] = unicode('{:,}'.format(int(pago['monto']))).replace(",", ".")
                    fila['monto_vendedor'] = unicode('{:,}'.format(monto_vendedor)).replace(",", ".")

                    cuotas_detalles = get_cuota_information_by_lote(pago['lote'].id, int(pago['nro_cuota']), True, True,
                                                                    venta)
                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                    fecha_1 = cuotas_detalles[0]['fecha']
                    parts_1 = fecha_1.split("/")
                    year_1 = parts_1[2];
                    mes_1 = int(parts_1[1]) - 1;
                    mes_year = monthNames[mes_1] + "/" + year_1;
                    fila['mes'] = mes_year

                    # if venta.lote.manzana.fraccion != g_fraccion:
                    if monto_vendedor != 0:
                        ok = False
                        # Se suman los TOTALES por VENDEDOR
                        total_vendedor_monto_vendedor += int(monto_vendedor)
                        total_vendedor_monto_pagado += int(pago['monto'])

                        # Acumulamos para los TOTALES GENERALES
                        total_general_monto_pagado += int(pago['monto'])
                        total_general_monto_vendedor += int(monto_vendedor)

                        filas_vendedor.append(fila)

                else:

                    montos = calculo_montos_liquidacion_vendedores(pago, venta, lista_cuotas_ven)
                    monto_vendedor = montos['monto_vendedor']
                    fecha_pago_str = unicode(pago['fecha_de_pago'])
                    try:
                        fecha_pago = unicode(
                            datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"))
                    except Exception, error:
                        print error + ": " + fecha_pago_str

                    # Se setean los datos de cada fila
                    fila = {}
                    fila['mismo_vendedor'] = True
                    fila['vendedor'] = unicode(venta.vendedor)
                    fila['plan'] = unicode(venta.plan_de_pago_vendedor)
                    fila['fecha_de_pago'] = fecha_pago
                    fila['fecha_de_pago_order'] = pago['fecha_de_pago']
                    fila['lote'] = unicode(pago['lote'])
                    fila['cliente'] = unicode(venta.cliente)
                    fila['nro_cuota'] = unicode(pago['nro_cuota_y_total'])
                    fila['total_de_cuotas'] = unicode('{:,}'.format(int(pago['monto']))).replace(",", ".")
                    fila['monto_vendedor'] = unicode('{:,}'.format(monto_vendedor)).replace(",", ".")

                    cuotas_detalles = get_cuota_information_by_lote(pago['lote'].id, int(pago['nro_cuota']), True, True,
                                                                    venta)
                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                    fecha_1 = cuotas_detalles[0]['fecha']
                    parts_1 = fecha_1.split("/")
                    year_1 = parts_1[2];
                    mes_1 = int(parts_1[1]) - 1;
                    mes_year = monthNames[mes_1] + "/" + year_1;
                    fila['mes'] = mes_year

                    # if venta.vendedor != g_vendedor:
                    if monto_vendedor != 0:
                        ok = False
                        # Se suman los TOTALES por VENDEDOR
                        total_vendedor_monto_vendedor += int(monto_vendedor)
                        total_vendedor_monto_pagado += int(pago['monto'])

                        # Acumulamos para los TOTALES GENERALES
                        total_general_monto_pagado += int(pago['monto'])
                        total_general_monto_vendedor += int(monto_vendedor)

                        filas_vendedor.append(fila)

            except Exception, error:
                print "Error: " + unicode(error) + ", Id Pago: " + unicode(pago['id']) + ", Fraccion: " + unicode(
                    pago['fraccion']) + ", lote: " + unicode(pago['lote']) + " Nro cuota: " + unicode(
                    unicode(pago['nro_cuota_y_total']))

    # Totales GENERALES
    # filas = sorted(filas, key=lambda f: f['fecha_de_pago'])
    if filas_vendedor:
        filas_vendedor = sorted(filas_vendedor, key=lambda f: (f['fecha_de_pago_order']))
        filas_vendedor[0]['mismo_vendedor'] = False
        filas.extend(filas_vendedor)

        fila = {}
        fila['total_monto_pagado'] = unicode('{:,}'.format(total_vendedor_monto_pagado)).replace(",", ".")
        fila['total_monto_vendedor'] = unicode('{:,}'.format(total_vendedor_monto_vendedor)).replace(",", ".")
        total_fraccion_monto_vendedor = 0
        total_fraccion_monto_pagado = 0
        fila['ultimo_pago'] = True
        filas.append(fila)

    fila = {}
    fila['total_general_pagado'] = unicode('{:,}'.format(total_general_monto_pagado)).replace(",", ".")
    fila['total_general_vendedor'] = unicode('{:,}'.format(total_general_monto_vendedor)).replace(",", ".")
    ley = int(total_general_monto_pagado * 0.015)
    filas.append(fila)
    filas[0]['mismo_vendedor'] = False

    ultimo = "&fecha_ini=" + fecha_ini + "&fecha_fin=" + fecha_fin

    lista = filas
    # aquiiiii
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    sheet.paper_size_code = 1
    # sheet.set_portrait(False)
    sheet.fit_width_to_pages = 1
    style = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                        'font: name Calibri, bold True; align: horiz center')
    style2 = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                         'font: name Calibri, bold True, height 200;')
    style3 = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz center')
    style4 = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz right')
    style5 = xlwt.easyxf(
        'pattern: pattern solid, fore_colour white;''font: name Calibri, bold True, height 200 ; align: horiz right')

    style_normal = xlwt.easyxf('font: name Calibri, height 200;')
    style_normal_centrado = xlwt.easyxf('font: name Calibri, height 200; align: horiz center')

    style_fraccion = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                                 'font: name Calibri, bold True; align: horiz center')
    # Titulo
    # sheet.write_merge(0,0,0,7, 'PROPAR S.R.L.' ,style3)
    # sheet.write_merge(1,1,1,7, 'Sistema de Control de Loteamiento' ,style3)

    # sheet.header_str = 'PROPAR S.R.L.'
    periodo_1 = fecha_ini
    periodo_2 = fecha_fin
    usuario = unicode(request.user)
    sheet.header_str = (
        u"&LFecha: &D Hora: &T \nUsuario: " + usuario + " "
                                                        u"&CPROPAR S.R.L.\n LIQUIDACION GENERAL DE VENDEDORES "
                                                        u"&RPeriodo del " + periodo_1 + " al " + periodo_2 + " \nPage &P of &N"
    )
    # sheet.footer_str = 'things'



    c = 0
    sheet.write_merge(c, c, 0, 6, "Liquidacion General de Vendedores: ", style)
    c += 1
    for pago in filas:
        try:
            if pago['total_monto_pagado'] == True and pago['ultimo_pago'] == False:
                c += 1
                sheet.write_merge(c, c, 0, 4, "Liquidacion", style2)

                sheet.write(c, 5, unicode(pago['total_monto_pagado']), style5)
                sheet.write(c, 6, unicode(pago['total_monto_vendedor']), style5)
        except Exception, error:
            print error
            pass

        c += 1
        try:
            if pago['mismo_vendedor'] == False:
                # sheet.write(c, 0, "Fraccion: " + pago['fraccion'],style2)
                sheet.write_merge(c, c, 0, 7, unicode(pago['vendedor']), style_fraccion)
                c += 1
                sheet.write(c, 0, 'Lote', style)
                sheet.write(c, 1, 'Fecha de pago', style)
                sheet.write(c, 2, 'Cliente', style)
                sheet.write(c, 3, 'Nro cuota', style)
                sheet.write(c, 4, 'Mes', style)
                sheet.write(c, 5, 'Monto Pag.', style)
                sheet.write(c, 6, 'Vendedor', style)
                c += 1

            sheet.write(c, 0, unicode(pago['lote']), style_normal_centrado)
            sheet.write(c, 1, unicode(pago['fecha_de_pago']), style_normal_centrado)
            sheet.write(c, 2, unicode(pago['cliente']), style_normal)
            sheet.write(c, 3, unicode(pago['nro_cuota']), style_normal_centrado)
            sheet.write(c, 4, unicode(pago['mes']), style_normal_centrado)
            try:
                sheet.write(c, 5, unicode(pago['total_de_cuotas']), style4)
            except Exception, error:
                sheet.write(c, 5, unicode(pago['monto_pagado']), style4)

            sheet.write(c, 6, unicode(pago['monto_vendedor']), style4)
        except Exception, error:
            print error

        try:
            if (pago['ultimo_pago'] == True):
                c += 1
                sheet.write_merge(c, c, 0, 4, "Liquidacion", style2)
                sheet.write(c, 5, unicode(pago['total_monto_pagado']), style5)
                sheet.write(c, 6, unicode(pago['total_monto_vendedor']), style5)
        except Exception, error:
            print error
            pass

        try:
            if (pago['total_general_pagado']):
                c += 1
                sheet.write_merge(c, c, 0, 4, "Liquidacion Total", style2)
                sheet.write(c, 5, unicode(pago['total_general_pagado']), style5)
                sheet.write(c, 6, unicode(pago['total_general_vendedor']), style5)


        except Exception, error:
            print error
            pass

        # Ancho de la columna Lote
        col_lote = sheet.col(0)
        col_lote.width = 256 * 12  # 12 characters wide

        # Ancho de la columna Fecha
        col_fecha = sheet.col(1)
        col_fecha.width = 256 * 12  # 10 characters wide

        # Ancho de la columna Nombre
        col_nombre = sheet.col(2)
        col_nombre.width = 256 * 25  # 25 characters wide

        # Ancho de la columna Nro cuota
        col_nro_cuota = sheet.col(3)
        col_nro_cuota.width = 256 * 10  # 6 characters wide

        # Ancho de la columna mes
        col_mes = sheet.col(4)
        col_mes.width = 256 * 8  # 8 characters wide

        # Ancho de la columna monto pagado
        col_monto_pagado = sheet.col(5)
        col_monto_pagado.width = 256 * 10  # 12 characters wide

        # Ancho de la columna monto vendedor
        col_monto_inmo = sheet.col(6)
        col_monto_inmo.width = 256 * 12  # 15 characters wide

        # Ancho de la columna monto propietario
        col_nombre = sheet.col(7)
        col_nombre.width = 256 * 11  # 11 characters wide

    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo
    fecha_actual = datetime.datetime.now().date()
    fecha_str = unicode(fecha_actual)
    fecha = unicode(datetime.datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y"))

    # if b_fraccion:
    #     response['Content-Disposition'] = 'attachment; filename=' + 'liq_vend_'+g_nombre_fraccion+'_'+fecha+'.xls'
    # elif b_vendedor:
    #     response['Content-Disposition'] = 'attachment; filename=' + 'liq_vend_'+g_nombre_vendedor+'_'+fecha+'.xls'
    # else:
    #     response['Content-Disposition'] = 'attachment; filename=' + 'liquidacion_vendedores_.xls'
    response['Content-Disposition'] = 'attachment; filename=' + 'liquidacion_general_vendedores_.xls'

    wb.save(response)
    return response


def liquidacion_gerentes_reporte_excel(request):
    tipo_liquidacion = request.GET['tipo_liquidacion']
    fecha_ini = request.GET['fecha_ini']
    fecha_fin = request.GET['fecha_fin']
    fecha_ini_parsed = unicode(datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date())
    fecha_fin_parsed = unicode(datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date())
    query = (
        '''
    SELECT pc.* FROM principal_pagodecuotas pc, principal_lote l, principal_manzana m, principal_fraccion f
    WHERE pc.fecha_de_pago >= \'''' + fecha_ini_parsed +
        '''\' AND pc.fecha_de_pago <= \'''' + fecha_fin_parsed +
        '''\'
    AND (pc.lote_id = l.id AND l.manzana_id=m.id AND m.fraccion_id=f.id) ORDER BY pc.vendedor_id, f.id, pc.fecha_de_pago
    '''
    )

    print(query)
    lista_pagos = list(PagoDeCuotas.objects.raw(query))
    if tipo_liquidacion == 'gerente_ventas':
        tipo_gerente = "Gerente de Ventas"
    if tipo_liquidacion == 'gerente_admin':
        tipo_gerente = "Gerente Administrativo"

    # totales por vendedor
    total_importe = 0
    total_comision = 0

    # totales generales
    total_general_importe = 0
    total_general_comision = 0
    k = 0  # variable de control
    cuotas = []
    # Seteamos los datos de las filas
    for i, cuota_item in enumerate(lista_pagos):
        nro_cuota = get_nro_cuota(cuota_item)
        cuota = {}
        com = 0
        # Esta es una regla de negocio, los vendedores cobran comisiones segun el numero de cuota, maximo hasta la cuota Nro 9.
        # Si el plan de pago tiene hasta 12 cuotas, los vendedores cobran una comision sobre todas las cuotas.
        cuotas_para_vendedor = ((cuota_item.plan_de_pago_vendedor.cantidad_cuotas) * (
            cuota_item.plan_de_pago_vendedor.intervalos)) - cuota_item.plan_de_pago_vendedor.cuota_inicial
        # A los vendedores le corresponde comision por las primeras 4 (maximo 5) cuotas impares.
        if ((nro_cuota % 2 != 0 and nro_cuota <= cuotas_para_vendedor) or (
                        cuota_item.plan_de_pago.cantidad_de_cuotas <= 12 and nro_cuota <= 12)):
            if k == 0:
                # Guardamos el vendedor asociado a la primera cuota que cumple con la condicion, para tener algo con que comparar.
                vendedor_actual = cuota_item.vendedor.id
                fraccion_actual = cuota_item.lote.manzana.fraccion
            k += 1
            # print k
            if (cuota_item.vendedor.id == vendedor_actual and cuota_item.lote.manzana.fraccion == fraccion_actual):
                # comision de las cuotas
                com = int(cuota_item.total_de_cuotas * (
                    float(cuota_item.plan_de_pago_vendedor.porcentaje_de_cuotas) / float(100)))
                if (cuota_item.venta.entrega_inicial):
                    # comision de la entrega inicial, si la hubiere
                    com_inicial = int(cuota_item.venta.entrega_inicial * (
                        float(cuota_item.plan_de_pago_vendedor.porcentaje_cuota_inicial) / float(100)))
                    cuota['concepto'] = "Entrega Inicial"
                    cuota['cuota_nro'] = unicode(0) + '/' + unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                    cuota['comision'] = unicode('{:,}'.format(com_inicial)).replace(",", ".")
                else:
                    cuota['concepto'] = "Pago de Cuota"
                    cuota['cuota_nro'] = unicode(nro_cuota) + '/' + unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                    cuota['comision'] = unicode('{:,}'.format(com)).replace(",", ".")
                cuota['fraccion'] = unicode(cuota_item.lote.manzana.fraccion)
                cuota['vendedor'] = unicode(cuota_item.vendedor)
                cuota['fraccion_id'] = cuota_item.lote.manzana.fraccion.id
                cuota['lote'] = unicode(cuota_item.lote)
                cuota['fecha_pago'] = unicode(cuota_item.fecha_de_pago)
                cuota['importe'] = unicode('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".")

                # Sumamos los totales por vendedor
                total_importe += cuota_item.total_de_cuotas
                total_comision += com
                # Guardamos el ultimo lote que cumple la condicion en dos variables, por si se convierta en el ultimo lote para cerrar la fraccion
                # actual, o por si sea el ultimo lote de la lista.
                anterior = cuota
                ultimo = cuota
                # Hay cambio de lote pero NO es el ultimo elemento todavia
            else:
                com = int(cuota_item.total_de_cuotas * (
                    float(cuota_item.plan_de_pago_vendedor.porcentaje_de_cuotas) / float(100)))
                if (cuota_item.venta.entrega_inicial):
                    # comision de la entrega inicial, si la hubiere
                    com_inicial = int(cuota_item.venta.entrega_inicial * (
                        float(cuota_item.plan_de_pago_vendedor.porcentaje_cuota_inicial) / float(100)))
                    cuota['concepto'] = "Entrega Inicial"
                    cuota['cuota_nro'] = unicode(0) + '/' + unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                    cuota['comision'] = unicode('{:,}'.format(com_inicial)).replace(",", ".")
                else:
                    cuota['concepto'] = "Pago de Cuota"
                    cuota['cuota_nro'] = unicode(nro_cuota) + '/' + unicode(cuota_item.plan_de_pago.cantidad_de_cuotas)
                    cuota['comision'] = unicode('{:,}'.format(com)).replace(",", ".")
                cuota['fraccion'] = unicode(cuota_item.lote.manzana.fraccion)
                cuota['vendedor'] = unicode(cuota_item.vendedor)
                cuota['fraccion_id'] = cuota_item.lote.manzana.fraccion.id
                cuota['lote'] = unicode(cuota_item.lote)
                cuota['fecha_pago'] = unicode(cuota_item.fecha_de_pago)
                cuota['importe'] = unicode('{:,}'.format(cuota_item.total_de_cuotas)).replace(",", ".")
                cuota['total_importe'] = unicode('{:,}'.format(total_importe)).replace(",", ".")
                cuota['total_comision'] = unicode('{:,}'.format(total_comision)).replace(",", ".")

                # Se CERAN  los TOTALES por VENDEDOR
                total_importe = 0
                total_comision = 0

                # Sumamos los totales por fraccion
                total_importe += cuota_item.total_de_cuotas
                total_comision += com
                vendedor_actual = cuota_item.vendedor.id
                fraccion_actual = cuota_item.lote.manzana.fraccion
                ultimo = cuota
            total_general_importe += cuota_item.total_de_cuotas
            total_general_comision += com
            cuotas.append(cuota)
            # Si es el ultimo lote, cerramos totales de fraccion
        if (len(lista_pagos) - 1 == i):
            try:
                ultimo['total_importe'] = unicode('{:,}'.format(total_importe)).replace(",", ".")
                ultimo['total_comision'] = unicode('{:,}'.format(total_comision)).replace(",", ".")
                ultimo['total_general_importe'] = unicode('{:,}'.format(total_general_importe)).replace(",", ".")
                ultimo['total_general_comision'] = unicode('{:,}'.format(total_general_comision)).replace(",", ".")
            except Exception, error:
                print error
                pass

    monto_calculado = int(math.ceil((float(total_general_importe) * float(0.1)) / float(2)))
    monto_calculado = unicode('{:,}'.format(monto_calculado)).replace(",", ".")

    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    sheet.paper_size_code = 1
    style = xlwt.easyxf('pattern: pattern solid, fore_colour green;'
                        'font: name Arial, bold True;')
    style2 = xlwt.easyxf('font: name Arial, bold True;')
    # cabeceras
    sheet.write(0, 0, "Fecha", style)
    sheet.write(0, 1, "Vendedor", style)
    sheet.write(0, 2, "Cuota Nro.", style)
    sheet.write(0, 3, "Importe", style)
    sheet.write(0, 4, "Comision", style)

    # contador de filas
    c = 0
    for i, cuota in enumerate(cuotas):
        if (i == len(cuotas) - 1):
            try:
                if (cuota['total_general_importe']):
                    c += 1
                    sheet.write(c, 0, unicode(cuota['fecha_pago']))
                    sheet.write(c, 1, unicode(cuota['vendedor']))
                    sheet.write(c, 2, unicode(cuota['cuota_nro']))
                    sheet.write(c, 3, unicode(cuota['importe']))
                    sheet.write(c, 4, unicode(cuota['comision']))
                    c += 1
                    sheet.write(c, 0, "Totales del Vendedor", style2)
                    sheet.write(c, 3, unicode(cuota['total_importe']))
                    sheet.write(c, 4, unicode(cuota['total_comision']))
                    c += 1
                    sheet.write(c, 0, "Totales Generales", style2)
                    sheet.write(c, 3, unicode(cuota['total_general_importe']))
                    sheet.write(c, 4, unicode(cuota['total_general_comision']))
            except Exception, error:
                print error
                pass
        else:
            try:
                if (cuota['total_importe']):
                    c += 1
                    sheet.write(c, 0, "Totales del Vendedor", style2)
                    sheet.write(c, 3, unicode(cuota['total_importe']))
                    sheet.write(c, 4, unicode(cuota['total_comision']))
            except Exception, error:
                print error
                pass
            c += 1
            sheet.write(c, 0, unicode(cuota['fecha_pago']))
            sheet.write(c, 1, unicode(cuota['vendedor']))
            sheet.write(c, 2, unicode(cuota['cuota_nro']))
            sheet.write(c, 3, unicode(cuota['importe']))
            sheet.write(c, 4, unicode(cuota['comision']))
    c += 2
    sheet.write(c, 0, "Gerente: ", style2)
    sheet.write(c, 1, tipo_gerente, style2)
    c += 1
    sheet.write(c, 0, "Liquidacion: ", style2)
    sheet.write(c, 1, monto_calculado, style2)
    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo
    response['Content-Disposition'] = 'attachment; filename=' + 'liquidacion_gerentes.xls'
    wb.save(response)
    return response


def informe_movimientos_reporte_excel(request):
    lista_movimientos = []
    lote_ini_orig = request.GET['lote_ini']
    lote_fin_orig = request.GET['lote_fin']
    fecha_ini = request.GET['fecha_ini']
    fecha_fin = request.GET['fecha_fin']
    lote_ini_parsed = unicode(lote_ini_orig)
    lote_fin_parsed = unicode(lote_fin_orig)
    fecha_ini_parsed = None
    fecha_fin_parsed = None
    lotes = []
    lotes.append(lote_ini_parsed)
    lotes.append(lote_fin_parsed)
    # print lotes
    rango_lotes_id = []
    try:
        for l in lotes:
            fraccion_int = int(l[0:3])
            nombre_fraccion = Fraccion.objects.get(id=fraccion_int)
            manzana_int = int(l[4:7])
            lote_int = int(l[8:])
            manzana = Manzana.objects.get(fraccion_id=fraccion_int, nro_manzana=manzana_int)
            lote = Lote.objects.get(manzana=manzana.id, nro_lote=lote_int)
            rango_lotes_id.append(lote.id)
        print rango_lotes_id
    except Exception, error:
        print error
    lote_ini = str(rango_lotes_id[0])
    lote_fin = str(rango_lotes_id[1])
    lista_movimientos = []
    print 'lote inicial->' + unicode(lote_ini)
    print 'lote final->' + unicode(lote_fin)
    if fecha_ini != '' and fecha_fin != '':
        fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date()
        fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date()
        try:
            lista_ventas = Venta.objects.filter(lote_id__range=(lote_ini, lote_fin)).order_by('lote__nro_lote')
            lista_reservas = Reserva.objects.filter(lote_id__range=(lote_ini, lote_fin),
                                                    fecha_de_reserva__range=(fecha_ini_parsed, fecha_fin_parsed))
            lista_cambios = CambioDeLotes.objects.filter(
                Q(lote_nuevo_id__range=(lote_ini, lote_fin)) | Q(lote_a_cambiar__range=(lote_ini, lote_fin)),
                fecha_de_cambio__range=(fecha_ini_parsed, fecha_fin_parsed))
            lista_transferencias = TransferenciaDeLotes.objects.filter(lote_id__range=(lote_ini, lote_fin),
                                                                       fecha_de_transferencia__range=(
                                                                           fecha_ini_parsed, fecha_fin_parsed))
        except Exception, error:
            print error
            lista_ventas = []
            lista_reservas = []
            lista_cambios = []
            lista_transferencias = []
            pass
    else:
        try:
            lista_ventas = Venta.objects.filter(lote_id__range=(lote_ini, lote_fin)).order_by('lote__nro_lote')
            lista_cambios = CambioDeLotes.objects.filter(
                Q(lote_nuevo_id__range=(lote_ini, lote_fin)) | Q(lote_a_cambiar__range=(lote_ini, lote_fin)))
            lista_reservas = Reserva.objects.filter(lote_id__range=(lote_ini, lote_fin))
            lista_transferencias = TransferenciaDeLotes.objects.filter(lote_id__range=(lote_ini, lote_fin))
        except Exception, error:
            print error
            lista_ventas = []
            lista_reservas = []
            lista_cambios = []
            lista_transferencias = []
            pass

    if lista_ventas:
        print('Hay ventas asociadas a este lote')
        lista_movimientos = []
        # En este punto tenemos ventas asociadas a este lote
        try:
            for item_venta in lista_ventas:
                try:
                    resumen_venta = {}
                    fecha_venta_str = unicode(item_venta.fecha_de_venta)
                    resumen_venta['fecha_de_venta'] = unicode(
                        datetime.datetime.strptime(fecha_venta_str, "%Y-%m-%d").strftime("%d/%m/%Y"))
                    resumen_venta['lote'] = item_venta.lote
                    resumen_venta['cliente'] = item_venta.cliente
                    resumen_venta['cantidad_de_cuotas'] = item_venta.plan_de_pago.cantidad_de_cuotas
                    resumen_venta['precio_final'] = unicode('{:,}'.format(item_venta.precio_final_de_venta)).replace(
                        ",", ".")
                    resumen_venta['entrega_inicial'] = unicode('{:,}'.format(item_venta.entrega_inicial)).replace(",",
                                                                                                                  ".")
                    resumen_venta['tipo_de_venta'] = item_venta.plan_de_pago.tipo_de_plan
                    RecuperacionDeLotes.objects.get(venta=item_venta.id)
                    try:
                        venta_pagos_query_set = get_pago_cuotas_2(item_venta, fecha_ini_parsed, fecha_fin_parsed)
                        resumen_venta['recuperacion'] = True
                    except PagoDeCuotas.DoesNotExist:
                        venta_pagos_query_set = []
                except RecuperacionDeLotes.DoesNotExist:
                    print 'se encontro la venta no recuperada, la venta actual'
                    try:
                        venta_pagos_query_set = get_pago_cuotas_2(item_venta, fecha_ini_parsed, fecha_fin_parsed)
                        resumen_venta['recuperacion'] = False
                    except PagoDeCuotas.DoesNotExist:
                        venta_pagos_query_set = []

                ventas_pagos_list = []
                ventas_pagos_list.insert(0,
                                         resumen_venta)  # El primer elemento de la lista de pagos es el resumen de la venta
                saldo_anterior = item_venta.precio_final_de_venta
                monto = item_venta.entrega_inicial
                saldo = saldo_anterior - monto
                tipo_de_venta = item_venta.plan_de_pago.tipo_de_plan
                for pago in venta_pagos_query_set:
                    saldo_anterior = saldo
                    monto = long(pago['monto'])
                    saldo = saldo_anterior - monto
                    cuota = {}
                    cuota['vencimiento'] = ""
                    cuota['tipo_de_venta'] = tipo_de_venta
                    fecha_pago_str = unicode(pago['fecha_de_pago'])
                    cuota['fecha_de_pago'] = unicode(
                        datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"))
                    cuota['id'] = pago['id']
                    cuota['nro_cuota'] = pago['nro_cuota_y_total']

                    cuotas_detalles = []
                    cuotas_detalles = get_cuota_information_by_lote(pago['lote'].id, int(pago['nro_cuota']), True, True,
                                                                    item_venta)
                    cuota['vencimiento'] = cuota['vencimiento'] + unicode(cuotas_detalles[0]['fecha']) + ' '

                    monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
                    fecha_1 = cuota['vencimiento']
                    parts_1 = fecha_1.split("/")
                    year_1 = parts_1[2];
                    mes_1 = int(parts_1[1]) - 1;
                    mes_year = monthNames[mes_1] + "/" + year_1;
                    cuota['mes'] = mes_year
                    cuota['saldo_anterior'] = unicode('{:,}'.format(int(saldo_anterior))).replace(",", ".")
                    cuota['monto'] = unicode('{:,}'.format(int(pago['monto']))).replace(",", ".")
                    cuota['saldo'] = unicode('{:,}'.format(int(saldo))).replace(",", ".")
                    ventas_pagos_list.append(cuota)
                lista_movimientos.append(ventas_pagos_list)
        except Exception, error:
            print error

    mostrar_transferencias = False
    mostrar_mvtos = False
    mostrar_reservas = False
    mostrar_cambios = False

    if lista_movimientos:
        mostrar_mvtos = True
    if lista_cambios:
        mostrar_cambios = True
    if lista_reservas:
        mostrar_reservas = True
    if lista_transferencias:
        mostrar_transferencias = True

    ultimo = "&lote_ini=" + lote_ini_orig + "&lote_fin=" + lote_fin_orig + "&fecha_ini=" + fecha_ini + "&fecha_fin=" + fecha_fin

    lista = lista_movimientos

    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    sheet.paper_size_code = 1
    style = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                        'font: name Calibri, bold True, height 200; align: horiz center')
    style2 = xlwt.easyxf('font: name Calibri, height 200;')

    style3 = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz right')

    style4 = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz center')

    # Este estilo pidio Ivan para pulir el informe en una forma visual mas agradable, antes usaba el style4 que es en negrita
    style_titulos_columna_resaltados_centrados = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                                                             'font: name Calibri; align: horiz center')

    # BORDES PARA las columnas de titulos
    borders = xlwt.Borders()
    borders.top = xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.DOUBLE
    style_titulos_columna_resaltados_centrados.borders = borders
    usuario = unicode(request.user)

    if fecha_ini != '' and fecha_fin != '':
        sheet.header_str = (
            u"&LFecha: &D Hora: &T \nUsuario: " + usuario + " "
                                                            u"&CPROPAR S.R.L.\n MOVIMIENTOS DE LOTES "
                                                            u"&RPeriodo del : " + fecha_ini + " al " + fecha_fin + " \nPage &P of &N"
        )
    else:
        sheet.header_str = (
            u"&LFecha: &D Hora: &T \nUsuario: " + usuario + " "
                                                            u"&CPROPAR S.R.L.\n MOVIMIENTOS DE LOTES "
                                                            u"&RPage &P of &N"
        )

    c = 0

    if mostrar_mvtos == True:
        for venta in lista:
            for i, pago in enumerate(venta):
                if i == 0:
                    if pago['recuperacion']:
                        # cabeceras
                        # A pedido de Ivan, se dejan de mostrar estas cabeceras de resumenes de venta, es decir, las cabeceras
                        # sheet.write_merge(c,c,0,6, "Venta lote: "+unicode(pago['lote'])+" a "+unicode(pago['cliente']), style)
                        # c=c+1
                        # sheet.write(c, 0, "Lote", style)
                        # sheet.write(c, 1, "Fecha", style)
                        # sheet.write(c, 2, "Cliente", style)
                        # sheet.write(c, 3, "Tipo", style)
                        # sheet.write(c, 4, "Estado", style)
                        # sheet.write(c, 5, "Entrega Inicial", style)
                        # sheet.write(c, 6, "Precio Venta", style)
                        #
                        # c=c+1
                        #
                        # sheet.write(c, 0, unicode(pago['lote']), style4)
                        # sheet.write(c, 1, pago['fecha_de_venta'], style4)
                        # sheet.write(c, 2, unicode(pago['cliente']), style2)
                        # sheet.write(c, 3, pago['tipo_de_venta'], style2)
                        # sheet.write(c, 4, "VENTA RECUPERADA", style4)
                        # sheet.write(c, 5, pago['entrega_inicial'], style3)
                        # sheet.write(c, 6, pago['precio_final'], style3)

                        if pago['tipo_de_venta'] == 'credito':
                            c = c + 1
                            fraccion = Fraccion.objects.get(id=pago['lote'].codigo_paralot[:3])
                            lote = Lote.objects.get(codigo_paralot=pago['lote'].codigo_paralot)
                            sheet.write_merge(c, c, 0, 6, "Pagos: " + fraccion.nombre + ' ' + unicode(
                                pago['lote']) + " a " + unicode(
                                pago['cliente']) + "    Estado:  VENTA RECUPERADA " + "Cta Cte Ctral: " + unicode(
                                lote.cuenta_corriente_catastral), style4)
                            c = c + 1
                            sheet.write(c, 0, "Fecha", style_titulos_columna_resaltados_centrados)
                            sheet.write(c, 1, "Cuota", style_titulos_columna_resaltados_centrados)
                            sheet.write(c, 2, "Vencimiento", style_titulos_columna_resaltados_centrados)
                            sheet.write(c, 3, "Mes", style_titulos_columna_resaltados_centrados)
                            sheet.write(c, 4, "Saldo Anterior", style_titulos_columna_resaltados_centrados)
                            sheet.write(c, 5, "Monto", style_titulos_columna_resaltados_centrados)
                            sheet.write(c, 6, "Saldo", style_titulos_columna_resaltados_centrados)

                        c = c + 1

                    else:

                        # cabeceras
                        # sheet.write_merge(c,c,0,6, "Venta lote: "+unicode(pago['lote'])+" a "+unicode(pago['cliente']), style)
                        # c=c+1
                        # sheet.write(c, 0, "Lote", style)
                        # sheet.write(c, 1, "Fecha", style)
                        # sheet.write(c, 2, "Cliente", style)
                        # sheet.write(c, 3, "Tipo", style)
                        # sheet.write(c, 4, "Estado", style)
                        # sheet.write(c, 5, "Entrega Inicial", style)
                        # sheet.write(c, 6, "Precio Venta", style)
                        #
                        # c=c+1
                        #
                        # sheet.write(c, 0, unicode(pago['lote']), style4)
                        # sheet.write(c, 1, pago['fecha_de_venta'], style4)
                        # sheet.write(c, 2, unicode(pago['cliente']), style2)
                        # sheet.write(c, 3, pago['tipo_de_venta'], style4)
                        # sheet.write(c, 4, "VENTA ACTUAL", style4)
                        # sheet.write(c, 5, pago['entrega_inicial'], style3)
                        # sheet.write(c, 6, pago['precio_final'], style3)

                        if pago['tipo_de_venta'] == 'credito':
                            # c=c+1
                            # sheet.write_merge(c,c,0,6, "Pagos de la Venta: "+unicode(pago['lote'])+" a "+unicode(pago['cliente']), style4)
                            fraccion = Fraccion.objects.get(id=pago['lote'].codigo_paralot[:3])
                            lote = Lote.objects.get(codigo_paralot=pago['lote'].codigo_paralot)
                            sheet.write_merge(c, c, 0, 6, "Pagos: " + fraccion.nombre + ' ' + unicode(
                                pago['lote']) + " a " + unicode(
                                pago['cliente']) + "    Estado: VENTA ACTUAL " + "Cta Cte Ctral: " + unicode(
                                lote.cuenta_corriente_catastral), style4)
                            c = c + 1
                            sheet.write(c, 0, "Fecha", style_titulos_columna_resaltados_centrados)
                            sheet.write(c, 1, "Cuota", style_titulos_columna_resaltados_centrados)
                            sheet.write(c, 2, "Vencimiento", style_titulos_columna_resaltados_centrados)
                            sheet.write(c, 3, "Mes", style_titulos_columna_resaltados_centrados)
                            sheet.write(c, 4, "Saldo Anterior", style_titulos_columna_resaltados_centrados)
                            sheet.write(c, 5, "Monto", style_titulos_columna_resaltados_centrados)
                            sheet.write(c, 6, "Saldo", style_titulos_columna_resaltados_centrados)

                        c = c + 1
                else:

                    sheet.write(c, 0, pago['fecha_de_pago'], style4)
                    sheet.write(c, 1, pago['nro_cuota'], style4)
                    sheet.write(c, 2, pago['vencimiento'], style4)
                    sheet.write(c, 3, pago['mes'], style4)
                    sheet.write(c, 4, pago['saldo_anterior'], style3)
                    sheet.write(c, 5, pago['monto'], style3)
                    sheet.write(c, 6, pago['saldo'], style3)

                    c = c + 1

    if mostrar_cambios == True:
        # poner titulo de cambio
        sheet.write_merge(c, c, 0, 3, "Cambio de Lote", style)
        c = c + 1
        sheet.write(c, 0, "Fecha", style)
        sheet.write(c, 1, "Cliente", style)
        sheet.write(c, 2, "Lote a Cambiar", style)
        sheet.write(c, 3, "Lote Nuevo", style)

        c = c + 1

        for cambio in lista_cambios:
            sheet.write(c, 0, unicode(
                datetime.datetime.strptime(unicode(cambio.fecha_de_cambio), "%Y-%m-%d").strftime("%d/%m/%Y")), style4)
            sheet.write(c, 1, unicode(cambio.cliente), style2)
            sheet.write(c, 2, unicode(cambio.lote_a_cambiar), style4)
            sheet.write(c, 3, unicode(cambio.lote_nuevo), style4)

            c = c + 1

    if mostrar_reservas == True:
        # poner titulo de reserva y lote reservado
        sheet.write_merge(c, c, 0, 3, "Reserva de Lote", style)
        c = c + 1
        sheet.write(c, 0, "Fecha", style)
        sheet.write(c, 1, "Cliente", style)
        sheet.write(c, 2, "Lote", style)
        c = c + 1

        for reserva in lista_reservas:
            sheet.write(c, 0, unicode(
                datetime.datetime.strptime(unicode(reserva.fecha_de_reserva), "%Y-%m-%d").strftime("%d/%m/%Y")), style4)
            sheet.write(c, 1, unicode(reserva.cliente), style2)
            sheet.write(c, 2, unicode(reserva.lote), style4)
            c = c + 1

    if mostrar_transferencias == True:
        # poner titulo de transferencia
        sheet.write_merge(c, c, 0, 3, "Transferencia de Lote", style)
        c = c + 1
        sheet.write(c, 0, "Fecha", style)
        sheet.write(c, 1, "Cliente Orig.", style)
        sheet.write(c, 2, "Cliente Trans.", style)
        sheet.write(c, 3, "Vendedor", style)
        sheet.write(c, 4, "Plan de Pago", style)

        c = c + 1

        for transferencia in lista_transferencias:
            sheet.write(c, 0, unicode(
                datetime.datetime.strptime(unicode(transferencia.fecha_de_transferencia), "%Y-%m-%d").strftime(
                    "%d/%m/%Y")), style4)
            sheet.write(c, 1, unicode(transferencia.cliente_original), style2)
            sheet.write(c, 2, unicode(transferencia.cliente), style2)
            sheet.write(c, 3, unicode(transferencia.vendedor), style2)
            sheet.write(c, 4, unicode(transferencia.plan_de_pago), style2)

            c = c + 1

    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo
    response['Content-Disposition'] = 'attachment; filename=' + 'informe_movimientos.xls'
    wb.save(response)
    return response


def informe_ventas(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
                if (filtros_establecidos(request.GET, 'informe_ventas') == False):
                    t = loader.get_template('informes/informe_ventas.html')
                    c = RequestContext(request, {
                        'object_list': [],
                    })
                    return HttpResponse(t.render(c))
                else:  # Parametros seteados
                    lista_movimientos = []
                    t = loader.get_template('informes/informe_ventas.html')
                    lote_id = request.GET['busqueda']
                    busqueda_label = request.GET['busqueda_label']
                    busqueda = lote_id
                    lote = Lote.objects.get(pk=lote_id)
                    lista_ventas = Venta.objects.filter(lote_id=lote.id).order_by('-fecha_de_venta')
                    try:
                        for item_venta in lista_ventas:
                            try:
                                resumen_venta = {}
                                resumen_venta['id'] = item_venta.id
                                resumen_venta['fecha_de_venta'] = datetime.datetime.strptime(
                                    unicode(item_venta.fecha_de_venta), "%Y-%m-%d").strftime("%d/%m/%Y")
                                resumen_venta['lote'] = item_venta.lote
                                resumen_venta['cliente'] = item_venta.cliente
                                resumen_venta['cantidad_de_cuotas'] = item_venta.plan_de_pago.cantidad_de_cuotas
                                resumen_venta['precio_final'] = unicode(
                                    '{:,}'.format(item_venta.precio_final_de_venta)).replace(",", ".")
                                resumen_venta['precio_de_cuota'] = unicode(
                                    '{:,}'.format(item_venta.precio_de_cuota)).replace(",", ".")
                                resumen_venta['fecha_primer_vencimiento'] = datetime.datetime.strptime(
                                    unicode(item_venta.fecha_primer_vencimiento), "%Y-%m-%d").strftime("%d/%m/%Y")
                                resumen_venta['entrega_inicial'] = unicode(
                                    '{:,}'.format(item_venta.entrega_inicial)).replace(",", ".")
                                resumen_venta['vendedor'] = item_venta.vendedor
                                resumen_venta['plan_de_pago'] = item_venta.plan_de_pago
                                #resumen_venta['pagos_realizados'] = item_venta.pagos_realizados
                                resumen_venta['recuperado'] = item_venta.recuperado

                                # venta_pagos_query_set = get_pago_cuotas(item_venta,None,None)
                                venta_pagos_query_set = PagoDeCuotas.objects.filter(venta_id=item_venta.id).order_by(
                                    "fecha_de_pago", "id")

                                #para insertar la cantidad de pagos realizados en el resumen de venta
                                cant_pagos = 0
                                #obtenemos la sumatoria de los distintos pagos de la venta.
                                for paymet in venta_pagos_query_set:
                                    cant_pagos = cant_pagos + paymet.nro_cuotas_a_pagar

                                resumen_venta['pagos_realizados'] = cant_pagos

                                venta = Venta.objects.get(pk=item_venta.id)
                                #actualizamos la cantidad de pagos realizados dentro de ventas.
                                venta.pagos_realizados = int(cant_pagos)
                                venta.save()
                            except Exception, error:
                                print error
                            ventas_pagos_list = []
                            ventas_pagos_list.insert(0,
                                                     resumen_venta)  # El primer elemento de la lista de pagos es el resumen de la venta
                            contador_cuotas = 0

                            for pago in venta_pagos_query_set:
                                cuota = {}
                                cuota['fecha_de_pago'] = datetime.datetime.strptime(unicode(pago.fecha_de_pago),
                                                                                    "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")
                                cuota['id'] = pago.id
                                detalle_str = ""
                                cuota['detalle'] = ""
                                cuota['dias_atraso'] = ""
                                cuota['vencimiento'] = ""
                                try:
                                    cuota['id_transaccion'] = pago.transaccion.id
                                except:
                                    cuota['id_transaccion'] = None

                                if pago.factura_id != None:
                                    cuota['factura'] = pago.factura
                                else:
                                    cuota['factura'] = None
                                # Si se paga mas de una cuota
                                if pago.nro_cuotas_a_pagar > 1:
                                    cuota['nro_cuota'] = unicode(contador_cuotas + 1) + " al " + unicode(
                                        contador_cuotas + pago.nro_cuotas_a_pagar)

                                    # detalle para fecha de vencimiento

                                    c = 0
                                    cuota['vencimiento'] = ""
                                    cuota['dias_atraso'] = ""
                                    for x in range(0, pago.nro_cuotas_a_pagar):
                                        contador_cuotas = contador_cuotas + 1
                                        cuotas_detalles = []
                                        cuotas_detalles = get_cuota_information_by_lote(lote_id, contador_cuotas, True,
                                                                                        True)
                                        cuota['vencimiento'] = cuota['vencimiento'] + unicode(
                                            cuotas_detalles[0]['fecha']) + ' '

                                        fecha_pago_parsed = datetime.datetime.strptime(cuota['fecha_de_pago'],
                                                                                       "%d/%m/%Y %H:%M:%S").date()
                                        proximo_vencimiento_parsed = datetime.datetime.strptime(
                                            unicode(cuotas_detalles[0]['fecha']), "%d/%m/%Y").date()
                                        dias_atraso = obtener_dias_atraso(fecha_pago_parsed, proximo_vencimiento_parsed)
                                        cuota['dias_atraso'] = cuota['dias_atraso'] + " * " + unicode(
                                            dias_atraso) + " dias "

                                        c = c + 1
                                        pago_detalle = pago.detalle
                                        monto_intereses = 0
                                        if pago_detalle != None and pago_detalle != '':
                                            # pago_detalle = json.dumps(pago_detalle)
                                            pago_detalle = json.loads(pago_detalle)
                                            detalle_str = ""
                                            for x in range(0, len(pago_detalle)):
                                                try:
                                                    detalle_str = detalle_str + " Intereses: " + unicode('{:,}'.format(
                                                        pago_detalle['item' + unicode(x)]['intereses'])).replace(",",
                                                                                                                 ".")
                                                    monto_intereses = monto_intereses + int(
                                                        pago_detalle['item' + unicode(x)]['intereses'])
                                                except Exception, error:
                                                    try:
                                                        detalle_str = detalle_str + " Gestion Cobranza: " + unicode(
                                                            '{:,}'.format(int(pago_detalle['item' + unicode(x)][
                                                                                  'gestion_cobranza']))).replace(",",
                                                                                                                 ".")
                                                    except Exception, error:
                                                        print error


                                # si se paga solo una cuota
                                else:
                                    contador_cuotas = contador_cuotas + pago.nro_cuotas_a_pagar
                                    # detalle para fecha de vencimiento
                                    cuotas_detalles = []
                                    cuotas_detalles = get_cuota_information_by_lote(lote_id, contador_cuotas, True,
                                                                                    True, item_venta)
                                    try:
                                        cuota['vencimiento'] = unicode(cuotas_detalles[0]['fecha'])
                                    except:
                                        print "pago cancelado"

                                    fecha_pago_parsed = datetime.datetime.strptime(cuota['fecha_de_pago'],
                                                                                   "%d/%m/%Y %H:%M:%S").date()
                                    proximo_vencimiento_parsed = datetime.datetime.strptime(cuota['vencimiento'],
                                                                                            "%d/%m/%Y").date()
                                    dias_atraso = obtener_dias_atraso(fecha_pago_parsed, proximo_vencimiento_parsed)
                                    cuota['dias_atraso'] = cuota['dias_atraso'] + " * " + unicode(
                                        dias_atraso) + " dias "

                                    cuota['nro_cuota'] = unicode(contador_cuotas)
                                    pago_detalle = pago.detalle
                                    monto_intereses = 0
                                    if pago_detalle != None and pago_detalle != '':
                                        # pago_detalle = json.dumps(pago_detalle)
                                        pago_detalle = json.loads(pago_detalle)
                                        detalle_str = ""
                                        for x in range(0, len(pago_detalle)):
                                            try:
                                                detalle_str = detalle_str + " Intereses: " + unicode('{:,}'.format(
                                                    pago_detalle['item' + unicode(x)]['intereses'])).replace(",", ".")
                                                monto_intereses = monto_intereses + int(
                                                    pago_detalle['item' + unicode(x)]['intereses'])
                                            except Exception, error:
                                                try:
                                                    detalle_str = detalle_str + " Gestion Cobranza: " + unicode(
                                                        '{:,}'.format(int(pago_detalle['item' + unicode(x)][
                                                                              'gestion_cobranza']))).replace(",", ".")
                                                except Exception, error:
                                                    print error

                                if pago.nro_cuotas_a_pagar > 1:
                                    monto_cuota = pago.total_de_pago - monto_intereses
                                    for x in range(x, pago.nro_cuotas_a_pagar + 1):
                                        cuota['detalle'] = cuota['detalle'] + ' Monto Cuota: ' + unicode(
                                            '{:,}'.format(monto_cuota / pago.nro_cuotas_a_pagar)).replace(",", ".")

                                    cuota['detalle'] = cuota['detalle'] + detalle_str
                                else:
                                    monto_cuota = pago.total_de_pago - monto_intereses
                                    cuota['detalle'] = 'Monto Cuota: ' + unicode('{:,}'.format(monto_cuota)).replace(
                                        ",", ".") + detalle_str

                                cuota['cantidad_cuotas'] = pago.nro_cuotas_a_pagar
                                cuota['monto'] = unicode('{:,}'.format(pago.total_de_pago)).replace(",", ".")
                                ventas_pagos_list.append(cuota)
                            lista_movimientos.append(ventas_pagos_list)
                    except Exception, error:
                        print error

                    lista = lista_movimientos

                    #                     paginator = Paginator(lista_movimientos, 25)
                    #                     page = request.GET.get('page')
                    #                     try:
                    #                         lista = paginator.page(page)
                    #                     except PageNotAnInteger:
                    #                         lista = paginator.page(1)
                    #                     except EmptyPage:
                    #                         lista = paginator.page(paginator.num_pages)

                    ultimo = "&busqueda=" + busqueda + "&busqueda_label=" + busqueda_label
                    c = RequestContext(request, {
                        'lista_ventas': lista,
                        'lote_id': lote_id,
                        'busqueda': busqueda,
                        'busqueda_label': busqueda_label,
                        'ultimo': ultimo,
                    })
                    return HttpResponse(t.render(c))
            else:
                t = loader.get_template('index2.html')
                grupo = request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))
        else:
            return HttpResponseRedirect(reverse('login'))


def informe_ventas_reporte_excel(request):
    lista_movimientos = []
    lote_id = request.GET['busqueda']
    busqueda_label = request.GET['busqueda_label']
    busqueda = lote_id
    lote = Lote.objects.get(pk=lote_id)
    lista_ventas = Venta.objects.filter(lote_id=lote.id).order_by('-fecha_de_venta')
    try:
        for item_venta in lista_ventas:
            try:
                resumen_venta = {}
                resumen_venta['id'] = item_venta.id
                resumen_venta['fecha_de_venta'] = datetime.datetime.strptime(unicode(item_venta.fecha_de_venta),
                                                                             "%Y-%m-%d").strftime("%d/%m/%Y")
                resumen_venta['lote'] = item_venta.lote
                resumen_venta['cliente'] = item_venta.cliente
                resumen_venta['cantidad_de_cuotas'] = item_venta.plan_de_pago.cantidad_de_cuotas
                resumen_venta['precio_final'] = unicode('{:,}'.format(item_venta.precio_final_de_venta)).replace(",",
                                                                                                                 ".")
                resumen_venta['precio_de_cuota'] = unicode('{:,}'.format(item_venta.precio_de_cuota)).replace(",", ".")
                resumen_venta['fecha_primer_vencimiento'] = datetime.datetime.strptime(
                    unicode(item_venta.fecha_primer_vencimiento), "%Y-%m-%d").strftime("%d/%m/%Y")
                resumen_venta['entrega_inicial'] = unicode('{:,}'.format(item_venta.entrega_inicial)).replace(",", ".")
                resumen_venta['vendedor'] = item_venta.vendedor
                resumen_venta['plan_de_pago'] = item_venta.plan_de_pago
                resumen_venta['pagos_realizados'] = item_venta.pagos_realizados
                resumen_venta['recuperado'] = item_venta.recuperado

                # venta_pagos_query_set = get_pago_cuotas(item_venta,None,None)
                venta_pagos_query_set = PagoDeCuotas.objects.filter(venta_id=item_venta.id).order_by("fecha_de_pago",
                                                                                                     "id")
            except Exception, error:
                print error
            ventas_pagos_list = []
            ventas_pagos_list.insert(0,
                                     resumen_venta)  # El primer elemento de la lista de pagos es el resumen de la venta
            contador_cuotas = 0

            for pago in venta_pagos_query_set:
                cuota = {}
                cuota['fecha_de_pago'] = datetime.datetime.strptime(unicode(pago.fecha_de_pago), "%Y-%m-%d").strftime(
                    "%d/%m/%Y")
                cuota['id'] = pago.id
                detalle_str = ""
                cuota['detalle'] = ""
                cuota['dias_atraso'] = ""
                cuota['vencimiento'] = ""
                try:
                    cuota['id_transaccion'] = pago.transaccion.id
                except:
                    cuota['id_transaccion'] = None

                if pago.factura_id != None:
                    cuota['factura'] = pago.factura
                else:
                    cuota['factura'] = None
                # Si se paga mas de una cuota
                if pago.nro_cuotas_a_pagar > 1:
                    cuota['nro_cuota'] = unicode(contador_cuotas + 1) + " al " + unicode(
                        contador_cuotas + pago.nro_cuotas_a_pagar)

                    # detalle para fecha de vencimiento

                    c = 0
                    cuota['vencimiento'] = ""
                    cuota['dias_atraso'] = ""
                    for x in range(0, pago.nro_cuotas_a_pagar):
                        contador_cuotas = contador_cuotas + 1
                        cuotas_detalles = []
                        cuotas_detalles = get_cuota_information_by_lote(lote_id, contador_cuotas, True, True)
                        cuota['vencimiento'] = cuota['vencimiento'] + unicode(cuotas_detalles[0]['fecha']) + ' '

                        fecha_pago_parsed = datetime.datetime.strptime(cuota['fecha_de_pago'], "%d/%m/%Y").date()
                        proximo_vencimiento_parsed = datetime.datetime.strptime(unicode(cuotas_detalles[0]['fecha']),
                                                                                "%d/%m/%Y").date()
                        dias_atraso = obtener_dias_atraso(fecha_pago_parsed, proximo_vencimiento_parsed)
                        cuota['dias_atraso'] = cuota['dias_atraso'] + " * " + unicode(dias_atraso) + " dias "

                        c = c + 1
                        pago_detalle = pago.detalle
                        monto_intereses = 0
                        if pago_detalle != None and pago_detalle != '':
                            # pago_detalle = json.dumps(pago_detalle)
                            pago_detalle = json.loads(pago_detalle)
                            detalle_str = ""
                            for x in range(0, len(pago_detalle)):
                                try:
                                    detalle_str = detalle_str + " Intereses: " + unicode(
                                        '{:,}'.format(pago_detalle['item' + unicode(x)]['intereses'])).replace(",", ".")
                                    monto_intereses = monto_intereses + int(
                                        pago_detalle['item' + unicode(x)]['intereses'])
                                except Exception, error:
                                    try:
                                        detalle_str = detalle_str + " Gestion Cobranza: " + unicode('{:,}'.format(
                                            int(pago_detalle['item' + unicode(x)]['gestion_cobranza']))).replace(",",
                                                                                                                 ".")
                                    except Exception, error:
                                        print error


                # si se paga solo una cuota
                else:
                    contador_cuotas = contador_cuotas + pago.nro_cuotas_a_pagar
                    # detalle para fecha de vencimiento
                    cuotas_detalles = []
                    cuotas_detalles = get_cuota_information_by_lote(lote_id, contador_cuotas, True, True, item_venta)
                    cuota['vencimiento'] = unicode(cuotas_detalles[0]['fecha'])

                    fecha_pago_parsed = datetime.datetime.strptime(cuota['fecha_de_pago'], "%d/%m/%Y").date()
                    proximo_vencimiento_parsed = datetime.datetime.strptime(cuota['vencimiento'], "%d/%m/%Y").date()
                    dias_atraso = obtener_dias_atraso(fecha_pago_parsed, proximo_vencimiento_parsed)
                    cuota['dias_atraso'] = cuota['dias_atraso'] + " * " + unicode(dias_atraso) + " dias "

                    cuota['nro_cuota'] = unicode(contador_cuotas)
                    pago_detalle = pago.detalle
                    monto_intereses = 0
                    if pago_detalle != None and pago_detalle != '':
                        # pago_detalle = json.dumps(pago_detalle)
                        pago_detalle = json.loads(pago_detalle)
                        detalle_str = ""
                        for x in range(0, len(pago_detalle)):
                            try:
                                detalle_str = detalle_str + " Intereses: " + unicode(
                                    '{:,}'.format(pago_detalle['item' + unicode(x)]['intereses'])).replace(",", ".")
                                monto_intereses = monto_intereses + int(pago_detalle['item' + unicode(x)]['intereses'])
                            except Exception, error:
                                try:
                                    detalle_str = detalle_str + " Gestion Cobranza: " + unicode('{:,}'.format(
                                        int(pago_detalle['item' + unicode(x)]['gestion_cobranza']))).replace(",", ".")
                                except Exception, error:
                                    print error

                if pago.nro_cuotas_a_pagar > 1:
                    monto_cuota = pago.total_de_pago - monto_intereses
                    for x in range(x, pago.nro_cuotas_a_pagar + 1):
                        cuota['detalle'] = cuota['detalle'] + ' Monto Cuota: ' + unicode(
                            '{:,}'.format(monto_cuota / pago.nro_cuotas_a_pagar)).replace(",", ".")

                    cuota['detalle'] = cuota['detalle'] + detalle_str
                else:
                    monto_cuota = pago.total_de_pago - monto_intereses
                    cuota['detalle'] = 'Monto Cuota: ' + unicode('{:,}'.format(monto_cuota)).replace(",",
                                                                                                     ".") + detalle_str

                cuota['cantidad_cuotas'] = pago.nro_cuotas_a_pagar
                cuota['monto'] = unicode('{:,}'.format(pago.total_de_pago)).replace(",", ".")
                ventas_pagos_list.append(cuota)
            lista_movimientos.append(ventas_pagos_list)
    except Exception, error:
        print error

    lista = lista_movimientos

    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    sheet.paper_size_code = 1
    style = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                        'font: name Calibri, bold True, height 200; align: horiz center')
    style2 = xlwt.easyxf('font: name Calibri, height 200;')

    style3 = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz right')

    style4 = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz center')

    usuario = unicode(request.user)

    sheet.header_str = (
        u"&LFecha: &D Hora: &T \nUsuario: " + usuario + " "
                                                        u"&CPROPAR S.R.L.\n INFORME VENTA DE LOTES "
                                                        u"&RPage &P of &N"
    )

    c = 0

    for venta in lista:
        for i, pago in enumerate(venta):
            if i == 0:
                # cabeceras
                sheet.write_merge(c, c, 0, 6, "Venta lote: " + unicode(pago['lote']) + " Vendedor: " + unicode(
                    pago['vendedor']) + " a Cliente: " + unicode(pago['cliente']) + " el: " + unicode(
                    pago['fecha_de_venta']), style)
                c = c + 1
                sheet.write(c, 0, "Fecha 1er Vto.", style)
                sheet.write(c, 1, "Plan de Pago", style)
                sheet.write(c, 2, "Entrega Inicial", style)
                sheet.write(c, 3, "Precio Cuota", style)
                sheet.write(c, 4, "Precio Venta", style)
                sheet.write(c, 5, "Cuotas Pagadas", style)
                sheet.write(c, 6, "Recuperado", style)

                c = c + 1

                sheet.write(c, 0, pago['fecha_primer_vencimiento'], style4)
                sheet.write(c, 1, unicode(pago['plan_de_pago']), style2)
                sheet.write(c, 2, unicode(pago['entrega_inicial']), style3)
                sheet.write(c, 3, unicode(pago['precio_de_cuota']), style3)
                sheet.write(c, 4, unicode(pago['precio_final']), style3)
                sheet.write(c, 5, unicode(pago['pagos_realizados']), style4)
                if pago['recuperado']:
                    sheet.write(c, 6, "SI", style4)
                else:
                    sheet.write(c, 6, "NO", style4)

                if pago['plan_de_pago'].tipo_de_plan == 'credito':
                    c = c + 1
                    sheet.write_merge(c, c, 0, 6,
                                      "Pagos de la Venta lote: " + unicode(pago['lote']) + " Vendedor: " + unicode(
                                          pago['vendedor']) + " a Cliente: " + unicode(
                                          pago['cliente']) + " el: " + unicode(pago['fecha_de_venta']), style)
                    c = c + 1
                    sheet.write(c, 0, "Fecha", style)
                    sheet.write(c, 1, "Cant. Cuotas", style)
                    sheet.write(c, 2, "Nro. Cuotas", style)
                    sheet.write(c, 3, "Monto", style)
                    sheet.write(c, 4, "Factura", style)
                    sheet.write(c, 5, "Transaccion", style)

                c = c + 1

            else:

                sheet.write(c, 0, pago['fecha_de_pago'], style4)
                sheet.write(c, 1, unicode(pago['cantidad_cuotas']), style4)
                sheet.write(c, 2, unicode(pago['nro_cuota']), style4)
                sheet.write(c, 3, unicode(pago['monto']), style3)
                if pago['factura'] is None:
                    sheet.write(c, 4, "Sin Factura", style4)
                else:
                    sheet.write(c, 4, unicode(pago['factura'].numero), style4)
                if pago['id_transaccion'] is None:
                    sheet.write(c, 5, "Interna", style4)
                else:
                    sheet.write(c, 5, unicode(pago['id_transaccion']), style4)

                c += 1

                col_nombre = sheet.col(1)
                col_nombre.width = 256 * 25

    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo
    response['Content-Disposition'] = 'attachment; filename=' + 'informe_movimientos.xls'
    wb.save(response)
    return response


def informe_pagos_practipago(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
                if not filtros_establecidos(request.GET, 'informe_pagos_practipago'):
                    t = loader.get_template('informes/informe_pagos_practipago.html')
                    c = RequestContext(request, {
                        'object_list': [],
                    })
                    return HttpResponse(t.render(c))
                else:  # Parametros seteados
                    t = loader.get_template('informes/informe_pagos_practipago.html')
                    sucursal_id = request.GET['sucursal']
                    sucursal_label = request.GET['sucursal_label']
                    fecha_ini = request.GET['fecha_ini']
                    fecha_fin = request.GET['fecha_fin']

                    fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y")
                    fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y")

                    lista_pagos = []
                    lista_transacciones = Transaccion.objects.filter(
                        estado="Pagado", updated__range=(fecha_ini_parsed, fecha_fin_parsed),
                    ).order_by("-updated")

                    contador_cuotas = 0
                    for transaccion in lista_transacciones:
                        try:
                            if sucursal_id is None or sucursal_id == '':
                                detalle = ""
                                pago = PagoDeCuotas.objects.get(transaccion_id=transaccion.id)

                                # Si se paga mas de una cuota
                                if pago.nro_cuotas_a_pagar > 1:
                                    cuotas_detalles = get_cuota_information_by_lote(
                                        pago.lote_id, pago.nro_cuotas_a_pagar, False, True
                                    )

                                    c = 0
                                    vencimiento = ""
                                    dias_de_atraso = ""
                                    for x in range(0, pago.nro_cuotas_a_pagar):
                                        contador_cuotas += 1

                                        vencimiento = vencimiento + unicode(cuotas_detalles[x]['fecha']) + ' '

                                        fecha_pago_parsed = datetime.datetime.strptime(
                                            pago.fecha_de_pago.strftime("%d/%m/%Y"), "%d/%m/%Y"
                                        ).date()

                                        proximo_vencimiento_parsed = datetime.datetime.strptime(
                                            unicode(cuotas_detalles[x]['fecha']), "%d/%m/%Y"
                                        ).date()

                                        dias_atraso = obtener_dias_atraso(
                                            fecha_pago_parsed, proximo_vencimiento_parsed
                                        )

                                        dias_de_atraso += " * " + unicode(dias_atraso) + "  "

                                        c += 1
                                        pago_detalle = pago.detalle
                                        monto_intereses = 0

                                        if pago_detalle is not None and pago_detalle != '':
                                            pago_detalle = json.loads(pago_detalle)
                                            cuota_ini = ""
                                            cuota_fin = ""
                                            detalle_str = ""
                                            try:
                                                cuota_ini = pago_detalle['item' + unicode(0)]['nro_cuota']
                                                cuota_fin = pago_detalle['item' + unicode(x)]['nro_cuota']

                                                monto_intereses += int(
                                                    pago_detalle['item' + unicode(x)]['intereses']
                                                )

                                                monto_cuota = cuotas_detalles[x]['monto_cuota']
                                                detalle_str = ' Cuota: ' + unicode(
                                                    '{:,}'.format(monto_cuota)).replace(
                                                    ",", ".") + " Intereses: " + unicode('{:,}'.format(
                                                    pago_detalle['item' + unicode(x)]['intereses']
                                                )).replace(",", ".")

                                            except Exception, error:
                                                print error
                                                try:
                                                    detalle_str = detalle_str + " Gestion Cobranza: " + unicode(
                                                        '{:,}'.format(int(pago_detalle['item' + unicode(x)][
                                                                'gestion_cobranza']))).replace(",",".")
                                                except Exception, error:
                                                    print error
                                            detalle += detalle_str
                                    nro_cuota = unicode(cuota_ini) + " al " + unicode(cuota_fin)



                                # si se paga solo una cuota
                                else:
                                    detalle = ""
                                    dias_de_atraso = ""
                                    # detalle para fecha de vencimiento
                                    cuotas_detalles = get_cuota_information_by_lote(pago.lote_id, 1, True,
                                                                                    True, pago.venta)
                                    vencimiento = unicode(cuotas_detalles[0]['fecha'])
                                    # fecha_pago_parsed = datetime.datetime.strptime(
                                    # cuota['fecha_de_pago'], "%d/%m/%Y").date()
                                    fecha_pago_parsed = datetime.datetime.strptime(
                                        pago.fecha_de_pago.strftime("%d/%m/%Y"), "%d/%m/%Y").date()
                                    proximo_vencimiento_parsed = datetime.datetime.strptime(vencimiento,
                                                                                            "%d/%m/%Y").date()
                                    dias_atraso = obtener_dias_atraso(fecha_pago_parsed, proximo_vencimiento_parsed)
                                    dias_de_atraso += " * " + unicode(
                                        dias_atraso) + " "

                                    pago_detalle = pago.detalle
                                    monto_intereses = 0
                                    if pago_detalle is not None and pago_detalle != '' or pago_detalle != '{}':
                                        # pago_detalle = json.dumps(pago_detalle)
                                        pago_detalle = json.loads(pago_detalle)
                                        detalle_str = ""
                                        cuota_ini = ""
                                        try:
                                            cuota_ini = pago_detalle['item' + unicode(0)]['nro_cuota']
                                            detalle_str = " Intereses: " + unicode('{:,}'.format(
                                                pago_detalle['item' + unicode(x)]['intereses']
                                            )).replace(",", ".")
                                            monto_intereses += int(
                                                pago_detalle['item' + unicode(x)]['intereses']
                                            )

                                            monto_cuota = cuotas_detalles[x]['monto_cuota']
                                            detalle = 'Cuota: ' + unicode(
                                                '{:,}'.format(monto_cuota)).replace(
                                                ",", ".") + detalle_str
                                        except Exception, error:
                                            print error
                                            try:
                                                detalle = detalle_str + " Gestion Cobranza: " + unicode(
                                                    '{:,}'.format(int(pago_detalle['item' + unicode(x)][
                                                                          'gestion_cobranza']))).replace(",", ".")

                                            except Exception, error:
                                                print error
                                        nro_cuota = unicode(cuota_ini)
                                    else:
                                        nro_cuota = unicode(obtener_cantidad_cuotas_pagadas(pago))

                                monto = unicode('{:,}'.format(pago.total_de_pago)).replace(",", ".")

                                pago_item = {
                                    'id': pago.id,
                                    'fecha_de_pago': datetime.datetime.strptime(
                                        unicode(pago.fecha_de_pago),"%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"),
                                    'cantidad_cuotas': pago.nro_cuotas_a_pagar,
                                    'vencimiento': vencimiento,
                                    'dias_atraso': dias_de_atraso,
                                    'nro_cuota': nro_cuota,
                                    'detalle': detalle,
                                    'monto': monto,
                                    'transaccion_id': transaccion.id,
                                    'lote': pago.lote
                                }
                                try:
                                    pago_item['factura'] = pago.factura
                                except Exception, error:
                                    print error
                                    pago_item['factura'] = None
                                lista_pagos.append(pago_item)

                            else: # ----------------------- por sucursal ----------------------------------------------
                                sucursal = Sucursal.objects.get(pk=sucursal_id)
                                pago = PagoDeCuotas.objects.get(transaccion_id=transaccion.id)
                                if pago.lote.manzana.fraccion.sucursal_id == sucursal.id:
                                    # Si se paga mas de una cuota
                                    if pago.nro_cuotas_a_pagar > 1:
                                        nro_cuota = unicode(contador_cuotas + 1) + " al " + unicode(
                                            contador_cuotas + pago.nro_cuotas_a_pagar)
                                        c = 0
                                        vencimiento = ""
                                        dias_de_atraso = ""
                                        for x in range(0, pago.nro_cuotas_a_pagar):
                                            contador_cuotas += 1
                                            cuotas_detalles = get_cuota_information_by_lote(pago.lote_id,
                                                                                            contador_cuotas, True, True)
                                            vencimiento = vencimiento + unicode(
                                                cuotas_detalles[0]['fecha']) + ' '
                                            fecha_pago_parsed = datetime.datetime.strptime(
                                                pago.fecha_de_pago.strftime("%d/%m/%Y"), "%d/%m/%Y").date()
                                            proximo_vencimiento_parsed = datetime.datetime.strptime(
                                                unicode(cuotas_detalles[0]['fecha']), "%d/%m/%Y").date()
                                            dias_atraso = obtener_dias_atraso(fecha_pago_parsed,
                                                                              proximo_vencimiento_parsed)
                                            dias_de_atraso += " * " + unicode(
                                                dias_atraso) + " dias "

                                            c += 1
                                            pago_detalle = pago.detalle
                                            monto_intereses = 0
                                            if pago_detalle is not None and pago_detalle != '':
                                                pago_detalle = json.loads(pago_detalle)
                                                detalle_str = ""
                                                for x in range(0, len(pago_detalle)):
                                                    try:
                                                        detalle_str = detalle_str + " Intereses: " + unicode(
                                                            '{:,}'.format(pago_detalle['item' + unicode(x)][
                                                                              'intereses'])).replace(",", ".")
                                                        monto_intereses += int(
                                                            pago_detalle['item' + unicode(x)]['intereses'])
                                                    except Exception, error:
                                                        try:
                                                            detalle_str = detalle_str + " Gestion Cobranza: " + unicode(
                                                                '{:,}'.format(int(pago_detalle['item' + unicode(x)][
                                                                                      'gestion_cobranza']))).replace(
                                                                ",", ".")
                                                        except Exception, error:
                                                            print error
                                    # si se paga solo una cuota
                                    else:
                                        contador_cuotas += pago.nro_cuotas_a_pagar
                                        # detalle para fecha de vencimiento
                                        cuotas_detalles = get_cuota_information_by_lote(pago.lote_id, contador_cuotas,
                                                                                        True, True, pago.venta)
                                        vencimiento = unicode(cuotas_detalles[0]['fecha'])
                                        fecha_pago_parsed = datetime.datetime.strptime(
                                            pago.fecha_de_pago.strftime("%d/%m/%Y"), "%d/%m/%Y").date()
                                        proximo_vencimiento_parsed = datetime.datetime.strptime(vencimiento,
                                                                                                "%d/%m/%Y").date()
                                        dias_atraso = obtener_dias_atraso(fecha_pago_parsed, proximo_vencimiento_parsed)
                                        dias_de_atraso = dias_atraso + " * " + unicode(
                                            dias_atraso) + " dias "
                                        nro_cuota = unicode(contador_cuotas)
                                        pago_detalle = pago.detalle
                                        monto_intereses = 0
                                        if pago_detalle is not None and pago_detalle != '':
                                            pago_detalle = json.loads(pago_detalle)
                                            detalle_str = ""
                                            for x in range(0, len(pago_detalle)):
                                                try:
                                                    detalle_str = detalle_str + " Intereses: " + unicode('{:,}'.format(
                                                        pago_detalle['item' + unicode(x)]['intereses'])).replace(",",
                                                                                                                 ".")
                                                    monto_intereses += int(
                                                        pago_detalle['item' + unicode(x)]['intereses'])
                                                except Exception, error:
                                                    try:
                                                        detalle_str = detalle_str + " Gestion Cobranza: " + unicode(
                                                            '{:,}'.format(int(pago_detalle['item' + unicode(x)][
                                                                                  'gestion_cobranza']))).replace(",",
                                                                                                                 ".")
                                                    except Exception, error:
                                                        print error

                                    monto = unicode('{:,}'.format(pago.total_de_pago)).replace(",", ".")

                                    pago_item = {
                                        'id': pago.id,
                                        'fecha_de_pago': datetime.datetime.strptime(
                                        unicode(pago.fecha_de_pago),"%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"),
                                        'cantidad_cuotas': pago.nro_cuotas_a_pagar,
                                        'vencimiento': vencimiento,
                                        'dias_atraso': dias_de_atraso,
                                        'nro_cuota': nro_cuota,
                                        'detalle': detalle,
                                        'monto': monto,
                                        'transaccion_id': transaccion.id,
                                        'lote': pago.lote
                                    }
                                    try:
                                        pago_item['factura'] = pago.factura
                                    except Exception, error:
                                        print error
                                        pago_item['factura'] = None
                                    lista_pagos.append(pago_item)
                        except Exception, error:
                            print error

                    ultimo = "&sucursal=" + sucursal_id + "&sucursal_label=" \
                             + sucursal_label + "&fecha_ini=" + fecha_ini + "&fecha_fin=" + fecha_fin
                    c = RequestContext(request, {
                        'lista_pagos': lista_pagos,
                        # 'lote_id' : lote_id,
                        'sucursal': sucursal_id,
                        'sucursal_label': sucursal_label,
                        'ultimo': ultimo,
                        'fecha_ini': fecha_ini,
                        'fecha_fin': fecha_fin,
                    })
                    return HttpResponse(t.render(c))

            else:
                t = loader.get_template('index2.html')
                grupo = request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))
        else:
            return HttpResponseRedirect(reverse('login'))


def informe_pagos_practipago_reporte_excel(request):
    lista_movimientos = []
    sucursal_id = request.GET['sucursal']
    sucursal_label = request.GET['sucursal_label']
    fecha_ini = request.GET['fecha_ini']
    fecha_fin = request.GET['fecha_fin']
    # lista_ventas = Venta.objects.filter(lote_id=lote.id).order_by('-fecha_de_venta')
    if sucursal_id != '':
        lista_ventas = Venta.objects.raw(
            '''SELECT * FROM principal_venta WHERE lote_id IN (SELECT principal_lote.id FROM principal_lote WHERE manzana_id IN (SELECT principal_manzana.id FROM principal_manzana WHERE fraccion_id IN (SELECT principal_fraccion.id FROM principal_fraccion WHERE sucursal_id = %s))) ORDER BY fecha_de_venta;''',
            [sucursal_id])
    else:
        lista_ventas = Venta.objects.raw('''SELECT * FROM principal_venta ORDER BY fecha_de_venta;''')
    try:
        for item_venta in lista_ventas:
            try:
                resumen_venta = {}
                resumen_venta['id'] = item_venta.id
                resumen_venta['fecha_de_venta'] = datetime.datetime.strptime(unicode(item_venta.fecha_de_venta),
                                                                             "%Y-%m-%d").strftime("%d/%m/%Y")
                resumen_venta['lote'] = item_venta.lote
                resumen_venta['cliente'] = item_venta.cliente
                resumen_venta['cantidad_de_cuotas'] = item_venta.plan_de_pago.cantidad_de_cuotas
                resumen_venta['precio_final'] = unicode('{:,}'.format(item_venta.precio_final_de_venta)).replace(",",
                                                                                                                 ".")
                resumen_venta['precio_de_cuota'] = unicode('{:,}'.format(item_venta.precio_de_cuota)).replace(",", ".")
                resumen_venta['fecha_primer_vencimiento'] = datetime.datetime.strptime(
                    unicode(item_venta.fecha_primer_vencimiento), "%Y-%m-%d").strftime("%d/%m/%Y")
                resumen_venta['entrega_inicial'] = unicode('{:,}'.format(item_venta.entrega_inicial)).replace(",", ".")
                resumen_venta['vendedor'] = item_venta.vendedor
                resumen_venta['plan_de_pago'] = item_venta.plan_de_pago
                resumen_venta['pagos_realizados'] = item_venta.pagos_realizados
                resumen_venta['recuperado'] = item_venta.recuperado

                # venta_pagos_query_set = get_pago_cuotas(item_venta,None,None)
                if fecha_ini != '' and fecha_fin != '':
                    fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").date()
                    fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").date()
                    venta_pagos_query_set = PagoDeCuotas.objects.filter(venta_id=item_venta.id).exclude(
                        transaccion_id__isnull=True).filter(
                        fecha_de_pago__range=(fecha_ini_parsed, fecha_fin_parsed)).order_by("fecha_de_pago", "id")
                else:
                    venta_pagos_query_set = PagoDeCuotas.objects.filter(venta_id=item_venta.id).exclude(
                        transaccion_id__isnull=True).order_by("fecha_de_pago", "id")
            except Exception, error:
                print error
            # cuando agrupamos si usamos esta lista
            # ventas_pagos_list = []
            # ventas_pagos_list.insert(0,resumen_venta) #El primer elemento de la lista de pagos es el resumen de la venta
            contador_cuotas = 0

            venta_tiene_pagos = False
            for pago in venta_pagos_query_set:
                venta_tiene_pagos = True
                cuota = {}
                # cuota['fecha_de_pago'] = datetime.datetime.strptime(unicode(pago.fecha_de_pago), "%Y-%m-%d").strftime("%d/%m/%Y")
                cuota['fecha_de_pago'] = datetime.datetime.strptime(unicode(pago.fecha_de_pago), "%Y-%m-%d").date()
                cuota['id'] = pago.id
                detalle_str = ""
                cuota['detalle'] = ""
                cuota['dias_atraso'] = ""
                cuota['vencimiento'] = ""
                try:
                    cuota['id_transaccion'] = pago.transaccion.id
                except:
                    cuota['id_transaccion'] = None

                if pago.factura_id != None:
                    cuota['factura'] = pago.factura
                else:
                    cuota['factura'] = None
                # Si se paga mas de una cuota
                if pago.nro_cuotas_a_pagar > 1:
                    cuota['nro_cuota'] = unicode(contador_cuotas + 1) + " al " + unicode(
                        contador_cuotas + pago.nro_cuotas_a_pagar)

                    # detalle para fecha de vencimiento

                    c = 0
                    cuota['vencimiento'] = ""
                    cuota['dias_atraso'] = ""
                    for x in range(0, pago.nro_cuotas_a_pagar):
                        contador_cuotas = contador_cuotas + 1
                        cuotas_detalles = []
                        cuotas_detalles = get_cuota_information_by_lote(pago.lote_id, contador_cuotas, True, True)
                        cuota['vencimiento'] = cuota['vencimiento'] + unicode(cuotas_detalles[0]['fecha']) + ' '

                        # fecha_pago_parsed = datetime.datetime.strptime(cuota['fecha_de_pago'], "%d/%m/%Y").date()
                        fecha_pago_parsed = datetime.datetime.strptime(cuota['fecha_de_pago'].strftime("%d/%m/%Y"),
                                                                       "%d/%m/%Y").date()
                        proximo_vencimiento_parsed = datetime.datetime.strptime(unicode(cuotas_detalles[0]['fecha']),
                                                                                "%d/%m/%Y").date()
                        dias_atraso = obtener_dias_atraso(fecha_pago_parsed, proximo_vencimiento_parsed)
                        cuota['dias_atraso'] = cuota['dias_atraso'] + " * " + unicode(dias_atraso) + " dias "

                        c = c + 1
                        pago_detalle = pago.detalle
                        monto_intereses = 0
                        if pago_detalle != None and pago_detalle != '':
                            # pago_detalle = json.dumps(pago_detalle)
                            pago_detalle = json.loads(pago_detalle)
                            detalle_str = ""
                            for x in range(0, len(pago_detalle)):
                                try:
                                    detalle_str = detalle_str + " Intereses: " + unicode(
                                        '{:,}'.format(pago_detalle['item' + unicode(x)]['intereses'])).replace(",", ".")
                                    monto_intereses = monto_intereses + int(
                                        pago_detalle['item' + unicode(x)]['intereses'])
                                except Exception, error:
                                    try:
                                        detalle_str = detalle_str + " Gestion Cobranza: " + unicode('{:,}'.format(
                                            int(pago_detalle['item' + unicode(x)]['gestion_cobranza']))).replace(",",
                                                                                                                 ".")
                                    except Exception, error:
                                        print error

                # si se paga solo una cuota
                else:
                    contador_cuotas = contador_cuotas + pago.nro_cuotas_a_pagar
                    # detalle para fecha de vencimiento
                    cuotas_detalles = []
                    cuotas_detalles = get_cuota_information_by_lote(pago.lote_id, contador_cuotas, True, True,
                                                                    item_venta)
                    cuota['vencimiento'] = unicode(cuotas_detalles[0]['fecha'])
                    # fecha_pago_parsed = datetime.datetime.strptime(cuota['fecha_de_pago'], "%d/%m/%Y").date()
                    fecha_pago_parsed = datetime.datetime.strptime(cuota['fecha_de_pago'].strftime("%d/%m/%Y"),
                                                                   "%d/%m/%Y").date()
                    proximo_vencimiento_parsed = datetime.datetime.strptime(cuota['vencimiento'], "%d/%m/%Y").date()
                    dias_atraso = obtener_dias_atraso(fecha_pago_parsed, proximo_vencimiento_parsed)
                    cuota['dias_atraso'] = cuota['dias_atraso'] + " * " + unicode(dias_atraso) + " dias "

                    cuota['nro_cuota'] = unicode(contador_cuotas)
                    pago_detalle = pago.detalle
                    monto_intereses = 0
                    if pago_detalle != None and pago_detalle != '':
                        # pago_detalle = json.dumps(pago_detalle)
                        pago_detalle = json.loads(pago_detalle)
                        detalle_str = ""
                        for x in range(0, len(pago_detalle)):
                            try:
                                detalle_str = detalle_str + " Intereses: " + unicode(
                                    '{:,}'.format(pago_detalle['item' + unicode(x)]['intereses'])).replace(",", ".")
                                monto_intereses = monto_intereses + int(pago_detalle['item' + unicode(x)]['intereses'])
                            except Exception, error:
                                try:
                                    detalle_str = detalle_str + " Gestion Cobranza: " + unicode('{:,}'.format(
                                        int(pago_detalle['item' + unicode(x)]['gestion_cobranza']))).replace(",", ".")
                                except Exception, error:
                                    print error

                if pago.nro_cuotas_a_pagar > 1:
                    monto_cuota = pago.total_de_pago - monto_intereses
                    for x in range(x, pago.nro_cuotas_a_pagar + 1):
                        cuota['detalle'] = cuota['detalle'] + ' Monto Cuota: ' + unicode(
                            '{:,}'.format(monto_cuota / pago.nro_cuotas_a_pagar)).replace(",", ".")

                    cuota['detalle'] = cuota['detalle'] + detalle_str
                else:
                    monto_cuota = pago.total_de_pago - monto_intereses
                    cuota['detalle'] = 'Monto Cuota: ' + unicode('{:,}'.format(monto_cuota)).replace(",",
                                                                                                     ".") + detalle_str

                cuota['cantidad_cuotas'] = pago.nro_cuotas_a_pagar
                cuota['monto'] = unicode('{:,}'.format(pago.total_de_pago)).replace(",", ".")
                # ventas_pagos_list.append(cuota)
                lista_movimientos.append(cuota)
                # si agrupamos si vamos a usar estas lineas
                # if venta_tiene_pagos:
                #     lista_movimientos.append(ventas_pagos_list)
    except Exception, error:
        print error

    # ordenamos la lista por la fecha de pago
    # lista_movimientos = sorted(lista_movimientos, key=lambda k: k['fecha_de_pago'])
    lista_movimientos.sort(key=lambda item: item['fecha_de_pago'])
    lista = lista_movimientos

    lista = lista_movimientos

    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('test', cell_overwrite_ok=True)
    sheet.paper_size_code = 1
    style = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                        'font: name Calibri, bold True, height 200; align: horiz center')
    style2 = xlwt.easyxf('font: name Calibri, height 200;')

    style3 = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz right')

    style4 = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz center')

    usuario = unicode(request.user)

    sheet.header_str = (
        u"&LFecha: &D Hora: &T \nUsuario: " + usuario + " "
                                                        u"&CPROPAR S.R.L.\n INFORME VENTA DE LOTES "
                                                        u"&RPage &P of &N"
    )
    c = 0

    sheet.write(c, 0, "Fecha de Pago", style)
    sheet.write(c, 1, "Cant. Cuotas", style)
    sheet.write(c, 2, "Nro. Cuotas", style)
    sheet.write(c, 3, "Monto", style)
    sheet.write(c, 4, "Factura", style)
    sheet.write(c, 5, "Transaccion", style)
    c = c + 1

    for pago in lista:
        # for i, pago in enumerate(venta):
        #     if i == 0:
        # cabeceras
        #         sheet.write_merge(c,c,0,6, "Venta lote: "+unicode(pago['lote'])+" Vendedor: "+unicode(pago['vendedor'])+" a Cliente: "+unicode(pago['cliente'])+ " el: "+unicode(pago['fecha_de_venta']), style)
        #         c=c+1
        #         sheet.write(c, 0, "Fecha 1er Vto.", style)
        #         sheet.write(c, 1, "Plan de Pago", style)
        #         sheet.write(c, 2, "Entrega Inicial", style)
        #         sheet.write(c, 3, "Precio Cuota", style)
        #         sheet.write(c, 4, "Precio Venta", style)
        #         sheet.write(c, 5, "Cuotas Pagadas", style)
        #         sheet.write(c, 6, "Recuperado", style)
        #
        #         c=c+1
        #
        #         sheet.write(c, 0, pago['fecha_primer_vencimiento'], style4)
        #         sheet.write(c, 1, unicode(pago['plan_de_pago']), style2)
        #         sheet.write(c, 2, unicode(pago['entrega_inicial']), style3)
        #         sheet.write(c, 3, unicode(pago['precio_de_cuota']), style3)
        #         sheet.write(c, 4, unicode(pago['precio_final']), style3)
        #         sheet.write(c, 5, unicode(pago['pagos_realizados']), style4)
        #         if pago['recuperado']:
        #             sheet.write(c, 6, "SI", style4)
        #         else:
        #             sheet.write(c, 6, "NO", style4)
        #
        #         if pago['plan_de_pago'].tipo_de_plan == 'credito':
        #             c=c+1
        #             sheet.write_merge(c,c,0,6, "Pagos de la Venta lote: "+unicode(pago['lote'])+" Vendedor: "+unicode(pago['vendedor'])+" a Cliente: "+unicode(pago['cliente'])+ " el: "+unicode(pago['fecha_de_venta']), style)
        #             c=c+1
        #             sheet.write(c, 0, "Fecha", style)
        #             sheet.write(c, 1, "Cant. Cuotas", style)
        #             sheet.write(c, 2, "Nro. Cuotas", style)
        #             sheet.write(c, 3, "Monto", style)
        #             sheet.write(c, 4, "Factura", style)
        #             sheet.write(c, 5, "Transaccion", style)
        #
        #         c=c+1
        #
        # else:

        # sheet.write(c, 0, pago['fecha_de_pago'], style4)
        sheet.write(c, 0, unicode(pago['fecha_de_pago'].strftime("%d/%m/%Y")), style4)
        sheet.write(c, 1, unicode(pago['cantidad_cuotas']), style4)
        sheet.write(c, 2, unicode(pago['nro_cuota']), style4)
        sheet.write(c, 3, unicode(pago['monto']), style3)
        if pago['factura'] == None:
            sheet.write(c, 4, "Sin Factura", style4)
        else:
            sheet.write(c, 4, unicode(pago['factura'].numero), style4)
        if pago['id_transaccion'] == None:
            sheet.write(c, 5, "Interna", style4)
        else:
            sheet.write(c, 5, unicode(pago['id_transaccion']), style4)

        c = c + 1

        col_nombre = sheet.col(1)
        col_nombre.width = 256 * 25

    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Crear un nombre intuitivo
    response['Content-Disposition'] = 'attachment; filename=' + 'informe_movimientos.xls'
    wb.save(response)
    return response


def calculo_montos_liquidacion_propietarios(pago, venta, lista_cuotas_inm):
    try:
        # cuotas_para_propietario=((venta.plan_de_pago.cantidad_cuotas_inmobiliaria)*(venta.plan_de_pago.intervalos_cuotas_inmobiliaria))-venta.plan_de_pago.inicio_cuotas_inmobiliaria
        # ultima_cuota_inmb = ((venta.plan_de_pago.cantidad_cuotas_inmobiliaria - 1) * venta.plan_de_pago.intervalos_cuotas_inmobiliaria) + venta.plan_de_pago.inicio_cuotas_inmobiliaria
        if (int(pago['nro_cuota']) in lista_cuotas_inm):
            monto_inmobiliaria = int(
                int(pago['monto']) * (float(venta.plan_de_pago.porcentaje_cuotas_inmobiliaria) / float(100)))
            monto_propietario = int(pago['monto']) - monto_inmobiliaria
            '''
            if(int(pago['nro_cuota']) % 2 != 0):
                monto_inmobiliaria = pago['monto']
                monto_propietario = 0
            else:
                monto_inmobiliaria = int(int(pago['monto']) * (float(venta.plan_de_pago.porcentaje_cuotas_administracion) / float(100)))
                monto_propietario = int(pago['monto']) - monto_inmobiliaria
            '''
        else:
            monto_inmobiliaria = int(
                int(pago['monto']) * (float(venta.plan_de_pago.porcentaje_cuotas_administracion) / float(100)))
            monto_propietario = int(pago['monto']) - monto_inmobiliaria

        monto = {}
        monto['monto_propietario'] = monto_propietario
        monto['monto_inmobiliaria'] = monto_inmobiliaria
        return monto
    except Exception, error:
        print error


def calculo_montos_liquidacion_vendedores(pago, venta, lista_cuotas_ven):
    try:
        # cuotas_para_propietario=((venta.plan_de_pago.cantidad_cuotas_inmobiliaria)*(venta.plan_de_pago.intervalos_cuotas_inmobiliaria))-venta.plan_de_pago.inicio_cuotas_inmobiliaria
        # ultima_cuota_inmb = ((venta.plan_de_pago.cantidad_cuotas_inmobiliaria - 1) * venta.plan_de_pago.intervalos_cuotas_inmobiliaria) + venta.plan_de_pago.inicio_cuotas_inmobiliaria
        if (int(pago['nro_cuota']) in lista_cuotas_ven):
            monto_vendedor = int(
                int(pago['monto']) * (float(venta.plan_de_pago_vendedor.porcentaje_de_cuotas) / float(100)))
            '''
            if(int(pago['nro_cuota']) % 2 != 0):
                monto_inmobiliaria = pago['monto']
                monto_propietario = 0
            else:
                monto_inmobiliaria = int(int(pago['monto']) * (float(venta.plan_de_pago.porcentaje_cuotas_administracion) / float(100)))
                monto_propietario = int(pago['monto']) - monto_inmobiliaria
            '''
        else:
            # monto_vendedor = int(int(pago['monto']) * (float(venta.plan_de_pago_vendedor.porcentaje_de_cuotas) / float(100)))
            monto_vendedor = 0

        monto = {}
        monto['monto_vendedor'] = monto_vendedor
        return monto
    except Exception, error:
        print error


def calculo_montos_liquidacion_propietarios_contado(venta):
    try:
        monto_inmobiliaria = int(
            int(venta.precio_final_de_venta) * (float(venta.plan_de_pago.porcentaje_inicial_inmobiliaria) / float(100)))
        monto_propietario = int(venta.precio_final_de_venta) - monto_inmobiliaria

        monto = {}
        monto['monto_propietario'] = monto_propietario
        monto['monto_inmobiliaria'] = monto_inmobiliaria
        return monto
    except Exception, error:
        print error


def calculo_montos_liquidacion_propietarios_entrega_inicial(venta):
    try:
        monto_inmobiliaria = int(
            int(venta.entrega_inicial) * (float(venta.plan_de_pago.porcentaje_inicial_inmobiliaria) / float(100)))
        monto_propietario = int(venta.entrega_inicial) - monto_inmobiliaria

        monto = {}
        monto['monto_propietario'] = monto_propietario
        monto['monto_inmobiliaria'] = monto_inmobiliaria
        return monto
    except Exception, error:
        print error


def calculo_montos_liquidacion_vendedores_contado(venta):
    try:
        monto_vendedor = int(
            int(venta.precio_final_de_venta) * (float(venta.plan_de_pago_vendedor.porcentaje_de_cuotas) / float(100)))
        monto = {}
        monto['monto_vendedor'] = monto_vendedor
        return monto
    except Exception, error:
        print error


def calculo_montos_liquidacion_vendedores_entrega_inicial(venta):
    try:
        monto_vendedor = int(
            int(venta.entrega_inicial) * (float(venta.plan_de_pago_vendedor.porcentaje_cuota_inicial) / float(100)))

        monto = {}
        monto['monto_vendedor'] = monto_vendedor
        return monto
    except Exception, error:
        print error


def calculo_montos_liquidacion_propietarios_2(pago, venta, lista_cuotas_inm):
    try:
        # cuotas_para_propietario=((venta.plan_de_pago.cantidad_cuotas_inmobiliaria)*(venta.plan_de_pago.intervalos_cuotas_inmobiliaria))-venta.plan_de_pago.inicio_cuotas_inmobiliaria
        # ultima_cuota_inmb = ((venta.plan_de_pago.cantidad_cuotas_inmobiliaria - 1) * venta.plan_de_pago.intervalos_cuotas_inmobiliaria) + venta.plan_de_pago.inicio_cuotas_inmobiliaria
        if (int(pago['nro_cuota']) in lista_cuotas_inm):
            monto_inmobiliaria = int(
                int(pago['monto']) * (float(venta.plan_de_pago.porcentaje_cuotas_inmobiliaria) / float(100)))
            monto_propietario = int(pago['monto']) - monto_inmobiliaria
            '''
            if(int(pago['nro_cuota']) % 2 != 0):
                monto_inmobiliaria = pago['monto']
                monto_propietario = 0
            else:
                monto_inmobiliaria = int(int(pago['monto']) * (float(venta.plan_de_pago.porcentaje_cuotas_administracion) / float(100)))
                monto_propietario = int(pago['monto']) - monto_inmobiliaria
            '''
        else:
            monto_inmobiliaria = int(
                int(pago['monto']) * (float(venta.plan_de_pago.porcentaje_cuotas_administracion) / float(100)))
            monto_propietario = int(pago['monto']) - monto_inmobiliaria

        monto = {}
        monto['monto_propietario'] = monto_propietario
        monto['monto_inmobiliaria'] = monto_inmobiliaria
        return monto
    except Exception, error:
        print error


def informe_facturacion(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
                if (filtros_establecidos(request.GET, 'informe_facturacion') == False):
                    t = loader.get_template('informes/informe_facturacion.html')
                    grupo = request.user.groups.get().id
                    c = RequestContext(request, {
                        'object_list': [],
                        'grupo': grupo
                    })
                    return HttpResponse(t.render(c))
                else:  # Parametros SETEADOS
                    t = loader.get_template('informes/informe_facturacion.html')

                    try:

                        fecha_ini = request.GET['fecha_ini']
                        fecha_fin = request.GET['fecha_fin']

                        busqueda = request.GET.get('busqueda', '')
                        busqueda_label = request.GET.get('busqueda_label', '')

                        sucursal = request.GET.get('sucursal', '')
                        sucursal_label = request.GET.get('sucursal_label', '')

                        fraccion = request.GET.get('fraccion', '')
                        fraccion_label = request.GET.get('fraccion_label', '')

                        concepto = request.GET.get('concepto', '')
                        concepto_label = request.GET.get('concepto_label', '')

                        anulados = request.GET.get('anulados', '')

                        todos_excepto_pago_cuota = request.GET.get('todos_excepto_pago_cuota', '')

                        usuario = request.user
                        grupo = usuario.groups.get().id

                        lista_totales = []

                        lista = proceso_informe_facturacion(fecha_ini, fecha_fin, busqueda, busqueda_label, sucursal, sucursal_label, fraccion, fraccion_label, concepto, concepto_label, anulados, todos_excepto_pago_cuota, usuario)

                        ultimo = "&fecha_ini=" + fecha_ini + "&fecha_fin=" + fecha_fin + "&busqueda=" + busqueda + "&busqueda_label=" + busqueda_label + "&anulados=" + anulados + "&todos_excepto_pago_cuota=" + todos_excepto_pago_cuota

                        #                         paginator = Paginator(filas, 25)
                        #                         page = request.GET.get('page')
                        #                         try:
                        #                             lista = paginator.page(page)
                        #                         except PageNotAnInteger:
                        #                             lista = paginator.page(1)
                        #                         except EmptyPage:
                        #                             lista = paginator.page(paginator.num_pages)

                        c = RequestContext(request, {
                            'object_list': lista,
                            'lista_totales': lista_totales,
                            'fecha_ini': fecha_ini,
                            'fecha_fin': fecha_fin,
                            'grupo': grupo,
                            'ultimo': ultimo,
                            'busqueda_label': busqueda_label,
                            'busqueda': busqueda,
                            'sucursal_label': sucursal_label,
                            'sucursal': sucursal,
                            'fraccion_label': fraccion_label,
                            'fraccion': fraccion,
                            'concepto_label': concepto_label,
                            'concepto': concepto,
                            'anulados': anulados,
                            'todos_excepto_pago_cuota': todos_excepto_pago_cuota,
                        })
                        return HttpResponse(t.render(c))
                    except Exception, error:
                        print error
            else:
                t = loader.get_template('index2.html')
                grupo = request.user.groups.get().id
                c = RequestContext(request, {
                    'grupo': grupo
                })
                return HttpResponse(t.render(c))
        else:
            return HttpResponseRedirect(reverse('login'))

def proceso_informe_facturacion(fecha_ini, fecha_fin, busqueda, busqueda_label, sucursal, sucursal_label, fraccion, fraccion_label, concepto, concepto_label, anulados, todos_excepto_pago_cuota, usuario):
    try:

        if fraccion == 'undefined' or fraccion_label == 'undefined':
            fraccion = ''
            fraccion_label = ''

        if sucursal == 'undefinded' or sucursal_label == 'undefined':
            sucursal = ''
            sucursal_label = ''

        if concepto == '' or concepto_label == 'undefined':
            concepto = ''
            concepto_label = ''

        if busqueda == '' or busqueda_label == 'undefined':
            busqueda = ''
            busqueda_label = ''

        fila = {}
        kwargs = {}
        filas = []
        # Totales GENERALES

        total_general_facturado = 0
        total_general_exentas = 0
        total_general_iva5 = 0
        total_general_iva10 = 0
        total_general_cuota_total = 0

        tipo_usuario = usuario.groups.get().name

        fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y").strftime("%Y-%m-%d")
        fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y").strftime("%Y-%m-%d")

        if anulados == 'solo_anulados':
            filtro_anulado = True
        elif anulados == 'no_anulados':
            filtro_anulado = False
        else:
            filtro_anulado = None

        if todos_excepto_pago_cuota == '1':
            todos_excepto_pago_cuota = True

        # Filtro Fecha
        kwargs['fecha__range'] = (fecha_ini_parsed, fecha_fin_parsed)

        # Filtro Usuario
        if tipo_usuario != 'Administradores' and tipo_usuario != 'operador_contable':
            kwargs['usuario'] = usuario
        else:
            if busqueda_label != '':
                kwargs['usuario'] = busqueda

        # Filtro Fraccion
        if fraccion != '':
            kwargs['lote__manzana__fraccion'] = fraccion

        # Filtro Sucursal
        if sucursal != '':
            kwargs['lote__manzana__fraccion_sucursal'] = sucursal

        # Filtro Anulado
        if filtro_anulado != None:
            kwargs['anulado'] = filtro_anulado

        # Filtro Concepto
        if concepto_label != '':
            kwargs['detalle__icontains'] = concepto_label

        # Filtro Todos excepto pago de cuotas
        if todos_excepto_pago_cuota == True:
            facturas = Factura.objects.filter(**kwargs).exclude(detalle__icontains='Pago de Cuota').order_by('numero')
            todos_excepto_pago_cuota = '1'
        else:
            facturas = Factura.objects.filter(**kwargs).order_by('numero')
            todos_excepto_pago_cuota = '0'

        for factura in facturas:

            # Totales Factura
            total_facturado = 0
            total_exentas = 0
            total_iva5 = 0
            total_cuota_total = 0
            total_iva10 = 0



            fecha_str = unicode(factura.fecha)
            fecha = unicode(datetime.datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y"))

            # Se setean los datos de cada fila
            fila = {}
            fila['id'] = factura.id
            fila['fecha'] = fecha
            fila['numero'] = factura.numero
            fila['cliente'] = unicode(factura.cliente)
            fila['ruc'] = unicode(factura.cliente.ruc)
            fila['lote'] = unicode(factura.lote.codigo_paralot)
            fila['tipo'] = unicode(factura.tipo)
            if factura.anulado == None or factura.anulado == False:
                fila['anulado'] = 'No'
            else:
                fila['anulado'] = 'SI'

            if factura.usuario_id != None:
                fila['usuario'] = unicode(factura.usuario)

            lista_detalles = json.loads(factura.detalle)
            for key, value in lista_detalles.iteritems():
                total_exentas += int(value['exentas'])
                total_iva5 += int(value['iva_5'])
                total_cuota_total += int(int(value['exentas']) + int(value['iva_5']))
                total_iva10 += int(value['iva_10'])
                total_facturado += int(int(value['cantidad']) * int(value['precio_unitario']))

            fila['total_exentas'] = unicode('{:,}'.format(total_exentas)).replace(",", ".")
            fila['total_iva5'] = unicode('{:,}'.format(total_iva5)).replace(",", ".")
            fila['total_cuota_total'] = unicode('{:,}'.format(total_cuota_total)).replace(",", ".")
            fila['total_iva10'] = unicode('{:,}'.format(total_iva10)).replace(",", ".")
            fila['total_facturado'] = unicode('{:,}'.format(total_facturado)).replace(",", ".")

            filas.append(fila)

            # Acumulamos para los TOTALES GENERALES
            total_general_exentas += int(total_exentas)
            total_general_iva5 += int(total_iva5)
            total_general_iva10 += int(total_iva10)
            total_general_facturado += int(total_facturado)
            total_general_cuota_total += int(total_cuota_total)

        # Totales GENERALES
        fila['total_general_facturado'] = unicode('{:,}'.format(total_general_facturado)).replace(
            ",", ".")
        fila['total_general_exentas'] = unicode('{:,}'.format(total_general_exentas)).replace(",",
                                                                                              ".")
        fila['total_general_iva5'] = unicode('{:,}'.format(total_general_iva5)).replace(",", ".")
        fila['total_general_iva10'] = unicode('{:,}'.format(total_general_iva10)).replace(",", ".")
        fila['total_general_cuota_total'] = unicode(
            '{:,}'.format(total_general_cuota_total)).replace(",", ".")

    except Exception, error:
        print error

    lista = filas
    return lista


def informe_facturacion_reporte_excel(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            if verificar_permisos(request.user.id, permisos.VER_INFORMES):
                if (filtros_establecidos(request.GET, 'informe_facturacion') == False):
                    t = loader.get_template('informes/informe_facturacion.html')
                    c = RequestContext(request, {
                        'object_list': [],
                    })
                    return HttpResponse(t.render(c))
                else:  # Parametros SETEADOS
                    t = loader.get_template('informes/informe_facturacion.html')
                    try:
                        fecha_ini = request.GET['fecha_ini']
                        fecha_fin = request.GET['fecha_fin']

                        busqueda = request.GET.get('busqueda', '')
                        busqueda_label = request.GET.get('busqueda_label', '')

                        sucursal = request.GET.get('sucursal', '')
                        sucursal_label = request.GET.get('sucursal_label', '')

                        fraccion = request.GET.get('fraccion', '')
                        fraccion_label = request.GET.get('fraccion_label', '')

                        concepto = request.GET.get('concepto', '')
                        concepto_label = request.GET.get('concepto_label', '')

                        anulados = request.GET.get('anulados', '')

                        todos_excepto_pago_cuota = request.GET.get('todos_excepto_pago_cuota', '')

                        usuario = request.user

                        filas = proceso_informe_facturacion(fecha_ini, fecha_fin, busqueda, busqueda_label, sucursal,
                                                            sucursal_label, fraccion, fraccion_label, concepto,
                                                            concepto_label, anulados, todos_excepto_pago_cuota, usuario)

                        totales_sucursales =0

                        wb = xlwt.Workbook(encoding='utf-8')
                        sheet = wb.add_sheet('test', cell_overwrite_ok=True)
                        sheet.paper_size_code = 1
                        style_titulo = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                                                   'font: name Calibri, bold True, height 200; align: horiz center')
                        style_normal = xlwt.easyxf('font: name Calibri, height 200;')

                        style_derecha = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz right')

                        style_centrado = xlwt.easyxf('font: name Calibri, height 200 ; align: horiz center')

                        style_titulo_derecha = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                                                           'font: name Calibri, bold True, height 200; align: horiz right')

                        usuario = unicode(request.user)
                        if busqueda_label == 'undefined':
                            nombre_usuario = usuario
                        else:
                            nombre_usuario = busqueda_label

                        if busqueda != '':
                            sheet.header_str = (
                                u"&LFecha: &D Hora: &T \nUsuario: " + nombre_usuario + " "
                                                                                u"&CPROPAR S.R.L.\n INFORME DE FACTURACION "
                                                                                u"&RPeriodo del : " + fecha_ini + " al " + fecha_fin + " \nPage &P of &N"
                            )

                            c = 0
                            sheet.write_merge(c, c, 0, 8, "Facturacion del Usuario: " + nombre_usuario, style_titulo)
                            c = c + 1
                            sheet.write(c, 0, 'Fecha', style_titulo)
                            sheet.write(c, 1, 'Numero', style_titulo)
                            sheet.write(c, 2, 'Lote', style_titulo)
                            sheet.write(c, 3, 'Cliente', style_titulo)
                            sheet.write(c, 4, 'RUC', style_titulo)
                            sheet.write(c, 5, 'Tipo', style_titulo)
                            sheet.write(c, 6, 'Exentas', style_titulo)
                            sheet.write(c, 7, 'IVA 5', style_titulo)
                            sheet.write(c, 8, 'Cuota Total', style_titulo)
                            sheet.write(c, 9, 'IVA 10', style_titulo)
                            sheet.write(c, 10, 'Monto', style_titulo)

                        else:
                            sheet.header_str = (
                                u"&LFecha: &D Hora: &T \nUsuario: " + nombre_usuario + " "
                                                                                u"&CPROPAR S.R.L.\n INFORME DE FACTURACION "
                                                                                u"&RPeriodo del : " + fecha_ini + " al " + fecha_fin + " \nPage &P of &N"
                            )

                            c = 0
                            sheet.write_merge(c, c, 0, 8, "Facturacion de todos los Usuarios", style_titulo)
                            c = c + 1
                            sheet.write(c, 0, 'Fecha', style_titulo)
                            sheet.write(c, 1, 'Numero', style_titulo)
                            sheet.write(c, 2, 'Lote', style_titulo)
                            sheet.write(c, 3, 'Cliente', style_titulo)
                            sheet.write(c, 4, 'RUC', style_titulo)
                            sheet.write(c, 5, 'Tipo', style_titulo)
                            sheet.write(c, 6, 'Exentas', style_titulo)
                            sheet.write(c, 7, 'IVA 5', style_titulo)
                            sheet.write(c, 8, 'Cuota Total', style_titulo)
                            sheet.write(c, 9, 'IVA 10', style_titulo)
                            sheet.write(c, 10, 'Monto', style_titulo)

                        sucursal = filas[0]['numero'][:3]

                        fil = 0
                        cant_filas = len(filas)
                        cont_filas = 0
                        for fila in filas:
                            #TODO: Ver que mierda es este tema de sucursales
                            # esta parte usamos para dividir las sucursales de acuerdo a los primeros 3 nros de factura
                            # y separar en el excel
                            # sucursal_aux = fila['numero'][:3]
                            # if sucursal_aux != sucursal:
                            #     sucursal = sucursal_aux
                            #     c += 1
                            #     # le agregamos el formato decimal a nuestra sumatoria por sucursal
                            #     totales_sucursales[fil][0] = unicode('{:,}'.format(totales_sucursales[fil][0])).replace(
                            #         ",", ".")
                            #     totales_sucursales[fil][1] = unicode('{:,}'.format(totales_sucursales[fil][1])).replace(
                            #         ",", ".")
                            #     totales_sucursales[fil][2] = unicode('{:,}'.format(totales_sucursales[fil][2])).replace(
                            #         ",", ".")
                            #     totales_sucursales[fil][3] = unicode('{:,}'.format(totales_sucursales[fil][3])).replace(
                            #         ",", ".")
                            #     totales_sucursales[fil][4] = unicode('{:,}'.format(totales_sucursales[fil][4])).replace(
                            #         ",", ".")
                            #     sheet.write(c, 6, totales_sucursales[fil][0], style_titulo)
                            #     sheet.write(c, 7, totales_sucursales[fil][1], style_titulo)
                            #     sheet.write(c, 8, totales_sucursales[fil][2], style_titulo)
                            #     sheet.write(c, 9, totales_sucursales[fil][3], style_titulo)
                            #     sheet.write(c, 10, totales_sucursales[fil][4], style_titulo)
                            #     fil += 1

                            c += 1
                            sheet.write(c, 0, fila['fecha'], style_centrado)
                            sheet.write(c, 1, fila['numero'], style_centrado)
                            sheet.write(c, 2, fila['lote'], style_centrado)
                            sheet.write(c, 3, fila['cliente'], style_normal)
                            sheet.write(c, 4, fila['ruc'], style_normal)
                            if fila['tipo'] == 'co':
                                sheet.write(c, 5, 'contado', style_centrado)
                            else:
                                sheet.write(c, 5, 'credito', style_centrado)
                            sheet.write(c, 6, fila['total_exentas'], style_derecha)
                            sheet.write(c, 7, fila['total_iva5'], style_derecha)
                            sheet.write(c, 8, fila['total_cuota_total'], style_derecha)
                            sheet.write(c, 9, fila['total_iva10'], style_derecha)
                            sheet.write(c, 10, fila['total_facturado'], style_derecha)
                            try:
                                # si se trata de la ultima fila, para el ultimo total de la sucursal debemos de colocar tambien
                                if (fila['total_general_facturado']):

                                    #TODO: Ver que mierda trató de hacer aquí con la sucursal
                                    # sheet.write(c, 6, fila['total_exentas'], style_derecha)
                                    # sheet.write(c, 7, fila['total_iva5'], style_derecha)
                                    # sheet.write(c, 8, fila['total_cuota_total'], style_derecha)
                                    # sheet.write(c, 9, fila['total_iva10'], style_derecha)
                                    # sheet.write(c, 10, fila['total_facturado'], style_derecha)
                                    # c += 1
                                    #
                                    # totales_sucursales[fil][0] = unicode(
                                    #     '{:,}'.format(totales_sucursales[fil][0])).replace(",", ".")
                                    # totales_sucursales[fil][1] = unicode(
                                    #     '{:,}'.format(totales_sucursales[fil][1])).replace(",", ".")
                                    # totales_sucursales[fil][2] = unicode(
                                    #     '{:,}'.format(totales_sucursales[fil][2])).replace(",", ".")
                                    # totales_sucursales[fil][3] = unicode(
                                    #     '{:,}'.format(totales_sucursales[fil][3])).replace(",", ".")
                                    # totales_sucursales[fil][4] = unicode(
                                    #     '{:,}'.format(totales_sucursales[fil][4])).replace(",", ".")
                                    # sheet.write(c, 6, totales_sucursales[fil][0], style_titulo)
                                    # sheet.write(c, 7, totales_sucursales[fil][1], style_titulo)
                                    # sheet.write(c, 8, totales_sucursales[fil][2], style_titulo)
                                    # sheet.write(c, 9, totales_sucursales[fil][3], style_titulo)
                                    # sheet.write(c, 10, totales_sucursales[fil][4], style_titulo)

                                    c += 1
                                    sheet.write_merge(c, c, 0, 5, "Totales Facturados", style_titulo)
                                    sheet.write(c, 6, fila['total_general_exentas'], style_titulo_derecha)
                                    sheet.write(c, 7, fila['total_general_iva5'], style_titulo_derecha)
                                    sheet.write(c, 8, fila['total_general_cuota_total'], style_titulo_derecha)
                                    sheet.write(c, 9, fila['total_general_iva10'], style_titulo_derecha)
                                    sheet.write(c, 10, fila['total_general_facturado'], style_titulo_derecha)
                            except Exception, error:
                                print error
                                pass

                        # Ancho de la columna Lote
                        col_lote = sheet.col(2)
                        col_lote.width = 256 * 12  # 12 characters wide

                        # Ancho de la columna Fecha
                        col_fecha = sheet.col(0)
                        col_fecha.width = 256 * 10  # 10 characters wide

                        # Ancho de la columna Nombre
                        col_nombre = sheet.col(3)
                        col_nombre.width = 256 * 22  # 22 characters wide

                        # Ancho de la columna Nro Factura
                        col_nro_factura = sheet.col(1)
                        col_nro_factura.width = 256 * 15  # 15 characters wide

                        # Ancho de la columna RUC
                        col_tipo = sheet.col(4)
                        col_tipo.width = 256 * 9  # 7 characters wide

                        # Ancho de la columna Tipo
                        col_tipo = sheet.col(5)
                        col_tipo.width = 256 * 7  # 7 characters wide

                        # Ancho de la columna exentas
                        col_exenta = sheet.col(6)
                        col_exenta.width = 256 * 10  # 9 characters wide

                        # Ancho de la columna iva5
                        col_iva5 = sheet.col(7)
                        col_iva5.width = 256 * 10  # 9 characters wide

                        # Ancho de la columna cuota total
                        col_cuota_total = sheet.col(8)
                        col_cuota_total.width = 256 * 10  # 9 characters wide

                        # Ancho de la columna iva10
                        col_iva10 = sheet.col(9)
                        col_iva10.width = 256 * 10  # 9 characters wide

                        # Ancho de la columna monto
                        col_monto = sheet.col(10)
                        col_monto.width = 256 * 12  # 9 characters wide

                        response = HttpResponse(content_type='application/vnd.ms-excel')
                        # Crear un nombre intuitivo
                        response['Content-Disposition'] = 'attachment; filename=' + 'informe_facturacion.xls'
                        wb.save(response)
                        return response
                    except Exception, error:
                        print error



def get_ultima_venta_no_recuperada_by_lote(lote_id):
    try:
        # print("lote_id ->" + lote_id)
        venta = [get_ultima_venta_no_recuperada(lote_id)]
        print venta
        object_list = [ob.as_json() for ob in venta]
        cuotas_details = get_cuotas_detail_by_lote(lote_id)
        # response = {
        # 'venta': object_list,
        # 'cuotas_details': cuotas_details,
        # }
        return cuotas_details
    except Exception, error:
        print error


def get_cuotas_details_by_lote(lote_id):
    try:
        cuotas_details = get_cuotas_detail_by_lote(lote_id)
        return cuotas_details
    except Exception, error:
        print error


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12)
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)
