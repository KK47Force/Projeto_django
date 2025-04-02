from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Mentorados, Navigators
from django.contrib import messages
from django.contrib.messages import constants

# Create your views here.
def mentorados(request):
    if not request.user.is_authenticated:
        return redirect('login')


    if request.method == 'GET':
        navegators = Navigators.objects.filter(user=request.user)
        mentorados = Mentorados.objects.filter(user=request.user).order_by('-criado_em')
        return render(request, 'mentorados.html', {'estagios': Mentorados.estagio_choices, 
                                                   'navegators': navegators,
                                                   'mentorados': mentorados,})
    elif request.method == 'POST':
        nome = request.POST.get('nome')
        estagio = request.POST.get('estagio')
        navigator = request.POST.get('navigator')
        foto = request.FILES.get('foto')

        mentorado = Mentorados(
            nome=nome,
            estagio=estagio,
            navigator_id=navigator,
            foto=foto,
            user=request.user
        )
        mentorado.save()

        messages.add_message(request, constants.SUCCESS, 'Mentorado cadastrado com sucesso!')
        return redirect('mentorados')