from django.contrib.auth.models import User
from django.db import models

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
