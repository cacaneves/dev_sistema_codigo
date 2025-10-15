from flask import Flask, request, jsonify

#cria um objeto flask, que vai ser o app
app = Flask(__name__)


app.config['JSON_AS_ASCII']=False
# se der errado, descomente o debaixo
# app.json.ensure.ascii = False
# usurio(id, nome, email, senha)
usuarios = [
    {'id':1, 'nome': 'Raphamel','email':'raphamengo@senai.br', 'senha':'Flamengo2019'},
    {'id':2, 'nome': 'David', 'email':'davidvarao@senai.br.br','senha':'varao123'},
    {'id':3,'nome':'Geovanni','email':'geovanni@senai.br','senha': 'PizzaoloTriocolor'}
]






# pq não estamos usando BD
# Ideia de autoincrement
proximo_id = 4


def validar_usuario(dados):
    # validar dados vindo das requisições
    # 3 retornos
    # 1-> se são validos (True)/False
    # 3 -> Dados validados
    # Existem dados no  JSON?
    if not dados:
        return False, "Corpo da requisição não pode ser vazio", None
    

    if 'nome' not in dados:
        return False, " Campo 'nome' é obrigatorio  ", None
    

    if not isinstance(dados['nome'], str):
        return False, "O campo 'nome'  deve ser textual", None
    
    nome = dados.get('nome', '').strip()

    # tenho o nome, o que eu quero validar?
    if not nome:
        return False, " Campo 'nome' não pode estar vazio", None
   
    # tamnho minimo 3 caracteres
    if len(nome) < 3:
        return False, "Campo 'nome' deve ter no mininmo 3 caracteres", None
    
    #---------------------------------------------------------------------
    # Se exixte o campo EMAIL no JSON
    if 'email' not in dados:
        return False, "Campo 'email' é obrigatório ", None
    
    if not isinstance(dados['email'], str):
        return False, "O campo 'email' ser textual", None
    
    if ('@' not in dados['email'] or '.' not in dados['email']):
        return False, "O email informado nã é válido", None
    
    email = dados.get('email', '').strip()

    if not email:
        return False, "Campo 'email' não pode estar vazio",None
    
    # Certeza- > Campo Email existe e  o email
    email_existente = [user for user in usuarios if email== user['email']]
    
    # verificar se há algum usuario com esse email
    if len(email_existente) > 0:
        return False, "Este email já está cadastrado", None
    
    #---------------------------------------------------------------------
    if 'senha'not in dados:
        return False, "Campo 'senha' é Obrigatório", None
    
    # senha já existe
    senha= dados.get('senha', '').strip()

    if not senha:
        return False, "Campo 'senha' não pode estar vazio", None
    
    if len(senha) < 8 and len(senha)> 50:
        return False, "Campo 'senha' com tamanho inválido", None
    
    dados_validados = {
        'nome': nome,
        'email': email,
        'senha': senha
    }
    return True, None, dados_validados
         

     
@app.route('/')
def home():
    return jsonify({
        'mg':"Bemvindo ao Geovanni's Pizza"})
# Rota Get - Listar usuario
@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    # recuperar os usuarios (sem senha)

    usuarios_sem_senha = []

    for usuario in usuarios:
        user = usuario.copy()
        user.pop('senha', None)
        usuarios_sem_senha.append(user)

    return jsonify({
        'dadps': usuarios_sem_senha,
        'total': len(usuarios)
    }) , 200

# POST -> Criar Usuarios
@app.route ('/usuarios', methods=['POST'])
def criar_usuario():

    global proximo_id

    valido, erro, dados_validados = validar_usuario(request.get_json())
    validar_usuario(request.get_json())

    # if valido == False é a mesma coisa que:
    if not valido:
        return jsonify({
            'erro': erro
        })
    
    novo_usuario = {
        'id': proximo_id,
        'nome': dados_validados['nome'],
        'email': dados_validados['senha'] 
    }
    usuarios.append(novo_usuario)
    # preparar proxima inserção
    proximo_id +=  1

    # já que não vamos mais usar novo_usuario
    # removeremos a senha dele para apresentar
    novo_usuario.pop('senha', None)

    return jsonify({
        'mensagem': 'Usuário criado com sucesso', 'usuario': novo_usuario
    }), 201

