from django.db import models
from django.contrib.auth.models import User
from propar01.settings import PATH_LOGO
from sucursal.models import Sucursal


class Cliente(models.Model):
    cedula = models.CharField(unique=True, max_length=10, blank=False, null=False)
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
            label=self.nombres + ' ' + self.apellidos,
            cedula=self.cedula,
            id=self.id)

    class Meta:
        permissions = (
            ('ver_listado_clientes', 'Ver listado de clientes'),
            ('ver_opciones_cliente', 'Ver opciones de clientes'),
        )


class LogUsuario(models.Model):
    fecha_hora = models.DateTimeField()
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    accion = models.CharField(max_length=255)
    tipo_objeto = models.CharField(max_length=255)
    id_objeto = models.CharField(max_length=255)
    codigo_lote = models.CharField(max_length=255)

    def __unicode__(self):
        return u'%s %s' % (
            self.usuario, self.accion)

    def as_json(self):
        return dict(
            label=self.usuario + ' ' + self.fecha_hora,
            id=self.id)

    class Meta:
        permissions = (
            ('ver_listado_logusuario', 'Ver listado de log de usuarios'),
            ('ver_opciones_logusuario', 'Ver opciones de log de usuarios'),
        )


class Propietario(models.Model):
    nombres = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255, blank=True)
    fecha_nacimiento = models.DateField('fecha de nacimiento', blank=True, null=True)
    fecha_ingreso = models.DateField('fecha de ingreso', blank=True, null=True)
    cedula = models.CharField(unique=True, max_length=10, blank=False, null=False)
    ruc = models.CharField(max_length=255, blank=True, null=True)
    direccion_particular = models.CharField(max_length=255, blank=True)
    telefono_particular = models.CharField(max_length=255, blank=True)
    celular_1 = models.CharField(max_length=255, blank=True)
    celular_2 = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return u'%s %s' % (self.nombres, self.apellidos)

    def as_json(self):
        return dict(
            label=self.nombres + ' ' + self.apellidos,
            cedula=self.cedula,
            id=self.id)

    class Meta:
        permissions = (
            ('ver_listado_propietarios', 'Ver listado de propietarios'),
            ('ver_opciones_propietario', 'Ver opciones de propietarios'),
        )


class ConceptoFactura(models.Model):
    descripcion = models.CharField(max_length=255)
    precio_unitario = models.IntegerField()
    exentas = models.CharField(max_length=255, blank=True)
    iva5 = models.BooleanField(default=False)
    iva10 = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s %s' % self.descripcion

    def as_json(self):
        return dict(
            label=self.descripcion,
            id=self.id)

    class Meta:
        permissions = (
            ('ver_listado_concepto_factura', 'Ver listado de conceptos de factura'),
            ('ver_opciones_concepto_factura', 'Ver opciones de conceptos de factura'),
        )


class PlanDePago(models.Model):
    nombre_del_plan = models.CharField(max_length=255)
    TIPO_CHOICES = (
        ("contado", "Contado"),
        ("credito", "Credito"),
    )
    tipo_de_plan = models.CharField(max_length=7, choices=TIPO_CHOICES)
    cantidad_de_cuotas = models.IntegerField(blank=True, null=True)
    porcentaje_inicial_inmobiliaria = models.FloatField()
    cantidad_cuotas_inmobiliaria = models.IntegerField()
    inicio_cuotas_inmobiliaria = models.IntegerField()
    intervalos_cuotas_inmobiliaria = models.IntegerField()
    porcentaje_cuotas_inmobiliaria = models.FloatField()
    porcentaje_cuotas_administracion = models.FloatField()
    porcentaje_inicial_gerente = models.FloatField()
    cantidad_cuotas_gerente = models.IntegerField()
    inicio_cuotas_gerente = models.IntegerField()
    intervalos_cuotas_gerente = models.IntegerField()
    porcentaje_cuotas_gerente = models.FloatField()
    monto_fijo_cuotas_gerente = models.IntegerField()
    cuotas_de_refuerzo = models.IntegerField()
    intervalo_cuota_refuerzo = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.nombre_del_plan

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
        ordering = ["nombre_del_plan"]


