from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Customer(models.Model):
    username = models.CharField(max_length=255)
    email = models.EmailField()
    password1 = models.CharField(max_length=255)
    password2 = models.CharField(max_length=255)
    image = models.ImageField(upload_to='users', null=True, blank=True)

    def __str__(self):
        return self.username