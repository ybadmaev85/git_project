from django.core.management import BaseCommand

from catalog.models import Student


class Command(BaseCommand):

    def handle(self, *args, **options):
        student_list = [
            {'last_name': 'Victor', 'first_name': 'Badmaev'},
            {'last_name': 'Ksenia', 'first_name': 'Safonova'},
            {'last_name': 'Anton', 'first_name': 'Smaznov'},
            {'last_name': 'Sofia', 'first_name': 'Makarkina'}
        ]

        # for student_item in student_list:
        #     Student.objects.create(**student_item)

        student_for_create = []
        for student_item in student_list:
            student_for_create.append(
                Student(**student_item)
            )

        Student.objects.bulk_create(student_for_create)