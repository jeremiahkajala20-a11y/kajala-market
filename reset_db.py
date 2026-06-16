import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kajala.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

# Drop all tables
with connection.cursor() as cursor:
    cursor.execute("DROP TABLE IF EXISTS sqlite_sequence;")
    for table in connection.introspection.table_names():
        cursor.execute(f"DROP TABLE IF EXISTS {table};")

print("Database cleared!")

# Run migrations
call_command('makemigrations')
call_command('migrate')

print("Migrations complete!")

# Create superuser
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='kajala_online').exists():
    User.objects.create_superuser('kajala_online', 'jeremiahkajala20@gmail.com', 'Admin@2024')
    print("Superuser created!")

print("✅ Database reset complete!")