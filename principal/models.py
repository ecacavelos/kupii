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
    def as_json(self):
        return dict(
            label=self.nombre,
            id=self.id)

class Manzana(models.Model):
    nro_manzana = models.IntegerField()
    fraccion = models.ForeignKey(Fraccion)   
    cantidad_lotes = models.IntegerField(null=True)
    def __unicode__(self):
        #return (self.nro_manzana)
        return('Manzana ' + str(self.id))
    class Meta:
        verbose_name_plural = "manzanas"
    def as_json(self):
        return dict(
            label=self.nro_manzana,
            id=self.id)
        
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
    porcentaje_cuota_inicial = models.IntegerField()
    cantidad_cuotas = models.IntegerField()
    cuota_inicial = models.IntegerField()
    intervalos = models.IntegerField()
    porcentaje_de_cuotas = models.IntegerField()
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

class PlanDePago(models.Model):
    nombre_del_plan = models.CharField(max_length=255)
    TIPO_CHOICES = (
        ("contado", "Contado"),
        ("credito", "Credito"),
    )
    tipo_de_plan = models.CharField(max_length=7, choices=TIPO_CHOICES)
    cantidad_de_cuotas = models.IntegerField(blank=True, null=True)
    porcentaje_inicial_inmobiliaria = models.IntegerField()
    cantidad_cuotas_inmobiliaria = models.IntegerField()
    inicio_cuotas_inmobiliaria = models.IntegerField()
    intervalos_cuotas_inmobiliaria = models.IntegerField()
    porcentaje_cuotas_inmobiliaria = models.IntegerField()
    porcentaje_cuotas_administracion = models.IntegerField()
    porcentaje_inicial_gerente = models.IntegerField()
    cantidad_cuotas_gerente = models.IntegerField()
    inicio_cuotas_gerente = models.IntegerField()
    intervalos_cuotas_gerente = models.IntegerField()
    porcentaje_cuotas_gerente = models.IntegerField()
    monto_fijo_cuotas_gerente = models.IntegerField()
    def __unicode__(self):
        return (self.nombre_del_plan)
    class Meta:
        verbose_name_plural = "planes de pago"

class Lote(models.Model):
    nro_lote = models.IntegerField()
    manzana = models.ForeignKey(Manzana)
    precio_contado = models.IntegerField()
    precio_credito = models.IntegerField()
    superficie = models.DecimalField('superficie (m2)', max_digits=8, decimal_places=2)
    cuenta_corriente_catastral = models.CharField(max_length=255, blank=True)
    boleto_nro = models.IntegerField(blank=True, null=True)
    ESTADO_CHOICES = (
        ("1", "Libre"),
        ("2", "Reservado"),
        ("3", "Vendido"),
        ("4", "4"),
        ("5", "Recuperado"),
    )
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES)
    def __unicode__(self):
        return (str(self.manzana).zfill(3) + "/" + str(self.id).zfill(4))

class Venta(models.Model):
    lote = models.ForeignKey(Lote)
    fecha_de_venta = models.DateField()
    cliente = models.ForeignKey(Cliente)
    vendedor = models.ForeignKey(Vendedor)
    plan_de_pago = models.ForeignKey(PlanDePago)
    entrega_inicial = models.BigIntegerField(blank=True, null=True)
    precio_de_cuota = models.BigIntegerField(blank=True, null=True)
    precio_final_de_venta = models.BigIntegerField()
    fecha_primer_vencimiento = models.DateField(blank=True, null=True)
    pagos_realizados = models.IntegerField(blank=True, null=True)
    def __unicode__(self):
        return (str(self.lote) + " a " + self.cliente.nombres + " " + self.cliente.apellidos)
    def as_json(self):
        return dict(
            venta_id = self.id,
            cliente_id = self.cliente.id,
            cliente = (str(self.cliente.nombres) + ' ' + (self.cliente.apellidos)),
            vendedor_id = self.vendedor.id,
            vendedor = (str(self.vendedor.nombres) + ' ' + (self.vendedor.apellidos)),
            plan_de_pago_id = self.plan_de_pago.id,
            plan_de_pago = self.plan_de_pago.nombre_del_plan,
            cantidad_cuotas = self.plan_de_pago.cantidad_de_cuotas,
            precio_de_cuota = self.precio_de_cuota,
            pagos_realizados = self.pagos_realizados,
        )
    
class Reserva(models.Model):
    lote = models.ForeignKey(Lote)
    fecha_de_reserva = models.DateField()
    cliente = models.ForeignKey(Cliente)
    def __unicode__(self):
        return (str(self.lote) + " a " + self.cliente.nombres + " " + self.cliente.apellidos)
    
class PagoDeCuotas(models.Model):
    lote = models.ForeignKey(Lote)
    fecha_de_pago = models.DateField()
    nro_cuotas_a_pagar = models.IntegerField()
    cliente = models.ForeignKey(Cliente)
    plan_de_pago = models.ForeignKey(PlanDePago)
    vendedor = models.ForeignKey(Vendedor)
    total_de_cuotas = models.IntegerField()
    total_de_mora = models.IntegerField()
    total_de_pago = models.IntegerField()

    
class TransferenciaDeLotes(models.Model):
    lote = models.ForeignKey(Lote)
    fecha_de_transferencia = models.DateField()
    cliente = models.ForeignKey(Cliente)
    vendedor = models.ForeignKey(Vendedor)
    plan_de_pago = models.ForeignKey(PlanDePago)
    
class CambioDeLotes(models.Model):
    cliente = models.ForeignKey(Cliente)
    lote_a_cambiar = models.ForeignKey(Lote,related_name='loteacambiar')
    lote_nuevo = models.ForeignKey(Lote)
    
class RecuperacionDeLotes(models.Model):
    lote = models.ForeignKey(Lote)
    fecha_de_transferencia = models.DateField()
    cliente = models.ForeignKey(Cliente)
    vendedor = models.ForeignKey(Vendedor)
    