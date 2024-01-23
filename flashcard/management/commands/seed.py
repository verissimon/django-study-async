from django.core.management.base import BaseCommand
from flashcard.models import Categoria
# python manage.py seed --mode=refresh
CATEGORIAS = ['Programação', 'Matemática', 'Português', 'Biologia']

""" Clear all data and create Categoria """
MODE_REFRESH = 'refresh'

""" Clear all data and do not create any object """
MODE_CLEAR = 'clear'

class Command(BaseCommand):
    help = "seed database for testing and development."

    def add_arguments(self, parser):
        parser.add_argument('--mode', type=str, help="Mode")

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        run_seed(self, options['mode'])
        self.stdout.write('done.')


def clear_data():
    """Deletes all the table data"""
    Categoria.objects.all().delete()

def create_categoria(nome_categoria):
    categoria = Categoria(
        nome = nome_categoria
    )
    categoria.save()
    return categoria

def run_seed(self, mode):
    """ Seed database based on mode

    :param mode: refresh / clear 
    :return:
    """
    clear_data()
    if mode == MODE_CLEAR:
        return

    for categoria in CATEGORIAS:
        create_categoria(categoria)


