from django.shortcuts import redirect

def index(req):
    if not req.user.is_authenticated:
        return redirect('login')

    return redirect('novo_flashcard')