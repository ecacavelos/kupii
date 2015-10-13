from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from principal.models import PlanDePago, PlanDePagoVendedor, Timbrado, RangoFactura, TimbradoRangoFacturaUsuario, ConceptoFactura
from parametros.forms import PlanDePagoForm, SearchForm, PlanDePagoVendedorForm, TimbradoForm, RangoFacturaForm, ConceptoFacturaForm
from django.core.urlresolvers import reverse, resolve
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from principal.common_functions import verificar_permisos
from principal import permisos
from django.contrib.auth.models import User
# Funcion principal del modulo de lotes.
def parametros(request):    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_OPCIONES):
            t = loader.get_template('parametros/index.html')
            c = RequestContext(request, {})
            return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login')) 

#Funcion del modulo plan de pagos
def plan_de_pago(request):    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_OPCIONES_PLANDEPAGO):
            t = loader.get_template('parametros/plan_pago/index.html')
            c = RequestContext(request, {})
            return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
#Funcion del modulo de concepto factura
def concepto_factura(request):    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_OPCIONES_PLANDEPAGO):
            t = loader.get_template('parametros/concepto_factura/index.html')
            c = RequestContext(request, {})
            return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
#Funcion del modulo timbrado
def timbrado(request):    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_OPCIONES_TIMBRADO):
            t = loader.get_template('parametros/timbrado/index.html')
            c = RequestContext(request, {})
            return HttpResponse(t.render(c))
        else:
            return HttpResponseRedirect(reverse('frontend_home'))
    else:
        return HttpResponseRedirect(reverse('login'))
    
#Funcion del modulo rango_factura
def rango_factura(request, timbrado_id):    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_OPCIONES_RANGO_FACTURA):
            t = loader.get_template('parametros/timbrado/rango_factura/index.html')
            c = RequestContext(request, {
                                        'id_timbrado': timbrado_id
                                        })
            return HttpResponse(t.render(c))
        else:
            return HttpResponseRedirect(reverse('frontend_home'))
    else:
        return HttpResponseRedirect(reverse('login'))

#Funcion del modulo plan de pagos vendedores
def plan_de_pago_vendedores(request):
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_OPCIONES_PLANDEPAGOVENDEDOR):
            t = loader.get_template('parametros/plan_pago_vendedores/index.html')
            c = RequestContext(request, {})
            return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))


#funcion para consultar el listado de todos los planes de pagos
def consultar_plan_de_pago(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_PLANDEPAGO):
            t = loader.get_template('parametros/plan_pago/listado.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
    if request.method == 'POST':
        data = request.POST
        search_form = SearchForm(data)        
        object_list = PlanDePago.objects.all().order_by('id')
        # En caso de que se haya solicitado una busqueda, filtramos de acuerdo al parametro correspondiente.
        search_field = data.get('filtro', '')
        message = ''
        if data.get('boton_buscar'):
            if data.get('buscar', '') != '':
                if search_field == 'N':
                    object_list = PlanDePago.objects.filter(nombre_del_plan__iexact=data.get('buscar', '')).order_by('id')
                elif search_field == 'T':
                    object_list = PlanDePago.objects.filter(tipo_de_plan__iexact=data.get('buscar', '')).order_by('id')
                elif search_field == 'C':
                    object_list = PlanDePago.objects.filter(cantidad_de_cuotas__iexact=data.get('buscar', '')).order_by('id')
                elif search_field == 'I':
                    object_list = PlanDePago.objects.filter(id=int(data.get('buscar', '')))
            else:
                message = "No se ingresaron datos para la busqueda."
    else:
        object_list = PlanDePago.objects.all().order_by('id')
        search_form = SearchForm({})
        message = ""
    paginator = Paginator(object_list, 25)
    page = request.GET.get('page')
    try:
        lista = paginator.page(page)
    except PageNotAnInteger:
        lista = paginator.page(1)
    except EmptyPage:
        lista = paginator.page(paginator.num_pages)  
    c = RequestContext(request, {
        'object_list': lista,
        'search_form': search_form,
        'message': message,
    })
    return HttpResponse(t.render(c))

#funcion para consultar el listado de todos los timbrados
def consultar_timbrado(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_TIMBRADO):
            t = loader.get_template('parametros/timbrado/listado.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
    if request.method == 'POST':
        data = request.POST
        search_form = SearchForm(data)        
        object_list = Timbrado.objects.all().order_by('id')
        # En caso de que se haya solicitado una busqueda, filtramos de acuerdo al parametro correspondiente.
        search_field = data.get('filtro', '')
        message = ''
        if data.get('boton_buscar'):
            if data.get('buscar', '') != '':
                
                if search_field == 'N':
                    object_list = Timbrado.objects.filter(numero__iexact=data.get('buscar', '')).order_by('id')
                #elif search_field == 'T':
                    #object_list = PlanDePago.objects.filter(tipo_de_plan__iexact=data.get('buscar', '')).order_by('id')
                #elif search_field == 'C':
                    #object_list = PlanDePago.objects.filter(cantidad_de_cuotas__iexact=data.get('buscar', '')).order_by('id')
                #elif search_field == 'I':
                    #object_list = PlanDePago.objects.filter(id=int(data.get('buscar', '')))
                    
            else:
                message = "No se ingresaron datos para la busqueda."
    else:
        object_list = Timbrado.objects.all().order_by('id')
        search_form = SearchForm({})
        message = ""
    paginator = Paginator(object_list, 25)
    page = request.GET.get('page')
    try:
        lista = paginator.page(page)
    except PageNotAnInteger:
        lista = paginator.page(1)
    except EmptyPage:
        lista = paginator.page(paginator.num_pages)  
    c = RequestContext(request, {
        'object_list': lista,
        'search_form': search_form,
        'message': message,
    })
    return HttpResponse(t.render(c))

#funcion para consultar el listado de todos los cenceptos de factura
def consultar_concepto_factura(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_TIMBRADO):
            t = loader.get_template('parametros/concepto_factura/listado.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
    if request.method == 'POST':
        data = request.POST
        search_form = SearchForm(data)        
        object_list = ConceptoFactura.objects.all().order_by('id')
        # En caso de que se haya solicitado una busqueda, filtramos de acuerdo al parametro correspondiente.
        search_field = data.get('filtro', '')
        message = ''
        if data.get('boton_buscar'):
            if data.get('buscar', '') != '':
                
                if search_field == 'N':
                    object_list = ConceptoFactura.objects.filter(descripcion__iexact=data.get('buscar', '')).order_by('id')
                #elif search_field == 'T':
                    #object_list = PlanDePago.objects.filter(tipo_de_plan__iexact=data.get('buscar', '')).order_by('id')
                #elif search_field == 'C':
                    #object_list = PlanDePago.objects.filter(cantidad_de_cuotas__iexact=data.get('buscar', '')).order_by('id')
                #elif search_field == 'I':
                    #object_list = PlanDePago.objects.filter(id=int(data.get('buscar', '')))
                    
            else:
                message = "No se ingresaron datos para la busqueda."
    else:
        object_list = ConceptoFactura.objects.all().order_by('id')
        search_form = SearchForm({})
        message = ""
    paginator = Paginator(object_list, 25)
    page = request.GET.get('page')
    try:
        lista = paginator.page(page)
    except PageNotAnInteger:
        lista = paginator.page(1)
    except EmptyPage:
        lista = paginator.page(paginator.num_pages)  
    c = RequestContext(request, {
        'object_list': lista,
        'search_form': search_form,
        'message': message,
    })
    return HttpResponse(t.render(c))

#funcion para consultar el listado de todos los rango_factura
def consultar_rango_factura(request, timbrado_id):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_RANGO_FACTURA):
            t = loader.get_template('parametros/timbrado/rango_factura/listado.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo,
                 'id_timbrado': timbrado_id
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
    if request.method == 'POST':
        data = request.POST
        search_form = SearchForm(data)
        object_list = TimbradoRangoFacturaUsuario.objects.filter(timbrado=timbrado_id).order_by('id')        
        object_list = TimbradoRangoFacturaUsuario.rango_factura
         
        # En caso de que se haya solicitado una busqueda, filtramos de acuerdo al parametro correspondiente.
        search_field = data.get('filtro', '')
        message = ''
        if data.get('boton_buscar'):
            if data.get('buscar', '') != '':
                
                if search_field == 'N':
                    object_list = RangoFactura.objects.filter(nro_sucursal__iexact=data.get('buscar', '')).order_by('id')
                #elif search_field == 'T':
                    #object_list = PlanDePago.objects.filter(tipo_de_plan__iexact=data.get('buscar', '')).order_by('id')
                #elif search_field == 'C':
                    #object_list = PlanDePago.objects.filter(cantidad_de_cuotas__iexact=data.get('buscar', '')).order_by('id')
                #elif search_field == 'I':
                    #object_list = PlanDePago.objects.filter(id=int(data.get('buscar', '')))
                    
            else:
                message = "No se ingresaron datos para la busqueda."
    else:
        object_list = TimbradoRangoFacturaUsuario.objects.filter(timbrado=timbrado_id).order_by('id')        
        rango_factura_list = []
        for trfu in object_list:
            rango_factura = RangoFactura.objects.get(pk=trfu.timbrado_id)
            rango_factura.usuario = trfu.usuario
            rango_factura_list.append(rango_factura)                                  
        
        search_form = SearchForm({})
        message = ""
    paginator = Paginator(rango_factura_list, 25)
    page = request.GET.get('page')
    try:
        lista = paginator.page(page)
    except PageNotAnInteger:
        lista = paginator.page(1)
    except EmptyPage:
        lista = paginator.page(paginator.num_pages)  
    c = RequestContext(request, {
        'object_list': lista,
        'search_form': search_form,
        'message': message,
        'id_timbrado': timbrado_id
    })
    return HttpResponse(t.render(c))

#funcion para consultar el listado de todos los planes de pagos de vendedores
def consultar_plan_de_pago_vendedores(request):    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_PLANDEPAGOVENDEDORES):
            t = loader.get_template('parametros/plan_pago_vendedores/listado.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
    if request.method == 'POST':
        data = request.POST
        search_form = SearchForm(data)        
        object_list = PlanDePagoVendedor.objects.all().order_by('id')
        # En caso de que se haya solicitado una busqueda, filtramos de acuerdo al parametro correspondiente.
        search_field = data.get('filtro', '')
        message = ''
        if data.get('boton_buscar'):
            if data.get('buscar', '') != '':
                if search_field == 'N':
                    object_list = PlanDePagoVendedor.objects.filter(nombre_del_plan__iexact=data.get('buscar', '')).order_by('id')
                elif search_field == 'T':
                    object_list = PlanDePagoVendedor.objects.filter(tipo_de_plan__iexact=data.get('buscar', '')).order_by('id')
                elif search_field == 'C':
                    object_list = PlanDePagoVendedor.objects.filter(cantidad_de_cuotas__iexact=data.get('buscar', '')).order_by('id')
                elif search_field == 'I':
                    object_list = PlanDePagoVendedor.objects.filter(id=int(data.get('buscar', '')))
            else:
                message = "No se ingresaron datos para la busqueda."
    else:
        object_list = PlanDePagoVendedor.objects.all().order_by('id')
        search_form = SearchForm({})
        message = ""
        
    paginator = Paginator(object_list, 25)
    page = request.GET.get('page')
    try:
        lista = paginator.page(page)
    except PageNotAnInteger:
        lista = paginator.page(1)
    except EmptyPage:
        lista = paginator.page(paginator.num_pages) 
    c = RequestContext(request, {
        'object_list': lista,
        'search_form': search_form,
        'message': message,
    })
    return HttpResponse(t.render(c))

# Funcion para consultar el detalle de un cliente.
def detalle_plan_de_pago(request, plandepago_id):    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_PLANDEPAGO):
            t = loader.get_template('parametros/plan_pago/detalle.html')
            grupo= request.user.groups.get().id
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
    object_list = PlanDePago.objects.get(pk=plandepago_id)
    message = ''

    if request.method == 'POST':
        data = request.POST
        if data.get('boton_guardar'):
            form = PlanDePagoForm(data, instance=object_list)
            if form.is_valid():
                message = "Se actualizaron los datos."
                form.save(commit=False)
                object_list.save()
        elif data.get('boton_borrar'):
            c = PlanDePago.objects.get(pk=plandepago_id)
            c.delete()
            return HttpResponseRedirect('/parametros/plan_pago/listado')
    else:
        form = PlanDePagoForm(instance=object_list)

    c = RequestContext(request, {
        'plandepago': object_list,
        'form': form,
        'message': message,
        'grupo': grupo
    })
    return HttpResponse(t.render(c))

# Funcion para consultar el detalle de un cliente.
def detalle_timbrado(request, timbrado_id):    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_TIMBRADO):
            t = loader.get_template('parametros/timbrado/detalle.html')
            grupo= request.user.groups.get().id
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
    object_list = Timbrado.objects.get(pk=timbrado_id)
    message = ''

    if request.method == 'POST':
        data = request.POST
        if data.get('boton_guardar'):
            form = TimbradoForm(data, instance=object_list)
            if form.is_valid():
                message = "Se actualizaron los datos."
                form.save(commit=False)
                object_list.save()
        elif data.get('boton_borrar'):
            c = Timbrado.objects.get(pk=timbrado_id)
            c.delete()
            return HttpResponseRedirect('/parametros/timbrado/listado')
    else:
        form = TimbradoForm(instance=object_list)

    c = RequestContext(request, {
        'timbrado': object_list,
        'form': form,
        'message': message,
        'grupo': grupo,
        'id_timbrado': timbrado_id
    })
    return HttpResponse(t.render(c))

# Funcion para consultar el detalle de un concepto de factura.
def detalle_concepto_factura(request, concepto_factura_id):    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_TIMBRADO):
            t = loader.get_template('parametros/concepto_factura/detalle.html')
            grupo= request.user.groups.get().id
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
    object_list = ConceptoFactura.objects.get(pk=concepto_factura_id)
    message = ''

    if request.method == 'POST':
        data = request.POST
        if data.get('boton_guardar'):
            form = ConceptoFacturaForm(data, instance=object_list)
            if form.is_valid():
                message = "Se actualizaron los datos."
                form.save(commit=False)
                object_list.save()
        elif data.get('boton_borrar'):
            c = ConceptoFactura.objects.get(pk=concepto_factura_id)
            c.delete()
            return HttpResponseRedirect('/parametros/concepto_factura/listado')
    else:
        form = ConceptoFacturaForm(instance=object_list)

    c = RequestContext(request, {
        'concepto_factura': object_list,
        'form': form,
        'message': message,
        'grupo': grupo,
        'id_concepto_factura': concepto_factura_id
    })
    return HttpResponse(t.render(c))


# Funcion para consultar el detalle de un rango_factura.
def detalle_rango_factura(request, timbrado_id, rango_factura_id):    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_RANGO_FACTURA):
            t = loader.get_template('parametros/timbrado/rango_factura/detalle.html')
            grupo= request.user.groups.get().id
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo,
                 'id_timbrado': timbrado_id
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
    object_list = RangoFactura.objects.get(pk=rango_factura_id)
    message = ''

    if request.method == 'POST':
        data = request.POST
        if data.get('boton_guardar'):
            form = RangoFacturaForm(data, instance=object_list)
            if form.is_valid():
                message = "Se actualizaron los datos."
                form.save(commit=False)
                usuario = TimbradoRangoFacturaUsuario.objects.get(rango_factura_id = rango_factura_id, timbrado_id=timbrado_id)
                usuario.usuario = User.objects.get(id=form.data['usuario'])
                usuario.save()
                object_list.save()
        elif data.get('boton_borrar'):
            c = RangoFactura.objects.get(pk=rango_factura_id)
            c.delete()
            return HttpResponseRedirect('/parametros/timbrado/'+unicode(timbrado_id)+'/rango_factura/listado')
    else:
        rango = TimbradoRangoFacturaUsuario.objects.get(timbrado_id= timbrado_id, rango_factura_id = rango_factura_id)
        form = RangoFacturaForm(instance=object_list)
        
        form.initial['usuario'] = unicode(rango.usuario_id)

    c = RequestContext(request, {
        'rango_factura': object_list,
        'form': form,
        'message': message,
        'grupo': grupo,
        'id_timbrado': timbrado_id,
        'usuario': User,
    })
    return HttpResponse(t.render(c))

