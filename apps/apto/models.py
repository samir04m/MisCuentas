from django.db import models
from django.contrib.auth.models import User

class Apartamento(models.Model):
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return "{}".format(self.nombre)

class Pagador(models.Model):
    apto = models.ForeignKey(Apartamento, null=False, blank=False, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    def __str__(self):
        return "{}".format(self.user.username)

class Persona(models.Model):
    nombre = models.CharField(max_length=50)
    pagador = models.ForeignKey(Pagador, null=False, blank=False, on_delete=models.CASCADE)
    def __str__(self):
        return "{}".format(self.nombre)

class Estadia(models.Model):
    fechaInicio = models.CharField(max_length=100)
    fechaFin = models.CharField(max_length=100)
    persona = models.ForeignKey(Persona, null=False, blank=False, on_delete=models.CASCADE)
    def __str__(self):
        return "{} - {} | {}".format(self.fechaInicio, self.fechaFin, self.persona.nombre)

class Empresa(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return "{}".format(self.nombre)

class Recibo(models.Model):
    periodo = models.CharField(max_length=50)
    valorPago = models.IntegerField()
    fechaInicio = models.CharField(max_length=100)
    fechaFin = models.CharField(max_length=100)
    diasFacturados = models.IntegerField()
    empresa = models.ForeignKey(Empresa, null=False, blank=False, on_delete=models.CASCADE)
    apto = models.ForeignKey(Apartamento, null=False, blank=False, on_delete=models.CASCADE)
    class Meta:
        ordering = ['-periodo']

class PagadorRecibo(models.Model):
    valorPago = models.IntegerField()
    pagador = models.ForeignKey(Pagador, null=False, blank=False, on_delete=models.CASCADE)
    recibo = models.ForeignKey(Recibo, null=False, blank=False, on_delete=models.CASCADE)