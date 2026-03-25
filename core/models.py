from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
   email = models.EmailField(unique=True)
   contact = models.CharField(max_length=10, unique=True)

def __str__(self):
        return self.username
    