class Fraccion(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)
    propietario = models.ForeignKey(Propietario, on_delete=models.PROTECT)
    cantidad_manzanas = models.IntegerField()
    cantidad_lotes = models.IntegerField()
    distrito = models.CharField(max_length=255, blank=True, null=True)
    finca = models.CharField(max_length=255, blank=True, null=True)
    aprobacion_municipal_nro = models.CharField(max_length=255, blank=True, null=True)
    fecha_aprobacion = models.DateField('fecha de aprobacion', blank=True, null=True)
    superficie_total = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.PROTECT)
    plan_pago = models.ForeignKey(PlanDePago, on_delete=models.PROTECT)

    def __unicode__(self):
        return u'%s' % self.nombre

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
    fraccion = models.ForeignKey(Fraccion, on_delete=models.PROTECT)
    cantidad_lotes = models.IntegerField(null=True)

    def __unicode__(self):
        # return (self.nro_manzana)
        return 'Manzana ' + unicode(self.nro_manzana)

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


class PlanDePagoVendedor(models.Model):
    nombre = models.CharField(max_length=255)
    TIPO_CHOICES = (
        ("contado", "Contado"),
        ("credito", "Credito"),
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    porcentaje_cuota_inicial = models.FloatField()
    cantidad_cuotas = models.IntegerField()
    cuota_inicial = models.IntegerField()
    intervalos = models.IntegerField()
    porcentaje_de_cuotas = models.FloatField()
    observacion = models.CharField(max_length=255)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "plandepagovendedores"
        permissions = (
            ('ver_listado_plandepagovendedores', 'Ver listado de plan de pago vendedores'),
            ('ver_opciones_plandepagovendedor', 'Ver opciones de plan de pago vendedores'),
        )

    def as_json(self):
        return dict(
            label=self.nombre,
            id=self.id)


class Vendedor(models.Model):
    nombres = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    # fecha_nacimiento = models.DateField('fecha de nacimiento')    
    cedula = models.CharField(unique=True, max_length=10, blank=False, null=False)
    # ruc = models.CharField(max_length=255)
    direccion = models.CharField('direccion del vendedor', max_length=255)
    telefono = models.CharField(max_length=255)
    celular_1 = models.CharField(max_length=255, blank=True)
    # celular_2 = models.CharField(max_length=255, blank=True)
    fecha_ingreso = models.DateField('fecha de ingreso')
    sucursal = models.CharField(max_length=255)
    plan_vendedor = models.ForeignKey(PlanDePagoVendedor, on_delete=models.PROTECT)

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
            label=self.nombres + ' ' + self.apellidos,
            cedula=self.cedula,
            id=self.id)


class Cobrador(models.Model):
    nombres = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    # fecha_nacimiento = models.DateField('fecha de nacimiento')    
    cedula = models.CharField(unique=True, max_length=10, blank=False, null=False)
    # ruc = models.CharField(max_length=255)
    direccion = models.CharField('direccion del cobrador', max_length=255)
    telefono_particular = models.CharField(max_length=255)
    celular_1 = models.CharField(max_length=255, blank=True)
    # celular_2 = models.CharField(max_length=255, blank=True)
    fecha_ingreso = models.DateField('fecha de ingreso')

    def __unicode__(self):
        return self.nombres + ' ' + self.apellidos

    class Meta:
        verbose_name_plural = "cobradores"
        permissions = (
            ('ver_listado_cobradores', 'Ver listado de cobradores'),
            ('ver_opciones_cobrador', 'Ver opciones de cobradores'),
        )


