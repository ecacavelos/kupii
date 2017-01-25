from django.db import models


class Configuraciones(models.Model):
    id = models.IntegerField(primary_key=True)
    copias_facturas = models.IntegerField()
    tipo_numeracion_manzana = models.CharField(max_length=6)
    codigo_empresa = models.CharField(max_length=4)
    tamanho_letra = models.FloatField()
    def as_json(self):
        return dict(
            codigo_empresa=self.codigo_empresa,
            tipo_numeracion_manzana=self.tipo_numeracion_manzana,
            copias_facturas=self.copias_facturas,
            id=self.id)
