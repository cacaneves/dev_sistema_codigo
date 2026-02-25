from django.db import models
from django.contrib.auth.hashers import make_password, check_password
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
    # 5 pontos - novo campo
    cpf = models.CharField(max_length=14,
                        null=False,
                        unique=True,
                        verbose_name='CPF',
                        help_text='CPF do usuário')
    
    # 10 pontos - soft delete
    ativo = models.BooleanField(default=True, verbose_name='Ativo')

    criado = models.DateTimeField(auto_now_add=True,
                    verbose_name='Criado em')
    atualizado = models.DateTimeField(auto_now=True,
                    verbose_name='Atualizado em')

    # 15 pontos - reset de senha    
    last_login = models.DateTimeField(verbose_name='Último Login', null=True, blank=True)
    
    # 20 pontos - favoritos
    favoritos = models.ManyToManyField('produtos.Produto',
                                        blank=True,
                                        related_name='favoritados',
                                        verbose_name='Meus Favoritos')
    
    @classmethod
    def get_email_field_name(cls):
        """
        Método exigido pelo Django para saber qual campo usar como email
        no envio de recuperação de senha.
        """
        return 'email'

    @property
    def is_active(self):
        """
        O Django busca por 'is_active', mas seu campo chama 'ativo'.
        Isso cria um 'atalho' para o Django entender.
        """
        return self.ativo
    
    @property
    def password(self):
        return self.senha
    @password.setter
    def password(self, value):
        """
        Permite definir user.password = '...' e isso salvar em self.senha
        """
        self.senha = value

    def set_password(self, raw_password):
        """
        Método auxiliar que o Django costuma chamar para definir senha com hash.
        """
        from django.contrib.auth.hashers import make_password
        self.senha = make_password(raw_password)
        
    class Meta:
        # nome da tabela
        db_table = 'usuarios'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['nome'] #ordena por nome (ordem alfabetica)
        # se fosse por data de criação
        # ordering = ['-criado'] 
        # ordem do mais recente (decrescente)
    
    def __repr__(self):
        return f'<Usuario {self.nome}>'
    
    def __str__(self):
        return f'{self.nome} ({self.email})'

    def verificar_senha(self, senha_texto):
        """
        Verifica se a senha fornecida está correta
        
        Args:
            senha_texto (str): Senha em texto puro
            
        Returns:
            bool: True se correta, False se incorreta
        """
        return check_password(senha_texto, self.senha)


    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para hashear a senha automaticamente
        
        IMPORTANTE: Este método é chamado sempre que criamos
        ou atualizamos um usuário!
        """
        # args e kwargs são argumentos posicionais e nomeados - Aceita qualquer argumento
        # Verifica se a senha precisa ser hasheada
        # Senhas hasheadas começam com o algoritmo (pbkdf2_sha256$)
        if self.senha and not self.senha.startswith('pbkdf2_sha256$'):
            self.senha = make_password(self.senha)
        
        super().save(*args, **kwargs)



    # criando a verificação se ele está autenticado
    # Isso faz com que qualquer instância desse modelo seja considerada autenticada pelo Django.
    @property
    def is_authenticated(self):
        """Retorna True sempre, pois objetos só existem se autenticados"""
        return True

    # Isso informa ao Django que esse objeto não é o tipo especial “AnonymousUser”, que representa usuários não logados.
    @property
    def is_anonymous(self):
        """Retorna False sempre, pois não é um usuário anônimo"""
        return False





