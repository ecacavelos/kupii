from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from principal.models import Propietario,Fraccion, Manzana, Lote
from fracciones.forms import FraccionForm, FraccionFormAdd
from django.db import reset_queries, close_connection
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse, resolve

# Funcion principal del modulo de fracciones.
def fracciones(request):
    
    
    if request.user.is_authenticated():
        t = loader.get_template('fracciones/index.html')
        c = RequestContext(request, {})
        return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))

# Funcion para consultar el listado de todas las fracciones.
def consultar_fracciones(request):
    
    
    if request.user.is_authenticated():
        t = loader.get_template('fracciones/listado.html')
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))
    
    object_list = Fraccion.objects.all().order_by('id')
    
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

# Funcion para el detalle de una fraccion: edita o borra una fraccion.
def detalle_fraccion(request, fraccion_id):
    close_connection()
    reset_queries()
    
    
    if request.user.is_authenticated():
        t = loader.get_template('fracciones/detalle.html')
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))    

    object_list = Fraccion.objects.get(pk=fraccion_id)
    message = ''

    if request.method == 'POST':
        data = request.POST
        if data.get('boton_guardar'):
            form = FraccionFormAdd(data, instance=object_list)
            if form.is_valid():
                message = "Se actualizaron los datos."
                form.save(commit=False)
                object_list.save()
                #return HttpResponseRedirect('/fracciones/listado')
            else:
                message = "No se pudo actualizar los datos."
                    
        elif data.get('boton_borrar'):
            f = Fraccion.objects.get(pk=fraccion_id)
            cantidad_manzanas = f.cantidad_manzanas
            cantidad_lotes = f.cantidad_lotes
            
            
      
            for i in range(1, cantidad_manzanas + 1):
                #m = Manzana.objects.get(nro_manzana=i, fraccion=fraccion_id)
                m = Manzana.objects.filter(nro_manzana=i, fraccion=fraccion_id)
                m_list= list(m)
                #m = Manzana.objects.raw('SELECT id FROM principal_lote WHERE (nro_manzana = '+unicode(i)+' AND fraccion_id = '+unicode(f.id)+')')
                manzana_id = m[0].id
                
                for j in range(1, cantidad_lotes + 1):
                    l = Lote.objects.filter(manzana_id=manzana_id, nro_lote=j)
                    l.delete()                
                m.delete()
            f.delete()
            return HttpResponseRedirect('/fracciones/listado')        
        
    else:        
        form = FraccionForm(instance=object_list)
                
    c = RequestContext(request, {
        'fraccion': object_list,
        'form': form,
        'message': message,
    })
    return HttpResponse(t.render(c))

# Funcion para agregar una nueva fraccion.
def agregar_fracciones(request):
    
    
    if request.user.is_authenticated():
        t = loader.get_template('fracciones/agregar2.html')
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login'))   

    if request.method == 'POST':
        form = FraccionForm(request.POST)
        lotes_por_manzana = request.POST['lotes_por_manzana']
        lotes_por_manzana = lotes_por_manzana.split(",")
        if form.is_valid():
            fraccion = form.save()
            cantidad_manzanas = fraccion.cantidad_manzanas
            # cantidad_lotes = fraccion.cantidad_lotes
            for i in range(1, cantidad_manzanas + 1):
                manzana = Manzana()
                manzana.fraccion = fraccion
                manzana.nro_manzana = i
                manzana.cantidad_lotes = lotes_por_manzana[i - 1]
                manzana.save()
            # Agregar las cantidad_manzanas que correspondan
            # total_manzanas = form.
            # while 
            # Redireccionamos al listado de clientes luego de agregar el nuevo cliente.
            return HttpResponseRedirect('/fracciones/listado')
    else:
        form = FraccionForm()

    c = RequestContext(request, {
        'form': form,
    })
    return HttpResponse(t.render(c))
def listar_busqueda_fracciones(request):
    
    busqueda = request.POST['busqueda']
    tipo_busqueda = request.POST['tipo_busqueda']
    object_list=[]
    
    
    if request.user.is_authenticated():
        t = loader.get_template('fracciones/listado.html')
        #c = RequestContext(request, {})
        #return HttpResponse(t.render(c))
    else:
        return HttpResponseRedirect(reverse('login')) 
        
    if tipo_busqueda == "numero":
        
        object_list = Fraccion.objects.filter(pk=busqueda)
    
    if tipo_busqueda == "propietario":
        propietario_list = Propietario.objects.filter(nombres__icontains=busqueda)
        for prop in propietario_list:
            query = Fraccion.objects.filter(propietario_id=prop.id)
            if query:
                for f in query:
                    object_list.append(f)
       
        
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