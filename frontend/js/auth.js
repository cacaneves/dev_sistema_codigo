// js/auth.js

const KEY_ACCESS = 'accessToken';
const KEY_REFRESH = 'refreshToken';

// ==========================================
// GERENCIAMENTO DE TOKENS
// ==========================================

/**
 * Verifica se o usuário está autenticado.
 * 
 * @returns {boolean} true se o usuário estiver autenticado, false caso contrário
 */
function isAuthenticated() {
    return !!localStorage.getItem(KEY_ACCESS);
}

/**
 * Salva os tokens de acesso e refresh no localStorage.
 * 
 * @param {string} access - Token de acesso
 * @param {string} refresh - Token de refresh
 * @returns {undefined} undefined
 */
function salvarTokens(access, refresh) {
    localStorage.setItem(KEY_ACCESS, access);
    localStorage.setItem(KEY_REFRESH, refresh);
}

/**
 * Remove os tokens de acesso e refresh do localStorage.
 * 
 * @returns {undefined} undefined
 */
function limparTokens() {
    localStorage.removeItem(KEY_ACCESS);
    localStorage.removeItem(KEY_REFRESH);
}

/**
 * Faz o logout do usuário.
 * 
 * Remove os tokens de acesso e refresh do localStorage.
 * 
 * @returns {Promise} Uma promessa resolvida com undefined.
 */
async function logout() {
    // 5 pontos - (3 extras, linkar logout api com frontend)
    const refresh = localStorage.getItem(KEY_REFRESH);
    const token = localStorage.getItem(KEY_ACCESS);

    // Se tiver um refresh token, avisa a API para invalidá-lo
    if (refresh && token) {
        try {
            // Não precisamos esperar o resultado (await), apenas enviamos.
            // Se der erro (ex: token já inválido), continuamos o logout local.
            await apiFetch('/usuarios/logout/', 'POST', { refresh: refresh }, token);
            console.log("Token invalidado na API com sucesso.");
        } catch (error) {
            console.warn("Erro ao tentar invalidar token na API (pode já estar expirado).");
        }
    }

    // De qualquer forma, limpa os dados do navegador
    limparTokens();
}

// ==========================================
// AÇÕES DE API (LOGIN, CADASTRO, PERFIL)
// ==========================================

/**
 * Faz o login do usuário com email e senha.
 * 
 * @param {string} email - Email do usuário.
 * @param {string} senha - Senha do usuário.
 * @returns {Promise} Um objeto com a resposta da API.
 * Se a resposta for OK, o token de acesso é salvo no localStorage.
 */
async function login(email, senha) {
    const result = await apiFetch('/usuarios/login/', 'POST', { email, senha });
    
    if (result.ok) {
        salvarTokens(result.data.access, result.data.refresh);
    }
    return result;
}

/**
 * Cadastra um novo usuário.
 * @param {Object} dados - Dados do usuário.
 * @param {string} dados.nome - Nome do usuário.
 * @param {string} dados.email - Email do usuário.
 * @param {string} dados.senha - Senha do usuário.
 * @param {string} dados.senha_confirmacao - Confirma a senha do usuário.
 * @returns {Promise} Resposta da API com o novo usuário.
 */
async function cadastrar(dados) {
    // dados deve conter: nome, email, senha, senha_confirmacao
    return await apiFetch('/usuarios/cadastro/', 'POST', dados);
}


/**
 * Tenta acessar o perfil do usuário com o token atual.
 * Se o token tiver expirado (401), tenta renovar o token.
 * Se o token for renovado com sucesso, tenta acessar o perfil de novo com o novo token.
 * Se falhou ao renovar, desloga o usuário.
 * @returns {Promise} Resposta da API com o perfil do usuário.
 */
async function getPerfil() {
    // Pega o token atual
    const token = localStorage.getItem(KEY_ACCESS);
    
    // 1. Tenta acessar com o token atual
    let result = await apiFetch('/usuarios/perfil/', 'GET', null, token);

    // 2. Se der 401 (Não autorizado), tenta renovar o token
    if (result.status === 401) {
        console.log("Token expirado. Tentando renovar...");
        const renovado = await renovarToken();
        
        if (renovado) {
            // 3. Se renovou, tenta acessar o perfil de novo com o novo token
            const novoToken = localStorage.getItem(KEY_ACCESS);
            result = await apiFetch('/usuarios/perfil/', 'GET', null, novoToken);
        } else {
            // Se falhou ao renovar, desloga o usuário
            logout();
        }
    }

    return result;
}


/**
 * Renova o token de acesso do usuário logado.
 * 
 * Se o usuário tem um token de refresh, este método
 * chama o endpoint de refresh e salva o novo token
 * de acesso.
 * 
 * @returns {Promise<boolean>} True se o token for renovado, false caso contrário.
 */
async function renovarToken() {
    const refresh = localStorage.getItem(KEY_REFRESH);
    if (!refresh) return false;

    // Chama seu endpoint customizado de refresh
    const result = await apiFetch('/usuarios/refresh/', 'POST', { refresh: refresh });

    if (result.ok) {
        // Salva o novo access token (mantém o refresh antigo)
        localStorage.setItem(KEY_ACCESS, result.data.access);
        return true;
    } else {
        return false;
    }
}

// ==========================================
// REDIRECIONAMENTOS
// ==========================================

/**
 * Redireciona para a página de perfil se o usuário estiver logado.
 * @returns {void} Nada, apenas redireciona.
 */
function redirecionarSeLogado() {
    if (isAuthenticated()) {
        window.location.href = 'perfil.html';
    }
}

/**
 * Redireciona para a página de login se o usuário não estiver logado.
 * @returns {void} Nada, apenas redireciona.
*/
function redirecionarSeNaoLogado() {
    if (!isAuthenticated()) {
        window.location.href = 'login.html';
    }
}


