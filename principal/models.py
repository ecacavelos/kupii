from django.db import models

class Cliente(models.Model):    
    cedula = models.CharField(unique=True,max_length=10, blank=False, null=False)
    nombres = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    fecha_nacimiento = models.DateField('fecha de nacimiento')
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
    telefono_particular = models.CharField(max_length=255, blank=True)
    telefono_laboral = models.CharField(max_length=255, blank=True)
    celular_1 = models.CharField(max_length=255)
    celular_2 = models.CharField(max_length=255, blank=True)
    nombre_conyuge = models.CharField('nombre del conyuge', max_length=255, blank=True)
    deuda_contraida = models.BigIntegerField(blank=True, null=True)
    def __unicode__(self):
        return unicode(u'%s %s' % (self.nombres, self.apellidos))
    def as_json(self):
        return dict(
            label= self.nombres + ' ' + self.apellidos,
            cedula= self.cedula,
            id=self.id)
    class Meta:
        permissions = (
            ('ver_listado_clientes', 'Ver listado de clientes'),
            ('ver_opciones_cliente', 'Ver opciones de clientes'),
        )    
    

class Propietario(models.Model):
    nombres = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255, blank=True)
    fecha_nacimiento = models.DateField('fecha de nacimiento',blank=True,null=True)
    fecha_ingreso = models.DateField('fecha de ingreso',blank=True,null=True)
    cedula = models.CharField(unique=True,max_length=10, blank=False, null=False)
    ruc = models.CharField(max_length=255, blank=True,null=True)
    direccion_particular = models.CharField(max_length=255, blank=True)
    telefono_particular = models.CharField(max_length=255, blank=True)
    celular_1 = models.CharField(max_length=255, blank=True)
    celular_2 = models.CharField(max_length=255, blank=True)
    def __unicode__(self):
        return u'%s %s' % (self.nombres, self.apellidos)
    def as_json(self):
        return dict(
            label= self.nombres + ' ' + self.apellidos,
            cedula= self.cedula,
            id=self.id)
    class Meta:
        permissions = (
            ('ver_listado_propietarios', 'Ver listado de propietarios'),
            ('ver_opciones_propietario', 'Ver opciones de propietarios'),
        )

class Fraccion(models.Model):
    id=models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255)
    ubicacion = models.CharField(max_length=255,blank=True,null=True)
    propietario = models.ForeignKey(Propietario,on_delete=models.PROTECT)
    cantidad_manzanas = models.IntegerField()
    cantidad_lotes = models.IntegerField()
    distrito = models.CharField(max_length=255,blank=True,null=True)
    finca = models.CharField(max_length=255, blank=True,null=True)
    aprobacion_municipal_nro = models.CharField(max_length=255, blank=True,null=True)
    fecha_aprobacion = models.DateField('fecha de aprobacion', blank=True, null=True)
    superficie_total = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    def __unicode__(self):
        return u'%s' % (self.nombre)
    class Meta:
        verbose_name_plural = "fracciones"
        permissions = (
            ('ver_listado_fracciones', 'Ver listado de fracciones'),
            ('ver_opciones_fraccion', 'Ver opciones de fracciones'),
        )
    def as_json(self):
        return dict(
            label=self.nombre,
            id=self.id)
        

class Manzana(models.Model):
    nro_manzana = models.IntegerField()
    fraccion = models.ForeignKey(Fraccion,on_delete=models.PROTECT)   
    cantidad_lotes = models.IntegerField(null=True)
    def __unicode__(self):
        #return (self.nro_manzana)
        return('Manzana ' + unicode(self.nro_manzana))
    class Meta:
        verbose_name_plural = "manzanas"
        permissions = (
            ('ver_listado_manzanas', 'Ver listado de manzanas'),
            ('ver_opciones_manzana', 'Ver opciones de manzanas'),
        )
    def as_json(self):
        return dict(
            cantidad=self.cantidad_lotes,        
            fraccion=self.fraccion_id,        
            label=self.nro_manzana, 
            id=self.id)
        
        
class Vendedor(models.Model):
    nombres = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    # fecha_nacimiento = models.DateField('fecha de nacimiento')    
    cedula = models.CharField(unique=True,max_length=10, blank=False, null=False)
    # ruc = models.CharField(max_length=255)
    direccion = models.CharField('direccion del vendedor', max_length=255)
    telefono = models.CharField(max_length=255)
    celular_1 = models.CharField(max_length=255, blank=True)
    # celular_2 = models.CharField(max_length=255, blank=True)
    fecha_ingreso = models.DateField('fecha de ingreso')
    sucursal = models.CharField(max_length=255)
    def __unicode__(self):
        return unicode(u'%s %s' % (self.nombres, self.apellidos))
    class Meta:
        verbose_name_plural = "vendedores"
        permissions = (
            ('ver_listado_vendedores', 'Ver listado de vendedores'),
            ('ver_opciones_vendedor', 'Ver opciones de vendedores'),
        )
    def as_json(self):
        return dict(
            label= self.nombres + ' ' + self.apellidos,
            cedula = self.cedula,
            id=self.id)

