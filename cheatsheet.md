# Cheatsheet flask e sqlalchemy

# Flask
Vi permette di creare applicazioni web.

## Definire una rotta
Con `@app.route` definisco una rotta e ci associo una funzione. Quello che rispondo (usando il `return` della funzione) è ciò che viene visualizzato nel browser.
```python
@app.route("/hello")
def hello():
    return "Hello, World!"
```

## Rispondere con HTML
Con `render_template` posso restituire un file HTML. 
```python
@app.route("/hello")
def hello():
    return render_template("hello.html")
```

In questo caso `hello.html` deve essere presente nella cartella `templates` che si trova nella stessa cartella del file Python.
```html
<html>
 <h1>Hello, World!</h1>
</html>
```

## Passare variabili al template
Posso passare variabili al template con `render_template` e poi usarle nel file HTML. Gliene posso passare quante ne voglio, con la sintassi `nome_variabile=valore_variabile`.
```python
@app.route("/hello")
def hello():
    nome = "Gigi"
    return render_template("hello.html", nome=nome)
```

Con `{{ nome }}` posso usare la variabile `nome` nel file HTML. 
```html
<html>
 <h1>Hello, {{ nome }}!</h1>
</html>
```

## Passare liste ed elaborarle nel template
Spesso ho bisogno di passare una lista al template. Ad esempio una lista di prodotti etc, per visualizzarli in un elenco.
```python
@app.route("/prodotti")
def prodotti():
    prodotti = [{"id": 1, "nome": "Banana"}, {"id": 2, "nome": "Pasta"}, {"id": 3, "nome": "Pizza"}]
    return render_template("prodotti.html", prodotti=prodotti)
```
Nel file HTML posso usare un ciclo `for` per visualizzare gli elementi della lista. Usando la sintassi `{% for prodotto in prodotti %}` posso iterare su ogni elemento della lista `prodotti`, con `{% endfor %}` chiudo il ciclo.
```html
<html>
 <h1>Prodotti</h1>
 <ul>
 {% for prodotto in prodotti %}
    <li>{{ prodotto.nome }}</li>
 {% endfor %}
 </ul>
</html>
```
Oltre al `for` è utile anche il `if`, per fare delle condizioni. Ad esempio, se voglio visualizzare solo i prodotti che hanno un certo id.
```html
<html>
 <h1>Prodotti</h1>
 <ul>
 {% for prodotto in prodotti %}
    {% if prodotto.id == 1 %}
        <li>{{ prodotto.nome }}</li>
    {% endif %}
 {% endfor %}
 </ul>
</html>
```
## Creare un form
Posso creare un form in HTML per inviare dati al server. Ad esempio, un form per registrare un nuovo prodotto.
```html
<html>
 <h1>Registrazione prodotto</h1>
 <form action="/nuovo_prodotto" method="POST">
    <label for="nome">Nome:</label>
    <input type="text" name="nome">
    <input type="number" name="prezzo">
    <input type="submit" value="Registrati">
 </form>
</html>
```
Dentro Flask dovrò prendere i dati del form inviato, in questo caso solo per le richieste che hanno il metodo `POST`
```python
@app.route("/nuovo_prodotto", methods=["POST"])
def nuovo_prodotto():
    nome = request.form["nome"]
    prezzo = request.form["prezzo"]
    # Una volta che ho i dati posso salvarli nel database
    prodotto = Prodotto(nome=nome, prezzo=prezzo) # Dichiaro l'oggetto da salvare
    session.add(prodotto) # Aggiungo l'oggetto alla sessione
    session.commit() # Salvo le modifiche nel database
    return render_template("successo.html")
```
Per ogni `input` del form, posso prendere il suo valore associato con request.form["nome_input"]. `nome_input` è il valore dell'attributo HTML `name` dell'input. Quindi ad esempio per prendere il valore di:
```html
<input type="text" name="nome">
```
Posso usare `request.form["nome"]`.
```python
@app.route("/nuovo_prodotto", methods=["POST"])
def nuovo_prodotto():
    nome = request.form["nome"]
    # Una volta che ho i dati posso salvarli nel database
    prodotto = Prodotto(nome=nome) # Dichiaro l'oggetto da salvare
    session.add(prodotto) # Aggiungo l'oggetto alla sessione
    session.commit() # Salvo le modifiche nel database
    return render_template("successo.html")
```

