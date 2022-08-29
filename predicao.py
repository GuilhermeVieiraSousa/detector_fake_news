
import pandas as pd
import numpy as np
import re #expressão regular
import pickle
#importe para retirar a acentuação das palavras
# usar antes pip install unidecode
import unidecode 
#import para tratamento de dados
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences


#download stopwords
nltk.download("stopwords")


stopwords = set(stopwords.words('portuguese'))


# Load model and vectorizer
model = pickle.load(open('model2.pkl', 'rb'))
tfidfvect = pickle.load(open('tfidfvect2.pkl', 'rb'))

classificacao = pickle.load(open('classificacao.pkl', 'rb'))
training_padded = pickle.load(open('training_padded.pkl', 'rb'))
ps = PorterStemmer()


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


def WordsEmbeddings(text):
    portugues = nltk.corpus.stopwords.words('portuguese')
    preprocessando = unidecode.unidecode(text) 
    
    preprocessando = re.sub('[^a-zA-Z]', ' ', preprocessando) # Se tiver algo diferente de palavras, ele ira preencher com espaco em branco
    preprocessando = preprocessando.lower() # deixando tudo em minúcuslo
    preprocessando = preprocessando.split() # Separa a frase em uma lista de sentencas. 
    preprocessando = [ps.stem(word) for word in preprocessando if not word in portugues ] # retirando stopwords
    preprocessando = ' '.join(preprocessando) # deixando novamente em frases
    #preprocessando = np.copy(training_padded)

    #Tokenização
    vocab_size = 10000
    trunc_type = "post"
    pad_type = "post"
    oov_tok = "<OOV>"

    tokenizer = Tokenizer(num_words = vocab_size, oov_token=oov_tok)
    
    tokenizer.fit_on_texts(preprocessando)
    word_index = tokenizer.word_index
    validation_sequences = tokenizer.texts_to_sequences(np.array(list(preprocessando)))
    validation_padded = pad_sequences(validation_sequences, padding=pad_type, truncating=trunc_type, maxlen = 4207)
    predicao = np.asarray(validation_padded)
    

    
    
    
    return classificacao.predict(predicao) 
    #return predicao


