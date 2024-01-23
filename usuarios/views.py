from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages, auth

def cadastro(req):
    if req.method == 'GET':
        return render(req, 'cadastro.html')
    elif req.method == 'POST':
        username = req.POST.get('username')
        senha = req.POST.get('senha')
        confirmar_senha = req.POST.get('confirmar_senha')

        if not senha == confirmar_senha:
            messages.add_message(
                req,
                constants.ERROR,
                'As senhas não coincídem'
            )
            return redirect('/usuarios/cadastro')

        user = User.objects.filter(
            username=username
            )

        if user.exists():
            messages.add_message(
                req,
                constants.ERROR,
                'Já existe um usuário com o mesmo username',
            )
            return redirect('/usuarios/cadastro')
        
        try:
            User.objects.create_user(
                username=username,
                password=senha
                )
            messages.add_message(
                req, 
                constants.SUCCESS, 
                'Usuário cadastrado com sucesso.'
            )
            return redirect('/usuarios/logar')
        except:
            messages.add_message(
                req,
                constants.ERROR,
                'Erro interno do sistema'
            )
            return redirect('/usuarios/cadastro')
        
def logar(req):
    if req.user.is_authenticated:
        return redirect('novo_flashcard')

    if req.method == 'GET':
        return render(req, 'login.html')
    elif req.method == 'POST':
        username = req.POST.get('username')
        senha = req.POST.get('senha')
        user = auth.authenticate(req, username=username, password=senha)

        if user:
            auth.login(req, user)
            messages.add_message(req, constants.SUCCESS, 'Logado com sucesso')
            return redirect('/flashcard/novo_flashcard')
            
        else:
            messages.add_message(req, constants.ERROR, 'Usuario ou senha invalidos')
            return redirect('/usuarios/logar')
        
def logout(req):
    auth.logout(req)
    return redirect('/usuarios/logar')