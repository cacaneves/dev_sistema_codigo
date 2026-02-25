from django.test import TestCase
from usuarios.models import Usuario
from usuarios.serializers import CadastroSerializer
# para testar APIs
from rest_framework.test import APITestCase
# para verificar a respostas dadas
from rest_framework import status
# usar os nomes das rotas
from rest_framework.reverse import reverse


# Create your tests here.

# TESTES UNITÁRIOS

class UsuarioTestesUnitarios(TestCase):

    def setUp(self):
        self.dados={
            'nome': 'Eliane',
            'email': 'eliane_crochet@senai.br',
            'senha': 'CafeComCocaCola#01',
            'cpf': '025.115.987-60'
        }
    
    def test_hashing(self):
        '''
        Valida se o metodo save() hasheou a senha
        '''

        usuario = Usuario.objects.create(**self.dados)

        # A senha não pode estar em texto puro
        self.assertNotEqual(usuario.senha, 'CafeComCocaCola#01')

        # Deve começar com o prefixo do algoritmo
        self.assertTrue(usuario.senha.startswith('pbkdf2_sha256$'))

    def test_soft_delete_padrao(self):
        usuario = Usuario.objects.create(**self.dados)

        self.assertTrue(usuario.ativo)

    # --------------------------------------------
    # Teste do Serializer

    def test_validar_cpf_limpo(self):
        '''Testa se o serializer valida cpf corretamente'''

        dados = self.dados.copy()
        dados['cpf'] = '123' #CPF Invalido
        serializer = CadastroSerializer(data=dados)

        # verifica se o serializer achou o erro
        self.assertFalse(serializer.is_valid())

        # verifica se o cpf esta na lista de erros do serializer
        self.assertIn('cpf', serializer.errors)

    def test_senha_sem_caracter_especial(self):
        '''Testa a regra de senha "forte"'''
        dados = self.dados.copy()

        dados['senha'] = 'Abcd1234'

        serializer = CadastroSerializer(data=dados)
        
        # verifica se o serializer achou erros
        self.assertFalse(serializer.is_valid())

        self.assertEqual(str(serializer.errors['senha'][0]), 
        'A senha deve conter pelo menos um caractere especial.')

# TESTES FUNCIONAIS

class UsuarioTestesFuncional(APITestCase):
    def _payload_cadastro(self, **overrides):
        data = {
            'nome':'Coca-Cola Zero',
            'email':'coca@zero.com',
            'cpf':'11111111111',
            'senha':'Minalba@500ml',
            'senha_confirmacao': 'Minalba@500ml'
        }
        data.update(overrides)
        return data
    
    def test_cadastro_usuario_sucesso(self):
        url = reverse('usuarios-cadastro') # /usuarios/cadastro
        response = self.client.post(
            url,
            self._payload_cadastro(),
            format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertIn('mensagem', response.data)
        self.assertIn('usuario', response.data)

        # ir até o banco
        self.assertTrue(
            Usuario.objects.filter(
                email=response.data['usuario']['email']).exists()
        )
        
    def test_atualizar_usuario(self):
        # Arrange
        url_cadastro = reverse('usuarios-cadastro')
        response_cadastro = self.client.post(
            url_cadastro,
            self._payload_cadastro(),
            format='json'
        )

        # pega o id do usuario criado
        usuario_id = response_cadastro.data['usuario']['id']

        # realiza login
        url_login = reverse('usuarios-login')
        credenciais = {
            'email': self._payload_cadastro()['email'],
            'senha': self._payload_cadastro()['senha']
        }

        login = self.client.post(url_login, credenciais, format='json')
        access = login.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

        # dados para atualização
        update = {
            'nome': 'Teste de Atualização'
        }

        url_update = reverse('usuarios-detail', args=[usuario_id])

        # Act
        response = self.client.patch(url_update, update, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('mensagem', response.data)
        self.assertEqual(response.data['mensagem'], 'Usuário atualizado com sucesso')

        # valida no banco
        self.assertTrue(Usuario.objects.filter(id=usuario_id,nome='Teste de Atualização').exists())



