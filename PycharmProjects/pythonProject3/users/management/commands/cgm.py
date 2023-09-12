from django.contrib.auth.models import Group, Permission

g1 = Group.objects.create(name='Manager')
p1, __ = Permission.objects.get_or_create(codename='catalog.add_user')
g1.permissions.add(p1)
