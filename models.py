from django.db import models
NULLABLE = {'blank': True, 'null': True}


class Category(models.Model):
    name = models.CharField(max_length=30, verbose_name='Порода')
    description = models.TextField(**NULLABLE, verbose_name='Описание')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'порода'
        verbose_name_plural = 'породы'

class Dog(models.Model):
    name = models.CharField(max_length=50, verbose_name='Кличка')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Порода')
    photo = models.ImageField(upload_to='dogs/', **NULLABLE, verbose_name='Фото')
    birth_day = models.DateField(**NULLABLE, verbose_name='Дата рождения')

    def __str__(self):
        return f'{self.name}({self.category})'

    class Meta:
        verbose_name = 'собака'
        verbose_name_plural = 'собаки'
