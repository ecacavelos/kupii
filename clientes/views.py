from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from principal.models import Cliente
from clientes.forms import ClienteForm, SearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse, resolve
from principal.common_functions import *
from principal import permisos
#from django.views.generic.list_detail import object_list

# Funcion principal del modulo de clientes.
def index(request):
    if request.user.is_authenticated():
        t = loader.get_template('clientes/index.html')
        c = RequestContext(request, {})
        return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    

# Funcion para consultar el listado de todos los clientes.
def consultar_clientes(request):
    
    if request.method == 'GET':
        if request.user.is_authenticated():
            t = loader.get_template('clientes/listado.html')
            if (filtros_establecidos(request.GET,'listado_clientes') == False):
                print('Parametros no seteados')
                object_list = Cliente.objects.all().order_by('id')
            else: #Parametros seteados
                print('Parametros de filtrado seteados')
                tipo_busqueda=request.GET['tipo_busqueda']
                busqueda_label=request.GET['busqueda_label']
                if tipo_busqueda == 'nombre':
                    object_list = Cliente.objects.filter(nombres__icontains=busqueda_label)
                else:
                    object_list = Cliente.objects.filter(cedula__icontains=busqueda_label)
            search_form = SearchForm({})
            message = ""            
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
                'search_form': search_form,
                'message': message,
            })
            return HttpResponse(t.render(c))
        else:
            return HttpResponseRedirect(reverse('login'))    
    else: #POST
        data = request.POST
        search_form = SearchForm(data)        
        object_list = Cliente.objects.all().order_by('id')
        # En caso de que se haya solicitado una busqueda, filtramos de acuerdo al parametro correspondiente.
        search_field = data.get('filtro', '')
        message = ''
        if data.get('boton_buscar'):
            if data.get('buscar', '') != '':
                if search_field == 'N':
                    object_list = Cliente.objects.filter(nombres__iexact=data.get('buscar', '')).order_by('id')
                elif search_field == 'A':
                    object_list = Cliente.objects.filter(apellidos__iexact=data.get('buscar', '')).order_by('id')
                elif search_field == 'C':
                    object_list = Cliente.objects.filter(cedula__iexact=data.get('buscar', '')).order_by('id')
                elif search_field == 'I':
                    object_list = Cliente.objects.filter(id=int(data.get('buscar', '')))
            else:
                message = "No se ingresaron datos para la busqueda."

# Funcion para consultar el detalle de un cliente.
def detalle_cliente(request, cliente_id):
    
    if request.user.is_authenticated():
        t = loader.get_template('clientes/detalle.html')
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))

    object_list = Cliente.objects.get(pk=cliente_id)
    message = ''

    if request.method == 'POST':
        data = request.POST
        if data.get('boton_guardar'):
            form = ClienteForm(data, instance=object_list)
            if form.is_valid():
                message = "Se actualizaron los datos."
                form.save(commit=False)
                object_list.save()
        elif data.get('boton_borrar'):
            c = Cliente.objects.get(pk=cliente_id)
            c.delete()
            return HttpResponseRedirect('/clientes/listado')
    else:
        form = ClienteForm(instance=object_list)

    c = RequestContext(request, {
        'cliente': object_list,
        'form': form,
        'message': message,
    })
    return HttpResponse(t.render(c))

# Funcion para agregar un nuevo cliente.
def agregar_clientes(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.ADD_CLIENTE):
            t = loader.get_template('clientes/agregar.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
            
    else:
        return HttpResponseRedirect(reverse('login'))
    
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            # Redireccionamos al listado de clientes luego de agregar el nuevo cliente.
            return HttpResponseRedirect('/clientes/listado')
    else:
        form = ClienteForm()

    c = RequestContext(request, {
        'form': form,
    })
    return HttpResponse(t.render(c))
