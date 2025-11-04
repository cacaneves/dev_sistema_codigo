const API_URL = "https://pokeapi.co/api/v2/pokemon/";

const form = document.querySelector("#formPokemon");

const input = document.querySelector("#nomePokemon");

const resultado = document.querySelector("#resultado");

form.addEventListener("submit", (event) => {
	event.preventDefault();

	const nome = input.value.trim().toLowerCase();
	// pegando o que o usuario digitou
	// tirando espaços em branco no inicio
	// e no fim e botando tudo em minusculo
	if (!nome) {
		resultado.innerHTML = "<h3>Por favor, digite um nome</h3>";
		return;
	}
	fetch(API_URL + nome)
		.then((response) => {
			if (!response.ok) {
				// se não foi okay
				throw new Error("Pokemon não encontrado");
			}
			return response.json();
		})
		.then((pokemon) => {
			const nomeFormatado =
				pokemon.name.charAt(0).toUpperCase() + pokemon.name.slice(1);
			// charAt(index) -> letra na posição
			// da string
			// slice(index) -> corta o vetor/string
			// repete o que esta a partir do index
			const tipos = pokemon.types.map((t) => t.type.name).join(", ");

			resultado.innerHTML = `
			<h2>${nomeFormatado} (#${pokemon.id}</h2>)
			<img src="${pokemon.sprites.front_default}"
			alt=${pokemon.name}>"
			<p>Tipo(s): ${tipos}</p>`;

			input.value = "";
		})
		.catch((erro)=>{
			resultado.innerHTML =
			`<p>${erro, message}</p>`
		})
});
