#!/usr/bin/env python
import os
import sys
from django.core.management import execute_from_command_line

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kajala.settings')
    
    # Create superuser automatically if it doesn't exist
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(username='kajala_online').exists():
        User.objects.create_superuser('kajala_online', 'jeremiahkajala20@gmail.com', 'Admin@2024')
        print("✅ Superuser 'kajala_online' created automatically!")
    
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()