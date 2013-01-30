from django.http import HttpResponse
from django.template import RequestContext, loader

# vista principal de la plataforma PROPAR
def index(request):    
    t = loader.get_template('index.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))