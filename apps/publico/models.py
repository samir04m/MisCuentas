from django.db import models

class Token(models.Model):
    token = models.CharField(max_length=100)
    data = models.CharField(max_length=250)
    description = models.CharField(max_length=100, null=True, blank=True)
    active = models.BooleanField(default=True)
