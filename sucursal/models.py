from django.db import models
class Sucursal(models.Model):
    nombre = models.CharField(max_length=30)
    def __unicode__(self):
        return u'%s' % (self.nombre)
