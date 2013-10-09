from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from principal.models import PlanDePago
from parametros.forms import PlanDePagoForm, SearchForm

# Funcion principal del modulo de lotes.
def parametros(request):
    t = loader.get_template('parametros/index.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))

#Funcion del modulo plan de pagos
def plan_de_pago(request):
    t = loader.get_template('parametros/plan_pago/index.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))

#funcion para consultar el listado de todos los planes de pagos
def consultar_plan_de_pago(request):
    t = loader.get_template('parametros/plan_pago/listado.html')
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

    c = RequestContext(request, {
        'object_list': object_list,
        'search_form': search_form,
        'message': message,
    })
    return HttpResponse(t.render(c))

# Funcion para consultar el detalle de un cliente.
def detalle_plan_de_pago(request, plandepago_id):
    t = loader.get_template('parametros/plan_pago/detalle.html')
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
    })
    return HttpResponse(t.render(c))

#funcion para agregar planes de pago
def agregar_plan_de_pago(request):
    t = loader.get_template('parametros/plan_pago/agregar.html')
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

def parametros_generales(request):
    t = loader.get_template('parametros/generales.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))
