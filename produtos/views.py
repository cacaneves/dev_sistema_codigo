from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import Produto, Categoria
from .serializers import ProdutoSerializer, CategoriaSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

# para alterar as permissoes, usar o permissions.py
# from .permissions import IsAdminOrReadOnly

class CategoriaViewSet(viewsets.ModelViewSet):
    serializer_class = CategoriaSerializer
    queryset = Categoria.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

class ProdutoViewSet(viewsets.ModelViewSet):
    serializer_class = ProdutoSerializer
    # Qualquer um lê (GET), só logado altera (POST, PUT, DELETE)
    permission_classes = [IsAuthenticatedOrReadOnly]

    # caso for só admin/staff
    # permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        # Implementando o Soft Delete (Extra): Só traz os ativos
        # 10 pontos - soft delete
        queryset = Produto.objects.filter(ativo=True)
        
        # Implementando Filtros/Lookups (Requisito de Produtos)
        marca = self.request.query_params.get('marca')
        nome = self.request.query_params.get('nome')
        categoria = self.request.query_params.get('categoria')
        categoria_nome = self.request.query_params.get('categoria_nome')
        if marca:
            queryset = queryset.filter(marca__iexact=marca)
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        if categoria:
            queryset = queryset.filter(categoria__id=categoria)
        if categoria_nome:
            queryset = queryset.filter(categoria__nome__icontains=categoria_nome)
            
        return queryset

    #extra, soft delete, 10 pontos
    def perform_destroy(self, instance):
        """
        Soft Delete: desativa o produto, mas o mantem no banco.
        """
        # 10 pontos - soft delete
        instance.ativo = False
        instance.save()
    
    # 20 pontos - favoritar/desfavoritar produtos
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def favoritar(self, request, pk=None):
        """
        Adiciona ou remove o produto dos favoritos (Toggle).
        Se já curtiu, descurte. Se não curtiu, curte.
        """
        produto = self.get_object() # Pega o produto pelo ID da URL
        user = request.user         # Pega o usuário logado pelo Token

        if user.favoritos.filter(id=produto.id).exists():
            user.favoritos.remove(produto)
            return Response({
                'mensagem': 'Produto removido dos favoritos.', 
                'favoritado': False}, 
                status=status.HTTP_200_OK)
        else:
            user.favoritos.add(produto)
            return Response({
                'mensagem': 'Produto adicionado aos favoritos!', 
                'favoritado': True}, 
                status=status.HTTP_200_OK)

    # Rota: GET /api/produtos/meus_favoritos/
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='meus-favoritos')
    def meus_favoritos(self, request):
        """
        Lista apenas os produtos favoritados pelo usuário logado.
        """
        user = request.user
        favoritos = user.favoritos.filter(ativo=True) # Só mostra favoritos que ainda estão ativos no sistema
        
        # Paginação padrão do ViewSet
        page = self.paginate_queryset(favoritos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(favoritos, many=True)
        return Response(serializer.data)