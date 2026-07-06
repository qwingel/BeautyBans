from django.db import models
from servers.models import Server


class AdminGroup(models.Model):
    name = models.CharField(max_length=64, unique=True)
    flags = models.CharField(max_length=32, default='', blank=True)
    immunity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Admin Group'
        verbose_name_plural = 'Admin Groups'

    def __str__(self):
        return self.name


class Admin(models.Model):
    steam_id = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'

    def __str__(self):
        return f'{self.name} ({self.steam_id})'


class AdminServer(models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='server_permissions')
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='admin_permissions')
    group = models.ForeignKey(AdminGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='server_assignments')
    flags = models.CharField(max_length=32, default='', blank=True, help_text='Индивидуальные флаги (если не используется группа)')
    immunity = models.IntegerField(default=0, blank=True, null=True, help_text='Индивидуальный иммунитет (если не используется группа)')
    duration = models.IntegerField(default=0, blank=True, help_text='Длительность прав в минутах (0 = навсегда)')
    expires_at = models.DateTimeField(null=True, blank=True, help_text='Дата истечения прав (вычисляется автоматически)')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Admin Server Permission'
        verbose_name_plural = 'Admin Server Permissions'
        unique_together = ('admin', 'server')

    def __str__(self):
        return f'{self.admin.name} → {self.server.name}'

    def get_effective_flags(self):
        return self.flags if self.flags else (self.group.flags if self.group else '')

    def get_effective_immunity(self):
        if self.immunity is not None:
            return self.immunity
        return self.group.immunity if self.group else 0

    def save(self, *args, **kwargs):
        if self.duration > 0:
            from django.utils import timezone
            from datetime import timedelta
            self.expires_at = timezone.now() + timedelta(minutes=self.duration)
        else:
            self.expires_at = None
        super().save(*args, **kwargs)

    def is_expired(self):
        """Проверка истёкших прав"""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() >= self.expires_at
