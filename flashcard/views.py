from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.contrib.messages import constants
from django.contrib import messages
from .models import Flashcard, Categoria, Desafio, FlashcardDesafio

def index(req):
    return HttpResponse('voce esta em flashcard/')

def novo_flashcard(req):
    if not req.user.is_authenticated:
        messages.add_message(req,
                             constants.ERROR,
                             'Usuario precisa estar autorizado para acessar flashcards')
        return redirect('/usuarios/logar')

    if req.method == 'GET':
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        flashcards = Flashcard.objects.filter(user=req.user)

        filtro_categoria = req.GET.get('categoria')
        filtro_dif = req.GET.get('dificuldade')

        if filtro_categoria:
            flashcards = flashcards.filter(categoria__id=filtro_categoria)

        if filtro_dif:
            flashcards = flashcards.filter(dificuldade=filtro_dif)

        return render(
            req,
            'novo_flashcard.html',
            {
                'categorias': categorias,
                'dificuldades': dificuldades,
                'flashcards': flashcards
            }
        )
    elif req.method == 'POST':
        pergunta = req.POST.get('pergunta')
        resposta = req.POST.get('resposta')
        categoria = req.POST.get('categoria') # id é mandado como value no formulário
        dificuldade = req.POST.get('dificuldade')

        if len(pergunta.strip()) == 0 or len(resposta.strip()) == 0:
            messages.add_message(
                req,
                constants.ERROR,
                'Preencha os campos de pergunta e resposta',
            )
            return redirect('/flashcard/novo_flashcard')
        
        Flashcard(
            user=req.user, # associa ao usuario logado
            pergunta=pergunta,
            resposta=resposta,
            categoria_id=categoria,
            dificuldade=dificuldade,
        ).save()

        messages.add_message(
            req,
            constants.SUCCESS,
            'Flashcard criado com sucesso'
        )
        return redirect('/flashcard/novo_flashcard')
    
def deletar_flashcard(req, id):
    flashcard = Flashcard.objects.get(id=id) # pega card cujo id foi passado na req 

    if not flashcard.user.id == req.user.id: # flashcard tem que pertencer a user que fez req
        messages.add_message(
            req,
            constants.WARNING,
            'Flashcard não pertence a usuário que fez requisição.'
        )
        return redirect('/flashcard/novo_flashcard')

    flashcard.delete()
    messages.add_message(
        req,
        constants.SUCCESS,
        'Flashcard deletado com sucesso.'
    )
    return redirect('/flashcard/novo_flashcard')

def iniciar_desafio(req):
    if req.method == 'GET':
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        return render(
            req,
            'iniciar_desafio.html',
            {
                'categorias': categorias,
                'dificuldades': dificuldades,
            })
    
    if req.method == 'POST':
        titulo = req.POST.get('titulo')
        categorias = req.POST.getlist('categoria')
        dificuldade = req.POST.get('dificuldade')
        qtd_perguntas = req.POST.get('qtd_perguntas')
        
        if titulo == '' or categorias == [] or not qtd_perguntas:
            messages.add_message(
                req,
                constants.WARNING,
                'Preencha o formulário corretamente. Dê um título, selecione uma ou mais categorias e escolha o número de questões do desafio.'
            )
            return redirect('/flashcard/iniciar_desafio')
                  
        if int(qtd_perguntas) < 1:
            messages.add_message(
                req,
                constants.WARNING,
                'O desafio deve ter uma quantidade de perguntas maior que zero.'
            )
            return redirect('/flashcard/iniciar_desafio')

        desafio = Desafio(
            user = req.user,
            titulo = titulo,
            quantidade_perguntas = qtd_perguntas,
            dificuldade = dificuldade,
        )
        desafio.save()
        desafio.categoria.add(*categorias)

        flashcards = (
            Flashcard.objects
                .filter(user = req.user)
                .filter(dificuldade = dificuldade)
                .filter(categoria_id__in = categorias) # categorias que pertencem a uma das categorias
                .order_by('?')
        )

        if flashcards.count() < int(qtd_perguntas):
            desafio.delete()
            messages.add_message(
                req,
                constants.WARNING,
                'Não há um número de flashcards grande o suficiente pertencentes a essa dificuldade e categorias.'
            )
            return redirect('/flashcard/iniciar_desafio')

        flashcards = flashcards[: int(qtd_perguntas)]

        for f in flashcards:
            flashcard_desafio = FlashcardDesafio(
                flashcard=f,
            )
            flashcard_desafio.save()
            desafio.flashcards.add(flashcard_desafio)

        desafio.save()
        messages.add_message(
                req,
                constants.SUCCESS,
                f'Desafio {desafio.titulo} criado com sucesso.'
            )
        return redirect('/flashcard/iniciar_desafio')
    
def listar_desafio(req):
    def get_dif_display(dif_tuple, dif_sigla):
        for tup in dif_tuple:
            if tup[0] == dif_sigla:
                return tup[1]
        return None
    
    desafios = Desafio.objects.filter(user = req.user)
    dificuldades = Flashcard.DIFICULDADE_CHOICES
    filtro_categoria = req.GET.get('categoria')
    filtro_dif: tuple = req.GET.get('dificuldade')
    
    if filtro_categoria:
        desafios = desafios.filter(categoria__id=filtro_categoria)
        messages.add_message(
            req,
            constants.SUCCESS,
            f'Desafios com categoria \'{Categoria.objects.get(id=filtro_categoria)}\' filtrados com sucesso.'
        )
    
    if filtro_dif:
        desafios = desafios.filter(dificuldade=filtro_dif)
        dif_display = get_dif_display(dificuldades, filtro_dif)
        messages.add_message(
            req,
            constants.SUCCESS,
            f'Desafios de dificuldade \'{dif_display}\' filtrados com sucesso.'
        )

    def get_desafio_status(desafio):
        for flash in desafio.flashcards.all():
            if flash.respondido == False: 
                # se pelo menos um flashcard não foi respondido,
                # o desafio é considerado não concluído
                return 'Não concluído'
            else:
                return 'Concluído'
            
    for desafio in desafios:
        desafio.status = get_desafio_status(desafio)

    return render(
        req,
        'listar_desafio.html',
        {
            'desafios': desafios,
            'categorias': Categoria.objects.all(),
            'dificuldades': dificuldades
        }
    )

def desafio(req, id):
    desafio = Desafio.objects.get(id=id)
    categorias = desafio.categoria.all()
    
    if not desafio.user == req.user:
        raise Http404()
        
    if req.method == 'GET':
        acertos = (
            desafio.flashcards
                .filter(respondido=True)
                .filter(acertou=True)
                .count()
                )
        erros = (
            desafio.flashcards
                .filter(respondido=True)
                .filter(acertou=False)
                .count()
                )
        faltantes = (
            desafio.flashcards
                .filter(respondido=False)
                .count()
                )
        return render(
            req,
            'desafio.html',
            {
                'desafio': desafio,
                'acertos': acertos,
                'erros': erros,
                'faltantes': faltantes,
                'categorias': categorias
            },
        )
    
def responder_flashcard(req, id):
    flashcard_desafio = FlashcardDesafio.objects.get(id=id)
    acertou = req.GET.get('acertou')
    desafio_id = req.GET.get('desafio_id')

    if not flashcard_desafio.flashcard.user == req.user:
        raise Http404()
    
    flashcard_desafio.respondido = True
    flashcard_desafio.acertou = True if acertou == '1' else False
    flashcard_desafio.save()

    return redirect(f'/flashcard/desafio/{desafio_id}')

