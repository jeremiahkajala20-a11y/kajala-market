from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create superuser if it does not exist'

    def handle(self, *args, **options):
        if not User.objects.filter(username='kajala_online').exists():
            User.objects.create_superuser(
                username='kajala_online',
                email='jeremiahkajala20@gmail.com',
                password='Admin@2024'
            )
            self.stdout.write(self.style.SUCCESS('✅ Superuser created successfully!'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ Superuser already exists.'))