from rest_framework import serializers
from .models import Produto, Categoria

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class ProdutoSerializer(serializers.ModelSerializer):

    categoria_nome = serializers.ReadOnlyField(source='categoria.nome')
    is_favorito = serializers.SerializerMethodField()
    class Meta:
        model = Produto
        fields = '__all__' # Pega todos os campos (nome, marca, preco, imagem, ativo...)
        read_only_fields = ['id', 'criado', 'atualizado']

    def get_is_favorito(self, obj):
        # Pega o usuário do contexto da requisição (quem está logado)
        """
        Retorna True se o produto for favorito do usuário, False caso contrário.
        """
        user = self.context.get('request').user
        if user and user.is_authenticated:
            # Verifica se o ID do produto está na lista de favoritos desse usuário
            return user.favoritos.filter(id=obj.id).exists()
        return False

    def validate_nome(self, value):
        """
        Validar nome do produto.
        
        O nome do produto deve ter no mínimo 3 caracteres.
        Se o nome for menor ou igual a 3 caracteres, lança um erro.
        :param value: nome do produto fornecido
        :return: nome do produto validado
        :raises serializers.ValidationError: se o nome for inválido
        """
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Nome deve ter no mínimo 3 caracteres")
        return value.strip()
    
    def validate_marca(self, value):
        """
        Validar marca do produto.
        
        A marca do produto deve ter no mínimo 3 caracteres.
        Se a marca for menor ou igual a 3 caracteres, lança um erro.
        :param value: marca do produto fornecida
        :return: marca validada
        :raises serializers.ValidationError: se a marca for inválida
        """
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Marca deve ter no mínimo 3 caracteres")
        return value.strip()

    def validate_preco(self, value):
        """
        Valida o preço fornecido e lança um erro se o preco for menor ou igual a zero.
        :param value: preco fornecido
        :return: preco validado
        :raises serializers.ValidationError: se o preco for inválido
        """
        if value <= 0:
            raise serializers.ValidationError("O preço deve ser maior que zero.")
        return value
    
    def validate_descricao(self, value):

        """
        Validar descrição do produto.
        
        A descri o do produto deve ter no mínimo 20 caracteres.
        Se a descri o for menor ou igual a 20 caracteres, lança um erro.
        :param value: descrição o do produto fornecida
        :return: descrição o validada
        :raises serializers.ValidationError: se a descrição o for inválida
        """
        if len(value) < 20:
            raise serializers.ValidationError("A descrição deve ter no mínimo 20 caracteres")
        return value
    
