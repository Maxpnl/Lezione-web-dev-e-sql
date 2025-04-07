---
marp: true
---
# Da cosa è composto un applicativo web
- Un **server web** che accetta richieste e risponde a richieste HTTP
    - Può essere sviluppato usando qualsiasi linguaggio e framework dedicati
    - Esempi: Flask, Django, Node.js, Ruby on Rails
- Un **database** che memorizza i dati dell'applicazione
    - Può essere relazionale (SQL) o non relazionale (NoSQL)
    - Esempi di DB relazionali: Postgres, MySQL, SQLite
    - Esempi di DB non relazionali: MongoDB, Redis, Clickhouse, Cassandra
- Un **frontend**
- Un **proxy HTTP** come Nginx o Apache (usato in produzione)
    - Permette di gestire le richieste per più applicativi con un solo server
    - Gestione migliore di file statici e performance in generale
---
![height:550px](assets/app_web.png)

---

# Database e applicazioni web

Ci sono tre modi di interfacciarsi al database:

- Query raw e prepared statements
- Query builder (SQLAlchemy Core)
- ORM (SQLAlchemy ORM, Django ORM)

---

# Query raw
- Le query raw sono scritte in SQL e inviate direttamente al database
```python
import psycopg2
# Connessione al database
conn = psycopg2.connect(
    host="localhost",
    database="bar_app",
    user="postgres",
    password="password"
)

with conn.cursor() as cur:
    # Esecuzione di una query raw
    cur.execute("SELECT * FROM products WHERE category = 'bevande'")
    results = cur.fetchall()
```
---
# Prepared statement
- Servono per processare l'input in maniera sicura
```python
import psycopg2
# Connessione al database
conn = psycopg2.connect(
    host="localhost",
    database="bar_app",
    user="postgres",
    password="password"
)
input_utente = "bevande"
with conn.cursor() as cur:
    # Esecuzione di una query raw
    cur.execute("SELECT * FROM products WHERE category = %s", (input_utente,))
    results = cur.fetchall()
```
---
# Perchè usare le prepared statement?
- Processare l'input utente con query raw può essere pericoloso!
```python
import psycopg2
# Input utente
nome_utente = "admin"
password = "password123"
with conn.cursor() as cur:
    # Esecuzione di una query raw
    cur.execute("SELECT * FROM utenti WHERE username = '" + nome_utente + "' AND password = '" + password + "'")
    results = cur.fetchall()
```
---
# Perchè usare le prepared statement?
- E se `nome_utente` fosse valorizzato a `admin' OR 1=1 --`?
- (`--` è un commento in SQL)

```python
"SELECT * FROM utenti WHERE username = '" + nome_utente + "' AND password = '" + password + "'"
```
```sql
SELECT * FROM utenti WHERE username = 'admin' OR 1=1 --' AND password = 'password123'
```
- La query sopra restituirebbe tutti gli utenti, non solo l'admin
- Si riesce a fare il bypass di un login! (SQL Injection)
---
# Query builder
- Un query builder è un'interfaccia per costruire query SQL usando un linguaggio di programmazione
- Utili per la modularità e la manutenibilità del codice
- Si possono costruire le query usando più funzioni, in maniera da poter riutilizzare alcuni pezzi di codice
- Rispetto a un ORM è più vicino al SQL puro, ma non è necessario scrivere tutto a mano
---
# Query builder
```python
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select
# Setup
engine = create_engine("postgresql://postgres:password@localhost/bar_app")
metadata = MetaData()
# Definizione tabella
products = Table(
    "products", 
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("category", String),
    Column("price", Integer)
)
# Query composte tramite metodi
query = select(products).where(products.c.category == "bevande")
with engine.connect() as conn:
    result = conn.execute(query)
    for row in result:
        print(row.name, row.price)
```
---
# Perchè usare un query builder
```python
def filter_by_category(query, category):
    return query.where(products.c.category == category)

def filter_by_price(query, price):
    return query.where(products.c.price < price)

def filter_by_name(query, name):
    return query.where(products.c.name == name)

def filter_products(filters = {}):
    query = select(products)
    if filters.get('category'):
        query = filter_by_category(query, filters['category'])
    if filters.get('price'):
        query = filter_by_price(query, filters['price'])
    if filters.get('name'):
        query = filter_by_name(query, filters['name'])
    return query
```
---
# Object Relational Mapping (ORM)
- Un ORM è un'interfaccia per mappare le tabelle del database a classi e oggetti
- Toglie completamente l'onere di scrivere query
- Utile per progetti con tante query semplici (CRUD)
- Può essere usato in concomitanza ad altri metodi (query builder o query raw)

