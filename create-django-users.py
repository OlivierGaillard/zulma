import json

import django
django.setup()

from django.contrib.auth.models import User


with open('django-users.json') as data_file:    
    django_users = json.load(data_file)

for user_dict in django_users:
    try:
        u = User.objects.get(username=user_dict.get('user'))
        u.set_password(user_dict.get('password'))
        u.save()
    except User.DoesNotExist:
        u = User()
        u.username = user_dict.get('user')
        u.set_password(user_dict.get('password'))
        u.is_superuser = user_dict.get('is_superuser', True)
        u.is_staff = user_dict.get('is_staff', True)
        u.save()

