from django.db import models

NULLABLE = {'blank': True, 'null': True}


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='Наименование')
    description = models.TextField(max_length=150, verbose_name='Описание')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Product(models.Model):
    name = models.CharField(max_length=50, verbose_name='Наименование')
    description = models.TextField(max_length= 150, verbose_name='Описание')
    photo = models.ImageField(upload_to='products/', **NULLABLE, verbose_name='Изображение')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    price = models.IntegerField(**NULLABLE, verbose_name='Цена за покупку')
    creation = models.DateField(**NULLABLE, verbose_name='Дата создания')
    last_change = models.DateField(**NULLABLE, verbose_name='Дата последнего изменения')

    def __str__(self):
        return f'{self.name} ({self.category})'

    class Meta:
        verbose_name = 'продукт'
        verbose_name_plural = 'продукты'
        ordering = ('name',)


class Version(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Наименование')
    num = models.IntegerField(**NULLABLE, verbose_name='Номер версии')
    name = models.CharField(max_length=50, verbose_name='Название версии')
    is_active = models.BooleanField(default=True, verbose_name='Текущая версия')

    def __str__(self):
        return f'{self.product} ({self.name})'

    class Meta:
        verbose_name = 'версия'
        verbose_name_plural = 'версии'
