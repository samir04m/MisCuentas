# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class Cuenta(models.Model):
    nombre = models.CharField('Nombre de la Cuenta', max_length=30)
    saldo = models.IntegerField('Saldo de cuenta')
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'
        ordering = ['nombre']

    def __str__(self):
        return "{} - {}".format(self.user.username, self.nombre)

class Etiqueta(models.Model):
    nombre = models.CharField('Nombre de la Etiqueta', max_length=50)
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Etiqueta'
        verbose_name_plural = 'Etiquetas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Persona(models.Model):
    nombre = models.CharField('Nombre de la Persona', max_length=90)
    isCreditCard = models.BooleanField('Es tarjeta de credito?', default=False)
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)

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
    info = models.TextField('Informacion', max_length=300)
    fecha = models.DateTimeField('Fecha')
    cuenta = models.ForeignKey(Cuenta, null=True, blank=True, on_delete=models.CASCADE)
    etiqueta = models.ForeignKey(Etiqueta, null=True, blank=True, on_delete=models.CASCADE)
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

class TransaccionPrestamo(models.Model):
    transaccion = models.ForeignKey(Transaccion, null=False, blank=False, on_delete=models.CASCADE)
    prestamo = models.ForeignKey(Prestamo, null=False, blank=False, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Transaccion del prestamo'
        verbose_name_plural = 'Transacciones del prestamo'
        ordering = ['-transaccion__fecha']

    def __str__(self):
        return "{} - Prestamo {} - Transaccion {} - $ {}".format(self.id, self.prestamo.id, self.transaccion.id, self.transaccion.cantidad)