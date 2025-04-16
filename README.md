# Cheatsheet
[cheatsheet](./cheatsheet.md)

# Esercizio 1

Implementare gli endpoint `/login` e `/register`, il login dovrà solo controllare
che l'email e la password siano corretti (rispondendo di conseguenza), mentre la registrazione dovrà controllare che
l'email non sia già presente nel database e che la password rispetti i requisiti di
sicurezza (almeno 8 caratteri, almeno una lettera maiuscola, almeno un numero).

[Progetto](/examples/flask_sqlalchemy_orm/)

### Setup
```bash
# Entra nella cartella del progetto
cd examples/flask_sqlalchemy_orm
# Crea un ambiente virtuale
python3 -m venv venv

# Attiva l'ambiente virtuale (Linux/Mac)
source venv/bin/activate
# Attiva l'ambiente virtuale (Windows)
venv\Scripts\activate

# Installa le dipendenze
pip install -r requirements.txt
# Avvia il server
python main.py
```

# Esercizio 2

Un cliente vuole un'applicazione per la gestione di una piscina. Ci saranno due tipi di utenti:
- Tesserati: possono prenotare corsi e accedere alla piscina
- Istruttori: possono gestire i corsi e gli utenti

Un istruttore può prenotare una corsia per un'ora al giorno per fare lezione, i tesserati possono iscriversi a qualunque corso (anche più di uno). 

I corsi sono creabili solo dalle 08:00 alle 20:00, devono iniziare e finire in orari tondi (es. 08:00, 09:00, 10:00, ecc.) e durare 1 ora.

Ci sono un totale di 12 corsie.

- Struttura il database in modo che sia possibile gestire le prenotazioni e i corsi.
- Implementa l'endpoint per la creazione di un corso da un istruttore (senza autenticazione).
- Implementa l'endpoint per la prenotazione di un corso da un tesserato (senza autenticazione).


# Esercizio 3
Un mercato vuole poter dare alle proprie bancarelle la possibilità mettere in mostra i prodotti che vendono, strutturare il database per gestire questa casistica.