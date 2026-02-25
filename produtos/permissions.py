from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permissão personalizada:
    - Qualquer um pode visualizar (GET, HEAD, OPTIONS).
    - Apenas administradores (is_staff=True) podem alterar (POST, PUT, DELETE).
    """
    def has_permission(self, request, view):
        # Se o método for seguro (apenas leitura), retorna True (permite)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Se for escrita, verifica se o usuário está logado E é staff (admin)
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)