# Generated by Django 4.2.4 on 2023-08-16 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailing',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, null=True, unique=True),
        ),
    ]