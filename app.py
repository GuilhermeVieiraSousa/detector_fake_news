
from flask import Flask, render_template, session, request, redirect, url_for
# render_template renderizar html,
# session criar sessão
# request serve para a função saber se vai usar o método get ou post
# redirect vai verificar se a sessão é válida
# urk_for chama as funções definidas
import re #expressão regular

import pickle
#import para detecção da lígua do texto
from langdetect import detect 
#importe para retirar a acentuação das palavras
# usar antes pip install unidecode
import unidecode 
#Conexão ao banco
from flask_mysqldb import MySQL 
import MySQLdb.cursors 

#import para tratamento de dados
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

app = Flask(__name__)
 
#download stopwords
nltk.download("stopwords")

stopwords = set(stopwords.words('portuguese'))

#dados do banco
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'detectorFakeNews'

app.secret_key = 'criar_Uma_Chave'


# Load model and vectorizer
model = pickle.load(open('model2.pkl', 'rb'))
tfidfvect = pickle.load(open('tfidfvect2.pkl', 'rb'))
ps = PorterStemmer()


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
        if login(email, senha):
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
        return historico()
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

    #Conectando ao banco
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #Salvando no banco
    cursor.execute('INSERT INTO noticia(id_usuario, noticia, resultado) VALUES (% s, % s, % s) ORDER BY data_analise desc', (session.get('id'), noticia, previsao, )) 
    mysql.connection.commit() #gravando a informação no banco     
    cursor.close() #fechar conexão com o banco
   
    return render_template('home.html', msg=previsao, usuario=session.get('nome'))

################ Funções para validação de campos

#preprpocessamento e predição do texto
def predicao(text):
    portugues = nltk.corpus.stopwords.words('portuguese')
    preprocessando = unidecode.unidecode(text) 
    preprocessando = re.sub('[^a-zA-Z]', ' ', preprocessando) # Se tiver algo diferente de palavras, ele ira preencher com espaco em branco
    preprocessando = preprocessando.lower() # deixando tudo em minúcuslo
    preprocessando = preprocessando.split() # Separa a frase em uma lista de sentencas. 
    preprocessando = [ps.stem(word) for word in preprocessando if not word in portugues ] # retirando stopwords
    preprocessando = ' '.join(preprocessando) # deixando novamente em frases
    preprocessando_vect = tfidfvect.transform([preprocessando]).toarray()
    predicao = 'FAKE' if model.predict(preprocessando_vect) == 'fake' else 'TRUE'
    return predicao  

#identificando a lingua e só permitindo texto em língua portuguesa
def idioma(texto):
    analise = detect(texto)
    result = analise
    if result != 'pt':
        return True
    return False      

#Verifica se atendo todos os requisitor(letras maiúsculas e minúsculas, tenha números e pelo menos 8 caracteres)
def validacaoSenha(senha):
    if not re.match("(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])", senha):    
        return False    
    elif  len(senha) <8:
       return False
    return True  

#Não permite nome que tenha números 
def validaçãoNome(nome):
    if re.match(r'[0-9]+', nome):
        return False
    return True    



################## FUNÇÕES PARA COMANDO NO BANCO DE DADOS


def verificaCadastro(email):
    #conectando ao banco
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #verificando se usuário já existe
    cursor.execute('SELECT * FROM usuario WHERE email = % s', (email, ))
    account = cursor.fetchone() #guarda resultado encontrado
    if account: #caso já exista o cadastro do e-mail
        cursor.close() #fechar conexão com o banco
        return True
    cursor.close() #fechar conexão com o banco
    return False

def cadastrado(nome, email, senha):
    #conectando ao banco
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
     #executando comando de inserção
    cursor.execute('INSERT INTO usuario(nome, senha, email) VALUES (% s, % s, % s)', (nome, senha, email, )) 
    mysql.connection.commit() #gravando a informação no banco
    cursor.close()
    
def login(email,senha):
    #Conectando ao banco
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #Verificando cadastro pelo e-mail e senha
    cursor.execute('SELECT * FROM usuario WHERE email = % s AND senha = % s', (email, senha, )) 
    account = cursor.fetchone()  #Capturando o primeiro resultado
    if account: # se existir
        #criando sessões 
        session['loggedin'] = True
        session['id'] = account['id_usuario'] 
        session['nome'] = account['nome']
        session['email'] = account['email']
        session['senha'] = account['senha']
        cursor.close() #fechando conexão            
        return True
    cursor.close() #fechando conexão      
    return False    

def alterarEmail(emailSession, emailAtual, emailNovo):
    #Conectando ao banco
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if emailSession == emailAtual : #verificando se o e-mail da conta em uso é o mesmo que foi digitado               
        cursor.execute('UPDATE usuario SET email = % s WHERE email= % s',(emailNovo, emailAtual))
        mysql.connection.commit() #Registra o Update
        session['email'] = emailNovo  #atualizando a sessão        
        cursor.close() #fechando conexão
        return True
    else:
        cursor.close()
        return False

def alteraSenha(emailSession,  emailSenha, senhaSession, senhaAtual, senhaNova):
    if emailSession == emailSenha and senhaSession == senhaAtual: #verificando se o e-mail e a senha da conta em são os mesmos que foram digiados
        if validacaoSenha(senhaNova) == False:
            return False
        #Conectando ao banco
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE usuario SET senha = % s WHERE email= % s AND senha = % s',(senhaNova, emailSenha, senhaAtual, ))
        mysql.connection.commit() #Registra o Update
        session['senha'] = senhaNova #atualizando a sessão
        cursor.close() #fechando conexão
        return True
    return False

def deletar(emailSession, email, senhaSession, senha):
    if emailSession == email and senhaSession == senha: #verificando se o e-mail e a senha da conta em são os mesmos que foram digiados
        #Conectando ao banco
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #exluindo registro 
        cursor.execute('DELETE FROM usuario WHERE email = % s AND senha  = % s',(email, senha, ))
        mysql.connection.commit() #Registra o DELETE
        cursor.close() #fechando conexão
        #finalizando sessão
        session.pop('loggedin', None) 
        session.pop('id', None) 
        session.pop('nome', None)
        session.pop('email', None)
        session.pop('senha', None)
        return True
    return False

def historico():
    #Conectando ao banco
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    id_usuario = session.get('id')
    cursor.execute('SELECT noticia, resultado, data_analise FROM noticia WHERE id_usuario = % s ORDER BY data_analise desc',(id_usuario, ))
    resultado = cursor.fetchall()
    cursor.close() #fechar conexão com o banco
    return  render_template("historico.html", resultado = resultado, usuario=session.get('nome'))
