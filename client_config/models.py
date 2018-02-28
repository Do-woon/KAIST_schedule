from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    chat_id = models.IntegerField(primary_key=True, unique=True)
    alarm_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.chat_id) + " : " + self.user.get_full_name()



