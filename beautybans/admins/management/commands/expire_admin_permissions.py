from django.core.management.base import BaseCommand
from django.utils import timezone
from admins.models import AdminServer


class Command(BaseCommand):
    help = 'Автоматически удаляет истёкшие права администраторов'

    def handle(self, *args, **options):
        # Находим все права с истёкшим сроком
        now = timezone.now()
        expired = AdminServer.objects.filter(
            expires_at__isnull=False,
            expires_at__lte=now
        )

        count = expired.count()
        if count > 0:
            expired.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Удалено истёкших прав: {count}')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Нет истёкших прав администраторов')
            )
