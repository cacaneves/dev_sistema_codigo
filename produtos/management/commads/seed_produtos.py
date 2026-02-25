# primeiro criar a pasta management e depois a commands
# criar um arquivo __init__.py nas duas
# para rodar o comando: python manage.py seed_produtos
from django.core.management.base import BaseCommand
from produtos.models import Produto
from faker import Faker # Lembre-se: pip install faker
import random


# 5 pontos - seed de dados
class Command(BaseCommand):
    help = 'Popula o banco de dados com produtos de teste (Sem Categorias)'

    def handle(self, *args, **kwargs):
        """
        Popula o banco de dados com produtos de teste (Sem Categorias)

        Criar 10 produtos de teste com nomes, marcas e descri es fictícias.
        O preço dos produtos é gerado aleatoriamente entre 50.00 e 5000.00.
        O status do produto é 'ativo' e a imagem é nula (pois o Faker não faz upload real de arquivos facilmente)
        """
        faker = Faker('pt_BR')
        
        self.stdout.write('Iniciando a criação de produtos...')

        # Lista de marcas fictícias para dar variedade
        marcas = ['Sony', 'Samsung', 'LG', 'Motorola', 'Dell', 'Apple', 'Logitech', 'Asus']

        for _ in range(10): # Cria 10 produtos
            
            # Gera um nome de produto com duas palavras (ex: "Cadeira Gamer")
            nome_produto = f"{faker.word().capitalize()} {faker.word().capitalize()}"
            
            # Gera descrição garantindo que tenha mais de 20 caracteres (sua regra de validação)
            descricao_texto = faker.text(max_nb_chars=100)
            while len(descricao_texto) < 20:
                descricao_texto += " " + faker.text(max_nb_chars=50)

            # Cria o produto no banco
            Produto.objects.create(
                nome=nome_produto,
                marca=random.choice(marcas),
                # Gera preço aleatório entre 50.00 e 5000.00
                preco=round(random.uniform(50.0, 5000.0), 2),
                descricao=descricao_texto,
                ativo=True,
                imagem=None # Deixamos nulo pois o Faker não faz upload real de arquivos facilmente
            )

        self.stdout.write(self.style.SUCCESS('Sucesso! 10 produtos foram cadastrados.'))