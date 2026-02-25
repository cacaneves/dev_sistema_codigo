from rest_framework import serializers
from .models import Usuario

# 10 pontos - reset de senha (ou 15 pontos com email)
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

# 5 pontos - novo campo
# 5 pontos - Validar Senhas
import re
# ============================================
# SERIALIZER DE CADASTRO
# ============================================

class CadastroSerializer(serializers.ModelSerializer):
    """
    Serializer para cadastro de novos usuários
    """
    senha = serializers.CharField(
        write_only=True,  # Não retorna senha na resposta
        min_length=8,
        style={'input_type': 'password'}
    )

    senha_confirmacao = serializers.CharField(
        write_only=True,  # Não retorna senha na resposta
        min_length=8,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = Usuario
        # 5 pontos - novo campo
        fields = ['nome', 'email', 'senha', 'senha_confirmacao', 'cpf']
    
    def validate_nome(self, value):
        """Validar nome"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Nome deve ter no mínimo 3 caracteres")
        return value.strip()
    
    def validate_email(self, value):
        """Validar email"""
        email = value.strip().lower()
        
        # Verificar se já existe
        if Usuario.objects.filter(email=email).exists():
            raise serializers.ValidationError("Este email já está cadastrado")
        
        return email
    
    def validate_senha(self, value):
        """Validar senha"""
        if len(value) < 8:
            raise serializers.ValidationError("Senha deve ter no mínimo 8 caracteres")
        if value.isdigit():
            raise serializers.ValidationError(
                'Senha não pode ser apenas números'
            )
        return value
    
    # 5 pontos - novo campo
    def validate_cpf(self, value):
        """Validar CPF"""
        cpf_limpo = re.sub(r'[^0-9]', '', value)
        if len(cpf_limpo) != 11:
            raise serializers.ValidationError("CPF inválido")
        return cpf_limpo
    
    # 5 pontos - Validar Senhas
    def validate_senha(self, value):
        """
        Valida: 1 maiúscula, 1 minúscula, 1 caractere especial, 1 número.
        """
        if len(value) < 8:
            raise serializers.ValidationError("Senha deve ter no mínimo 8 caracteres")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos uma letra maiúscula.")
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos uma letra minúscula.")
        
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos um número.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos um caractere especial.")
            
        return value
    
    def create(self, validated_data):
        """Criar usuário (senha será hasheada pelo model)"""
        validated_data.pop('senha_confirmacao', None)
        return Usuario.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        '''
        Ao atualizar, verifica se a senha é diferente 
        '''
        if 'senha' in validated_data:
            if instance.verificar_senha(
                validated_data['senha']):
                # chamar o metodo verificar_senha do modelo
                # e passar a senha digitada
                raise serializers.ValidationError({
                    'senha': 'Nova senha não pode ser igual a anterior'
                })
        # atualizar senha do usuario
        for campo, valor in validated_data.items():
            setattr(instance, campo, valor)
        instance.save()
        return instance


# ============================================
# SERIALIZER DE LOGIN
# ============================================

class LoginSerializer(serializers.Serializer):
    """
    Serializer para login (não vinculado a model)
    """
    email = serializers.EmailField(required=True)
    senha = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_email(self, value):
        """Normalizar email"""
        return value.strip().lower()
    
    def validate(self, data):
        """
        Validar credenciais
        """
        email = data.get('email')
        senha = data.get('senha')
        
        # Buscar usuário
        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("Email ou senha inválidos")
        
        # Verificar senha (usando método do model)
        if not usuario.verificar_senha(senha):
            raise serializers.ValidationError("Email ou senha inválidos")
        
        # Adicionar usuário aos dados validados
        data['usuario'] = usuario
        return data


# ============================================
# SERIALIZER DE USUÁRIO (para respostas)
# ============================================

class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para retornar dados do usuário
    (SEM senha!)
    """
    class Meta:
        model = Usuario
        fields = ['id', 'nome', 'email', 'criado']
        read_only_fields = ['id', 'criado']

# 10 pontos - reset de senha
class SolicitarResetSenhaSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # Verifica se o usuário existe
        """
        Verifica se o usuário com o e-mail fornecido existe.
        
        Se o usuário não for encontrado, lança um erro.
        :param value: e-mail fornecido
        :return: e-mail validado
        :raises serializers.ValidationError: se o usuário não for encontrado
        """
        if not Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Usuário com este e-mail não encontrado.")
        return value

# 10 pontos - reset de senha
class ConfirmarResetSenhaSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    nova_senha = serializers.CharField(
        write_only=True, min_length=8, style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """
        Valida os dados fornecidos para reset de senha.

        Verifica se o ID do usuário (uidb64) é válido e se o token é
        válido para este usuário.

        :raises serializers.ValidationError: se o ID for inválido ou
            se o token for inválido ou expirado.
        """
        try:
            # Decodifica o ID do usuário
            uid = force_str(urlsafe_base64_decode(attrs['uidb64']))
            self.user = Usuario.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
            raise serializers.ValidationError({
                "token": "Token inválido ou link expirado."})

        # Verifica se o token é válido para este usuário
        if not default_token_generator.check_token(self.user, attrs['token']):
            raise serializers.ValidationError({"token": "Token inválido ou expirado."})

        return attrs

    # Reutiliza a validação de senha forte do CadastroSerializer
    def validate_nova_senha(self, value):
        """
        Valida a nova senha fornecida para reset de senha.

        Verifica se a senha for forte (contém maiúscula, minúscula, número e caractere especial).
        Se a senha for fraca, lança um erro.
        :param value: nova senha fornecida
        :return: nova senha validada
        :raises serializers.ValidationError: se a senha for fraca
        """
        import re
        if not re.search(r'[A-Z]', value) or not re.search(r'[a-z]', value) or \
           not re.search(r'[0-9]', value) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
             raise serializers.ValidationError("Senha fraca (Requer: Maiúscula, minúscula, número e especial)")
        return value

    def save(self):
        # Define a nova senha usando o método set_password (que faz o hash)
        self.user.set_password(self.validated_data['nova_senha'])
        self.user.save()
        return self.user
