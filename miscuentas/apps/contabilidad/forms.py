from django import forms
from .models import *

class CuentaForm(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = ['nombre','saldo']

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
        }

class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ['nombre']

        widgets = {
            'nombre': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Nombre de la cuenta',
                    'id': 'nombre'
                }
            ),
        }
