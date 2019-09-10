from django import forms
from .models import *

class CuentaForm(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = ['nombre','saldo','user']

        widgets = {
            'nombre': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Nombre de la cuenta',
                    'id': 'nombre'
                }
            ),
            'saldo': forms.NumberInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Saldo en cuenta',
                    'id': 'nombre'
                }
            ),
            'user': forms.Select(
                attrs = {
                    'label':'',
                    'disabled':''
                }
            ),
        }
