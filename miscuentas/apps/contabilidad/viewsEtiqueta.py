from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import request
from .models import *
from .forms import *
from .myFuncs import *

@login_required
def listar_etiquetas(request):
    etiquetas = Etiqueta.objects.filter(user = request.user.id).order_by('nombre')
    return render(request, 'contabilidad/etiqueta/listar_etiquetas.html', {"etiquetas":etiquetas})

@login_required
def crear_etiqueta(request):
    if request.method == 'POST':
        form = EtiquetaForm(request.POST)
        if form.is_valid():
            etiqueta = form.save(commit=False)
            etiqueta.user = request.user
            etiqueta.save()
            return redirect('panel:listar_etiquetas')
    else:
        form = EtiquetaForm()

    return render(request, 'contabilidad/etiqueta/crear_etiqueta.html', {"form": form})

class EditarEtiqueta(UpdateView):
    model = Etiqueta
    form_class = EtiquetaForm
    template_name = 'contabilidad/etiqueta/crear_etiqueta.html'
    success_url = reverse_lazy('panel:listar_etiquetas')

class EliminarEtiqueta(DeleteView):
    model = Etiqueta
    template_name = 'contabilidad/etiqueta/etiqueta_confirm_delete.html'
    success_url = reverse_lazy('panel:listar_etiquetas')