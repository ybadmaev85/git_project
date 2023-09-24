from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    '''
    Класс пользователей сервиса
    '''
    username = None
    email = models.EmailField(max_length=254, verbose_name='e-mail', unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []