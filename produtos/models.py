from django.db import models

# Create your models here.

# 15 pontos - categorias
class Categoria(models.Model):
    nome = models.CharField(max_length=50, unique=True, verbose_name="Nome da Categoria")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nome
    
class Produto(models.Model):

    # 15 pontos - categorias
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.PROTECT, # Impede deletar categoria se tiver produtos nela
        related_name='produtos',
        verbose_name="Categoria",
        null=True # Permite nulo temporariamente para evitar conflito se já tiver dados
    )
    nome = models.CharField(
        max_length=100,
        verbose_name='Nome do Produto',
        help_text='Nome comercial do produto',
        null=False
    )
    marca = models.CharField(
        max_length=50,
        verbose_name='Marca',
        help_text='Fabricante ou marca do produto',
        null=False
    )
    preco = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Preço',
        help_text='Preço unitário do produto'
    )
    descricao = models.TextField(
        verbose_name='Descrição',
        help_text='Detalhes técnicos ou descrição comercial',
        null=True
    )
    # Campo para Upload de Imagem (Extra de 10pts)
    # Requer: pip install Pillow
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)
    # Campo para Soft Delete (Extra de 10pts)
    ativo = models.BooleanField(default=True)
    
    # Campos de auditoria
    criado = models.DateTimeField(auto_now_add=True)
    atualizado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'produtos'
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['nome'] # Ordenação padrão

    def __str__(self):
        """
        Retorna uma string representando o produto, 
        no formato "nome (marca) - R$ preco"

        :return: string
        """
        return f'{self.nome} ({self.marca}) - R$ {self.preco}'