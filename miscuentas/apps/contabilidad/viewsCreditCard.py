from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import request
from .models import *
from .forms import *
from .myFuncs import *

@login_required
def crear_creditCard(request):
    if request.method == 'POST':
        request.POST._mutable = True
        form = CreditCardForm(request.POST)
        form.data['cupo'] = int(form.data['cupo'].replace('.',''))
        if form.is_valid():
            creditCard = form.save(commit=False)
            creditCard.user = request.user
            try:
                creditCard.save()
                messages.success(request, 'Tarjeta de crédito creada', extra_tags='success')
            except Exception as ex:
                python(ex)
                messages.success(request, 'No fue posible crear la tarjeta debido a un error', extra_tags='error')
            return redirect('panel:panel')
    else:
        form = CreditCardForm()

    return render(request, 'contabilidad/creditCard/crear_creditCard.html', {"form": form})

@login_required
def vista_creditCard(request, creditCard_id):
    creditCard = get_object_or_404(CreditCard, id=creditCard_id, user=request.user)
    return render(request, 'contabilidad/creditCard/vista_creditCard.html', {"creditCard": creditCard})