# Funcion para consultar el detalle de un cliente.
def detalle_plan_de_pago_vendedores(request, plandepago_vendedor_id):    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_PLANDEPAGOVENDEDORES):
            t = loader.get_template('parametros/plan_pago_vendedores/detalle.html')
            grupo= request.user.groups.get().id
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
    object_list = PlanDePagoVendedor.objects.get(pk=plandepago_vendedor_id)
    message = ''

    if request.method == 'POST':
        data = request.POST
        if data.get('boton_guardar'):
            form = PlanDePagoVendedorForm(data, instance=object_list)
            if form.is_valid():
                message = "Se actualizaron los datos."
                form.save(commit=False)
                object_list.save()
        elif data.get('boton_borrar'):
            c = PlanDePagoVendedor.objects.get(pk=plandepago_vendedor_id)
            c.delete()
            return HttpResponseRedirect('/parametros/plan_pago_vendedores/listado')
    else:
        form = PlanDePagoVendedorForm(instance=object_list)

    c = RequestContext(request, {
        'plandepago': object_list,
        'form': form,
        'message': message,
        'grupo': grupo
    })
    return HttpResponse(t.render(c))


#funcion para agregar planes de pago
def agregar_plan_de_pago(request):
   
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.ADD_PLANDEPAGO): 
            t = loader.get_template('parametros/plan_pago/agregar.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
    if request.method == 'POST':
        form = PlanDePagoForm(request.POST)
        if form.is_valid():
            form.save()
            # Redireccionamos al listado de planes de pago luego de agregar el nuevo plan.
            return HttpResponseRedirect('/parametros/plan_pago/listado')
    else:
        form = PlanDePagoForm()

    c = RequestContext(request, {
        'form': form,
    })
    return HttpResponse(t.render(c))

#funcion para agregar timbrados
def agregar_timbrado(request):
   
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.ADD_TIMBRADO): 
            t = loader.get_template('parametros/timbrado/agregar.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
    if request.method == 'POST':
        form = TimbradoForm(request.POST)
        if form.is_valid():
            form.save()
            # Redireccionamos al listado de planes de pago luego de agregar el nuevo plan.
            return HttpResponseRedirect('/parametros/timbrado/listado')
    else:
        form = TimbradoForm()

    c = RequestContext(request, {
        'form': form,
    })
    return HttpResponse(t.render(c))

#funcion para agregar conceptos de facturas
def agregar_concepto_factura(request):
   
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.ADD_CONCEPTO_FACTURA): 
            t = loader.get_template('parametros/concepto_factura/agregar.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
    if request.method == 'POST':
        form = ConceptoFacturaForm(request.POST)
        if form.is_valid():
            form.save()
            # Redireccionamos al listado de planes de pago luego de agregar el nuevo plan.
            return HttpResponseRedirect('/parametros/concepto_factura/listado')
    else:
        form = ConceptoFacturaForm()

    c = RequestContext(request, {
        'form': form,
    })
    return HttpResponse(t.render(c))

#funcion para agregar timbrados
def agregar_rango_factura(request, timbrado_id):
   
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.ADD_RANGO_FACTURA): 
            t = loader.get_template('parametros/timbrado/rango_factura/agregar.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo,
                 'id_timbrado': timbrado_id
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
    if request.method == 'POST':
        form = RangoFacturaForm(request.POST)
        if form.is_valid():
            rangoFactura = form.save(commit=False)
            rangoFactura.save()
            timbradoRangoFacturaUsuario = TimbradoRangoFacturaUsuario()
            timbradoRangoFacturaUsuario.timbrado = Timbrado.objects.get(pk=timbrado_id)
            timbradoRangoFacturaUsuario.rango_factura = RangoFactura.objects.get(pk=rangoFactura.id)
            timbradoRangoFacturaUsuario.usuario = User.objects.get(id=form.data['usuario'])
            timbradoRangoFacturaUsuario.save()
            # Redireccionamos al listado de planes de pago luego de agregar el nuevo plan.
            return HttpResponseRedirect('/parametros/timbrado/listado/'+unicode(timbrado_id)+'/rango_factura/listado')
    else:
        form = RangoFacturaForm()

    c = RequestContext(request, {
        'form': form,
    })
    return HttpResponse(t.render(c))

#funcion para agregar planes de pago de vendedores
def agregar_plan_de_pago_vendedores(request):
  
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.ADD_PLANDEPAGOVENDEDOR): 
            t = loader.get_template('parametros/plan_pago_vendedores/agregar.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
    if request.method == 'POST':
        form = PlanDePagoVendedorForm(request.POST)
        if form.is_valid():
            form.save()
            # Redireccionamos al listado de planes de pago luego de agregar el nuevo plan.
            return HttpResponseRedirect('/parametros/plan_pago_vendedores/listado')
    else:
        form = PlanDePagoVendedorForm()

    c = RequestContext(request, {
        'form': form,
    })
    return HttpResponse(t.render(c))

def parametros_generales(request):
    
    if request.user.is_authenticated():
        t = loader.get_template('parametros/generales.html')
        c = RequestContext(request, {})
        return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
def listar_busqueda_ppagos(request):       
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_PLANDEPAGO): 
            t = loader.get_template('parametros/plan_pago/listado.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login')) 
    
    id_ppago = request.POST['plan_pago']
    if id_ppago:
        object_list=PlanDePago.objects.filter(pk=id_ppago)
    paginator=Paginator(object_list,15)
    page=request.GET.get('page')
    try:
        lista=paginator.page(page)
    except PageNotAnInteger:
        lista=paginator.page(1)
    except EmptyPage:
        lista=paginator.page(paginator.num_pages)
        
    c = RequestContext(request, {
        'object_list': lista,
    })
    return HttpResponse(t.render(c))

