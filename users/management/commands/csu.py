from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    '''
    Команда для создания администратора сервиса
    '''
    def handle(self, *args, **options) -> None:
        try:
            user = User.objects.create(
                email='admin@yandex.ru',
                first_name='admin',
                last_name='admin',
                is_staff=True,
                is_superuser=True,
            )

            user.set_password('admin')
            user.save()
        except:
            self.stderr.write('Ошибка создания администратора!')
