from django.contrib.auth.models import User
from django.db import models
from apps.contabilidad.models import Persona

class UserSetting(models.Model):
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    class Meta:
        verbose_name = 'UserSetting'
        verbose_name_plural = 'UserSettings'
        ordering = ['id']

    def __str__(self):
        return "{} {} {}".format(self.key, self.value, self.user)

class UserPersona(models.Model):
    admin = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE, related_name='user_admin')
    persona = models.ForeignKey(Persona, null=False, blank=False, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE, related_name='user_persona')
    def __str__(self):
        return "{} -> {} ({})".format(self.admin, self.user, self.persona)

class UserNotification(models.Model):
    message = models.TextField()
    date = models.DateTimeField()
    read = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.TextField(default=0) # 0-NoClasificado, 1-PagoPrestamo
    class Meta:
        ordering = ['-date']
