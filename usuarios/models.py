from django.db import models

# Create your models here.
class Usuario(models.Model):

    nome = models.CharField(max_length=80,
                            verbose_name='Nome',
                            help_text='Nome completo do usuário',
                            null=False)
    email = models.EmailField(unique=True,
                              verbose_name='E-mail',
                              help_text='E-mail do usuário',
                              null=False)
    senha = models.CharField(max_length=255,
                             verbose_name='Senha',
                             help_text='Senha do usuário',
                             null=False)
    criado = models.DateField(auto_now_add=True,
                    verbose_name='Criado em' )
    atualizado = models.DateTimeField(auto_now=True,
                    verbose_name='Atualizado em')
    
    class Meta:
        #nome da tabela
        db_table = 'usuarios'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['nome'] #ordena por nome (ordem alfabética)
        # se fosse por data de criação
        # ordering = ['-criado']
        # ordem do mais recente (decrescente)

    def __repr__(self):
        return f'<Usuario {self.nome}>'
    def __str__(self):
        return f'{self.nome} ({self.email})'    

     