# SQLAlchemy
SQLAlchemy è un ORM (Object Relational Mapper) che permette di interagire con il database in modo più semplice e intuitivo, senza dover scrivere query SQL a mano.
## Setup iniziale
```python
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///database.db")
Session = sessionmaker(bind=engine)
session = Session()
```
## Creare una tabella
Per creare una tabella sul database, creo una classe che estende `Base` e definisco gli attributi della tabella come variabili di classe. 
```python
class Prodotto(Base):
    __tablename__ = "prodotto" # Il nome della tabella sul database
    id = Column(Integer, primary_key=True) # La chiave primaria della tabella, di solito è un intero autoincrementante chiamato "id"
    # Posso definire quante colonne voglio, dandogli un tipo e un nome, in questo caso ho solo "nome" e "prezzo", una stringa e un intero
    nome = Column(String)
    prezzo = Column(Integer)
```
## Creare il database
Dopo aver definito le tabelle posso creare il database, uso il metodo `create_all` di `Base.metadata`, passando l'engine che ho creato prima.
```python
Base.metadata.create_all(engine)
```
## Aggiungere un oggetto al database
Per aggiungere un oggetto al database, creo un oggetto della classe che ho definito prima e lo aggiungo alla sessione. Poi salvo le modifiche con `session.commit()`.
```python
prodotto = Prodotto(nome="Banana", prezzo=1)
session.add(prodotto)
session.commit()
```
## Leggere gli oggetti dal database
Per leggere gli oggetti dal database, uso il metodo `query` della sessione. Posso filtrare i risultati con `filter` e usare `all()` per prendere tutti gli oggetti che soddisfano la condizione, altrimenti posso usare `first()` per prendere solo il primo oggetto che soddisfa la condizione.
```python
prodotti = session.query(Prodotto).filter(Prodotto.nome == "Banana").all()
prodotto_unico = session.query(Prodotto).filter(Prodotto.nome == "Banana").first()
for prodotto in prodotti:
    print(prodotto.nome, prodotto.prezzo)
```

# Come usarli insieme
Flask serve per "interagire con il browser", mentre SQLAlchemy serve per interagire con il database. Mettendoli insieme potete creare qualsiasi applicazione web.
In generale, il flusso di lavoro è:
1. Definisco le tabelle in base alla descrizione del progetto, le tabelle sono i dati che voglio salvare in modo persistente, per esempio prodotti, ordini, utenti, etc.
2. Creo le rotte in Flask, che servono per "interagire" con il browser, ad esempio per visualizzare i prodotti, registrare un nuovo prodotto, etc.
3. Nelle rotte uso SQLAlchemy per interagire con il database, ad esempio per salvare un nuovo prodotto, leggere i prodotti dal database, etc.
4. Uso i template HTML per visualizzare i dati nel browser, ad esempio per visualizzare la lista dei prodotti, il form di registrazione, etc.



## Esempio
```python
# Setup iniziale di python e flask
from flask import Flask, render_template, request
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
Base = declarative_base()
engine = create_engine("sqlite:///database.db") # database.db è il nome che sto dando al database, posso anche darne uno diverso
Session = sessionmaker(bind=engine)
session = Session()
# Definizione della tabella
class Prodotto(Base):
    __tablename__ = "prodotto"
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    prezzo = Column(Integer)

# Creazione del database
Base.metadata.create_all(engine)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/prodotti")
def prodotti():
    # Leggo i prodotti dal database e li passo al template
    # Posso usare anche il filtro per prendere solo i prodotti che mi interessano
    # Ad esempio, se voglio prendere solo i prodotti con prezzo maggiore di 10
    # prodotti = session.query(Prodotto).filter(Prodotto.prezzo > 10).all()
    prodotti = session.query(Prodotto).all()
    return render_template("prodotti.html", prodotti=prodotti)

@app.route("/nuovo_prodotto", methods=["POST", "GET"])
def nuovo_prodotto():
    # Accetto sia richieste di tipo GET che POST usando methods=["POST", "GET"], se non viene specificato il metodo, di default accetta solo GET
    # Se è una richiesta GET, restituisco il form di creazione
    if request.method == "GET":
        return render_template("nuovo_prodotto.html") # Ritorno il form di creazione prodotto
    # Se è una richiesta POST, prendo i dati del form e li salvo nel database
    nome = request.form["nome"]
    prezzo = request.form["prezzo"]
    prodotto = Prodotto(nome=nome, prezzo=prezzo)
    # Aggiungo il prodotto alla sessione, posso aggiungere quanti oggetti voglio, anche di tipo diverso
    session.add(prodotto)
    # Salvo le modifiche nel database
    session.commit()
    # Ritorno una pagina di successo
    return render_template("successo.html")
```

Ci andiamo a creare un file HTML per ogni rotta che abbiamo creato, ad esempio:
```html
<!-- Questo è il nostro index.html -->
<html>
 <h1>Benvenuto nel nostro negozio!</h1>
 <a href="/prodotti">Visualizza i prodotti</a>
 <a href="/nuovo_prodotto">Crea un prodotto</a>
</html>
```
```html
<!-- Questo è il nostro prodotti.html -->
<html>
 <h1>Prodotti</h1>
 <ul>
 {% for prodotto in prodotti %}
    <li>{{ prodotto.nome }} - {{ prodotto.prezzo }}</li>
 {% endfor %}
 </ul>
</html>
```html
```html
<!-- Questo è il nostro nuovo_prodotto.html -->
<html>
 <h1>Creazione prodotto</h1>
 <form action="/nuovo_prodotto" method="POST">
    <input type="text" name="nome">
    <input type="number" name="prezzo">
    <input type="submit" value="Registrati">
 </form>
</html>
```html
<!-- Questo è il nostro successo.html -->
<html>
 <h1>Prodotto creato con successo!</h1>
 <a href="/prodotti">Visualizza i prodotti</a>
</html>
```