class Lote(models.Model):
    codigo_paralot = models.CharField(max_length=20, blank=True, null=True)
    nro_lote = models.IntegerField()
    manzana = models.ForeignKey(Manzana, on_delete=models.PROTECT)
    cuota = models.IntegerField(blank=True)
    precio_contado = models.IntegerField()
    precio_credito = models.IntegerField()
    precio_costo = models.IntegerField()
    superficie = models.DecimalField('superficie (m2)', max_digits=8, decimal_places=2)
    cuenta_corriente_catastral = models.CharField(max_length=255, blank=True)
    boleto_nro = models.CharField(max_length=255, blank=True, null=True)
    comentarios = models.CharField(max_length=255, blank=True, null=True)
    casa_edificada = models.CharField(max_length=255, blank=True, null=True)
    ESTADO_CHOICES = (
        ("1", "Libre"),
        ("2", "Reservado"),
        ("3", "Vendido"),
        ("4", "Recuperado"),
    )
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES)

    def __unicode__(self):
        return unicode(self.codigo_paralot)

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
    class Meta:
        permissions = (
            ('ver_listado_ventas', 'Ver listado de ventas'),
        )

    lote = models.ForeignKey(Lote, on_delete=models.PROTECT)
    fecha_de_venta = models.DateField()
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    vendedor = models.ForeignKey(Vendedor, on_delete=models.PROTECT)
    plan_de_pago = models.ForeignKey(PlanDePago, on_delete=models.PROTECT)
    entrega_inicial = models.BigIntegerField(blank=True, null=True)
    precio_de_cuota = models.BigIntegerField(blank=True, null=True)
    precio_final_de_venta = models.BigIntegerField()
    fecha_primer_vencimiento = models.DateField(blank=True, null=True)
    pagos_realizados = models.IntegerField(blank=True, null=True)
    importacion_paralot = models.BooleanField(blank=False, null=False, default=False)
    plan_de_pago_vendedor = models.ForeignKey(PlanDePagoVendedor, on_delete=models.PROTECT)
    monto_cuota_refuerzo = models.BigIntegerField(blank=True, null=True)
    recuperado = models.BooleanField(blank=False, null=False, default=False)

    def __unicode__(self):
        return u'%s a %s - %s' % (unicode(self.lote), self.cliente.nombres, self.cliente.apellidos)

    def as_json(self):
        return dict(
            venta_id=self.id,
            cliente_id=self.cliente.id,
            cliente=unicode(self.cliente.nombres) + ' ' + self.cliente.apellidos,
            vendedor_id=self.vendedor.id,
            vendedor=unicode(self.vendedor.nombres) + ' ' + self.vendedor.apellidos,
            plan_de_pago_id=self.plan_de_pago.id,
            plan_de_pago=self.plan_de_pago.nombre_del_plan,
            cantidad_cuotas=self.plan_de_pago.cantidad_de_cuotas,
            precio_de_cuota=self.precio_de_cuota,
            entrega_inicial=self.entrega_inicial,
            precio_de_venta=self.precio_final_de_venta,
            pagos_realizados=self.pagos_realizados,
            fecha_de_venta=unicode(self.fecha_de_venta),
            importacion_paralot=unicode(self.importacion_paralot),
            plan_de_pago_vendedor_id=self.plan_de_pago_vendedor.id,
            plan_de_pago_vendedor=self.plan_de_pago_vendedor.nombre,
        )


class Reserva(models.Model):
    lote = models.ForeignKey(Lote, on_delete=models.PROTECT)
    fecha_de_reserva = models.DateField()
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)

    def __unicode__(self):
        return unicode(self.lote) + " a " + self.cliente.nombres + " " + self.cliente.apellidos


class Transaccion(models.Model):
    estado = models.CharField(max_length=30)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    id_transaccion_externa = models.IntegerField()
    updated = models.DateTimeField()


class Timbrado(models.Model):
    desde = models.DateField()
    hasta = models.DateField()
    numero = models.CharField(max_length=30)

    def as_json(self):
        return dict(
            label=self.numero,
            numero=self.numero,
            id=self.id)

    class Meta:
        permissions = (
            ('ver_listado_timbrado', 'Ver listado de Timbrados'),
            ('ver_opciones_timbrado', 'Ver opciones de Timbrados'),
        )


