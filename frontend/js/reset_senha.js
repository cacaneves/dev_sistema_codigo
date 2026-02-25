// js/recuperacao.js

document.addEventListener('DOMContentLoaded', () => {
    // Tenta inicializar a lógica de cada página
    configurarEsqueciSenha();
    configurarResetSenha();
});

/**
 * Lógica da página esqueci_senha.html
 */
function configurarEsqueciSenha() {
    const formEsqueci = document.getElementById('form-esqueci');
    
    // Se o formulário não existir nesta página, não faz nada
    if (!formEsqueci) return;

    formEsqueci.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const msgDiv = document.getElementById('mensagem');
        const btn = e.target.querySelector('button');

        // Feedback visual
        msgDiv.style.display = 'none';
        btn.disabled = true;
        btn.textContent = "Enviando...";

        // Chama a rota de SOLICITAR do backend
        // Ajuste a URL se necessário (ex: /password-reset/solicitar/)
        const result = await apiFetch('/password-reset/solicitar/', 'POST', { email: email });

        btn.disabled = false;
        btn.textContent = "Enviar Link";

        if (result.ok) {
            msgDiv.textContent = "Verifique seu e-mail (ou o console do servidor) para continuar.";
            msgDiv.className = "mensagem info";
            msgDiv.style.display = "block";
        } else {
            let erro = "E-mail não encontrado ou erro no servidor.";
            if (result.data && result.data.erro) erro = result.data.erro;
            
            msgDiv.textContent = erro;
            msgDiv.className = "mensagem erro";
            msgDiv.style.display = "block";
        }
    });
}

/**
 * Lógica da página reset_senha.html
 */
function configurarResetSenha() {
    const formReset = document.getElementById('form-reset');

    // Se o formulário não existir nesta página, não faz nada
    if (!formReset) return;

    // 1. Pega os parâmetros da URL
    const urlParams = new URLSearchParams(window.location.search);
    const uid = urlParams.get('uid');
    const token = urlParams.get('token');
    const msgDiv = document.getElementById('mensagem');

    // Validação inicial do link
    if (!uid || !token) {
        msgDiv.innerHTML = "Link inválido ou incompleto. Solicite novamente.";
        msgDiv.className = "mensagem erro";
        msgDiv.style.display = "block";
        formReset.querySelector('button').disabled = true;
        return;
    }

    formReset.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const novaSenha = document.getElementById('nova_senha').value;

        msgDiv.textContent = "Atualizando senha...";
        msgDiv.className = "mensagem info";
        msgDiv.style.display = "block";

        const dados = {
            uidb64: uid,
            token: token,
            nova_senha: novaSenha
        };

        const result = await apiFetch('/password-reset/confirmar/', 'POST', dados);

        if (result.ok) {
            msgDiv.textContent = "Senha alterada com sucesso! Redirecionando...";
            msgDiv.className = "mensagem sucesso";
            
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
        } else {
            let erro = "Erro ao alterar senha.";
            
            // Tratamento de erros do Django (Token inválido ou validação de senha)
            if (result.data) {
                if (result.data.token) erro = "Link expirado ou inválido.";
                else if (result.data.nova_senha) erro = result.data.nova_senha[0];
                else if (result.data.detail) erro = result.data.detail;
            }
            
            msgDiv.textContent = erro;
            msgDiv.className = "mensagem erro";
        }
    });
}