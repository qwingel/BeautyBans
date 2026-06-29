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
    group = models.ForeignKey(AdminGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='admins')
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
    flags = models.CharField(max_length=32, default='', blank=True)
    immunity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Admin Server Permission'
        verbose_name_plural = 'Admin Server Permissions'
        unique_together = ('admin', 'server')

    def __str__(self):
        return f'{self.admin.name} → {self.server.name}'
