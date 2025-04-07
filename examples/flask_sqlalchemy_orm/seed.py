import requests
# Seed di prodotti, customer, e ordini

products = [
    {"name": "Margherita", "category": "Pizze", "price": 7.5},
    {"name": "Peperoni", "category": "Pizze", "price": 8.0},
    {"name": "Carbonara", "category": "Pasta", "price": 9.0},
    {"name": "Tiramisu", "category": "Dolci", "price": 5.0},
]

# Creazione di prodotti
for product in products:
    response = requests.post(
        "http://127.0.0.1:5000/products",
        json=product,
    )
    print(response.text)  # Stampa la risposta del server
    
# Creazione di un cliente
response = requests.post(
    "http://127.0.0.1:5000/customers",
    json={
        "name": "Mario Rossi",
        "email": "mario.rossi@example.com",
    }
)

response = requests.post(
    "http://127.0.0.1:5000/orders",
    json={
        "customer_id": 1,
        "table_id": 1,
        "status": "in corso",
        "details": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 2, "quantity": 1},
        ],
    },
)