---

# Esempio ORM
```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# Setup
engine = create_engine("postgresql://postgres:password@localhost/bar_app")
Base = declarative_base()

# Definizione tabella
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    category = Column(String)
    price = Column(Integer)

# Creazione sessione
Session = sessionmaker(bind=engine)
session = Session()

# Query con ORM
products = session.query(Product).filter(Product.category == "bevande").all()
for product in products:
    print(product.name, product.price)

```
---
# Quando usare ciascun approccio

**ORM**:
- CRUD semplici e operazioni standard
- Quando la leggibilità e manutenibilità sono prioritarie
- Team che condividono uno standard comune

**Query builder / Raw SQL**:
- Query complesse con ottimizzazioni specifiche
- Performance critica
- Migrazioni e operazioni batch

Nel mondo reale si tende a usare un approccio ibrido, combinando i vantaggi di entrambi i metodi.

---
# Connessione al database

**Pattern comuni**:
- **Connection pooling**: Riutilizzo connessioni per efficienza, ne vengono tenute X aperte che vengono utilizzate da più thread
- **Lazy connection**: Connessione solo quando necessaria
- **Singleton**: Istanza condivisa del database
---
# Analisi funzionale e tecnica

**Analisi funzionale**:
- Definizione dei requisiti e use case
- User stories e flussi utente
- Definizione delle entità e modello dati concettuale

**Analisi tecnica**:
- Architettura dell'applicazione
- Scelta dello stack tecnologico e dei servizi esterni a cui affidarsi (pagamenti, notifiche)
- Progettazione dettagliata del database
- Definizione delle API e interfacce

---
# Analisi funzionale e tecnica

**Studio di fattibilità**:
- Tutte le richieste del cliente sono realizzabili?
- Tempi e costi stimati sono corretti?

---
# Esempio: Analisi funzionale per un'app di gestione bar

- Un bar vuole gestire gli ordini al tavolo usando un menu digitale
- Il cliente può ordinare dal tavolo scannerizzando un QR code
- Il barista può vedere gli ordini in tempo reale e gestirli
- Il barista può vedere le statistiche di vendita e i prodotti più richiesti
---

# Esempio: Analisi funzionale per un'app di gestione bar

**Requisiti principali**:
- Gestione degli ordini ai tavoli
- Monitoraggio delle vendite e statistiche

**Entità principali**:
- Prodotti (bevande, piatti, etc.)
- Ordini
- Clienti
- Tavoli

---
# Esempio: Analisi per un'app di gestione bar
### Struttura del database (prima bozza)
- **Prodotti**: id, nome, categoria, prezzo
- **Ordini**: id, id_prodotto, id_cliente, id_tavolo, stato
- **Clienti**: id, nome, email
- **Tavoli**: id, numero_tavolo
---
# Esempio: Analisi per un'app di gestione bar
- La struttura di prima limita a un solo prodotto per ordine!
### Struttura del database (seconda bozza)
- **Prodotti**: id, nome, categoria, prezzo
- **Ordini**: id, id_cliente, id_tavolo, stato
- **Dettagli_Ordine**: id, id_ordine, id_prodotto, quantità
- **Clienti**: id, nome, email
- **Tavoli**: id, numero_tavolo
---
# Esempio: Analisi per un'app di gestione bar
- Per ottenere le statistiche di vendita, conviene mantenere uno storico dei prezzi, in quanto possono cambiare nel tempo
### Struttura del database (terza bozza)
- **Prodotti**: id, nome, categoria
- **Storico_Prezzi**: id, id_prodotto, prezzo
- **Ordini**: id, id_cliente, id_tavolo, stato
- **Dettagli_Ordine**: id, id_ordine, id_prodotto, id_prezzo, quantità
- **Clienti**: id, nome, email
- **Tavoli**: id, numero_tavolo
---
# Esempio: Analisi per un'app di gestione bar
- Quando si fa un analisi funzionale/tecnica, è importante considerare scenari che il cliente potrebbe aver tralasciato
- Ad esempio, il cliente potrebbe non aver considerato che i prodotti possono cambiare prezzo nel tempo
- È importante fare domande e chiarire i requisiti con il cliente (o manager)
- **Eventuali cambiamenti ai requisiti sono molto più costosi da implementare in fase di sviluppo che in fase di analisi**
---
# Esempio: Analisi per un'app di gestione bar
- Una volta abbozzata la struttura del database, si può passare alla definizione delle API/interfacce/funzioni necessarie
- Ad esempio, per la gestione degli ordini, si potrebbero definire le seguenti API:
    - Creazione di un nuovo ordine
    - Aggiornamento dello stato di un ordine
    - Visualizzazione degli ordini in corso
    - Visualizzazione delle statistiche di vendita
