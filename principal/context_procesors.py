from principal.models import LogDeLogos
from propar01.configuraciones import PATH_LOGO


def objeto_logo(request):
    objeto_logo_seleccionado = {'nombre_de_archivo': ''}
    try:
        objeto_logo_seleccionado = LogDeLogos.objects.get(seleccionado=True)
    except:
        print 'todavia no hay un logo seleccionado'
    return {'objeto_logo': objeto_logo_seleccionado,
            'path_logo': PATH_LOGO,
            }


#register.assignment_tag(objeto_logo)
