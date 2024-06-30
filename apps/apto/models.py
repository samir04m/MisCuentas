from django.db import models
from django.contrib.auth.models import User
from apps.contabilidad.models import Prestamo, Persona

class Apartamento(models.Model):
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return "{}".format(self.nombre)

class Pagador(models.Model):
    apto = models.ForeignKey(Apartamento, null=False, blank=False, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    def __str__(self):
        return "{}".format(self.user.username)

class PersonaPagador(models.Model):
    nombre = models.CharField(max_length=50)
    pagador = models.ForeignKey(Pagador, null=False, blank=False, on_delete=models.CASCADE)
    def __str__(self):
        return "{}".format(self.nombre)

class Estadia(models.Model):
    fechaInicio = models.CharField(max_length=100)
    fechaFin = models.CharField(max_length=100)
    persona = models.ForeignKey(PersonaPagador, null=False, blank=False, on_delete=models.CASCADE)
    def __str__(self):
        return "{} - {} | {}".format(self.fechaInicio, self.fechaFin, self.persona.nombre)

class Empresa(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return "{}".format(self.nombre)

class Periodo(models.Model):
    nombre = models.CharField(max_length=20)
    class Meta:
        ordering = ['-nombre']
    def __str__(self):
        return "{}".format(self.nombre)

class Recibo(models.Model):
    valorPago = models.IntegerField()
    fechaInicio = models.CharField(max_length=100)
    fechaFin = models.CharField(max_length=100)
    diasFacturados = models.IntegerField()
    periodo = models.ForeignKey(Periodo, null=False, blank=False, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, null=False, blank=False, on_delete=models.CASCADE)
    apto = models.ForeignKey(Apartamento, null=False, blank=False, on_delete=models.CASCADE)
    class Meta:
        ordering = ['-periodo']
    def __str__(self):
        return "{} [{}] ${}".format(self.empresa, self.periodo, self.valorPago)

class PagadorRecibo(models.Model):
    valorPago = models.IntegerField()
    pagador = models.ForeignKey(Pagador, null=False, blank=False, on_delete=models.CASCADE)
    recibo = models.ForeignKey(Recibo, null=False, blank=False, on_delete=models.CASCADE)
    def __str__(self):
        return "{} ({} {}) -> ${}".format(self.pagador.user.username, self.recibo.empresa.nombre, self.recibo.periodo, self.valorPago )

class PeriodoPrestamoPersona(models.Model):
    periodo = models.ForeignKey(Periodo, null=False, blank=False, on_delete=models.CASCADE)
    prestamo = models.ForeignKey(Prestamo, null=False, blank=False, on_delete=models.CASCADE)
    persona = models.ForeignKey(Persona, null=False, blank=False, on_delete=models.CASCADE)
