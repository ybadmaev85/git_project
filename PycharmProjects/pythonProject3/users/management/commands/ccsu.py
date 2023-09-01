from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.create(
            email='admin@dota.com',
            first_name='Phantom',
            last_name='Assasin',
            is_superuser=True,
            is_staff=True,
            is_active=True
        )

        user.set_password('qwerty_boy7')
        user.save()