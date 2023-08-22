from django.db import models

NULLABLE = {'blank': True, 'null': True}

class Blog(models.Model):
    blog_title = models.CharField(max_length=150, verbose_name="Заголовок")
    blog_slug=models.CharField(max_length=150,verbose_name='slug', **NULLABLE)
    blog_text = models.TextField(verbose_name='Содержимое', **NULLABLE)
    blog_preview = models.ImageField(upload_to='blogs/', verbose_name='Превью', **NULLABLE)
    blog_creation=models.DateField(auto_now=False, auto_now_add=True, verbose_name='Дата создания',)
    blog_is_active=models.BooleanField(default=True, verbose_name='Опубликовано')
    blog_count=models.IntegerField(default=0, verbose_name='Просмотры')

    def __str__(self):
        return f'{self.blog_title}'

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ('blog_title',)
