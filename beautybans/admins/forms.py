from django import forms
from .models import Admin, AdminGroup, AdminServer


class AdminGroupForm(forms.ModelForm):
    class Meta:
        model = AdminGroup
        fields = ['name', 'flags', 'immunity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название группы'}),
            'flags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'abcdefgh'}),
            'immunity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0-100'}),
        }
        labels = {
            'name': 'Название',
            'flags': 'Флаги',
            'immunity': 'Иммунитет',
        }


class AdminForm(forms.ModelForm):
    class Meta:
        model = Admin
        fields = ['steam_id', 'name', 'is_active']
        widgets = {
            'steam_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'STEAM_0:1:123456'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя администратора'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'steam_id': 'Steam ID',
            'name': 'Имя',
            'is_active': 'Активен',
        }


class AdminServerForm(forms.ModelForm):
    class Meta:
        model = AdminServer
        fields = ['admin', 'server', 'group', 'flags', 'immunity']
        widgets = {
            'admin': forms.Select(attrs={'class': 'form-select'}),
            'server': forms.Select(attrs={'class': 'form-select'}),
            'group': forms.Select(attrs={'class': 'form-select'}),
            'flags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Оставьте пустым для флагов из группы'}),
            'immunity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Оставьте пустым для иммунитета из группы'}),
        }
        labels = {
            'admin': 'Администратор',
            'server': 'Сервер',
            'group': 'Группа',
            'flags': 'Индивидуальные флаги',
            'immunity': 'Индивидуальный иммунитет',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['admin'].empty_label = 'Выберите администратора'
        self.fields['server'].empty_label = 'Выберите сервер'
        self.fields['group'].empty_label = 'Без группы (индивидуальные права)'
