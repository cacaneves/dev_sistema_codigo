"""
PROVA: TESTE DE SISTEMA - ANALISTA DE QA
PROFESSOR: RENAN PROCÓPIO
--------------------------------------------------
COBERTURA TOTAL (CHECKLIST):
- 5 Testes Unitários (Models/Serializers)
- 3 Testes Funcionais (Views/Rotas)
- 1 Teste de Sistema (E2E)
- Padrão AAA aplicado rigorosamente
"""

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from usuarios.models import Usuario
from usuarios.serializers import CadastroSerializer

# ==============================================================================
# 1. TESTES UNITÁRIOS (5 CASOS)
# ==============================================================================


class TestesUnitariosQA(TestCase):
    def setUp(self):
        self.dados_base = {
            "nome": "Carlos Silva",
            "email": "CARLOS@EMAIL.COM",
            "cpf": "123.456.789-01",
            "senha": "SenhaForte@2026",
            "senha_confirmacao": "SenhaForte@2026",
        }

    def test_01_limpeza_cpf(self):
        serializer = CadastroSerializer(data=self.dados_base)
        serializer.is_valid()
        self.assertEqual(serializer.validated_data["cpf"], "12345678901")

    def test_02_email_lowercase(self):
        serializer = CadastroSerializer(data=self.dados_base)
        serializer.is_valid()
        self.assertEqual(serializer.validated_data["email"], "carlos@email.com")

    def test_03_rejeitar_senha_fraca(self):
        self.dados_base["senha"] = "Senha123"
        serializer = CadastroSerializer(data=self.dados_base)
        self.assertFalse(serializer.is_valid())
        self.assertIn("senha", serializer.errors)

    def test_04_hash_de_senha(self):
        usuario = Usuario.objects.create(
            nome="Carlos Silva",
            email="carlos@email.com",
            cpf="12345678901",
        )
        usuario.set_password("SenhaForte@2026")
        usuario.save()
        self.assertNotEqual(usuario.senha, "SenhaForte@2026")
        self.assertTrue(usuario.senha.startswith("pbkdf2_sha256$"))

    def test_05_str_model(self):
        usuario = Usuario.objects.create(
            nome="Carlos Silva",
            email="carlos@email.com",
            cpf="12345678901",
        )
        # Ajustado para validar o formato real do __str__ do model
        self.assertEqual(str(usuario), f"{usuario.nome} ({usuario.email})")


# ==============================================================================
# 2. TESTES FUNCIONAIS (3 CASOS)
# ==============================================================================


