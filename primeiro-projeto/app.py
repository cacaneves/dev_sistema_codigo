from flask import Flask
# importando a Class Flask do modulo flask

# criar uma instancia do Flask = objeto
app = Flask(__name__)
#__name__ é o nome do modulo atual -> navegaçaõ

# Definir Rotas  (Endpoints)
# quando acessar ao servidor, chame essa função

@app.route('/')
def home():
    return 'Ola mundo'


@app.route('/sobre')
def sobre():
    return 'Estamos na aula de Dev de Sistema Estamos aprendendo Excel com Flask'


@ app.route('/contato')
def contato():
    return '21 9999-9999\n'\
     'email: ta_dificil@dev_sistemas.senai.br'

 # Rota com parâmetro  
@app.route('/usuario/<nome>')
def usuario(nome):
    return f'Prezado, {nome} espero que essa mensagem o encontre bem'


# Rota com parâmetro numérico
@app.route('/produto/<int:id>')
def produto(id):
    return f'Você escolheu o produto com {id}'

# flask ele converte string em um resposta HTTP

# executar o servidor
if __name__ == '__main__':
    app.run(debug=True)
    # debug -> srvidor no modo de desenvolvimento
    # ativa o reload automatico e mostra
    # os erros de forma detalhada

