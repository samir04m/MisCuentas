# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class Cuenta(models.Model):
    nombre = models.CharField('Nombre de la Cuenta', max_length=30)
    saldo = models.IntegerField('Saldo de cuenta')
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    visible = models.BooleanField('Visible', default=True)

    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'
        ordering = ['nombre']

    def __str__(self):
        return "{} - {}".format(self.user.username, self.nombre)

class Etiqueta(models.Model):
    nombre = models.CharField('Nombre de la Etiqueta', max_length=50)
    tipo = models.IntegerField(default=1)
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Etiqueta'
        verbose_name_plural = 'Etiquetas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class SubTag(models.Model):
    nombre = models.CharField(max_length=50)
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    class Meta:
        verbose_name = 'SubTag'
        verbose_name_plural = 'SubTags'
        ordering = ['nombre']
    def __str__(self):
        return self.nombre

class Persona(models.Model):
    nombre = models.CharField('Nombre de la Persona', max_length=90)
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    visible = models.BooleanField('Visible', default=True)

    class Meta:
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Transaccion(models.Model):
    TIPO_CHOICES = [('ingreso', 'Ingreso'),
                    ('egreso', 'Egreso')]
    tipo = models.CharField('Tipo de transaccion', max_length=30, choices=TIPO_CHOICES)
    saldo_anterior = models.IntegerField('Saldo anterior')
    cantidad = models.IntegerField('Cantidad')
    info = models.TextField('Descripción', max_length=300)
    fecha = models.DateTimeField('Fecha')
    estado = models.IntegerField('Estado', default=1) # 0 programada, 1 realizada, 2 realizada agrupada, 3 padre grupo
    cuenta = models.ForeignKey(Cuenta, null=True, blank=True, on_delete=models.CASCADE)
    etiqueta = models.ForeignKey(Etiqueta, null=True, blank=True, on_delete=models.CASCADE)
    subtag = models.ForeignKey(SubTag, null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Transaccion'
        verbose_name_plural = 'Transacciones'
        ordering = ['-fecha']

    def __str__(self):
        cuentaNombre = self.cuenta.nombre if self.cuenta else "(no Cuenta)"
        return "{} - {} {} ${} - {}".format(self.id, self.tipo, cuentaNombre, self.cantidad, self.fecha.strftime("%d/%b/%Y"))

class Prestamo(models.Model):
    TIPO_CHOICES = [('yopresto', 'Yo presto'),
                    ('meprestan','Me prestan')]
    tipo = models.CharField('Tipo de prestamo', max_length=30, choices=TIPO_CHOICES)
    cantidad = models.IntegerField('Cantidad')
    info = models.CharField('Informacion', max_length=200)
    cancelada = models.BooleanField('Cancelada', default=False)
    saldo_pendiente = models.IntegerField('Saldo pendiente')
    fecha = models.DateTimeField('Fecha')
    cuenta = models.ForeignKey(Cuenta, null=True, blank=True, on_delete=models.CASCADE)
    persona = models.ForeignKey(Persona, null=False, blank=False, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Prestamo'
        verbose_name_plural = 'Prestamos'
        ordering = ['-fecha']

    def __str__(self):
        return "{} - {} {} - {}".format(self.id, self.tipo, self.persona.nombre, self.fecha.strftime("%d/%b/%Y"))

    def nombreTipoInvertido(self):
        tipo_dict = dict(self.TIPO_CHOICES)
        tipoContrario = 'yopresto' if self.tipo == 'meprestan' else 'meprestan'
        return tipo_dict.get(tipoContrario, None)


class TransaccionPrestamo(models.Model):
    transaccion = models.ForeignKey(Transaccion, null=False, blank=False, on_delete=models.CASCADE)
    prestamo = models.ForeignKey(Prestamo, null=False, blank=False, on_delete=models.CASCADE)
    tipo = models.IntegerField(default=2) # 1 ingreso/egreso prestamo - 2 pago prestamo

    class Meta:
        verbose_name = 'TransaccionPrestamo'
        verbose_name_plural = 'TransaccionPrestamo'
        ordering = ['-transaccion__fecha']

    def __str__(self):
        return "{} - Prestamo {} - Transaccion {} - $ {}".format(self.id, self.prestamo.id, self.transaccion.id, self.transaccion.cantidad)

class CreditCard(models.Model):
    nombre = models.CharField(max_length=90)
    cupo = models.IntegerField()
    cupoDisponible = models.IntegerField('Cupo disponible')
    diaCorte = models.IntegerField('Dia de corte')
    diaPago = models.IntegerField('Dia de pago')
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    visible = models.BooleanField('Visible', default=True)

    class Meta:
        verbose_name = 'CreditCard'
        verbose_name_plural = 'CreditCards'
        ordering = ['id']

    def __str__(self):
        return self.nombre

    def deuda(self):
        return self.cupo - self.cupoDisponible

class CompraCredito(models.Model):
    creditCard = models.ForeignKey(CreditCard, null=False, blank=False, on_delete=models.CASCADE)
    etiqueta = models.ForeignKey(Etiqueta, null=True, blank=True, on_delete=models.CASCADE)
    valor = models.IntegerField('Valor de la compra')
    cuotas = models.IntegerField('Número de cuotas', default=1)
    info = models.TextField('Informacion', max_length=300)
    deuda = models.IntegerField()
    cancelada = models.BooleanField('Cancelada', default=False)
    fecha = models.DateTimeField('Fecha')

    class Meta:
        verbose_name = 'CompraCredito'
        verbose_name_plural = 'CompraCredito'
        ordering = ['-fecha']

    def __str__(self):
        return "{} {} {}".format(self.creditCard.nombre, self.valor, self.fecha)

class TransaccionPagoCredito(models.Model):
    compraCredito = models.ForeignKey(CompraCredito, null=False, blank=False, on_delete=models.CASCADE)
    transaccion = models.ForeignKey(Transaccion, null=False, blank=False, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'TransaccionPagoCredito'
        verbose_name_plural = 'TransaccionPagoCredito'
        ordering = ['id']

    def __str__(self):
        return "{} - {} | ({})Transaccion".format(self.compraCredito.id, self.compraCredito.creditCard.nombre, self.transaccion.id)

class GrupoTransaccion(models.Model):
    transaccionPadre = models.ForeignKey(Transaccion, null=False, blank=False, on_delete=models.CASCADE, related_name='transacciones_padres')
    transaccionHija = models.ForeignKey(Transaccion, null=False, blank=False, on_delete=models.CASCADE, related_name='transacciones_hijas')
    class Meta:
        verbose_name = 'GrupoTransaccion'
        verbose_name_plural = 'GrupoTransaccion'
    def __str__(self):
        return "{} - {}".format(self.transaccionPadre, self.transaccionHija)

class CompraCreditoPrestamo(models.Model):
    compraCredito = models.ForeignKey(CompraCredito, null=False, blank=False, on_delete=models.CASCADE)
    prestamo = models.ForeignKey(Prestamo, null=False, blank=False, on_delete=models.CASCADE)
    class Meta:
        verbose_name = 'CompraCreditoPrestamo'
        verbose_name_plural = 'CompraCreditoPrestamo'

class SolicitudPagoPrestamo(models.Model):
    valorPago = models.IntegerField()
    info = models.CharField(max_length=250, null=True, blank=True)
    prestamo = models.ForeignKey(Prestamo, null=True, blank=True, on_delete=models.CASCADE)
    cuenta = models.ForeignKey(Cuenta, null=True, blank=True, on_delete=models.CASCADE)
    fechaPago = models.CharField(max_length=250, null=True, blank=True)
    pagoMultiple = models.BooleanField(default=False)
    pagoMultipleTipoPrestamo = models.CharField(max_length=20, null=True, blank=True)
    pagoMultiplePersonaId = models.IntegerField(null=True, blank=True)
    usuarioSolicita = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_solicita')
    usuarioAprueba = models.ForeignKey(User, on_delete=models.CASCADE,  related_name='user_aprueba')
    fechaSolicitud = models.DateTimeField()
    estado = models.IntegerField(default=0) # 0-Creado, 1-Aprobada, 2-Rechazada
    class Meta:
        ordering = ['-fechaSolicitud']
    def __str__(self):
        return "{} - {} - Estado {}".format(self.id, self.usuarioSolicita, self.estado)

class SolicitudCreacionPrestamo(models.Model):
    tipo = models.CharField(max_length=30)
    valor = models.IntegerField()
    info = models.TextField()
    fechaPrestamo = models.CharField(max_length=100, null=True, blank=True)
    cuenta = models.ForeignKey(Cuenta, null=True, blank=True, on_delete=models.CASCADE)
    persona = models.ForeignKey(Persona, null=False, blank=False, on_delete=models.CASCADE)
    usuarioSolicita = models.ForeignKey(User, on_delete=models.CASCADE, related_name='userSolicita')
    usuarioAprueba = models.ForeignKey(User, on_delete=models.CASCADE,  related_name='userAprueba')
    fechaSolicitud = models.DateTimeField()
    estado = models.IntegerField(default=0) # 0-Creado, 1-Aprobada, 2-Rechazada
    class Meta:
        ordering = ['-fechaSolicitud']
    def __str__(self):
        return "{} - {} - Estado {}".format(self.id, self.usuarioSolicita, self.estado)

