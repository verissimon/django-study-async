from django.shortcuts import render, redirect, HttpResponse
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
                .filter(categoria_id__in = categorias)
                .order_by('?')
        )

        if flashcards.count() < int(qtd_perguntas):
            messages.add_message(
                req,
                constants.WARNING,
                f'a quantidade máxima de flashcards disponíveis para essa(s) categoria(s) e dificuldade deve ser: {flashcards.count()}.'
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

        return HttpResponse('Desafio criado com sucesso')