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
                    'id': 'saldo'
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

class EtiquetaForm(forms.ModelForm):
    class Meta:
        model = Etiqueta
        fields = ['nombre']

        widgets = {
            'nombre': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Nombre de la etiqueta',
                    'id': 'nombre'
                }
            ),
        }

class TransaccionForm(forms.ModelForm):
    class Meta:
        model = Transaccion
        fields = ['cantidad','info']

        widgets = {
            'cantidad': forms.NumberInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Valor o cantidad',
                    'min':'50',
                    'id': 'cantidad'
                }
            ),
            'info': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Infromacion (opcional)',
                    'id': 'info'
                }
            ),
        }

class PrestamoForm(forms.ModelForm):
    class Meta:
        model = Prestamo
        fields = ['tipo','cantidad','info']

        widgets = {
            'tipo': forms.Select(
                attrs = {
                    'class':'form-control',
                    'id': 'tipo',
                    'required':''
                }
            ),
            'cantidad': forms.NumberInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Valor o cantidad',
                    'min':'50',
                    'id': 'cantidad'
                }
            ),
            'info': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Infromacion (opcional)',
                    'id': 'info'
                }
            ),
        }
