from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

# 10 pontos - reset de senha
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from .serializers import SolicitarResetSenhaSerializer, ConfirmarResetSenhaSerializer

from .models import Usuario
from .serializers import UsuarioSerializer, CadastroSerializer, LoginSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para usuários com cadastro e login
    """

    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    # 10 pontos - soft delete
    def get_queryset(self):
        """
        Retorna queryset com todos os usuários se o usuário for admin,
        se não retorna queryset com usuários ativos.
        """
        if (
            self.request.user.is_authenticated
            and self.request.user.email == "admin@email.com"
        ):
            return Usuario.objects.all()

        return self.queryset.filter(ativo=True)

    def get_permissions(self):
        """
        Define permissões por action

        - cadastro e login: público (AllowAny)
        - list e retrieve: público (AllowAny)
        - update, partial_update, destroy: precisa estar autenticado
        """
        if self.action in ["cadastro", "login", "list", "retrieve", "refresh_token"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    # ============================================
    # ACTION: CADASTRO
    # ============================================

    @action(
        detail=False,
        methods=["post"],
        url_path="cadastro",
        serializer_class=CadastroSerializer,
    )
    def cadastro(self, request):
        """
        POST /usuarios/cadastro/

        Cadastra um novo usuário.

        Body:
        {
            "nome": "João Silva",
            "email": "joao@example.com",
            "senha": "senha12345678"
        }

        Resposta (201):
        {
            "mensagem": "Usuário cadastrado com sucesso",
            "usuario": {
                "id": 1,
                "nome": "João Silva",
                "email": "joao@example.com",
                "criado": "2024-11-17T10:00:00Z"
            }
        }
        """
        serializer = CadastroSerializer(data=request.data)

        if serializer.is_valid():
            # Criar usuário (senha será hasheada automaticamente)
            usuario = serializer.save()

            return Response(
                {
                    "mensagem": "Usuário cadastrado com sucesso",
                    "usuario": UsuarioSerializer(usuario).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response({"erro": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # ============================================
    # ACTION: LOGIN
    # ============================================

    @action(
        detail=False,
        methods=["post"],
        url_path="login",
        serializer_class=LoginSerializer,
    )
    def login(self, request):
        """
        POST /usuarios/login/

        Faz login de um usuário.

        Body:
        {
            "email": "joao@example.com",
            "senha": "senha12345678"
        }

        Resposta (200):
        {
            "mensagem": "Login realizado com sucesso",
            "usuario": {
                "id": 1,
                "nome": "João Silva",
                "email": "joao@example.com",
                "criado": "2024-11-17T10:00:00Z"
            }
            "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",  ← TOKEN DE ACESSO
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."  ← TOKEN DE REFRESH
        }
        """
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            # Pegar usuário validado
            usuario = serializer.validated_data["usuario"]

            refresh = RefreshToken.for_user(usuario)
            access = refresh.access_token

            return Response(
                {
                    "mensagem": "Login realizado com sucesso",
                    "usuario": UsuarioSerializer(usuario).data,
                    "access": str(access),  # Token de acesso
                    "refresh": str(refresh),  # Token de refresh
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"erro": serializer.errors}, status=status.HTTP_401_UNAUTHORIZED
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="perfil",
        permission_classes=[IsAuthenticated],
    )
    def perfil(self, request):
        """
        GET /perfil/
        Retorna as informações do perfil do usuário autenticado

        Resposta (200):
        {
            "id": 1,
            "nome": "João Silva",
            "email": "joao@example.com",
            "criado": "2024-11-17T10:00:00Z"
        }
        """
        user_id = request.auth.payload.get("user_id")

        try:
            usuario = Usuario.objects.get(id=user_id)
            serializer = UsuarioSerializer(usuario)
            return Response(serializer.data)
        except Usuario.DoesNotExist:
            return Response(
                {"erro": "Usuário não encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

    # ============================================
    # ACTION: LOGOUT
    # ============================================
    # 5 pontos - logout api
    @action(
        detail=False,
        methods=["post"],
        url_path="logout",
        permission_classes=[IsAuthenticated],
    )
    def logout(self, request):
        """
        Invalida o Refresh Token do usuário (Blacklist).
        Necessário: 'BLACKLIST_AFTER_ROTATION = True' no settings.
        """
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"erro": "Refresh token é obrigatório"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"mensagem": "Logout realizado com sucesso"},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            return Response(
                {"erro": "Token inválido ou erro ao realizar logout"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # Adicione authentication_classes=[] para garantir que o Django
    # não tente validar o token expirado no header da requisição
    @action(
        detail=False,
        methods=["post"],
        url_path="refresh",
        permission_classes=[AllowAny],
        authentication_classes=[],
    )
    def refresh_token(self, request):
        refresh_token_str = request.data.get("refresh")

        if not refresh_token_str:
            return Response({"erro": "Refresh token obrigatório"}, status=400)

        try:
            # 1. Tenta decodificar o token
            refresh = RefreshToken(refresh_token_str)

            # 2. Busca o usuário
            user_id = refresh["user_id"]
            usuario = Usuario.objects.get(id=user_id)

            # 3. Gera novo Access Token manualmente
            from rest_framework_simplejwt.tokens import AccessToken

            new_access_token = AccessToken.for_user(usuario)

            return Response({"access": str(new_access_token)})

        except Usuario.DoesNotExist:
            print(f"ERRO REFRESH: Usuário ID {user_id} não encontrado.")
            return Response({"erro": "Usuário não encontrado"}, status=401)
        except TokenError as e:
            print(f"ERRO REFRESH: Token inválido. Detalhe: {e}")
            return Response({"erro": "Token inválido ou expirado"}, status=401)
        except Exception as e:
            print(f"ERRO REFRESH GERAL: {e}")
            return Response({"erro": "Erro interno na renovação"}, status=400)

    def partial_update(self, request, pk=None):
        usuario = self.get_object()

        # comparar com request.user, não com payload
        if usuario.id != request.user.id:
            return Response(
                {"erro": "Você só pode atualizar seu próprio perfil"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = CadastroSerializer(usuario, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "mensagem": "Usuário atualizado com sucesso",
                    "usuario": UsuarioSerializer(usuario).data,
                }
            )

        return Response({"erro": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # 10 pontos - soft delete
    def destroy(self, request, pk=None):
        """
        DELETE /usuarios/<pk>/
        Só permite deletar o próprio perfil
        """
        usuario = self.get_object()

        # Verificar se é o próprio usuário
        user_id_from_token = request.auth.payload.get("user_id")
        if usuario.id != user_id_from_token:
            return Response(
                {"erro": "Você só pode deletar seu próprio perfil"},
                status=status.HTTP_403_FORBIDDEN,
            )
        # soft delete
        usuario.ativo = False
        usuario.save()
        nome = usuario.nome
        # usuario.delete()

        return Response(
            {"mensagem": f"Usuário {nome} deletado com sucesso"},
            status=status.HTTP_200_OK,
        )


# 10 pontos - password reset
class PasswordResetViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    # O queryset é exigido pelo DRF para viewsets genéricos, mas não será usado diretamente aqui.
    # Definimos como none() apenas para evitar erros de validação do router.
    queryset = Usuario.objects.none()

    def get_serializer_class(self):
        """
        Retorna o serializer_class apropriado para a ação.

        'solicitar' retorna SolicitarResetSenhaSerializer,
        'confirmar' retorna ConfirmarResetSenhaSerializer,
        e qualquer outro valor retorna o serializer_class padrão.
        """
        if self.action == "solicitar":
            return SolicitarResetSenhaSerializer
        if self.action == "confirmar":
            return ConfirmarResetSenhaSerializer
        return super().get_serializer_class()

    # Rota gerada: POST /api/password-reset/solicitar/
    @action(detail=False, methods=["post"], url_path="solicitar")
    def solicitar(self, request):
        """
        POST /api/password-reset/solicitar/

        Solicita a recuperação de senha.

        Body:
        {
            "email": "joao@example.com"
        }

        Resposta (200):
        {
            "mensagem": "E-mail de recuperação enviado."
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = Usuario.objects.get(email=email)

        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        # Link apontando para o seu Frontend
        reset_link = (
            f"http://127.0.0.1:5500/reset_senha.html?uid={uidb64}&token={token}"
        )

        mensagem = f"Olá {user.nome},\n\nPara redefinir sua senha, clique no link:\n{reset_link}"
        # 5 pontos extras
        send_mail(
            "Recuperação de Senha - Docelar",
            mensagem,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return Response({"mensagem": "E-mail de recuperação enviado."})

    # Rota gerada: POST /api/password-reset/confirmar/
    @action(detail=False, methods=["post"], url_path="confirmar")
    def confirmar(self, request):
        """
        POST /api/password-reset/confirmar/

        Confirma a recuperação de senha.

        Body:
        {
            "uidb64": "MzQ2MzI1NDI0Njg=",
            "token": "5a7a6f55-690e-4fc2-b078-3a866e9624b",
            "nova_senha": "nova_senha123456"
        }

        Resposta (200):
        {
            "mensagem": "Senha alterada com sucesso"
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"mensagem": "Senha alterada com sucesso!"})