@app.route('/login', methods = ['POST'])
def login():
    dados = request.get_json()

    if not dados:
        return jsonify({
            'erro': 'Corpo da requisição não pode estar vazio'
        }), 400
    
    email = dados.get('email', '').strip().lower()
    senha = dados.get('senha', '').strip()

    if not email or not senha:
        return jsonify({
            'erro': 'Os campos de email e senha são obrigatórios'
        }), 400
    
    usuario = [user for user in usuarios if email == user ['email']]

    if len(usuario) < 1:
        return jsonify({
            'erro': 'Email ou senha inválidos'
        }), 400
    usuario = usuario[0]
    
    if  senha != usuario['senha']:
        return jsonify ({
            'erro':'Email ou senha inválidos'
        }), 400

    usuario.pop('senha', None)
    return jsonify({
        'mensagem':'Login realizado com sucesso',
        'usuario':usuario,
        'token': f"token_user_{usuario['id']}"
    }), 200
    
    

    #verificar
    # 1. Se há dados
    # 2. verificar se há email e senha
    # 3. verificar se o usuario
    # (email ou nome, vc escolhe ) esta cadastrado
    # 4. verificar se a senha esta igual

@app.route('/usuarios/<int:id_usuario>', methods=['DELETE'])
def deletar_usurio(id_usuario):

    global usuarios

    #  forma 1 -> caçar o usuario e remover
    #  forma 2 -> repetir a lista, exceto o usuario a ser removido

    # forma 2 
    qtd_usuario = len(usuarios)

    usuarios = [user for user in usuarios 
                if user ['id'] != id_usuario]
    
    if len(usuarios) == qtd_usuario:
        return jsonify({
            'erro':'Usurio informado não foi encontrado'
        }), 400
    
    return jsonify({
        'mensagem':'Usuário deletado com sucesso',
        'id_deletado': id_usuario
    }), 200

    # Atualizar -> 2 Metodos
    # 1. Put -> Atualiza completamente um usuario
    # 1.1 -> passar todas as informações
    # (se não quiser mudar,  passa de novo os dados antigos)
    # 2. Patch-> Atualiza parcialmente um usuario
    # 2.1 -> passar apenas os campos que voce deseja atuaalizar

@app.route('/usuarios/<int:id_usuario>', methods= ['PATCH'])
def atualizar_usuario(id_usuario):
    usuario = next((user for user in usuarios if user ['id']==id_usuario), None)
    
    if not usuario:
        return jsonify({
            'erro':'Usuário não encontrado'
        }), 404
    
    dados = request.get_json()

    if not dados:
        return jsonify({
            'erro':'Corpo da requisição não pode estar vazio'
        }), 400
    
    if 'nome' in dados:
        nome = dados['nome'].strip()
        if len(nome) < 3:
            return jsonify({
                'erro':'Nome deve ter mais que 3 caracteres'
            }), 400
        usuario['nome'] = nome

    if 'email' in dados:
        email = dados['email'].strip().lower()
        if ('@' not in dados['email']or
            '.' not in email):
            return jsonify({
                'erro':'O email informado não é válido'
            }), 400
    email_existente = next((user for user in usuarios if email == user ['email']), None)
    
    if email_existente:
        return jsonify({
            'erro':'Email já estás cadastrado'
        }), 400
    usuario ['email']= email

    if 'senha' in dados:
        senha = dados['senha'].strip()
        if not len(senha)> 8 or not len(senha)> 50:
            return jsonify({
                'erro':'A senha deve ter no mínimo 8 \
                    caracteres e no máximo 50'
            }), 400
        if senha == usuario['senha']:
            return jsonify({
                'erro':'A senha não pode ser igual\
                       a anterior '
            }), 400
        
        usuario['senha']= senha

    user = usuario.copy()
    user.pop('senha', None)

    return jsonify({
        'mensagem':'Usuario atualizado com sucesso',
        'usuario': user
    }), 200

        


#iniciar o servidor -> porta padrão 5000
if __name__== '__main__':
    app.run(debug=True)