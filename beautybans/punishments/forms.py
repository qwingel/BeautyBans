from django import forms
from .models import Punishment


class PunishmentForm(forms.ModelForm):
    class Meta:
        model = Punishment
        fields = ['punishment_type', 'target_steam_id', 'target_name', 'target_ip', 'ban_subnet', 'reason', 'admin', 'server', 'duration']
        widgets = {
            'punishment_type': forms.Select(attrs={'class': 'form-control'}),
            'target_steam_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'STEAM_0:1:123456'}),
            'target_name': forms.TextInput(attrs={'class': 'form-control'}),
            'target_ip': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '127.0.0.1'}),
            'ban_subnet': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'admin': forms.Select(attrs={'class': 'form-control'}),
            'server': forms.Select(attrs={'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Минуты (0 = перманент)'}),
        }


class UnbanForm(forms.Form):
    unban_reason = forms.CharField(
        label='Причина снятия',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=True
    )
