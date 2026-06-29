from django import forms
from .models import Server


class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = ['name', 'ip', 'port', 'rcon_password', 'game_type', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'ip': forms.TextInput(attrs={'class': 'form-control'}),
            'port': forms.NumberInput(attrs={'class': 'form-control'}),
            'rcon_password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'game_type': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
