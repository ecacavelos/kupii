# -*- encoding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from principal.models import Lote, Cliente
from tipo_contacto.models import TipoContacto
from motivo_contacto.models import MotivoContacto


class Contacto(models.Model):
    lote = models.ForeignKey(Lote, on_delete=models.PROTECT)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    tipo_contacto = models.ForeignKey(TipoContacto, on_delete=models.PROTECT, related_name='tipo_contacto_id')
    motivo_contacto = models.ForeignKey(MotivoContacto, on_delete=models.PROTECT, related_name='motivo_contacto_id')
    remitente_usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha_contacto = models.DateTimeField()
    numero_direccion_contactado = models.TextField()
    mensaje_enviado = models.TextField()
    proximo_contacto = models.DateTimeField()
    respondido = models.BooleanField(default=False)
    recipiente = models.TextField()
    fecha_respuesta = models.DateTimeField()
    tipo_respuesta = models.ForeignKey(TipoContacto, on_delete=models.PROTECT, related_name='tipo_respuesta_id', null=True, blank=True)
    mensaje_respuesta = models.TextField()
    comentarios_gerencia = models.TextField()

    class Meta:
        db_table = 'contactos'
