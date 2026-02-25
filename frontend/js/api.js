// js/api.js

// URL do Backend Django (ajuste a porta se necessário, ex: 8000 ou 8080)
const BASE_URL = 'http://localhost:8080'; 


/**
 * Faz uma requisição HTTP para o Backend Django
 * @param {string} endpoint - URL do endpoint no Backend Django
 * @param {string} [method='GET'] - Método HTTP (GET, POST, PUT, DELETE, etc.)
 * @param {object} [body=null] - Corpo da requisição (JSON)
 * @param {string} [token=null] - Token de autenticação (JWT)
 * @returns {Promise} - Retorna uma promessa com o resultado da requisição
 * @example
 * apiFetch('usuarios/', 'GET')
 * @example
 * apiFetch('usuarios/', 'POST', { nome: 'Geovanni', email: 'pizza35reais@senai.br' })
 * @example
 * apiFetch('usuarios/', 'PUT', { nome: 'Geovanni', email: 'pizza35reais@senai.br' }, 'token-1234567890')
 */
async function apiFetch(endpoint, method = 'GET', body = null, token = null) {
    const headers = {};

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        method: method,
        headers: headers,
    };

    if (body) {
        // Se o body for FormData (envio de arquivo), o navegador define o Content-Type sozinho.
        // Se for um objeto comum, nós definimos como JSON.
        if (body instanceof FormData) {
            config.body = body;
        } else {
            headers['Content-Type'] = 'application/json';
            config.body = JSON.stringify(body);
        }
    }

    try {
        const response = await fetch(`${BASE_URL}${endpoint}`, config);
        
        // Tenta fazer o parse do JSON, mas trata caso venha vazio (ex: delete)
        let data = {};
        try {
            data = await response.json();
        } catch (e) {
            data = {};
        }

        return {
            ok: response.ok,
            status: response.status,
            data: data
        };
    } catch (error) {
        console.error('Erro na requisição:', error);
        return {
            ok: false,
            status: 500,
            data: { erro: 'Erro de conexão com o servidor' }
        };
    }
}

