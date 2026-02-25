# Ele cria uma autenticação JWT personalizada para o DRF, 
# adaptada ao seu modelo de usuário customizado (Usuario), 
# já que não usamos o User padrão do Django (tabela auth_user).

# A classe JWTAuthentication do SimpleJWT assume que os usuários estão na tabela padrão do Django.
# Como nesse projeto isso não é verdade, 
# precisa sobrescrever parte da lógica para que o SimpleJWT procure na sua tabela.

from rest_framework_simplejwt.authentication import JWTAuthentication
# Isso traz a autenticação original, que você vai herdar e modificar.
from rest_framework.exceptions import AuthenticationFailed
# Se algo der errado (usuário não existe, token inválido), você lança essa exceção.
from .models import Usuario

# Herda o comportamento padrão e modificando apenas o necessário.
class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Sobrescreve o método padrão para buscar na tabela 'usuarios'
        em vez da tabela 'auth_user' padrão do Django.
        Esse método é chamado depois que o token já foi decodificado e validado.
        Ele deve retornar o usuário correspondente ao token.    
        """
        try:
            user_id = validated_token['user_id']
            # Fazer o SimpleJWT buscar usuários na sua tabela usuarios
            # Em vez de buscar na tabela auth_user
            user = Usuario.objects.get(id=user_id)
            return user
        except Usuario.DoesNotExist:
            raise AuthenticationFailed('Usuário não encontrado', code='user_not_found')
        except KeyError:
            raise AuthenticationFailed('Token inválido', code='token_invalid')
            # Isso evita que um token malformado seja aceito.