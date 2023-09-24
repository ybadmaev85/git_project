from django.db import models
from django.utils import timezone

from users.models import User

NULLABLE = {'null': True, 'blank': True}


class Client(models.Model):
    '''
    Модель клиента сервиса
    '''
    fullname = models.CharField(max_length=100, verbose_name='ФИО')
    email = models.EmailField(max_length=254, verbose_name='E-mail')
    comment = models.TextField(verbose_name='Комментарий', **NULLABLE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь сервиса', **NULLABLE)

    def str(self) -> str:
        return f'{self.email}'

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'клиенты'
        unique_together = ('email', 'user')


class MailingRegularity(models.Model):
    '''
    Модель переодичности рассылки
    '''
    name = models.CharField(max_length=50, verbose_name='Переодичность', unique=True)

    def __str__(self) -> str:
        return f'{self.name}'

    class Meta:
        verbose_name = 'переодичность'
        verbose_name_plural = 'переодичности'


class MailingStatus(models.Model):
    '''
    Модель статуса рассылки
    '''
    name = models.CharField(max_length=50, verbose_name='Статус', unique=True)

    def __str__(self) -> str:
        return f'{self.name}'

    class Meta:
        verbose_name = 'статус'
        verbose_name_plural = 'статусы'


class Mailing(models.Model):
    '''
    Модель рассылки
    '''
    title = models.CharField(max_length=80, verbose_name='Тема')
    body = models.TextField(verbose_name='Тело')
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True, **NULLABLE)
    sending_time = models.DateTimeField(default=timezone.now, verbose_name='Время')
    regularity = models.ForeignKey(MailingRegularity, on_delete=models.SET_NULL, verbose_name='Переодичность',
                                   **NULLABLE)
    status = models.ForeignKey(MailingStatus, on_delete=models.CASCADE, verbose_name='Статус', **NULLABLE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь сервиса', **NULLABLE)

    def __str__(self) -> str:
        return f'{self.title}'

    class Meta:
        verbose_name = 'рассылка'
        verbose_name_plural = 'рассылки'


class MailingLogs(models.Model):
    '''
    Модель логов рассылки
    '''
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name='Рассылка')
    attempt_datetime = models.DateTimeField(default=timezone.now, verbose_name='Последняя попытка')
    status = models.BooleanField(default=True, verbose_name='Статус попытки', **NULLABLE)
    server_response = models.TextField(verbose_name='Ответ сервера', default='OK')

    def __str__(self) -> str:
        return f'{self.mailing.title} - {self.status}'

    class Meta:
        verbose_name = 'лог рассылки'
        verbose_name_plural = 'логи рассылки'