class RangoFactura(models.Model):
    nro_sucursal = models.CharField(max_length=30)
    nro_boca = models.CharField(max_length=30)
    nro_desde = models.CharField(max_length=30)
    nro_hasta = models.CharField(max_length=30)

    def as_json(self):
        return dict(
            label=unicode(self.nro_sucursal + "-" + self.nro_boca),
            nro_sucursal=self.nro_sucursal,
            nro_boca=self.nro_boca,
            nro_desde=self.nro_desde,
            nro_hasta=self.nro_hasta,
            id=self.id)

    class Meta:
        permissions = (
            ('ver_listado_rango_factura', 'Ver listado de Rangos de Facturas'),
            ('ver_opciones_rango_factura', 'Ver opciones de Rangos de Facturas'),
        )


class TimbradoRangoFacturaUsuario(models.Model):
    timbrado = models.ForeignKey(Timbrado, on_delete=models.PROTECT)
    rango_factura = models.ForeignKey(RangoFactura, on_delete=models.PROTECT)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)

    def as_json(self):
        return dict(
            label=unicode(self.nro_sucursal + "-" + self.nro_boca),
            nro_sucursal=self.nro_sucursal,
            nro_boca=self.nro_boca,
            nro_desde=self.nro_desde,
            nro_hasta=self.nro_hasta,
            id=self.id)

    class Meta:
        permissions = (
            ('ver_listado_rango_factura', 'Ver listado de Rangos de Facturas'),
            ('ver_opciones_rango_factura', 'Ver opciones de Rangos de Facturas'),
        )


class Factura(models.Model):
    fecha = models.DateField()
    numero = models.CharField(max_length=30)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    lote = models.ForeignKey(Lote, on_delete=models.PROTECT)
    rango_factura = models.ForeignKey(RangoFactura, on_delete=models.PROTECT)
    tipo = models.CharField(max_length=2)
    detalle = models.TextField()
    anulado = models.BooleanField(default=False)
    observacion = models.TextField()
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    impresa = models.BooleanField(default=False)


class CoordenadasFactura(models.Model):
    # FACTURA 1
    # Timbrado
    # timbrado_1x = models.FloatField()
    # timbrado_1y = models.FloatField()
    # Numero
    numero_1x = models.FloatField()
    numero_1y = models.FloatField()
    # Fecha
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)

    fecha_1x = models.FloatField()
    fecha_1y = models.FloatField()
    # Contado
    contado_1x = models.FloatField()
    contado_1y = models.FloatField()
    # Credito
    credito_1x = models.FloatField()
    credito_1y = models.FloatField()
    # Fraccion
    fraccion_1x = models.FloatField()
    fraccion_1y = models.FloatField()
    # Nombre
    nombre_1x = models.FloatField()
    nombre_1y = models.FloatField()
    # Manzana
    manzana_1x = models.FloatField()
    manzana_1y = models.FloatField()
    # Lote
    lote_1x = models.FloatField()
    lote_1y = models.FloatField()
    # RUC
    ruc_1x = models.FloatField()
    ruc_1y = models.FloatField()
    # Telefono
    telefono_1x = models.FloatField()
    telefono_1y = models.FloatField()
    # Direccion
    direccion_1x = models.FloatField()
    direccion_1y = models.FloatField()
    # Superficie
    superficie_1x = models.FloatField()
    superficie_1y = models.FloatField()
    # Cuenta Corriente Catastral
    cta_cte_ctral_1x = models.FloatField()
    cta_cte_ctral_1y = models.FloatField()
    # Cantidad
    cantidad_1x = models.FloatField()
    cantidad_1y = models.FloatField()
    # Descripcion
    descripcion_1x = models.FloatField()
    descripcion_1y = models.FloatField()
    # Precio Unitario
    precio_1x = models.FloatField()
    precio_1y = models.FloatField()
    # Exentas
    exentas_1x = models.FloatField()
    exentas_1y = models.FloatField()
    # IVA5
    iva5_1x = models.FloatField()
    iva5_1y = models.FloatField()
    # IVA10
    iva10_1x = models.FloatField()
    iva10_1y = models.FloatField()
    # Sub Exentas
    sub_exentas_1x = models.FloatField()
    sub_exentas_1y = models.FloatField()
    # Sub IVA5
    sub_iva5_1x = models.FloatField()
    sub_iva5_1y = models.FloatField()
    # Sub IVA 10
    sub_iva10_1x = models.FloatField()
    sub_iva10_1y = models.FloatField()
    # Total Venta
    total_venta_1x = models.FloatField()
    total_venta_1y = models.FloatField()
    # Total a pagar letras
    total_a_pagar_letra_1x = models.FloatField()
    total_a_pagar_letra_1y = models.FloatField()
    # Total a pagar exentas iva5
    total_a_pagar_exentas_iva5_1x = models.FloatField()
    total_a_pagar_exentas_iva5_1y = models.FloatField()
    # Total a pagar numero
    total_a_pagar_num_1x = models.FloatField()
    total_a_pagar_num_1y = models.FloatField()
    # Liquidacion iva5
    liq_iva5_1x = models.FloatField()
    liq_iva5_1y = models.FloatField()
    # Liquidacion iva10
    liq_iva10_1x = models.FloatField()
    liq_iva10_1y = models.FloatField()
    # Liquidacion total iva
    liq_total_iva_1x = models.FloatField()
    liq_total_iva_1y = models.FloatField()

    # FACTURA 2
    # Timbrado
    # timbrado_2x = models.FloatField()
    # timbrado_2y = models.FloatField()
    # Numero
    numero_2x = models.FloatField()
    numero_2y = models.FloatField()
    # Fecha
    fecha_2x = models.FloatField()
    fecha_2y = models.FloatField()
    # Contado
    contado_2x = models.FloatField()
    contado_2y = models.FloatField()
    # Credito
    credito_2x = models.FloatField()
    credito_2y = models.FloatField()
    # Fraccion
    fraccion_2x = models.FloatField()
    fraccion_2y = models.FloatField()
    # Nombre
    nombre_2x = models.FloatField()
    nombre_2y = models.FloatField()
    # Manzana
    manzana_2x = models.FloatField()
    manzana_2y = models.FloatField()
    # Lote
    lote_2x = models.FloatField()
    lote_2y = models.FloatField()
    # RUC
    ruc_2x = models.FloatField()
    ruc_2y = models.FloatField()
    # Telefono
    telefono_2x = models.FloatField()
    telefono_2y = models.FloatField()
    # Direccion
    direccion_2x = models.FloatField()
    direccion_2y = models.FloatField()
    # Superficie
    superficie_2x = models.FloatField()
    superficie_2y = models.FloatField()
    # Cuenta Corriente Catastral
    cta_cte_ctral_2x = models.FloatField()
    cta_cte_ctral_2y = models.FloatField()
    # Cantidad
    cantidad_2x = models.FloatField()
    cantidad_2y = models.FloatField()
    # Descripcion
    descripcion_2x = models.FloatField()
    descripcion_2y = models.FloatField()
    # Precio Unitario
    precio_2x = models.FloatField()
    precio_2y = models.FloatField()
    # Exentas
    exentas_2x = models.FloatField()
    exentas_2y = models.FloatField()
    # IVA5
    iva5_2x = models.FloatField()
    iva5_2y = models.FloatField()
    # IVA10
    iva10_2x = models.FloatField()
    iva10_2y = models.FloatField()
    # Sub Exentas
    sub_exentas_2x = models.FloatField()
    sub_exentas_2y = models.FloatField()
    # Sub IVA5
    sub_iva5_2x = models.FloatField()
    sub_iva5_2y = models.FloatField()
    # Sub IVA 10
    sub_iva10_2x = models.FloatField()
    sub_iva10_2y = models.FloatField()
    # Total Venta
    total_venta_2x = models.FloatField()
    total_venta_2y = models.FloatField()
    # Total a pagar letras
    total_a_pagar_letra_2x = models.FloatField()
    total_a_pagar_letra_2y = models.FloatField()
    # Total a pagar exentas iva5
    total_a_pagar_exentas_iva5_2x = models.FloatField()
    total_a_pagar_exentas_iva5_2y = models.FloatField()
    # Total a pagar numero
    total_a_pagar_num_2x = models.FloatField()
    total_a_pagar_num_2y = models.FloatField()
    # Liquidacion iva5
    liq_iva5_2x = models.FloatField()
    liq_iva5_2y = models.FloatField()
    # Liquidacion iva10
    liq_iva10_2x = models.FloatField()
    liq_iva10_2y = models.FloatField()
    # Liquidacion total iva
    liq_total_iva_2x = models.FloatField()
    liq_total_iva_2y = models.FloatField()

    # FACTURA 3
    # Timbrado
    # timbrado_3x = models.FloatField()
    # timbrado_3y = models.FloatField()
    # Numero
    numero_3x = models.FloatField()
    numero_3y = models.FloatField()
    # Fecha
    fecha_3x = models.FloatField()
    fecha_3y = models.FloatField()
    # Contado
    contado_3x = models.FloatField()
    contado_3y = models.FloatField()
    # Credito
    credito_3x = models.FloatField()
    credito_3y = models.FloatField()
    # Fraccion
    fraccion_3x = models.FloatField()
    fraccion_3y = models.FloatField()
    # Nombre
    nombre_3x = models.FloatField()
    nombre_3y = models.FloatField()
    # Manzana
    manzana_3x = models.FloatField()
    manzana_3y = models.FloatField()
    # Lote
    lote_3x = models.FloatField()
    lote_3y = models.FloatField()
    # RUC
    ruc_3x = models.FloatField()
    ruc_3y = models.FloatField()
    # Telefono
    telefono_3x = models.FloatField()
    telefono_3y = models.FloatField()
    # Direccion
    direccion_3x = models.FloatField()
    direccion_3y = models.FloatField()
    # Superficie
    superficie_3x = models.FloatField()
    superficie_3y = models.FloatField()
    # Cuenta Corriente Catastral
    cta_cte_ctral_3x = models.FloatField()
    cta_cte_ctral_3y = models.FloatField()
    # Cantidad
    cantidad_3x = models.FloatField()
    cantidad_3y = models.FloatField()
    # Descripcion
    descripcion_3x = models.FloatField()
    descripcion_3y = models.FloatField()
    # Precio Unitario
    precio_3x = models.FloatField()
    precio_3y = models.FloatField()
    # Exentas
    exentas_3x = models.FloatField()
    exentas_3y = models.FloatField()
    # IVA5
    iva5_3x = models.FloatField()
    iva5_3y = models.FloatField()
    # IVA10
    iva10_3x = models.FloatField()
    iva10_3y = models.FloatField()
    # Sub Exentas
    sub_exentas_3x = models.FloatField()
    sub_exentas_3y = models.FloatField()
    # Sub IVA5
    sub_iva5_3x = models.FloatField()
    sub_iva5_3y = models.FloatField()
    # Sub IVA 10
    sub_iva10_3x = models.FloatField()
    sub_iva10_3y = models.FloatField()
    # Total Venta
    total_venta_3x = models.FloatField()
    total_venta_3y = models.FloatField()
    # Total a pagar letras
    total_a_pagar_letra_3x = models.FloatField()
    total_a_pagar_letra_3y = models.FloatField()
    # Total a pagar exentas iva5
    total_a_pagar_exentas_iva5_3x = models.FloatField()
    total_a_pagar_exentas_iva5_3y = models.FloatField()
    # Total a pagar numero
    total_a_pagar_num_3x = models.FloatField()
    total_a_pagar_num_3y = models.FloatField()
    # Liquidacion iva5
    liq_iva5_3x = models.FloatField()
    liq_iva5_3y = models.FloatField()
    # Liquidacion iva10
    liq_iva10_3x = models.FloatField()
    liq_iva10_3y = models.FloatField()
    # Liquidacion total iva
    liq_total_iva_3x = models.FloatField()
    liq_total_iva_3y = models.FloatField()


