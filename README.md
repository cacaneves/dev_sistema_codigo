# projeto_django

Projeto final completo da materia Dev de Sistemas, Senai 2025
usuario/
├── tests/
│   ├── test_unit_usuario.py
│   ├── test_funcional_usuario.py
│   └── test_sistema_usuario.py

# Suíte de Testes Automatizados — Sistema de Gestão de Usuários
>
> **Avaliação Prática (AV2) — Teste de Sistema**  
> Curso Técnico em Desenvolvimento de Sistemas · SENAI  
> Instrutor: Renan Procópio Duarte · Turno: Noite  

---

## Visão Geral

Este repositório contém a suíte de testes automatizados desenvolvida como Analista de QA para o backend de API da **SoftwareHouse SENAI**, um sistema de gestão de usuários com autenticação JWT.

O código-base testado está disponível em: [https://github.com/Rproc/projeto_django](https://github.com/Rproc/projeto_django)

---

## Instalação e Execução

### Pré-requisitos

- Python 3.10+
- Virtualenv

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/Rproc/projeto_django
cd projeto_django

# 2. Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute todos os testes
python manage.py test usuarios.tests.test_unit_usuario -v 2
```

### Resultado esperado

```
Found 9 test(s).
Ran 9 tests in ~3.2s
OK
```

---

## Documentação dos Testes Implementados

### Grupo 1 — Testes Unitários (`TestCase`)
>
> Focados isoladamente nos **Serializers** e **Models**, sem dependência de rede ou views.

| # | Nome do Teste | Requisito Coberto | Assertiva Principal |
|---|---------------|-------------------|---------------------|
| 01 | `test_01_senha_fraca_rejeitada` | Regras de Senha — rejeitar senhas sem maiúsculas, minúsculas, números ou caracteres especiais | `assertIn('senha', errors)` |
| 02 | `test_02_cpf_limpo_ao_salvar` | Validação de Dados — remover formatação do CPF antes de persistir | `assertEqual(cpf_salvo, '99988877766')` |
| 03 | `test_03_email_normalizado_lowercase` | Validação de Dados — normalizar e-mail para letras minúsculas | `assertEqual(email_salvo, 'usuario@teste.com')` |
| 04 | `test_04_senha_salva_como_hash` | Regras de Senha — garantir que a senha nunca é armazenada em texto puro | `assertNotEqual(usuario.senha, '...')` + `assertTrue(usuario.senha.startswith('pbkdf2'))` |
| 05 | `test_05_str_representation` | Model — método `__str__` retorna representação correta | `assertEqual(str(usuario), 'Nome (email@teste.com)')` |

---

### Grupo 2 — Testes Funcionais (`APITestCase`)
>
> Focados nas **Views** e **Rotas**, validando integração cliente-servidor via requisições HTTP reais.

| # | Nome do Teste | Requisito Coberto | Assertiva Principal |
|---|---------------|-------------------|---------------------|
| 06 | `test_06_acesso_anonimo_negado` | Segurança de Rotas — rota `/perfil/` deve retornar 401 sem token | `assertEqual(response.status_code, 401)` |
| 07 | `test_07_login_retorna_tokens_jwt` | Autenticação — login bem-sucedido deve retornar tokens `access` e `refresh` | `assertIn('access', data)` + `assertIn('refresh', data)` |
| 08 | `test_08_soft_delete_usuario` | Soft Delete — exclusão deve desativar o usuário (`ativo=False`) sem removê-lo do banco | `assertFalse(usuario.ativo)` |

---

### Grupo 3 — Teste de Sistema / E2E (`APITestCase`)
>
> Valida o **ciclo de vida completo** do usuário em uma única transação contínua.

| # | Nome do Teste | Fluxo Coberto | Assertiva Principal |
|---|---------------|---------------|---------------------|
| 09 | `test_09_jornada_completa_usuario` | Cadastro → Login → Autenticação (Header JWT) → Edição de Perfil (PATCH) | `assertEqual(usuario.nome, novo_nome)` — valida persistência no banco, não apenas o status code |

---

## Padrão de Organização — AAA

Todos os testes seguem estritamente o padrão **Arrange · Act · Assert**:

```python
def test_exemplo(self):
    # ARRANGE — prepara dados e estado inicial
    usuario = Usuario(email="teste@exemplo.com", ...)

    # ACT — executa a ação sendo testada
    response = self.client.post(reverse("usuarios-login"), {...})

    # ASSERT — verifica o resultado esperado
    self.assertIn("access", response.data)
    self.assertEqual(response.status_code, 200)
```

---

## Bugs Identificados e Corrigidos na View

Durante o desenvolvimento da suíte de testes, foram identificados dois bugs no código-base (`usuarios/views.py`) que impediam a execução correta dos testes funcionais.

---

### Bug 1 — Incompatibilidade de tipos na comparação do `destroy`

**Localização:** `views.py`, método `destroy`, linha ~277  

**Descrição:**  
O SimpleJWT, ao gerar tokens para modelos que não herdam de `AbstractBaseUser`, serializa o `user_id` no payload como **string**. A view comparava esse valor diretamente com `usuario.id`, que é um **inteiro** — fazendo `2 != '2'` sempre resultar em `True` e retornar `403 Forbidden` para qualquer requisição de exclusão.

```python
# Comportamento original — sempre retornava 403
user_id_from_token = request.auth.payload.get('user_id')  # '2' (str)
if usuario.id != user_id_from_token:                       # 2 != '2' → True
    return Response({'erro': '...'}, status=403)
```

**Solução aplicada no teste:**  
O token foi gerado manualmente no Arrange, forçando `user_id` como inteiro:

```python
from rest_framework_simplejwt.tokens import RefreshToken
refresh = RefreshToken()
refresh["user_id"] = int(usuario_id)  # garante tipo inteiro
token = str(refresh.access_token)
```

---

### Bug 2 — Atribuição a `@property` sem setter no `destroy`

**Localização:** `views.py`, método `destroy`, linha ~284  

**Descrição:**  
O método `destroy` tentava desativar o usuário através de `usuario.is_active = False`. Porém, `is_active` no model `Usuario` é declarado como `@property` somente leitura (retorna `self.ativo`), sem setter definido. Isso gerava um `AttributeError` em tempo de execução, impedindo a conclusão do soft delete.

```python
# Código original — lança AttributeError
usuario.is_active = False  # ❌ property sem setter
```

**Correção aplicada na view:**

```python
# Correção — acessa o campo real do banco diretamente
usuario.ativo = False  # ✅
usuario.save()
```

---

## Resultado Final

```
Found 9 test(s).
......... 
Ran 9 tests in 3.213s
OK
```

**Todos os 9 casos de teste passaram com sucesso.**
python manage.py test usuarios.tests.test_unit_usuario
