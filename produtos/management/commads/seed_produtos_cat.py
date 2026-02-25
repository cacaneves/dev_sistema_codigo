# primeiro criar a pasta management e depois a commands
# criar um arquivo __init__.py nas duas
# para rodar o comando: python manage.py seed_produtos_cat

# 5 pontos - seed de dados com categorias
import random
from django.core.management.base import BaseCommand
from produtos.models import Produto, Categoria
from faker import Faker # pip install faker

class Command(BaseCommand):
    help = 'Popula o banco com Categorias e Produtos de teste'

    def handle(self, *args, **kwargs):
        """
        Popula o banco com Categorias e Produtos de teste

        Cria 5 categorias e 10 produtos de teste com nomes, marcas e descri es fictícias.
        O preco dos produtos é gerado aleatoriamente entre 50.00 e 5000.00.
        O status do produto é 'ativo' e a imagem é nula (pois o Faker não faz upload real de arquivos facilmente)
        """

        faker = Faker('pt_BR')
        
        self.stdout.write('Criando categorias...')
        lista_categorias = ['Eletrônicos', 'Roupas', 'Casa', 'Livros', 'Esportes']
        objs_categorias = []
        
        for cat in lista_categorias:
            c, created = Categoria.objects.get_or_create(nome=cat, defaults={'descricao': f'Produtos de {cat}'})
            objs_categorias.append(c)

        self.stdout.write('Criando produtos...')
        
        marcas = ['Sony', 'Samsung', 'Nike', 'Adidas', 'Dell', 'Apple']
        
        for _ in range(10): # 10 produtos de teste
            nome_produto = f"{faker.word().capitalize()} {faker.word().capitalize()}"
            descricao = faker.text(max_nb_chars=100) # Descrição > 20 chars
            
            # Garante que a descrição tenha min 20 chars
            if len(descricao) < 20:
                descricao += " " + descricao 

            Produto.objects.create(
                nome=nome_produto,
                marca=random.choice(marcas),
                preco=round(random.uniform(50.0, 5000.0), 2),
                descricao=descricao,
                categoria=random.choice(objs_categorias),
                ativo=True
                # Imagem deixamos null no seed ou usamos um placeholder se quiser
            )

        self.stdout.write(self.style.SUCCESS('Sucesso! Banco populado com Categorias e Produtos.'))