from django import forms
from .models import Server


class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = ['name', 'ip', 'port', 'rcon_password', 'game_type', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название сервера'}),
            'ip': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '127.0.0.1'}),
            'port': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '27015'}),
            'rcon_password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'RCON пароль (необязательно)', 'required': False}),
            'game_type': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Название',
            'ip': 'IP адрес',
            'port': 'Порт',
            'rcon_password': 'RCON пароль',
            'game_type': 'Тип игры',
            'is_active': 'Активен',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['game_type'].empty_label = 'Выберите тип игры'
