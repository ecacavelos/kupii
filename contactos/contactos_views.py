# -*- encoding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from contactos.contactos_models import Contacto
from contactos.contactos_forms import ContactoAddForm, ContactoEditForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from principal.common_functions import *
from principal import permisos


# Método para consultar el listado de Contactos.
def listado_contactos(request):
    if request.user.is_authenticated():
        # Si el usuario está logueado
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_CONTACTOS):
            # Si el usuario tiene permiso
            t = loader.get_template('contactos/listado_contacto.html')

            # Parametros de busqueda
            # Rango de fecha
            fecha_ini = request.GET.get('fecha_ini', '')
            fecha_fin = request.GET.get('fecha_fin', '')

            # Lote
            lote_id = request.GET.get('lote_id', '')
            codigo_lote = request.GET.get('codigo_lote', '')

            # Cliente
            cliente_id = request.GET.get('cliente_id', '')
            nombre_cliente = request.GET.get('nombre_cliente', '')

            # Usuario
            usuario_id = request.GET.get('usuario_id', '')
            nombre_usuario = request.GET.get('nombre_usuario', '')

            # Respondido
            respondido = request.GET.get('respondido', '')

            # Formato Reporte
            formato_reporte = request.GET.get('formato_reporte', 'pantalla')

            # Ultima busqueda
            ultima_busqueda = "&fecha_ini=" + fecha_ini + "&fecha_fin=" + fecha_fin + "&lote_id=" + lote_id + \
                              "&codigo_lote=" + codigo_lote + "&cliente_id=" + cliente_id + "&nombre_cliente=" + \
                              nombre_cliente + "&formato_reporte=" + formato_reporte + "&usuario_id=" + usuario_id + "&nombre_usuario=" + "&respondido=" + respondido

            if lote_id == '' and cliente_id == '' and fecha_ini == '' and fecha_fin == '' and usuario_id == '' and respondido == '':
                # obtenemos todos los contactos en ordenados por fecha descendente
                contactos = Contacto.objects.all().order_by('-fecha_contacto')
            else:
                # obtenemos los contactos por filtros ordenados por fecha descendente
                filtros = {}

                # Rango de fecha
                if fecha_ini == 'undefined' or fecha_fin == 'undefined' or fecha_ini == '' or fecha_fin == '':
                    fecha_ini = ''
                    fecha_fin = ''
                # Filtro Rango Fecha
                if fecha_ini != '' and fecha_fin != '':
                    # Se parsea la fecha que viene del formulario de busqueda para consultar a la base de datos
                    fecha_ini_parsed = datetime.datetime.strptime(fecha_ini, "%d/%m/%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                    fecha_fin_parsed = datetime.datetime.strptime(fecha_fin, "%d/%m/%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                    filtros['fecha_contacto__range'] = (fecha_ini_parsed, fecha_fin_parsed)

                # Lote
                if lote_id == 'undefined' or codigo_lote == 'undefined':
                    lote_id = ''
                    codigo_lote = ''
                # Filtro Lote
                if lote_id != '':
                    filtros['lote_id'] = lote_id

                # Cliente
                if cliente_id == 'undefined' or nombre_cliente == 'undefined':
                    cliente_id = ''
                    nombre_cliente = ''
                # Filtro cliente
                if cliente_id != '':
                    filtros['cliente_id'] = cliente_id

                # Usuario
                if usuario_id == 'undefined' or nombre_usuario == 'undefined':
                    usuario_id = ''
                    nombre_usuario = ''
                # Filtro usuario
                if usuario_id != '':
                    filtros['remitente_usuario_id'] = usuario_id

                # Respondido
                if respondido == 'undefined':
                    respondido = ''
                # Filtro rrspondido
                if respondido != '':
                    if respondido == 'True':
                        respondido = True
                    else:
                        respondido = False
                    filtros['respondido'] = respondido

                # obtenemos los contactos segun los filtros ordenados por fecha de contacto de forma descendente
                contactos = Contacto.objects.filter(**filtros).order_by('-fecha_contacto')

            if formato_reporte == 'pantalla':
                # Si la respuesta se muestra en pantalla
                paginator = Paginator(contactos, 15)
                page = request.GET.get('page')
                try:
                    lista_paginada = paginator.page(page)
                except PageNotAnInteger:
                    lista_paginada = paginator.page(1)
                except EmptyPage:
                    lista_paginada = paginator.page(paginator.num_pages)

                c = RequestContext(request, {
                    'lista_paginada': lista_paginada,
                    'fecha_ini': fecha_ini,
                    'fecha_fin': fecha_fin,
                    'lote_id': lote_id,
                    'codigo_lote': codigo_lote,
                    'cliente_id': cliente_id,
                    'nombre_cliente': nombre_cliente,
                    'usuario_id': usuario_id,
                    'nombre_usuario': nombre_usuario,
                    'respondido': respondido,
                    'ultima_busqueda': ultima_busqueda,
                    'usuario': request.user,
                    'tipo_usuario': request.user.groups.get().name,
                })
                return HttpResponse(t.render(c))

            elif formato_reporte == 'excel':
                # Si la respuesta se muestra en pantalla
                print "excel"
                # TODO: aplicar la logica del excel


        else:
            # si no tiene permisos se le redirige al home
            return HttpResponseRedirect(reverse('frontend_home'))
    else:
        # si no está logueado se le redirige al login
        return HttpResponseRedirect(reverse('login'))


# Metodo para agregar un nuevo contacto.
def agregar_contacto(request):
    if request.user.is_authenticated():
        # Si el usuario está autenticado verifica los permisos
        if verificar_permisos(request.user.id, permisos.ADD_CONTACTO):
            # Template para agregar contacto
            t = loader.get_template('contactos/agregar_contacto.html')
            # Se inicializa la variable de mensaje
            message = ""

            if request.method == 'POST':
                # Si se está guardando el contacto
                form = ContactoAddForm(request.POST)
                if form.is_valid():
                    # Si el formulario es valido
                    form.save()
                    id_objeto = form.instance.id
                    codigo_lote = form.instance.lote.codigo_paralot
                    loggear_accion(request.user, "Agregar", "Contacto", id_objeto, codigo_lote)
                    return HttpResponseRedirect(reverse('frontend_listado_contactos'))

                else:
                    # Si el formulario es invalido
                    message = "Debe Completar los campos requeridos"
                    form = ContactoAddForm()
            else:
                # Si se está entrando por primera vez a agregar (GET)
                form = ContactoAddForm()

            # Renderiza el formulario en el template tanto para la primera vez como para formulario inválido
            tipo_usuario = request.user.groups.get().name
            c = RequestContext(request, {
                'form': form,
                'message': message,
                'id_usuario': request.user.id,
                'tipo_usuario': tipo_usuario,
            })
            return HttpResponse(t.render(c))

        else:
            # si no tiene permisos se le redirige al home
            return HttpResponseRedirect(reverse('frontend_home'))

    else:
        # si no está logueado se le redirige al login
        return HttpResponseRedirect(reverse('login'))


# Método para ver un contacto: edita o borra un contacto.
def detalle_contacto(request, contacto_id):
    if request.user.is_authenticated():
        # Si el usuario está autenticado verifica los permisos
        if verificar_permisos(request.user.id, permisos.VER_DETALLE_CONTACTO):
            # Template para agregar contacto
            t = loader.get_template('contactos/detalle_contacto.html')

            # Se obtiene el objeto contacto a partir del id
            contacto = Contacto.objects.get(pk=contacto_id)
            message = ''
            message_id = "message"

            if request.method == 'POST':
                # Se envía una peticion por post
                data = request.POST
                form = ContactoEditForm(request.POST, instance=contacto)
                # TODO: ver como preguntar directamente desde el form la info del boton que se presionó
                if data.get('boton_guardar'):
                    # Si se envió la edición  del contacto
                    if form.is_valid():
                        message = "Se actualizaron los datos."
                        message_id = "message-success"

                        # Se loggea la accion del usuario
                        id_objeto = contacto_id
                        if form.instance.lote is not None:
                            codigo_lote = form.instance.lote.codigo_paralot
                        else:
                            codigo_lote = ""
                        loggear_accion(request.user, "Actualizar", "Contacto", id_objeto, codigo_lote)
                        form.save()
                    else:
                        # Formulario invalido
                        message = "No se pudo actualizar los datos."
                        message_id = "message-error"

                elif data.get('boton_borrar'):
                    # Si se quiere borrar el contacto
                    if form.instance.lote is not None:
                        codigo_lote = form.instance.lote.codigo_paralot
                    else:
                        codigo_lote = ""
                    id_objeto = contacto_id
                    # Se loggea la accion del usuario
                    loggear_accion(request.user, "Borrar Contacto(" + codigo_lote + ")", "Contacto", id_objeto,
                                   codigo_lote)
                    form.instance.delete()
                    return HttpResponseRedirect(reverse('frontend_listado_contactos'))
            else:
                # Si se accede a la pantalla para editar un contacto
                form = ContactoEditForm(instance=contacto)
            tipo_usuario = request.user.groups.get().name
            c = RequestContext(request, {
                'form': form,
                'message_id': message_id,
                'message': message,
                'id_usuario': request.user.id,
                'tipo_usuario': tipo_usuario,
            })
            return HttpResponse(t.render(c))

        else:
            # si no tiene permisos se le redirige al home
            return HttpResponseRedirect(reverse('frontend_home'))
    else:
        # si no está logueado se le redirige al login
        return HttpResponseRedirect(reverse('login'))