class PagoDeCuotas(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.PROTECT)
    transaccion = models.ForeignKey(Transaccion, on_delete=models.PROTECT)
    lote = models.ForeignKey(Lote, on_delete=models.PROTECT)
    fecha_de_pago = models.DateField()
    nro_cuotas_a_pagar = models.IntegerField()
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    plan_de_pago = models.ForeignKey(PlanDePago, on_delete=models.PROTECT)
    plan_de_pago_vendedores = models.ForeignKey(PlanDePagoVendedor, on_delete=models.PROTECT)
    vendedor = models.ForeignKey(Vendedor, on_delete=models.PROTECT)
    total_de_cuotas = models.IntegerField()
    total_de_mora = models.IntegerField()
    total_de_pago = models.IntegerField()
    factura = models.ForeignKey(Factura, on_delete=models.PROTECT)
    detalle = models.TextField()
    cuota_obsequio = models.BooleanField(default=False)

    def as_json(self):
        return dict(
            lote=unicode(self.lote),
            fecha_de_pago=unicode(self.fecha_de_pago),
            cliente=u'%s' % self.cliente,
            plan_de_pago=self.plan_de_pago_id,
            plan_de_pago_vendedores=self.plan_de_pago_vendedores_id,
            nro_cuotas_a_pagar=self.nro_cuotas_a_pagar,
            total_de_cuotas=self.total_de_cuotas,

        )

    def __unicode__(self):
        return u'%s - %s' % (self.lote, self.fecha_de_pago)


