# django-study-flashcards

## App para controle de estoque

Site simples feito com django para registrar, listar e excluir produtos.

### 1. Pré-requisitos

Após clonar o repositório, configure o ambiente da seguinte forma. Certifique-se de ter python e pip instalados.

```bash
python3 -m venv venv        # cria env virtual
# ativa env virtual
source venv/bin/activate    # (Linux)
venv\Scripts\Activate       # (Windows)
# instala pacotes no ambiente
pip install django; pip install pillow
```

### 2. Criando tabelas no banco de dados

```bash
python3 manage.py migrate
```

### 3. Povoe a tabela com categorias de flashcards

Em `/flashcard/management/commands/seed.py` edite a lista CATEGORIAS com as áreas de conhecimento dos flashcards:

```python
CATEGORIAS = ['Programação', 'Matemática', 'Português', 'Biologia']
```

Em seguida, execute no terminal `python3 manage.py seed` para povoar a tabela Categoria.

### 4. Executando o servidor de desenvolvimento

```bash
python3 manage.py runserver
```

A aplicação está sendo executada no endereço <http://127.0.0.1:8000/>
