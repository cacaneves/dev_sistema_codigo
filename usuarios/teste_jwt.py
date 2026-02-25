import requests

# Configurações
BASE_URL = "http://localhost:8080"
EMAIL = "teste_dev@email.com"  # Mude o email se rodar mais de uma vez
SENHA = "senhaForte123"

def main():
    print("--- 1. TENTATIVA DE CADASTRO ---")
    payload_cadastro = {
        "nome": "Usuario Dev",
        "email": EMAIL,
        "senha": SENHA,
        "senha_confirmacao": SENHA
    }
    resp = requests.post(f"{BASE_URL}/usuarios/cadastro/", json=payload_cadastro)
    print(f"Status: {resp.status_code}")
    print(resp.json())

    print("\n--- 2. LOGIN ---")
    payload_login = {"email": EMAIL, "senha": SENHA}
    resp = requests.post(f"{BASE_URL}/usuarios/login/", json=payload_login)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code != 200:
        print("Erro ao logar. Encerrando.")
        return

    tokens = resp.json()
    access = tokens.get('access')
    refresh = tokens.get('refresh')
    print(f"Access Token obtido: {bool(access)}")
    print(f"Refresh Token obtido: {bool(refresh)}")

    print("\n--- 3. ACESSAR PERFIL (COM TOKEN) ---")
    headers = {'Authorization': f'Bearer {access}'}
    resp = requests.get(f"{BASE_URL}/usuarios/perfil/", headers=headers)
    print(f"Status: {resp.status_code}")
    print(resp.json())

    print("\n--- 4. ACESSAR PERFIL (SEM TOKEN) ---")
    resp = requests.get(f"{BASE_URL}/usuarios/perfil/")
    print(f"Status: {resp.status_code} (Esperado: 401)")

    print("\n--- 5. REFRESH TOKEN ---")
    resp = requests.post(f"{BASE_URL}/usuarios/refresh/", json={'refresh': refresh})
    print(f"Status: {resp.status_code}")
    
    novo_access = resp.json().get('access')
    
    if novo_access:
        print("\n--- 6. TESTE COM NOVO TOKEN ---")
        headers['Authorization'] = f'Bearer {novo_access}'
        resp = requests.get(f"{BASE_URL}/usuarios/perfil/", headers=headers)
        print(f"Status final: {resp.status_code}")
        print("Dados:", resp.json())
    else:
        print("Falha ao renovar token.")
        print(resp.json())

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("Erro: O servidor não está rodando em localhost:8080")