class PlanDePagoVendedor(models.Model):
    nombre = models.CharField(max_length=255)
    TIPO_CHOICES = (
        ("contado", "Contado"),
        ("credito", "Credito"),
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    porcentaje_cuota_inicial = models.IntegerField()
    cantidad_cuotas = models.IntegerField()
    cuota_inicial = models.IntegerField()
    intervalos = models.IntegerField()
    porcentaje_de_cuotas = models.IntegerField()
    observacion = models.CharField(max_length=255)
    def __unicode__(self):
        return (self.nombre)
    class Meta:
        verbose_name_plural = "plandepagovendedores"
        permissions = (
            ('ver_listado_plandepagovendedores', 'Ver listado de plan de pago vendedores'),
            ('ver_opciones_plandepagovendedor', 'Ver opciones de plan de pago vendedores'),
        )
    
    def as_json(self):
        return dict(
            label= self.nombre,
            id=self.id)        

class Cobrador(models.Model):
    nombres = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    # fecha_nacimiento = models.DateField('fecha de nacimiento')    
    cedula = models.CharField(unique=True,max_length=10, blank=False, null=False)
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
        permissions = (
            ('ver_listado_cobradores', 'Ver listado de cobradores'),
            ('ver_opciones_cobrador', 'Ver opciones de cobradores'),
        )


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
    cuotas_de_refuerzo = models.IntegerField()
    intervalo_cuota_refuerzo = models.IntegerField(blank=True, null=True)
    def __unicode__(self):
        return (self.nombre_del_plan)
    
    def as_json(self):
        return dict(
            label=self.nombre_del_plan,
            id=self.id)
    
    class Meta:
        verbose_name_plural = "planes de pago"
        permissions = (
            ('ver_listado_plandepago', 'Ver listado de planes de pago'),
            ('ver_opciones_plandepago', 'Ver opciones de planes de pago'),
        )
        
class Lote(models.Model):
    codigo_paralot = models.CharField(max_length=20,blank=True, null=True)
    nro_lote = models.IntegerField()    
    manzana = models.ForeignKey(Manzana,on_delete=models.PROTECT)
    precio_contado = models.IntegerField()
    precio_credito = models.IntegerField()
    precio_costo = models.IntegerField()
    superficie = models.DecimalField('superficie (m2)', max_digits=8, decimal_places=2)
    cuenta_corriente_catastral = models.CharField(max_length=255, blank=True)
    boleto_nro = models.CharField(max_length=255,blank=True, null=True)
    ESTADO_CHOICES = (
        ("1", "Libre"),
        ("2", "Reservado"),
        ("3", "Vendido"),
        ("4", "Recuperado"),
    )
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES)
    def __unicode__(self):
        return (unicode(self.manzana).zfill(3) + "/" + unicode(self.nro_lote).zfill(4))
    
    def as_json(self):
        return dict(
            label=self.nro_lote,
            id=self.nro_lote)
    class Meta:
        permissions = (
            ('ver_listado_lotes', 'Ver listado de lotes'),
            ('ver_opciones_lote', 'Ver opciones de lotes'),
            ('cambio_lote', 'Cambio lotes'),
            ('transferencia_lote', 'Transferir lotes'),
            ('recuperar_lote', 'Recuperar lotes'),
        )

class Venta(models.Model):
    lote = models.ForeignKey(Lote,on_delete=models.PROTECT)
    fecha_de_venta = models.DateField()
    cliente = models.ForeignKey(Cliente,on_delete=models.PROTECT)
    vendedor = models.ForeignKey(Vendedor,on_delete=models.PROTECT)
    plan_de_pago = models.ForeignKey(PlanDePago, on_delete=models.PROTECT)
    entrega_inicial = models.BigIntegerField(blank=True, null=True)
    precio_de_cuota = models.BigIntegerField(blank=True, null=True)
    precio_final_de_venta = models.BigIntegerField()
    fecha_primer_vencimiento = models.DateField(blank=True, null=True)
    pagos_realizados = models.IntegerField(blank=True, null=True)
    importacion_paralot=models.BooleanField(blank=False, null=False)
    plan_de_pago_vendedor=models.ForeignKey(PlanDePagoVendedor,on_delete=models.PROTECT)
    monto_cuota_refuerzo = models.BigIntegerField(blank=True, null=True)
    def __unicode__(self):
        return u'%s a %s - %s' % (unicode(self.lote), self.cliente.nombres, self.cliente.apellidos)    
    def as_json(self):
        return dict(
            venta_id = self.id,
            cliente_id = self.cliente.id,
            cliente = (unicode(self.cliente.nombres) + ' ' + (self.cliente.apellidos)),
            vendedor_id = self.vendedor.id,
            vendedor = (unicode(self.vendedor.nombres) + ' ' + (self.vendedor.apellidos)),
            plan_de_pago_id = self.plan_de_pago.id,
            plan_de_pago = self.plan_de_pago.nombre_del_plan,
            cantidad_cuotas = self.plan_de_pago.cantidad_de_cuotas,
            precio_de_cuota = self.precio_de_cuota,
            entrega_inicial = self.entrega_inicial,
            precio_de_venta = self.precio_final_de_venta,
            pagos_realizados = self.pagos_realizados,
            fecha_de_venta = unicode(self.fecha_de_venta),
            importacion_paralot=unicode(self.importacion_paralot),
            plan_de_pago_vendedor_id = self.plan_de_pago_vendedor.id,
            plan_de_pago_vendedor = self.plan_de_pago_vendedor.nombre,            
        )
        class Meta:
            permissions = (
                ('ver_listado_ventas', 'Ver listado de ventas'),
            )
    
