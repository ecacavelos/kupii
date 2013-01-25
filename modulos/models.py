from django.db import models

# Create your models here.
class Cliente(models.Model):    
    nombres = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    fecha_nacimiento = models.DateField('fecha de nacimiento')
    cedula = models.CharField(max_length=8)
    ruc = models.CharField(max_length=255)
    direccion_particular = models.CharField(max_length=255)
    direccion_cobro = models.CharField('direccion de cobro', max_length=255)    
    telefono_particular = models.CharField(max_length=255)
    telefono_laboral = models.CharField(max_length=255, blank=True)
    celular_1 = models.CharField(max_length=255)
    celular_2 = models.CharField(max_length=255, blank=True)
    nombre_conyuge = models.CharField('nombre del conyuge', max_length=255, blank=True)
    def __unicode__(self):
        return (self.nombres + ' ' + self.apellidos)
    
class Fraccion(models.Model):        
    nombre = models.CharField(max_length=255)
    ubicacion = models.CharField(max_length=255)
    propietario = models.ForeignKey(Cliente)
    cantidad_manzanas = models.IntegerField()
    cantidad_lotes = models.IntegerField()
    finca = models.CharField(max_length=255)
    aprobacion_municipal_nro = models.CharField(max_length=255)
    fecha_aprobacion = models.DateField('fecha de aprobacion')
    superficie_total = models.IntegerField()
    def __unicode__(self):
        return (self.nombre + ' - ' + self.ubicacion)
    class Meta:
        verbose_name_plural = "fracciones"
        
class Lote(models.Model):    
    precio_contado = models.IntegerField()
    precio_credito = models.IntegerField()
    precio_costo = models.IntegerField('precio de costo')
    superficie = models.IntegerField('superficie (m2)')
    cuenta_corriente_catastral = models.CharField(max_length=255)
    def __unicode__(self):
        return ('Lote - Cuenta Corriente: ' + str(self.cuenta_corriente_catastral))
    
class Vendedor(models.Model):
    nombres = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    fecha_nacimiento = models.DateField('fecha de nacimiento')
    fecha_ingreso = models.DateField('fecha de ingreso')
    cedula = models.CharField(max_length=8)
    ruc = models.CharField(max_length=255)
    direccion_particular = models.CharField(max_length=255)
    telefono_particular = models.CharField(max_length=255)
    celular_1 = models.CharField(max_length=255)
    celular_2 = models.CharField(max_length=255, blank=True)
    def __unicode__(self):
        return (self.nombres + ' ' + self.apellidos)
    class Meta:
        verbose_name_plural = "vendedores"
