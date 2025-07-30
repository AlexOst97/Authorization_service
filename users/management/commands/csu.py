from django.core.management import BaseCommand
from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.create(
            phone_number="123456789", first_name="Александр", last_name="Останин"
        )
        user.set_password("123456789")
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