class TransferenciaDeLotes(models.Model):
    lote = models.ForeignKey(Lote, on_delete=models.PROTECT)
    fecha_de_transferencia = models.DateField()
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    cliente_original = models.ForeignKey(Cliente, related_name='clienteoriginal')
    vendedor = models.ForeignKey(Vendedor, on_delete=models.PROTECT)
    plan_de_pago = models.ForeignKey(PlanDePago, on_delete=models.PROTECT)


class CambioDeLotes(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    fecha_de_cambio = models.DateField()
    lote_a_cambiar = models.ForeignKey(Lote, related_name='loteacambiar')
    lote_nuevo = models.ForeignKey(Lote, on_delete=models.PROTECT)


class RecuperacionDeLotes(models.Model):
    lote = models.ForeignKey(Lote, on_delete=models.PROTECT)
    venta = models.ForeignKey(Venta, on_delete=models.PROTECT)
    fecha_de_recuperacion = models.DateField()
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    vendedor = models.ForeignKey(Vendedor, on_delete=models.PROTECT)
    # plan_de_pago = models.ForeignKey(PlanDePago, on_delete=models.PROTECT)


class LogDeLogos(models.Model):
    nombre_archivo = models.CharField(max_length=80)
    imagen = models.ImageField(upload_to=PATH_LOGO)


class PermisosAdicionales(models.Model):
    class Meta:
        permissions = (
            ('ver_listado_opciones', 'Ver listado de opciones de las acciones'),
            ('ver_informes', 'Ver informes'),
            ('ver_ficha_lote', 'Ver Ficha Lote')
        )


class ConfiguracionIntereses(models.Model):
    codigo_empresa = models.CharField(max_length=4)
    porcentaje_interes_cuota = models.IntegerField()
    gestion_cobranza = models.BooleanField(blank=False, null=False, default=False)
    dias_de_gracia = models.IntegerField()
    cuotas_dias_gracia = models.IntegerField()

class Configuraciones(models.Model):
    id = models.IntegerField(primary_key=True)
    copias_facturas = models.IntegerField()
    tipo_numeracion_manzana = models.CharField(max_length=6)
    codigo_empresa = models.CharField(max_length=4)
    def as_json(self):
        return dict(
            codigo_empresa=self.codigo_empresa,
            tipo_numeracion_manzana=self.tipo_numeracion_manzana,
            copias_facturas=self.copias_facturas,
            id=self.id)