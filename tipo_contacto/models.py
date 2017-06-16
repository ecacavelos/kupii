from django.db import models


class TipoContacto(models.Model):
    descripcion = models.CharField(max_length=100)

    class Meta:
        db_table = 'tipo_contacto'

    def __unicode__(self):
        return u'%s' % self.descripcion

    def as_json(self):
        return dict(
            label=self.descripcion,
            id=self.id)