class Reserva(models.Model):
    lote = models.ForeignKey(Lote,on_delete=models.PROTECT)
    fecha_de_reserva = models.DateField()
    cliente = models.ForeignKey(Cliente,on_delete=models.PROTECT)
    def __unicode__(self):
        return (unicode(self.lote) + " a " + self.cliente.nombres + " " + self.cliente.apellidos)
    
class Transaccion(models.Model):
    estado = models.CharField(max_length=30)
    cliente = models.ForeignKey(Cliente,on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True) 

class PagoDeCuotas(models.Model):
    venta = models.ForeignKey(Venta,on_delete=models.PROTECT)
    transaccion = models.ForeignKey(Transaccion,on_delete=models.PROTECT)
    lote = models.ForeignKey(Lote,on_delete=models.PROTECT)
    fecha_de_pago = models.DateField()
    nro_cuotas_a_pagar = models.IntegerField()
    cliente = models.ForeignKey(Cliente,on_delete=models.PROTECT)
    plan_de_pago = models.ForeignKey(PlanDePago, on_delete=models.PROTECT)
    plan_de_pago_vendedores = models.ForeignKey(PlanDePagoVendedor,on_delete=models.PROTECT)
    vendedor = models.ForeignKey(Vendedor,on_delete=models.PROTECT)
    total_de_cuotas = models.IntegerField()
    total_de_mora = models.IntegerField()
    total_de_pago = models.IntegerField()
    def as_json(self):
        return dict(
            lote=unicode(self.lote),
            fecha_de_pago=unicode(self.fecha_de_pago),
            cliente=u'%s' % (self.cliente),
            plan_de_pago=self.plan_de_pago_id,
            plan_de_pago_vendedores=self.plan_de_pago_vendedores_id, 
            nro_cuotas_a_pagar = self.nro_cuotas_a_pagar,
            total_de_cuotas = self.total_de_cuotas,
            
        )
    def __unicode__(self):
        return u'%s - %s' % (self.lote, self.fecha_de_pago)

class TransferenciaDeLotes(models.Model):
    lote = models.ForeignKey(Lote,on_delete=models.PROTECT)
    fecha_de_transferencia = models.DateField()
    cliente = models.ForeignKey(Cliente,on_delete=models.PROTECT)
    cliente_original = models.ForeignKey(Cliente,related_name='clienteoriginal')
    vendedor = models.ForeignKey(Vendedor,on_delete=models.PROTECT)
    plan_de_pago = models.ForeignKey(PlanDePago, on_delete=models.PROTECT)

class CambioDeLotes(models.Model):
    cliente = models.ForeignKey(Cliente,on_delete=models.PROTECT)
    fecha_de_cambio = models.DateField()
    lote_a_cambiar = models.ForeignKey(Lote,related_name='loteacambiar')
    lote_nuevo = models.ForeignKey(Lote,on_delete=models.PROTECT)

class RecuperacionDeLotes(models.Model):
    lote = models.ForeignKey(Lote,on_delete=models.PROTECT)
    venta= models.ForeignKey(Venta,on_delete=models.PROTECT)
    fecha_de_recuperacion = models.DateField()
    cliente = models.ForeignKey(Cliente,on_delete=models.PROTECT)
    vendedor = models.ForeignKey(Vendedor,on_delete=models.PROTECT)
    #plan_de_pago = models.ForeignKey(PlanDePago, on_delete=models.PROTECT)
    
    
class Timbrado(models.Model):
    desde = models.DateField()
    hasta = models.DateField()
    numero = models.CharField(max_length=30)
    def as_json(self):
        return dict(
            label= self.numero,
            numero = self.numero,
            id=self.id)


class Factura(models.Model):
    fecha = models.DateField()
    numero = models.CharField(max_length=30)
    cliente = models.ForeignKey(Cliente,on_delete=models.PROTECT)
    lote = models.ForeignKey(Lote,on_delete=models.PROTECT)
    timbrado = models.ForeignKey(Timbrado,on_delete=models.PROTECT)
    tipo = models.CharField(max_length=2)
    detalle = models.TextField()
    
class PermisosAdicionales(models.Model): 
    class Meta:
        permissions = (
            ('ver_listado_opciones', 'Ver listado de opciones de las acciones'),
            ('ver_informes', 'Ver informes'),
        )
