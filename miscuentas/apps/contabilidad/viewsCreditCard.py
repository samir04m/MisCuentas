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
            creditCard.cupoDisponible = creditCard.cupo
            creditCard.user = request.user
            try:
                creditCard.save()
                messages.success(request, 'Tarjeta de crédito creada', extra_tags='success')
            except Exception as ex:
                print("----- Exception -----", ex)
                messages.success(request, 'No fue posible crear la tarjeta debido a un error', extra_tags='error')
            return redirect('panel:panel')
    else:
        form = CreditCardForm()

    return render(request, 'contabilidad/creditCard/crear_creditCard.html', {"form": form})

@login_required
def vista_creditCard(request, creditCard_id):
    creditCard = get_object_or_404(CreditCard, id=creditCard_id, user=request.user)
    deudaActual = creditCard.cupo - creditCard.cupoDisponible
    context = {
        "creditCard": creditCard,
        "deudaActual": deudaActual
    }
    return render(request, 'contabilidad/creditCard/vista_creditCard.html', context)

@login_required
def compra_creditCard(request, creditCard_id):
    creditCard = get_object_or_404(CreditCard, id=creditCard_id, user=request.user)
    if request.method == 'POST':
        valor = validarMiles(int(request.POST.get('valor').replace('.','')))
        cuotas = int(request.POST.get('cuotas'))
        info = request.POST.get('info')
        fecha = datetime.now()
        # etiquetaId = int(request.POST.get('tag')) if request.POST.get('tag') else None
        etiquetaId = request.POST.get('tag')
        if request.POST.get('newTag'):
            nuevaEtiqueta = getEtiqueta(request.POST.get('newTag'), request.user)
            etiquetaId = nuevaEtiqueta.id
        print('====', type(etiquetaId))
        try:
            compra = crearCompraCredito(creditCard, etiquetaId, valor, cuotas, info, fecha)
            messages.success(request, 'Compra registrada', extra_tags='success')
        except Exception as ex:
            print("----- Exception -----", ex)
            messages.success(request, 'No fue posible registrar la compra', extra_tags='error')
        return redirect('panel:vista_creditCard', creditCard.id)
    else:
        context = {"creditCard": creditCard, "tags":getSelectEtiquetas(request)}
        return render(request, 'contabilidad/creditCard/compra_creditCard.html', context)

@login_required
def vista_compra(request, compra_id):
    compra = get_object_or_404(CompraCredito, id=compra_id)
    print(dir(compra))
    for tra in compra.transaccionpagocredito_set.all():
        print(tra)
        
    return render(request, 'contabilidad/creditCard/vista_compraCredito.html', {"compra":compra})