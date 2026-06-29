import uuid
from django.db import models

# Create your models here.
class Server(models.Model):
    GAME_CHOICES = [
        ('cs16', 'Counter-Strike 1.6'),
        ('cs2', 'Counter-Strike 2'),
    ]

    name = models.CharField(max_length=64)
    ip = models.GenericIPAddressField()
    port = models.IntegerField(default=27015)
    rcon_password = models.CharField(max_length=128)
    game_type = models.CharField(max_length=8, choices=GAME_CHOICES, default='cs16')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Server'
        verbose_name_plural = 'Servers'

    def __str__(self):
        return f'{self.name} ({self.ip}:{self.port})'