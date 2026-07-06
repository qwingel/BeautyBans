from django.core.management.base import BaseCommand
from django.utils import timezone
from punishments.models import Punishment


class Command(BaseCommand):
    help = 'Автоматически снимает истёкшие наказания'

    def handle(self, *args, **options):
        # Находим все активные наказания с истёкшим сроком
        now = timezone.now()
        expired = Punishment.objects.filter(
            is_active=True,
            expires_at__isnull=False,
            expires_at__lte=now
        )

        count = 0
        for punishment in expired:
            punishment.is_active = False
            punishment.unban_reason = 'Истёк срок наказания'
            punishment.save()
            count += 1

        if count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Снято наказаний: {count}')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Нет истёкших наказаний')
            )
