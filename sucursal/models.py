from django.db import models
class Sucursal(models.Model):
    id=models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=30)
    def __unicode__(self):
        return u'%s' % (self.nombre)
    def as_json(self):
        return dict(
            label=self.nombre,
            id=self.id)
