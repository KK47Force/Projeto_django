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

        estagios_flat = []
        qtd_estagios = []
        for i in Mentorados.estagio_choices:
            estagios_flat.append(i[1])

        for i, j in Mentorados.estagio_choices:
            x = Mentorados.objects.filter(estagio=i).filter(user=request.user).count()
            qtd_estagios.append(x)
            
            

        return render(request, 'mentorados.html', {'estagios': Mentorados.estagio_choices, 
                                                   'navegators': navegators,
                                                   'mentorados': mentorados,
                                                   'estagios_flat': estagios_flat,
                                                   'qtd_estagios': qtd_estagios,})
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