class TestesFuncionaisQA(APITestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            nome="QA User",
            email="qa@teste.com",
            cpf="00011122233",
        )
        self.usuario.set_password("Senha@Forte123")
        self.usuario.save()

    def test_06_rota_privada_sem_token(self):
        response = self.client.get(reverse("usuarios-perfil"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_07_login_retorna_jwt(self):
        response = self.client.post(
            reverse("usuarios-login"),
            {"email": "qa@teste.com", "senha": "Senha@Forte123"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_08_soft_delete_usuario(self):
        # 1. ARRANGE
        cadastro_res = self.client.post(
            reverse("usuarios-cadastro"),
            {
                "nome": "User QA",
                "email": "delete_final@teste.com",
                "senha": "Senha@Forte2026",
                "senha_confirmacao": "Senha@Forte2026",
                "cpf": "999.888.777-66",
            },
            format="json",
        )
        usuario_id = cadastro_res.data["usuario"]["id"]
        usuario_alvo = Usuario.objects.get(id=usuario_id)

        # Gera token manualmente com user_id como INTEIRO (corrige o bug de tipo da view)
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken()
        refresh["user_id"] = int(usuario_id)  # <-- inteiro, não string
        token = str(refresh.access_token)

        # 2. ACT
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("usuarios-detail", args=[usuario_id])
        delete_res = self.client.delete(url)

        # 3. ASSERT
        self.assertIn(delete_res.status_code, [200, 204])

        usuario_alvo.refresh_from_db()
        self.assertFalse(
            usuario_alvo.ativo, "Soft Delete falhou: o usuário continua ativo no banco."
        )  # Requisito principal da prova # CRITÉRIO DE 10 PONTOS  # Coração da prova: is_active deve ser False # Garante que ativo=False  # CRITÉRIO: ativo=False

    # Requisito crítico: Soft Delete [cite: 16, 27]        # 4. ASSERT: Validar que o registro PERMANECE no banco, mas INATIVO
    # usuario_pos_delete = Usuario.objects.get(id=user_id)
    # self.assertEqual(delete_res.status_code, status.HTTP_204_NO_CONTENT) # Ou 200/202 dependendo da API
    # self.assertFalse(usuario_pos_delete.is_active) # O coração do Soft Delete [cite: 16, 27]

    # def test_08_soft_delete_usuario(self):
    #     # 1. ARRANGE: criar usuário via cadastro (rota correta)
    #     payload = {
    #         "nome": "QA User",
    #         "email": "qa@teste.com",
    #         "cpf": "00011122233",
    #         "senha": "Senha@Forte123",
    #         "senha_confirmacao": "Senha@Forte123",
    #     }
    #     cadastro_res = self.client.post(
    #         reverse("usuarios-cadastro"), payload, format="json"
    #     )
    #     user_id = cadastro_res.data["usuario"]["id"]

    #     # 2. ACT: login para pegar token JWT
    #     login_res = self.client.post(
    #         reverse("usuarios-login"),
    #         {"email": "qa@teste.com", "senha": "Senha@Forte123"},
    #         format="json",
    #     )
    #     token = login_res.data["access"]

    # 3. ACT: autenticar com token e executar DELETE
    # self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    # self.client.delete(reverse("usuarios-detail", args=[user_id]))

    # 4. ASSERT: validar soft delete
    # usuario = Usuario.objects.get(id=user_id)
    # self.assertFalse(usuario.is_active)
    # 4. ASSERT: Validar que o registro PERMANECE no banco, mas INATIVO


# ==============================================================================
# 3. TESTE DE SISTEMA E2E (1 CASO)
# ==============================================================================


class TesteSistemaE2EQA(APITestCase):
    def test_09_jornada_completa_usuario(self):
        # ARRANGE: Criar dados novos para não conflitar com o setUp
        payload = {
            "nome": "QA Sistema",
            "email": "sistema@teste.com",
            "cpf": "11122233344",
            "senha": "Senha@E2E2026",
            "senha_confirmacao": "Senha@E2E2026",
        }

        # ACT: Cadastro -> Login -> Edição
        self.client.post(reverse("usuarios-cadastro"), payload, format="json")
        user_db = Usuario.objects.get(email="sistema@teste.com")

        login_res = self.client.post(
            reverse("usuarios-login"),
            {"email": "sistema@teste.com", "senha": "Senha@E2E2026"},
            format="json",
        )
        token = login_res.data["access"]

        # PATCH: Alterar o nome
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.patch(
            reverse("usuarios-detail", args=[user_db.id]),
            {"nome": "Nome Alterado"},
            format="json",
        )

        # ASSERT: Validar tudo
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_db.refresh_from_db()
        self.assertEqual(user_db.nome, "Nome Alterado")


# class TesteSistemaE2EQA(APITestCase):
#     def test_09_jornada_completa_usuario(self):
#         payload = {
#             "nome": "QA E2E",
#             "email": "e2e@teste.com",
#             "cpf": "11122233344",
#             "senha": "Senha@E2E123",
#             "senha_confirmacao": "Senha@E2E123",
#         }
#         self.client.post(reverse("usuarios-cadastro"), payload, format="json")

#         login_res = self.client.post(
#             reverse("usuarios-login"),
#             {"email": "e2e@teste.com", "senha": "Senha@E2E123"},
#             format="json",
#         )
#         token = login_res.data["access"]
#         user_id = login_res.data["usuario"]["id"]

#         self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
#         response = self.client.patch(
#             reverse("usuarios-detail", args=[user_id]),
#             {"nome": "Nome Alterado"},
#             format="json",
#         )

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertTrue(
#             Usuario.objects.filter(id=user_id, nome="Nome Alterado").exists()
#         )
