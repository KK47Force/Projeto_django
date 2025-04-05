from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from .models import Mentorados, Navigators, DisponibilidadeHorarios, Reuniao, Tarefa, Upload
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime, timedelta
from . auth import valida_token
import locale

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
    

def reunioes(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'GET':
        reunioes = Reuniao.objects.filter(data__mentor=request.user)
        return render(request, 'reunioes.html', {'reunioes': reunioes})
    
    elif request.method == 'POST':
        data = request.POST.get('data')
        data = datetime.strptime(data, '%Y-%m-%dT%H:%M')

        disponibilidades = DisponibilidadeHorarios.objects.filter(mentor=request.user).filter(
            data_inicial__gte = data - timedelta(minutes=50),
            data_inicial__lte = data + timedelta(minutes=50)
        )

        if disponibilidades.exists():
            messages.add_message(request, constants.ERROR, 'Você já possui uma reunião em aberto.')
            return redirect('reunioes')

        disponibilidades = DisponibilidadeHorarios(
            data_inicial=data,
            mentor=request.user
        )

        disponibilidades.save()
        

        messages.add_message(request, constants.SUCCESS, 'Reunião cadastrada com sucesso!')
        return redirect('reunioes')
    

def auth(request):
    if request.method == 'GET':
        return render(request, 'auth_mentorado.html')
    
    if request.method == 'POST':
        token = request.POST.get('token')

        if not Mentorados.objects.filter(token=token).exists():
            messages.add_message(request, constants.ERROR, 'Token inválido.')
            return redirect('auth_mentorado')
        
        response = redirect('escolher_dia')
        response.set_cookie('auth_token', token, max_age=36000)

        return response
    

def escolher_dia(request):
    if not valida_token(request.COOKIES.get('auth_token')):
        return redirect('auth_mentorado')
    if request.method == 'GET':
        mentorado = valida_token(request.COOKIES.get('auth_token'))
        disponibilidades = DisponibilidadeHorarios.objects.filter(
            data_inicial__gte=datetime.now(),
            agendado =False,
            mentor =mentorado.user
        ).values_list('data_inicial', flat=True)

        datas_unicas = {}
        for i in disponibilidades:
            data_str = i.strftime('%d-%m-%Y')
            # Criar dicionário com informações da data
            if data_str not in datas_unicas:
                datas_unicas[data_str] = {
                    'data': i.strftime('%d-%m-%Y'),
                    'mes': i.strftime('%B').capitalize(),
                    'dia': i.strftime('%A').capitalize()
                }
        info_datas = list(datas_unicas.values())

        # tornar mes e dia diamicos
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil')
        return render(request, 'escolher_dia.html', {'info_datas': info_datas})
    

def agendar_reuniao(request):
    if not valida_token(request.COOKIES.get('auth_token')):
        return redirect('auth_mentorado')
    

    if request.method == 'GET':
        data = request.GET.get("data")
        data = datetime.strptime(data, '%d-%m-%Y')
        mentorado = valida_token(request.COOKIES.get('auth_token'))
        horarios = DisponibilidadeHorarios.objects.filter(
            data_inicial__gte=data,
            data_inicial__lt=data + timedelta(days=1),
            agendado=False,
            mentor = mentorado.user
        )
        return render(request, 'agendar_reuniao.html', {'horarios': horarios,
                                                        'tags': Reuniao.tag_choices,})
    
    elif request.method == 'POST':
        horario_id = request.POST.get('horario')
        tag = request.POST.get('tag')
        descricao = request.POST.get('descricao')

        #validar se o horario agendaddo é realmente de um mentor do mentorado

        reuniao = Reuniao(
            data_id=horario_id,
            mentorado=valida_token(request.COOKIES.get('auth_token')),
            tag=tag,
            descricao=descricao,
        )

        reuniao.save()

        horario = DisponibilidadeHorarios.objects.get(id=horario_id)
        horario.agendado = True
        horario.save()

        messages.add_message(request, constants.SUCCESS, 'Reunião agendada com sucesso!')
        return redirect('escolher_dia')
    

def tarefa(request, id):
    mentorado = Mentorados.objects.get(id=id)
    if mentorado.user != request.user:
        raise Http404()

    if request.method == 'GET':
        tarefas = Tarefa.objects.filter(mentorado=mentorado)
        videos = Upload.objects.filter(mentorado=mentorado).order_by('-id')
        return render(request, 'tarefa.html', {'mentorado': mentorado, 
                                               'tarefas': tarefas, 
                                               'videos': videos})
    if request.method == 'POST':
        tarefa = Tarefa(
            mentorado=mentorado,
            tarefa=request.POST.get('tarefa')
        )
        tarefa.save()
        return redirect(f'/mentorados/tarefa/{id}')


def upload(request, id):
    mentorado = Mentorados.objects.get(id=id)
    if mentorado.user != request.user:
        raise Http404()

    video = request.FILES.get('video')
    upload = Upload(
        mentorado=mentorado,
        video=video
    )
    upload.save()
    return redirect(f'/mentorados/tarefa/{mentorado.id}')
