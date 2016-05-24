from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from principal.models import Vendedor
from vendedores.forms import VendedorForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse, resolve
from principal.common_functions import verificar_permisos
from principal import permisos
#from django.views.generic.list_detail import object_list

# Funcion principal del modulo de vendedores.
def vendedores(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_OPCIONES_VENDEDOR):
            t = loader.get_template('vendedores/index.html')
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

# Funcion para consultar el listado de todas los vendedores.
def consultar_vendedores(request):
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_VENDEDORES):
            t = loader.get_template('vendedores/listado.html')
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
    
    object_list = Vendedor.objects.all().order_by('id')
    
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
    
    

# Funcion para el detalle de un vendedor: edita o borra un vendedor.
def detalle_vendedor(request, vendedor_id):
    
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.VER_LISTADO_VENDEDORES):
            t = loader.get_template('vendedores/detalle.html')
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

    object_list = Vendedor.objects.get(pk=vendedor_id)
    message = ''

    if request.method == 'POST':
        data = request.POST
        if data.get('boton_guardar'):
            form = VendedorForm(data, instance=object_list)
            if form.is_valid():
                message = "Se actualizaron los datos."
                form.save(commit=False)
                object_list.save()
        elif data.get('boton_borrar'):
            f = Vendedor.objects.get(pk=vendedor_id)
            f.delete()
            #return HttpResponseRedirect('/vendedores/listado')
            return HttpResponseRedirect(reverse('frontend_listado_vendedores'))
    else:
        form = VendedorForm(instance=object_list)

    c = RequestContext(request, {
        'vendedor': object_list,
        'form': form,
        'message': message,
        'grupo': grupo
    })
    return HttpResponse(t.render(c))

# Funcion para agregar un nuevo vendedor.
def agregar_vendedores(request):
    
    
    if request.user.is_authenticated():
        if verificar_permisos(request.user.id, permisos.ADD_VENDEDOR):
            t = loader.get_template('vendedores/agregar.html')
            #c = RequestContext(request, {})
            #return HttpResponse(t.render(c))
        else:
            t = loader.get_template('index2.html')
            grupo= request.user.groups.get().id
            c = RequestContext(request, {
                'grupo': grupo                                     })
            return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))

    if request.method == 'POST':
        form = VendedorForm(request.POST)
        if form.is_valid():
            form.save()
            # Redireccionamos al listado de lotes luego de agregar el nuevo lote.
            #return HttpResponseRedirect('/vendedores/listado')
            return HttpResponseRedirect(reverse('frontend_listado_vendedores'))
    else:
        form = VendedorForm()

    c = RequestContext(request, {
        'form': form,
    })
    return HttpResponse(t.render(c))
