from django.db import models

class Cliente(models.Model):
    nombres = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    fecha_nacimiento = models.DateField('fecha de nacimiento')
    cedula = models.CharField(max_length=8)
    ruc = models.CharField(max_length=255)
    SEXO_CHOICES = (
        ("M", "Masculino"),
        ("F", "Femenino"),
    )
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    ESTADOCIVIL_CHOICES = (
        ("S", "Soltero(a)"),
        ("C", "Casado(a)"),
        ("V", "Viudo(a)"),
    )
    estado_civil = models.CharField(max_length=1, choices=ESTADOCIVIL_CHOICES)
    direccion_particular = models.CharField(max_length=255)
    direccion_cobro = models.CharField('direccion de cobro', max_length=255)    
    telefono_particular = models.CharField(max_length=255)
    telefono_laboral = models.CharField(max_length=255, blank=True)
    celular_1 = models.CharField(max_length=255)
    celular_2 = models.CharField(max_length=255, blank=True)
    nombre_conyuge = models.CharField('nombre del conyuge', max_length=255, blank=True)
    deuda_contraida = models.BigIntegerField(blank=True, null=True)
    def __unicode__(self):
        return (str(self.nombres) + ' ' + str(self.apellidos))

class Propietario(models.Model):
    nombres = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255, blank=True)
    fecha_nacimiento = models.DateField('fecha de nacimiento', blank=True, null=True)
    fecha_ingreso = models.DateField('fecha de ingreso')
    cedula = models.CharField(max_length=8, blank=True)
    ruc = models.CharField(max_length=255, blank=True)
    direccion_particular = models.CharField(max_length=255, blank=True)
    telefono_particular = models.CharField(max_length=255, blank=True)
    celular_1 = models.CharField(max_length=255, blank=True)
    celular_2 = models.CharField(max_length=255, blank=True)
    def __unicode__(self):
        return (self.nombres + ' ' + self.apellidos)

class Fraccion(models.Model):
    nombre = models.CharField(max_length=255)
    ubicacion = models.CharField(max_length=255)
    propietario = models.ForeignKey(Propietario)
    cantidad_manzanas = models.IntegerField()
    cantidad_lotes = models.IntegerField()
    distrito = models.CharField(max_length=255)
    finca = models.CharField(max_length=255, blank=True)
    aprobacion_municipal_nro = models.CharField(max_length=255, blank=True)
    fecha_aprobacion = models.DateField('fecha de aprobacion', blank=True, null=True)
    superficie_total = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    def __unicode__(self):
        return (self.nombre)
    class Meta:
        verbose_name_plural = "fracciones"
    
class Vendedor(models.Model):
    nombres = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    # fecha_nacimiento = models.DateField('fecha de nacimiento')    
    cedula = models.CharField(max_length=8)
    # ruc = models.CharField(max_length=255)
    direccion = models.CharField('direccion del vendedor', max_length=255)
    telefono = models.CharField(max_length=255)
    celular_1 = models.CharField(max_length=255, blank=True)
    # celular_2 = models.CharField(max_length=255, blank=True)
    fecha_ingreso = models.DateField('fecha de ingreso')
    def __unicode__(self):
        return (self.nombres + ' ' + self.apellidos)
    class Meta:
        verbose_name_plural = "vendedores"

class Cobrador(models.Model):
    nombres = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    # fecha_nacimiento = models.DateField('fecha de nacimiento')    
    cedula = models.CharField(max_length=8, blank=True)
    # ruc = models.CharField(max_length=255)
    direccion = models.CharField('direccion del cobrador', max_length=255)
    telefono_particular = models.CharField(max_length=255)
    celular_1 = models.CharField(max_length=255, blank=True)
    # celular_2 = models.CharField(max_length=255, blank=True)
    fecha_ingreso = models.DateField('fecha de ingreso')
    def __unicode__(self):
        return (self.nombres + ' ' + self.apellidos)
    class Meta:
        verbose_name_plural = "cobradores"

class PlanDeVendedores(models.Model):
    nombre_del_plan = models.CharField(max_length=255)
    def __unicode__(self):
        return (self.nombre_del_plan)
    class Meta:
        verbose_name_plural = "planes de vendedores"

class PlanDePagos(models.Model):
    nombre_del_plan = models.CharField(max_length=255)
    tipo_de_plan = models.BooleanField('Plan a Credito')
    cantidad_de_cuotas = models.IntegerField(blank=True, null=True)
    def __unicode__(self):
        return (self.nombre_del_plan)
    class Meta:
        verbose_name_plural = "planes de pagos"
        
class Lote(models.Model):
    fraccion = models.ForeignKey(Fraccion)
    manzana = models.IntegerField()
    nro_lote = models.IntegerField()
    precio_contado = models.IntegerField()
    precio_credito = models.IntegerField()
    precio_de_cuota = models.IntegerField()
    superficie = models.DecimalField('superficie (m2)', max_digits=8, decimal_places=2)
    cuenta_corriente_catastral = models.CharField(max_length=255, blank=True)
    boleto_nro = models.IntegerField(blank=True, null=True)
    ESTADO_CHOICES = (
        ("1", "Libre"),
        ("2", "2"),
        ("3", "Vendido"),
        ("4", "4"),
        ("5", "Recuperado"),
    )
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES)    
    def __unicode__(self):
        return (str(self.fraccion.id).zfill(3) + "/" + str(self.manzana).zfill(3) + "/" + str(self.nro_lote).zfill(4))
    class Meta:
        unique_together = (("fraccion", "manzana", "nro_lote"),)

class Venta(models.Model):
    lote = models.ForeignKey(Lote)
    fecha_de_venta = models.DateField()
    cliente = models.ForeignKey(Cliente)
    vendedor = models.ForeignKey(Vendedor)
    plan_de_vendedor = models.ForeignKey(PlanDeVendedores)
    plan_de_pago = models.ForeignKey(PlanDePagos)
    entrega_inicial = models.BigIntegerField()
    precio_de_cuota = models.BigIntegerField()
    cuota_de_refuerzo = models.BigIntegerField()
    precio_final_de_venta = models.BigIntegerField()
    fecha_primer_vencimiento = models.DateField()
    pagos_realizados = models.IntegerField(blank=True, null=True)
    def __unicode__(self):
        return (str(self.lote) + " a " + self.cliente.nombres + " " + self.cliente.apellidos)
