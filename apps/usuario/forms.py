from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegistroUsuarioForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'email']

        widgets = {
            'username': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Nombre de Usuario',
                    'id': 'username',
                    'autocapitalize':'none'
                }
            ),
            'email': forms.EmailInput(
                attrs = {
                    'class':'form-control mb-3',
                    'placeholder':'Correo electronico',
                    'id': 'email'
                }
            ),

        }
