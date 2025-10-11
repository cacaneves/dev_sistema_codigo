from flask import Flask, request, jsonify

#cria um objeto flask, que vai ser o app
app = Flask(__name__)


app.config['JSON_AS_ASCII']=False
# se der errado, descomente o debaixo
# app.json.ensure.ascii = False
# usurio(id, nome, email, senha)
usuarios = [
    {'id':1, 'nome': 'Raphamel','emaiol':'raphamengo@senai.br', 'senha':'Flamengo2019'},
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
    
    email = dados.get('email', '').strip()

    if not email:
        return False, "Campo 'email' não pode estar vazio",None
    
    # Certeza- > Campo Email existe e  o email
    email_existente = [user for user in usuarios if email== user ['email']]
    
    # verificar se há algum usuario com esse email
    if len(email_existente) > 0:
        return False, "Este email já está cadastrado", None
    
    #---------------------------------------------------------------------
    if 'senha'not in dados:
        return False, "Campo 'senha' é Obrigatório", None
    
    # senha já existe
    senha= dados.get('swnha', '').strip()

    if not senha:
        return False, "Campo 'senha' não pode estar vazio", None
    
    if le(senha) < 8 and len(senha)> 50:
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



#iniciar o servidor -> porta padrão 5000
if __name__== '__main__':
    app.rim(debug=True)