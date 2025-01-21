import os
from django.core.management import call_command
from django.contrib.auth import get_user_model

def create_superuser():
    User = get_user_model()
    username = os.environ.get('SUPERUSER_USERNAME')
    password = os.environ.get('SUPERUSER_PASSWORD')

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, password=password)
        print(f'Superuser {username} created.')
    else:
        print(f'Superuser {username} already exists.')

if __name__ == '__main__':
    create_superuser()
