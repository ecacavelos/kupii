from django.http import HttpResponse
from django.template import RequestContext, loader
from modulos.models import Cliente
from modulos.forms import SearchForm, ClienteForm, ClienteFormSet

def index(request):    
    t = loader.get_template('clientes/index.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))

def modulo_clientes(request):
    t = loader.get_template('clientes/clientes.html')    
    
    if request.method == 'POST':
        data = request.POST
        message = data.get('search_string','')
        object_list = Cliente.objects.filter(nombres=message)
        search_form = SearchForm(request.POST)
    else:
        message = "0"
        object_list = Cliente.objects.all()
        search_form = SearchForm()

    c = RequestContext(request, {
        'message': message,
        'object_list': object_list,
        'search_form': search_form,
    })
    return HttpResponse(t.render(c))
