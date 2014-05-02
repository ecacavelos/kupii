from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from principal.models import Propietario
from propietarios.forms import PropietarioForm, SearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


#from django.views.generic.list_detail import object_list


# Funcion principal del modulo de propietarios.
def index(request):
    
    if request.user.is_authenticated():
        t = loader.get_template('propietarios/index.html')
        c = RequestContext(request, {})
        return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login")

# Funcion para consultar el listado de todos los propietarios.
def consultar_propietarios(request):
    
    if request.user.is_authenticated():
        t = loader.get_template('propietarios/listado.html')
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login")
 
    if request.method == 'POST':
        data = request.POST
        search_form = SearchForm(data)        
        object_list = Propietario.objects.all().order_by('id')
        # En caso de que se haya solicitado una busqueda, filtramos de acuerdo al parametro correspondiente.
        search_field = data.get('filtro', '')
        message = ''
        if data.get('boton_buscar'):
            if data.get('buscar', '') != '':
                if search_field == 'N':
                    object_list = Propietario.objects.filter(nombres__iexact=data.get('buscar', '')).order_by('id')
                elif search_field == 'A':
                    object_list = Propietario.objects.filter(apellidos__iexact=data.get('buscar', '')).order_by('id')
                elif search_field == 'C':
                    object_list = Propietario.objects.filter(cedula__iexact=data.get('buscar', '')).order_by('id')
                elif search_field == 'I':
                    object_list = Propietario.objects.filter(id=int(data.get('buscar', '')))
            else:
                message = "No se ingresaron datos para la busqueda."
    else:
        object_list = Propietario.objects.all().order_by('id')
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

# Funcion para consultar el detalle de un propietario.
def detalle_propietario(request, propietario_id):
    
    if request.user.is_authenticated():
        t = loader.get_template('propietarios/detalle.html')
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login")
 
    object_list = Propietario.objects.get(pk=propietario_id)
    message = ''
 
    if request.method == 'POST':
        data = request.POST
        if data.get('boton_guardar'):
            form = PropietarioForm(data, instance=object_list)
            if form.is_valid():
                message = "Se actualizaron los datos."
                form.save(commit=False)
                object_list.save()
        elif data.get('boton_borrar'):
            c = Propietario.objects.get(pk=propietario_id)
            c.delete()
            return HttpResponseRedirect('/propietarios/listado')
    else:
        form = PropietarioForm(instance=object_list)
 
    c = RequestContext(request, {
        'propietario': object_list,
        'form': form,
        'message': message,
    })
    return HttpResponse(t.render(c))

# Funcion para agregar un nuevo propietario.
def agregar_propietarios(request):
    
    if request.user.is_authenticated():
        t = loader.get_template('propietarios/agregar.html')
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login")

    if request.method == 'POST':
        form = PropietarioForm(request.POST)
        if form.is_valid():
            form.save()
            # Redireccionamos al listado de propietarios luego de agregar el nuevo propietario.
            return HttpResponseRedirect('/propietarios/listado')
    else:
        form = PropietarioForm()

    c = RequestContext(request, {
        'form': form,
    })
    return HttpResponse(t.render(c))