---
# Esempio: Analisi per un'app di gestione bar
- Implementiamo questi endpoint in Flask usando l'ORM di SQLAlchemy
---
# Esempio: Analisi per un'app di gestione bar
- Supponiamo che le statistiche di vendita che ci interessano siano:
    - Totale vendite per prodotto
    - Totale vendite per categoria
    - Totale vendite per mese
---
# Esempio: Analisi per un'app di gestione bar
- Ecco 3 strategie per implementare queste statistiche:
    - **All'interno del nostro codice (query piccole)**: Avremo una funzione che prende tutti gli ordini e per ciascun prodotto calcola il totale delle vendite, facendo una query al database per ogni prodotto
    - **All'interno del nostro codice (poche query grosse)**: Avremo una funziona che prende tutti gli ordini e per ciascuno calcola il totale delle vendite, facendo una sola query al database
    - **All'interno del database**: Possiamo anche usare le query SQL per calcolare le statistiche direttamente nel database, usando le funzioni di aggregazione
---
# Esempio: Analisi per un'app di gestione bar
- La prima opzione è la più semplice da implementare, ma è la meno performante
- La seconda opzione è più performante, ma richiede più codice e più query al database, per basi di dati grandi potrebbe essere un problema
- La terza opzione è la più performante e scalabile, ma richiede una maggiore conoscenza di SQL
- In generale, è meglio delegare al database il calcolo dei dati aggregati, in quanto è ottimizzato per questo tipo di operazioni
---
# Esempio: Analisi per un'app di gestione bar
- Prima opzione:
```python
@app.route("/stats", methods=["GET"])
def get_stats():
    sales_per_product = {}
    details = session.query(OrderDetail).all()
    # Per ogni dettaglio, otteniamo il prodotto e il prezzo
    for detail in details:
        # Qui sotto faccio 2 query per ogni prodotto acquistato!!!
        product = session.query(Product).filter(Product.id == detail.product_id).first()
        price = session.query(Price).filter(Price.id == detail.price_id).first()
        # Aggiungiamo il prezzo al totale delle vendite per prodotto
        if product.name not in sales_per_product:
            sales_per_product[product.name] = 0
        sales_per_product[product.name] += price.price * detail.quantity
    # Restituiamo le vendite per prodotto
    return jsonify(sales_per_product)
```
---
# Esempio: Analisi per un'app di gestione bar
- Seconda opzione:
```python
@app.route("/stats", methods=["GET"])
def get_stats():
    # Otteniamo tutti il totale di vendite per prodotto
    orders = (
        session.query(OrderDetail)
        .join(Product)
        .join(Price)
        .all()
    )
    stats = {}
    for order in orders:
        product_name = order.product.name
        if product_name not in stats:
            stats[product_name] = 0
        stats[product_name] += order.price.price * order.quantity
    return jsonify(stats)
```
---
# Esempio: Analisi per un'app di gestione bar
- Terza opzione:
```python
@app.route("/stats", methods=["GET"])
def get_stats():
    # Otteniamo il totale venduto per ogni prodotto
    stats = (
        session.query(Product.name, func.sum(OrderDetail.quantity * Price.price))
        .join(OrderDetail)
        .join(Price)
        .group_by(Product.name)
        .all()
    )
    result = {}
    for stat in stats:
        result[stat[0]] = stat[1]
    return jsonify(result)
```
---