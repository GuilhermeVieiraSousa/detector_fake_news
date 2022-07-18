from flask import Flask, render_template, session, request, redirect, url_for
# render_template renderizar html,
# session criar sessão
# request serve para a função saber se vai usar o método get ou post
# redirect vai verificar se a sessão é válida
# urk_for chama as funções definidas
import re #expressão regular
import pandas as pd
import joblib
import pickle

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
        email = request.form['emailCadastro']
        #conectando ao banco
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #verificando se usuário já existe
        cursor.execute('SELECT * FROM usuario WHERE email = % s', (email, ))
        account = cursor.fetchone() #guarda resultado encontrado
        if account: #caso já exista o cadastro do e-mail
            msg = 'E-mail já cadastrado !'
        elif re.match(r'[0-9]+', nome):
            msg='Nome de usuário não pode conter números'
        elif not  re.match(r'[A-Za-z0-9]+', senha) :
            msg='Senha não atende aos requisitos mínimos'       
        
        elif  len(senha) <8:
            msg='Senha precisa ter 8 caracteres ou mais'        
        else: 
            #executando comando de inserção
            cursor.execute('INSERT INTO usuario(nome, senha, email) VALUES (% s, % s, % s)', (nome, senha, email, )) 
            mysql.connection.commit() #gravando a informação no banco
            msg = 'Conta registrada'
            return render_template('cadastro.html', msg=msg)  
    else:
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
        #Conectando ao banco
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #Verificando cadastro pelo e-mail e senha
        cursor.execute('SELECT * FROM usuario WHERE email = % s AND senha = % s', (email, senha, )) 
        account = cursor.fetchone()  #Capturando o primeiro resultado
        if account: # se existir 
            session['loggedin'] = True
            session['id'] = account['id_usuario'] 
            session['nome'] = account['nome']
            session['email'] = account['email']
            session['senha'] = account['senha']            
            
            return redirect(url_for('home'))
        else: 
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)
    

@app.route("/alterar", methods=['POST', 'GET'])
def alterar():
    if(not session):
        return render_template('home.html')
    #criando variáveis pelo form
    elif request.method == 'POST':
        emailSession = session.get('email')
        senhaSession = session.get('senha')
        emailAtual = request.form['emailAntigo'] 
        senhaAtual = request.form['senhaAntiga']
        emailSenha = request.form['emailSenha']
        emailNovo = request.form['emailNovo']
        senhaNova = request.form['senhaNova']
        #Conectando ao banco
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if emailAtual and emailNovo and not senhaAtual or not senhaNova:            
            if emailSession == emailAtual :                
                cursor.execute('UPDATE usuario SET email = % s WHERE email= % s',(emailNovo, emailAtual))
                mysql.connection.commit() #Registra o Update
                msg = 'E-mail alterado com sucesso'
                return render_template('alterar.html', msg=msg)
            else:
                msg = 'E-mail não correspondente'
                return render_template('alterar.html', msg=msg)
        elif emailSenha and senhaAtual and senhaNova and not emailAtual or not emailNovo:            
            if emailSession == emailSenha and senhaSession == senhaAtual:                
                cursor.execute('UPDATE usuario SET senha = % s WHERE email= % s AND senha = % s',(senhaNova, emailSenha, senhaAtual, ))
                mysql.connection.commit() #Registra o Update
                msg = 'Senha com sucesso'
                return render_template('alterar.html', msg=msg)
            else:
                msg = 'Senha não correspondente'
                return render_template('alterar.html', msg=msg)
        msg = 'Campos faltantes ou para alterar o e-mail, digite apenas área "Alterar e-mail" e para senha digite apenas na área "Alterara senha" '
        return render_template("alterar.html", msg)     
    return render_template("alterar.html") 

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
        #Conectando ao banco
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        if emailSession == email and senhaSession == senha: # se existir
            #exluindo registro 
            cursor.execute('DELETE FROM usuario WHERE email = % s AND senha  = % s',(email, senha, ))
            mysql.connection.commit() #Registra o DELETE
            msg = 'Conta deletada com sucesso'
            #finalizando sessão
            session.pop('loggedin', None) 
            session.pop('id', None) 
            session.pop('nome', None)
            session.pop('email', None)
            session.pop('senha', None)
            return render_template('home.html', msg=msg)
        else:          
            msg = 'Dados incorretos'
            return render_template("deletar.html", msg=msg) 
    return render_template("deletar.html")    
   

@app.route("/historico", methods=['POST', 'GET'])
def historico():
    if(session):
       return render_template("historico.html")
    return render_template("home.html")


#rota de teste para sair da ssessão
@app.route('/sair', methods=['POST', 'GET'])
def sair_sessao():          
    session.pop('loggedin', None) 
    session.pop('id', None) 
    session.pop('nome', None)
    session.pop('email', None)
    session.pop('senha', None)     
    return redirect(url_for('login'))

@app.route('/analisando', methods=[ 'POST', 'GET'])
def analisando():

    #carregando arquico pkl
    analise = joblib.load("model_lr.pkl")
    

    # pegando valor pelo input
    noticia = request.form["areaNoticia"]
    
    # criando dataframe
    X = pd.DataFrame([[noticia]], columns = ["noticias"])
        
    # fazendo analise preditiva
    previsao = analise.predict(X)[0]      
    
   
    return render_template('home.html', msg=previsao)
   