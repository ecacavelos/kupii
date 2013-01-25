from django.http import HttpResponse
# Create your views here.
from django.template import Context, RequestContext, loader
from modulos.models import Cliente

def index(request):
    object_list = Cliente.objects.all()
    t = loader.get_template('clientes/index.html')
    c = RequestContext(request, {
        'object_list': object_list,
    })
    return HttpResponse(t.render(c))