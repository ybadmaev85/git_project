from django.db import models

from mailings.models import NULLABLE

from PIL import Image


class Article(models.Model):
    '''
    Модель статьи блога
    '''
    title = models.CharField(max_length=100, verbose_name='Заголовок')
    body = models.TextField('Содержимое')
    image = models.ImageField(upload_to='blog/', verbose_name='Изображение')
    view_count = models.PositiveIntegerField(verbose_name='Кол-во просмотров', default=0, **NULLABLE)
    publish_date = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name='Дата публикации', **NULLABLE)

    def __str__(self) -> str:
        return f'{self.title}'

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)
        max_size = (1200, 800)

        # сжимает изображения до 1200x800
        if img.width != max_size[0] or img.height != max_size[1]:
            resized_image = img.resize(max_size)
            resized_image.save(self.image.path)

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
