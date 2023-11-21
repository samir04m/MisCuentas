from django.db import models

class Token(models.Model):
    token = models.CharField(max_length=100)
    data = models.CharField(max_length=250)
    active = models.BooleanField(default=True)
