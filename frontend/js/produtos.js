// js/produtos.js

const listaDiv = document.getElementById('lista-produtos');
const inputBusca = document.getElementById('busca');
const loadingDiv = document.getElementById('loading');

document.addEventListener('DOMContentLoaded', () => {
    carregarProdutos();
});

let timeoutBusca;
if (inputBusca) {
    inputBusca.addEventListener('input', (e) => {
        clearTimeout(timeoutBusca);
        timeoutBusca = setTimeout(() => {
            carregarProdutos(e.target.value);
        }, 500);
    });
}

async function carregarProdutos(termo = '') {
    listaDiv.innerHTML = '';
    loadingDiv.style.display = 'block';

    let url = '/produtos/';
    if (termo) {
        url += `?nome=${termo}`;
    }

    // Importante: Passar o token para o backend saber quem é o usuário e retornar o "is_favorito" correto
    const token = localStorage.getItem('accessToken');
    const result = await apiFetch(url, 'GET', null, token);
    
    loadingDiv.style.display = 'none';

    if (result.ok) {
        renderizarProdutos(result.data);
    } else {
        listaDiv.innerHTML = '<p style="color: white; text-align: center;">Erro ao carregar produtos.</p>';
    }
}

function renderizarProdutos(dados) {
    const produtos = dados.results ? dados.results : dados;

    if (produtos.length === 0) {
        listaDiv.innerHTML = '<p style="color: white; text-align: center;">Nenhum produto encontrado.</p>';
        return;
    }

    produtos.forEach(produto => {
        let imgUrl = produto.imagem || 'https://placehold.co/600x400?text=Sem+Foto';
        const catNome = produto.categoria_nome || 'Geral';
        
        // Lógica do Coração: Se is_favorito for true, usa coração cheio, senão vazio
        const iconeCoracao = produto.is_favorito ? '❤️' : '🤍';
        
        const card = document.createElement('div');
        card.className = 'card-produto';
        card.innerHTML = `
            <div class="img-container">
                <img src="${imgUrl}" alt="${produto.nome}">
                <button class="btn-favorito" onclick="toggleFavorito(${produto.id})" title="Favoritar">
                    ${iconeCoracao}
                </button>
            </div>
            <div class="info-produto">
                <span class="categoria-tag">${catNome}</span>
                <h3>${produto.nome}</h3>
                <p class="descricao">${produto.descricao}</p>
                <div class="preco">R$ ${parseFloat(produto.preco).toFixed(2)}</div>
            </div>
        `;
        listaDiv.appendChild(card);
    });
}

// Função chamada ao clicar no coração
async function toggleFavorito(id) {
    const token = localStorage.getItem('accessToken');
    if (!token) {
        alert("Faça login para favoritar produtos!");
        return;
    }

    // Chama a API
    const result = await apiFetch(`/produtos/${id}/favoritar/`, 'POST', {}, token);

    if (result.ok) {
        // Recarrega a lista para atualizar a cor do coração
        // (Passamos o valor atual da busca para não perder o filtro)
        carregarProdutos(inputBusca ? inputBusca.value : '');
    } else {
        alert("Erro ao favoritar.");
    }
}


/**
 * Carrega APENAS os produtos favoritados pelo usuário
 */
async function carregarFavoritos() {
    const token = localStorage.getItem('accessToken');
    if (!token) {
        alert("Faça login para ver seus favoritos!");
        return;
    }

    listaDiv.innerHTML = '';
    loadingDiv.style.display = 'block';
    
    // Limpa o campo de busca visualmente para indicar que é uma lista especial
    if(inputBusca) inputBusca.value = '';

    // Chama a rota específica que criamos no backend (action 'meus_favoritos')
    // O DRF converte o nome da função (meus_favoritos) para URL com hífen (meus-favoritos)
    const result = await apiFetch('/produtos/meus-favoritos/', 'GET', null, token);
    
    loadingDiv.style.display = 'none';

    if (result.ok) {
        // Reaproveitamos a mesma função de renderizar!
        renderizarProdutos(result.data);
        
        if ((result.data.results && result.data.results.length === 0) || result.data.length === 0) {
            listaDiv.innerHTML = '<p style="color: white; text-align: center; width: 100%; font-size: 1.2em;">Você ainda não tem favoritos.</p>';
        }
    } else {
        listaDiv.innerHTML = '<p style="color: white; text-align: center;">Erro ao carregar favoritos.</p>';
    }
}