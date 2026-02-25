// js/criar_produto.js

// Elementos do DOM
const form = document.getElementById('form-produto');
const selectCategoria = document.getElementById('categoria');
const msgDiv = document.getElementById('mensagem');

document.addEventListener('DOMContentLoaded', () => {
    // 1. Segurança: Verifica se está logado
    redirecionarSeNaoLogado();

    // 2. Carrega as opções do select
    carregarCategorias();
});

/**
 * Busca as categorias na API e preenche o <select>
 */
async function carregarCategorias() {
    // Reset visual
    selectCategoria.innerHTML = '<option value="">Carregando...</option>';

    const result = await apiFetch('/categorias/', 'GET');
    
    if (result.ok) {
        selectCategoria.innerHTML = '<option value="">Selecione uma categoria...</option>';
        
        // O DRF pode retornar array puro ou objeto paginado { results: [...] }
        const categorias = result.data.results ? result.data.results : result.data;
        
        categorias.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.id; // O valor enviado será o ID
            option.textContent = cat.nome;
            selectCategoria.appendChild(option);
        });
    } else {
        selectCategoria.innerHTML = '<option value="">Erro ao carregar categorias</option>';
        mostrarMensagem('Não foi possível carregar as categorias.', 'erro');
    }
}

/**
 * Evento de Envio do Formulário
 */
if (form) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Validação básica do select
        if (!selectCategoria.value) {
            mostrarMensagem('Por favor, selecione uma categoria.', 'erro');
            return;
        }

        mostrarMensagem('Enviando dados...', 'info');

        // Criação do FormData para envio de Arquivos + Texto
        const formData = new FormData();
        
        formData.append('nome', document.getElementById('nome').value);
        formData.append('marca', document.getElementById('marca').value);
        formData.append('preco', document.getElementById('preco').value);
        formData.append('descricao', document.getElementById('descricao').value);
        formData.append('categoria', selectCategoria.value);
        formData.append('ativo', 'true'); 
        
        // Verifica se há imagem selecionada
        const imagemInput = document.getElementById('imagem');
        if (imagemInput.files.length > 0) {
            formData.append('imagem', imagemInput.files[0]);
        }

        // Token necessário para POST
        const token = localStorage.getItem('accessToken');

        // Envia para API
        // O api.js detectará que é FormData e ajustará os headers automaticamente
        const result = await apiFetch('/produtos/', 'POST', formData, token);

        if (result.ok) {
            mostrarMensagem('Produto cadastrado com sucesso!', 'sucesso');
            // Redireciona após 1.5s
            setTimeout(() => {
                window.location.href = 'produtos.html';
            }, 1500);
        } else {
            console.error(result.data);
            
            // Tratamento de erros comuns do Django DRF
            let textoErro = 'Erro ao cadastrar produto.';
            if (result.data) {
                // Tenta pegar a primeira mensagem de erro disponível
                const chavesErro = Object.keys(result.data);
                if (chavesErro.length > 0) {
                    const campo = chavesErro[0];
                    const msg = result.data[campo];
                    textoErro = `${campo.toUpperCase()}: ${Array.isArray(msg) ? msg[0] : msg}`;
                }
            }
            mostrarMensagem(textoErro, 'erro');
        }
    });
}

/**
 * Função auxiliar para exibir mensagens na div #mensagem
 */
function mostrarMensagem(texto, tipo) {
    msgDiv.textContent = texto;
    msgDiv.className = `mensagem ${tipo}`; // ex: mensagem erro
    msgDiv.style.display = 'block';
}