from django.shortcuts import render
from django.http import JsonResponse
from usuarios.models import Usuario


def home(request):
    """
    Rota principal da API, retorna uma mensagem de boas-vindas
    e a versão da API.
    """
    return JsonResponse({
        'mensagem': "Bem vindo ao Geovanni's Pizza - Django Version",
        'versao': '1.0'
    })


def listar_usuarios(request):
    # Passo 1: ir no banco e trazer os usuarios
    
	usuarios = Usuario.objects.all()
	dados = []
	for usuario in usuarios:
		dados.append({
			'id': usuario.id,
			'nome': usuario.nome,
			'email': usuario.email,
			'criado':usuario.criado.isoformat()
		})
            
	return JsonResponse({
		'usuarios': dados,
		'total': len(dados)
	})