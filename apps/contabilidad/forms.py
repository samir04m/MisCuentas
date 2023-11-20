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
                    'class':'form-control puntoMiles',
                    'placeholder':'Saldo en cuenta',
                    'id': 'saldo',
                    'type': 'text',
                    'autocomplete': 'off'
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
                    'id': 'nombre',
                    'autocomplete': 'off'
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
                    'id': 'nombre',
                    'autocomplete': 'off'
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
                    'placeholder':'Valor',
                    'id': 'cantidad',
                    'type': 'text',
                    'autocomplete': 'off'
                }
            ),
            'info': forms.Textarea(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Descripción',
                    'id': 'info',
                    'rows': 2
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
                    'placeholder':'$',
                    'id': 'cantidad',
                    'type': 'text',
                    'autocomplete': 'off'
                }
            ),
            'info': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'id': 'info',
                    'autocomplete': 'off'
                }
            ),
        }

class CreditCardForm(forms.ModelForm):
    class Meta:
        model = CreditCard
        fields = ['nombre','cupo','diaCorte','diaPago']

        widgets = {
            'nombre': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Nombre de la tarjeta',
                    'id': 'nombre'
                }
            ),
            'cupo': forms.NumberInput(
                attrs = {
                    'class':'form-control puntoMiles',
                    'placeholder':'Cupo de la tarjeta',
                    'id': 'cupo',
                    'type': 'text',
                    'autocomplete': 'off'
                }
            ),
            'diaCorte': forms.NumberInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Dia de corte',
                    'id': 'diaCorte',
                    'type': 'number',
                    'min': '1',
                    'max': '31'
                }
            ),
            'diaPago': forms.NumberInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Dia limite de pago',
                    'id': 'diaPago',
                    'type': 'number',
                    'min': '1',
                    'max': '31'
                }
            )
        }