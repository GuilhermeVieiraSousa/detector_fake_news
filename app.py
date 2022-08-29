from flask import Flask, render_template, session, request, redirect, url_for
# render_template renderizar html,
# session criar sessão
# request serve para a função saber se vai usar o método get ou post
# redirect vai verificar se a sessão é válida
# urk_for chama as funções definidas

#imports das valicações de campos
from validacao import idioma
from validacao import validacaoSenha
from validacao import validaçãoNome

#imports para os comando do banco de dados
from bd import verificaCadastro
from bd import cadastrado
from bd import loginBD
from bd import alterarEmail
from bd import alteraSenha
from bd import deletar
from bd import historicoBD
from bd import salvandoNoticia

#importe para predicao
from predicao import predicao
from predicao import WordsEmbeddings






#Conexão ao banco
from flask_mysqldb import MySQL 
import MySQLdb.cursors 



app = Flask(__name__)
 

#dados do banco
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'detectorFakeNews'

app.secret_key = 'criar_Uma_Chave'




mysql = MySQL(app)

@app.route("/", methods=['POST', 'GET'])
def home():  
      
    return render_template("home.html", usuario=session.get('nome')),200

@app.route("/cadastro", methods=['POST', 'GET'])
def cadastro():
    msg=''
    if(session):       
       return render_template("home.html")
    elif request.method == 'POST':        
        #criando variáveis
        nome = request.form['nomeCadastro']
        senha = request.form['senhaCadastro']
        senhaNovamente = request.form['senhaCadastroNovamente'] 
        email = request.form['emailCadastro']
        if verificaCadastro(email):
            msg="E-mail já cadastrado"
        elif validaçãoNome(nome)==False:
            msg='Nome de usuário não pode conter números'
        elif validacaoSenha(senha)==False:
            msg='Senha não atende aos requisitos mínimos'
        elif senha != senhaNovamente:
            msg = 'Senha diferentes digitadas'        
        else: 
            cadastrado(nome, email, senha)
            msg = 'Conta registrada'          
            return render_template('cadastro.html', msg=msg)      
    return render_template('cadastro.html', msg=msg) 
    
@app.route("/login", methods=['POST', 'GET'])
def login():
    msg = '' 
    if(session):
       return render_template("home.html")    
    elif request.method == 'POST':
        #criando variáveis pelo form 
        email = request.form['emailLogin'] 
        senha = request.form['senhaLogin']
        if loginBD(email, senha):
            return redirect(url_for('home'))       
        else: 
           msg = 'E-mail/Senha não encontrados!'
    return render_template('login.html', msg=msg)
    

@app.route("/alterarEmail", methods=['POST', 'GET'])
def alterar_email():
    if(not session):
        return render_template('home.html')
    #criando variáveis pelo form
    elif request.method == 'POST':
        emailSession = session.get('email')
        emailAtual = request.form['emailAntigo']    
        emailNovo = request.form['emailNovo']
        #Conectando ao banco
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if emailAtual and emailNovo: #verifica se os campos foram digitados           
            if alterarEmail(emailSession, emailAtual, emailNovo):
                msg = 'E-mail alterado com sucesso'
                return render_template('alterar_email.html', msg=msg, usuario=session.get('nome'))
            else:
                msg = 'E-mail não correspondente'
                return render_template('alterar_email.html', msg=msg, usuario=session.get('nome'))                
    return render_template("alterar_email.html", usuario=session.get('nome'))

