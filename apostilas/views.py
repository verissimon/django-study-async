from django.shortcuts import render, redirect
from django.contrib.messages import constants
from django.contrib import messages
from .models import Apostila, ViewApostila
from flashcard.models import Categoria

def adicionar_apostilas(req):
    if req.method == 'GET':
        categorias = Categoria.objects.all()
        apostilas = Apostila.objects.filter(user=req.user)
        views_totais = ViewApostila.objects.filter(apostila__user = req.user).count()
        filtro_categoria = req.GET.get('categoria')

        if filtro_categoria:
            apostilas = apostilas.filter(categoria__id=filtro_categoria)
            
        return render(
                req,
                'adicionar_apostilas.html',
                {
                    'apostilas': apostilas,
                    'categorias': categorias,
                    'views_totais': views_totais
                }
            )
    
    elif req.method == 'POST':
        titulo = req.POST.get('titulo')
        categoria = req.POST.get('categoria')
        arquivo = req.FILES['arquivo']

        apostila = Apostila(
            user=req.user,
            titulo=titulo,
            categoria_id=categoria,
            arquivo=arquivo
            )
        apostila.save()

        messages.add_message(
            req,
            constants.SUCCESS,
            'Apostila adicionada com sucesso.'
        )

        return redirect('/apostilas/adicionar_apostilas/')
    
def apostila(req, id):
    apostila = Apostila.objects.get(id=id)

    filtro_views = ViewApostila.objects.filter(apostila=apostila)
    views_unicas = filtro_views.values('ip').distinct().count()
    views_totais = filtro_views.count()

    ViewApostila(
        ip = req.META['REMOTE_ADDR'],
        apostila=apostila
    ).save()
    views = [views_unicas, views_totais]
    return render(req, 'apostila.html',
                {
                    'apostila': apostila,
                    'views': views
                })