def listar_busqueda_timbrado(request):       
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_TIMBRADO): 
            t = loader.get_template('parametros/timbrado/listado.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login')) 
    
    id_timbrado = request.POST['timbrado']
    if id_timbrado:
        object_list=Timbrado.objects.filter(pk=id_timbrado)
    paginator=Paginator(object_list,15)
    page=request.GET.get('page')
    try:
        lista=paginator.page(page)
    except PageNotAnInteger:
        lista=paginator.page(1)
    except EmptyPage:
        lista=paginator.page(paginator.num_pages)
        
    c = RequestContext(request, {
        'object_list': lista,
    })
    return HttpResponse(t.render(c))

def listar_busqueda_rango_factura(request, timbrado_id):       
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_RANGO_FACTURA): 
            t = loader.get_template('parametros/timbrado/rango_factura/listado.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo,
                 'id_timbrado': timbrado_id
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login')) 
    
    id_rango_factura = request.POST['rango_factura']
    if id_rango_factura:
        object_list=RangoFactura.objects.filter(pk=id_rango_factura)
    paginator=Paginator(object_list,15)
    page=request.GET.get('page')
    try:
        lista=paginator.page(page)
    except PageNotAnInteger:
        lista=paginator.page(1)
    except EmptyPage:
        lista=paginator.page(paginator.num_pages)
        
    c = RequestContext(request, {
        'object_list': lista,
    })
    return HttpResponse(t.render(c))

def listar_busqueda_concepto_factura(request, concepto_factura_id):       
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_CONCEPTO_FACTURA):
            t = loader.get_template('parametros/timbrado/rango_factura/listado.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo,
                 'id_timbrado': timbrado_id
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login')) 
    
    id_rango_factura = request.POST['rango_factura']
    if id_rango_factura:
        object_list=RangoFactura.objects.filter(pk=id_rango_factura)
    paginator=Paginator(object_list,15)
    page=request.GET.get('page')
    try:
        lista=paginator.page(page)
    except PageNotAnInteger:
        lista=paginator.page(1)
    except EmptyPage:
        lista=paginator.page(paginator.num_pages)
        
    c = RequestContext(request, {
        'object_list': lista,
    })
    return HttpResponse(t.render(c))

def listar_busqueda_ppagos_vendedores(request):       
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_PLANDEPAGOVENDEDORES): 
            t = loader.get_template('parametros/plan_pago_vendedores/listado.html')
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                 'grupo': grupo
            })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login')) 
    
    id_ppago_vendedor = request.POST['plan_pago_vendedores']
    if id_ppago_vendedor:
        object_list=PlanDePagoVendedor.objects.filter(pk=id_ppago_vendedor)
    paginator=Paginator(object_list,15)
    page=request.GET.get('page')
    try:
        lista=paginator.page(page)
    except PageNotAnInteger:
        lista=paginator.page(1)
    except EmptyPage:
        lista=paginator.page(paginator.num_pages)
        
    c = RequestContext(request, {
        'object_list': lista,
    })
    return HttpResponse(t.render(c))
