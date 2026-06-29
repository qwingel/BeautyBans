from django import forms
from .models import Admin, AdminGroup, AdminServer


class AdminGroupForm(forms.ModelForm):
    class Meta:
        model = AdminGroup
        fields = ['name', 'flags', 'immunity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'flags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'abcdefgh'}),
            'immunity': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class AdminForm(forms.ModelForm):
    class Meta:
        model = Admin
        fields = ['steam_id', 'name', 'group', 'is_active']
        widgets = {
            'steam_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'STEAM_0:1:123456'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AdminServerForm(forms.ModelForm):
    class Meta:
        model = AdminServer
        fields = ['admin', 'server', 'flags', 'immunity']
        widgets = {
            'admin': forms.Select(attrs={'class': 'form-control'}),
            'server': forms.Select(attrs={'class': 'form-control'}),
            'flags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'abcdefgh'}),
            'immunity': forms.NumberInput(attrs={'class': 'form-control'}),
        }
