from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from principal.models import Manzana
from manzanas.forms import ManzanaForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Funcion principal del modulo de manzanas.
def manzanas(request):
    
    if request.user.is_authenticated():
        t = loader.get_template('manzanas/index.html')
        c = RequestContext(request, {})
        return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login") 

# Funcion para consultar el listado de todas las manzanas.
def consultar_manzanas(request):
    
    
    if request.user.is_authenticated():
        t = loader.get_template('manzanas/listado.html')
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login") 
    
    object_list = Manzana.objects.all().order_by('id')
    
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

def agregar_lotes_por_manzana(request):
    
    #id_propietario = request.GET['cant_manzanas']
    
    
    if request.user.is_authenticated():
        t = loader.get_template('manzanas/agregar.html')
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login") 
    
    if request.method == 'POST':
        form = ManzanaForm(request.POST)
        if form.is_valid():
            Manzana = form.save()
            
            return HttpResponseRedirect('/manzanas/listado')
    else:
        form = ManzanaForm()

    c = RequestContext(request, {
        'form': form,
    })
    return HttpResponse(t.render(c))

# Funcion para el detalle de una fraccion: edita o borra una fraccion.
def detalle_manzana(request, manzana_id):
     
    
    if request.user.is_authenticated():
        t = loader.get_template('manzanas/detalle.html') 
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login")  
 
    object_list = Manzana.objects.get(pk=manzana_id)
    message = ''
 
    if request.method == 'POST':
        data = request.POST
        if data.get('boton_guardar'):
            form = ManzanaForm(data, instance=object_list)
            if form.is_valid():
                message = "Se actualizaron los datos."
                form.save(commit=False)
                object_list.save()
        elif data.get('boton_borrar'):
            f = Manzana.objects.get(pk=manzana_id)
            f.delete()
            return HttpResponseRedirect('/manzanas/listado')
    else:        
        form = ManzanaForm(instance=object_list)
                 
    c = RequestContext(request, {
        'manzana': object_list,
        'form': form,
        'message': message,
    })
    return HttpResponse(t.render(c))
def listar_busqueda_manzanas(request):
    
    busqueda = request.POST['busqueda']
    
    
    if request.user.is_authenticated():
        t = loader.get_template('manzanas/listado.html') 
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login") 
    
    fraccion,manzana=busqueda.split("/") 
    object_list=Manzana.objects.filter(nro_manzana=int(manzana),fraccion_id=int(fraccion))
        
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