@app.route("/alterarSenha", methods=['POST', 'GET'])
def alterar_senha():
    if(not session):
        return render_template('home.html')
    #criando variáveis pelo form
    elif request.method == 'POST':
        emailSession = session.get('email')
        senhaSession = session.get('senha')
        senhaAtual = request.form['senhaAntiga']
        emailSenha = request.form['emailSenha']
        senhaNova = request.form['senhaNova']        
        if emailSenha and senhaAtual and senhaNova:  #verifica se ps campos foram digitados          
            if(alteraSenha(emailSession,  emailSenha, senhaSession, senhaAtual, senhaNova)):
                msg = 'Senha alterada com sucesso'            
                return render_template('alterar_senha.html', msg=msg, usuario=session.get('nome'))
            else:
                msg = 'Senha ou E-mail não correspondente'
                return render_template('alterar_senha.html', msg=msg, usuario=session.get('nome'))     
    return render_template("alterar_senha.html", usuario=session.get('nome')) 

@app.route("/deletar", methods=['POST', 'GET'])
def deletar():
    if(not session):
        return render_template('home.html')
    #criando variáveis pelo form
    elif request.method == 'POST':
        emailSession = session.get('email')
        senhaSession = session.get('senha')
        email = request.form['emailDel'] 
        senha = request.form['senhaDel']
        if deletar(emailSession, email, senhaSession, senha): # se existir           
            msg = 'Conta deletada com sucesso'            
            return render_template('home.html', msg=msg, usuario=session.get('nome'))
        else:          
            msg = 'Dados incorretos'
            return render_template("deletar.html", msg=msg, usuario=session.get('nome')) 
    return render_template("deletar.html", usuario=session.get('nome'))    
   

@app.route("/historico", methods=['POST', 'GET'])
def historico():
    
    if(session):
                     
            return  render_template("historico.html", resultado = historicoBD(), usuario=session.get('nome'))
    return render_template("home.html")



@app.route('/sair', methods=['POST', 'GET'])
def sair_sessao():          
    session.pop('loggedin', None) 
    session.pop('id', None) 
    session.pop('nome', None)
    session.pop('email', None)
    session.pop('senha', None)
    session.pop('idEnvio', None)
    session.pop('email', None)     
    return redirect(url_for('login'))

@app.route('/esqueceu_senha', methods=['POST', 'GET'])
def esqueceu_senha():     
    if(session):
        return redirect(url_for('home'))
    if request.method == 'POST':
        #capturando dados do form
        emailCadastrado = request.form['emailCadastrado']
        nomeCadastrado = request.form['nomeCadastrado']
        senhaNovaCadastrada = request.form['senhaNovaCadastrada']
        #Conectando ao banco
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #Verificando cadastro pelo e-mail e senha
        cursor.execute('SELECT * FROM usuario WHERE email = % s AND nome = % s', (emailCadastrado, nomeCadastrado )) 
        account = cursor.fetchone()  #Capturando o primeiro resultado
        if account: # se existir 
            if validacaoSenha(senhaNovaCadastrada)==False:
                msg="Senha não atende os requisitos mínimos"
                cursor.close() #fechando conexão
                return render_template('alterar_senha.html', msg=msg, usuario=session.get('nome'))               
            cursor.execute('UPDATE usuario SET senha = % s WHERE email= % s AND nome = % s',(senhaNovaCadastrada, emailCadastrado, nomeCadastrado, ))
            mysql.connection.commit() #Registra o Update
            msg = 'Senha nova cadastrada com sucesso'
            cursor.close() #fechando conexão
            return render_template('esqueceu_senha.html', msg=msg)             
        else: 
            msg = 'Nenhuma encontrada com esse nome e e-mail'
            return render_template('esqueceu_senha.html', msg=msg)
    return render_template('esqueceu_senha.html')
    
@app.route('/analisando', methods=[ 'POST', 'GET'])
def analisando():

    # Pegando o texto dos forms
    noticia = request.form["areaNoticia"] 
    
    if idioma(noticia):
        msg='notícia não está em língua portuguesa'
        return render_template('home.html', msg=msg)

    # Fazendo previsão do texto 
    previsao = predicao(noticia)

    #Salvando notícia no BD
    salvandoNoticia(noticia, previsao)

   
   
    return render_template('home.html', msg=previsao, usuario=session.get('nome'))








