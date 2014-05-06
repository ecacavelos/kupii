from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from principal.models import Lote, Fraccion, Manzana
from lotes.forms import LoteForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Funcion principal del modulo de lotes.
def informes(request):
    
    if request.user.is_authenticated():
        t = loader.get_template('informes/index.html')
        c = RequestContext(request, {})
        return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login") 

def lotes_libres(request):
    
    
    if request.user.is_authenticated():
        t = loader.get_template('informes/lotes_libres.html')
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login") 
    
    object_list = Lote.objects.filter(estado="1").order_by('manzana', 'nro_lote')
    
    total_lotes = object_list.count()
    m=[]
    f=[]
    
    for i in range(0, total_lotes): 
        manzana_id = object_list[i].manzana_id
        m.append(Manzana.objects.get(pk = manzana_id))
        
        #setattr(object_list[i], 'nro_manzana', m.nro_manzana)
        fraccion_id = m[i].fraccion_id
        f.append(Fraccion.objects.get(pk = fraccion_id))
        #setattr(object_list[i], 'fraccion', fraccion_id)
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
        'manzana': m,
        'fraccion': f,
        
    })
    return HttpResponse(t.render(c))

def listar_busqueda_lotes(request):
    
    busqueda = request.POST['busqueda']
    
    if request.user.is_authenticated():
        t = loader.get_template('informes/lotes_libres.html')
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect("/login") 
    
    x=str(busqueda)
    fraccion_int = int(x[0:3])
    manzana_int =int(x[4:7])
    lote_int = int(x[8:])
    myfraccion = Fraccion.objects.filter(id=fraccion_int)
    fraccion_manzanas = Manzana.objects.filter(fraccion=myfraccion)
    for manzana in fraccion_manzanas:
        if manzana.nro_manzana == manzana_int:
            mymanzana = manzana
        
    object_list = Lote.objects.filter(manzana_id=mymanzana.id, nro_lote=lote_int, estado="1")
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
        'manzana': fraccion_manzanas,
        'fraccion': myfraccion,
        
    })
    return HttpResponse(t.render(c))
