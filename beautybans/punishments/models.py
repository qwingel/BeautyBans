from django.db import models
from django.utils import timezone
from servers.models import Server
from admins.models import Admin


class Punishment(models.Model):
    PUNISHMENT_TYPES = [
        ('ban', 'Бан'),
        ('mute', 'Мут'),
        ('gag', 'Гаг'),
    ]

    punishment_type = models.CharField(max_length=8, choices=PUNISHMENT_TYPES)
    target_steam_id = models.CharField(max_length=64)
    target_name = models.CharField(max_length=64)
    target_ip = models.GenericIPAddressField(null=True, blank=True, help_text='IP адрес игрока')
    ban_subnet = models.BooleanField(default=False, help_text='Банить всю подсеть')
    reason = models.TextField()
    admin = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True, blank=True, related_name='punishments_issued')
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='punishments')
    duration = models.IntegerField(help_text='Длительность в минутах (0 = перманент)')
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    unbanned_by = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True, blank=True, related_name='punishments_removed')
    unban_reason = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Punishment'
        verbose_name_plural = 'Punishments'
        ordering = ['-issued_at']

    def __str__(self):
        return f'{self.get_punishment_type_display()}: {self.target_name} ({self.target_steam_id})'

    def save(self, *args, **kwargs):
        if not self.pk and self.duration > 0:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=self.duration)
        super().save(*args, **kwargs)

    def is_expired(self):
        if self.duration == 0:
            return False
        return timezone.now() >= self.expires_at if self.expires_at else False

    def get_time_remaining(self):
        if not self.is_active or self.duration == 0:
            return None
        if self.expires_at:
            delta = self.expires_at - timezone.now()
            if delta.total_seconds() > 0:
                return delta
        return None

    def get_time_remaining_minutes(self):
        """Возвращает оставшееся время в минутах"""
        delta = self.get_time_remaining()
        if delta:
            return int(delta.total_seconds() / 60)
        return None

    def auto_expire(self):
        """Автоматически снимает наказание если оно истекло"""
        if self.is_active and self.is_expired():
            self.is_active = False
            self.unban_reason = 'Истёк срок наказания'
            self.save()
            return True
        return False
