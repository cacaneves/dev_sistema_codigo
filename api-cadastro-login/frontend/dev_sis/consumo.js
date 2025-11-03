const API_URL = "https://jsonplaceholder.typicode.com/users";

const btn = document.querySelector("#btnCarregar");

const listaUsuarios = document.querySelector("#listaUsuarios");

btn.addEventListener(
	"click", //function(){}
	() => {
		fetch(API_URL)
			// Faz a requisição http
			.then((response) => response.json())
			// Converter a resposta em JSON
			.then((usuarios) => {
				// função para exibir esses dados
				// escrever em uma lista
				listaUsuarios.innerHTML = "";
				// Limpar a lista antes de escrever
				usuarios.forEach((usuario) => {
					// adicionar na lista
					// primeiro passo é criar um <li>
					let item = document.createElement("li");
					item.textContent = `${usuario.name} | ${usuario.email}`;
					listaUsuarios.appendChild(item);
				});
			})
			.catch((erro) => {
				// alert("Erro ao buscar Usuarios: " + erro);
				console.error("Erro ao buscar Usuarios: ", erro);
				listaUsuarios.innerHTML = "<li>Erro ao buscar usuarios</li>";
			});
	}
);


