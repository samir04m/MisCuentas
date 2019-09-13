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
    cantidad = models.IntegerField('Cantidad')
    info = models.CharField('Informacion', max_length=100, null=True, blank=True)
    fecha = models.DateTimeField('Fecha', auto_now=False, auto_now_add=True)
    cuenta = models.ForeignKey(Cuenta, null=False, blank=False, on_delete=models.CASCADE)
    etiqueta = models.ForeignKey(Etiqueta, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Transaccion'
        verbose_name_plural = 'Transacciones'
        ordering = ['-fecha']

    def __str__(self):
        return self.tipo

class Prestamo(models.Model):
    TIPO_CHOICES = [('yopresto', 'Yo presto'),
                    ('meprestan','Me prestan')]
    tipo = models.CharField('Tipo de prestamo', max_length=30, choices=TIPO_CHOICES)
    cantidad = models.IntegerField('Cantidad')
    info = models.CharField('Informacion', max_length=100, null=True, blank=True)
    cancelada = models.BooleanField('Cancelada', default=False)
    fecha = models.DateTimeField('Fecha', auto_now=False, auto_now_add=True)
    cuenta = models.ForeignKey(Cuenta, null=False, blank=False, on_delete=models.CASCADE)
    persona = models.ForeignKey(Persona, null=False, blank=False, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Prestamo'
        verbose_name_plural = 'Prestamos'
        ordering = ['-fecha']

    def __str__(self):
        return self.tipo
