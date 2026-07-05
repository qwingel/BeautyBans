from django import forms
from .models import Punishment


class PunishmentForm(forms.ModelForm):
    class Meta:
        model = Punishment
        fields = ['punishment_type', 'target_steam_id', 'target_name', 'target_ip', 'ban_subnet', 'reason', 'admin', 'server', 'duration']
        widgets = {
            'punishment_type': forms.Select(attrs={'class': 'form-select'}),
            'target_steam_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'STEAM_0:1:123456'}),
            'target_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя игрока'}),
            'target_ip': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '127.0.0.1 (необязательно)'}),
            'ban_subnet': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Причина наказания'}),
            'admin': forms.Select(attrs={'class': 'form-select'}),
            'server': forms.Select(attrs={'class': 'form-select'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0 для перманента, минуты для временного'}),
        }
        labels = {
            'punishment_type': 'Тип наказания',
            'target_steam_id': 'Steam ID игрока',
            'target_name': 'Имя игрока',
            'target_ip': 'IP адрес',
            'ban_subnet': 'Банить подсеть /24',
            'reason': 'Причина',
            'admin': 'Администратор',
            'server': 'Сервер',
            'duration': 'Длительность (минуты)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Устанавливаем пустой выбор вместо "-------"
        self.fields['punishment_type'].empty_label = 'Выберите тип'
        self.fields['admin'].empty_label = 'Консоль (без админа)'
        self.fields['server'].empty_label = 'Выберите сервер'


class UnbanForm(forms.Form):
    unban_reason = forms.CharField(
        label='Причина снятия',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Укажите причину снятия наказания'}),
        required=True
    )
