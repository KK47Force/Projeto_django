from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib import auth

def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        # se a senha não for igual a confirmar_senha, redireciona para a página de cadastro
        # se a senha for menor que 6, redireciona para a página de cadastro
        # se o usuário já existir, redireciona para a página de cadastro

        if senha != confirmar_senha:
            messages.add_message(request, constants.ERROR, 'As senhas não são iguais.')
            return redirect('/usuarios/cadastro/')
        
        if len(senha) < 6:
            messages.add_message(request, constants.ERROR, 'A senha deve ter no mínimo 6 caracteres.')
            return redirect('/usuarios/cadastro/')
        
        users = User.objects.filter(username=username)

        if users.exists():
            messages.add_message(request, constants.ERROR, 'Esse usuário já existe.')
            return redirect('/usuarios/cadastro/')

        User.objects.create_user(username=username, password=senha)

        return redirect('/usuarios/login/')


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = authenticate(request, username=username, password=senha)

        if user:
            auth.login(request, user)
            return redirect('/mentorados/')
        
        messages.add_message(request, constants.ERROR, 'Usuário ou senha inválidos.')

        return redirect('login')