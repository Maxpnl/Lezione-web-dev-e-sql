from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy import select, func

# Setup
app = Flask(__name__)
# Setup con SQLLite
engine = create_engine("sqlite:///orders.db")
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


# Definizione tabelle
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    category = Column(String)
    
    prices = relationship("Price", back_populates="product")
    details = relationship("OrderDetail", back_populates="product")
    
class Price(Base):
    __tablename__ = "prices"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    price = Column(Integer)
    
    product = relationship("Product", back_populates="prices")
    details = relationship("OrderDetail", back_populates="price")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    table_id = Column(Integer, ForeignKey("tables.id"))
    status = Column(String)
    
    customer = relationship("Customer", back_populates="orders")
    table = relationship("Table", back_populates="orders")
    details = relationship("OrderDetail", back_populates="order")


class OrderDetail(Base):
    __tablename__ = "order_details"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    price_id = Column(Integer, ForeignKey("prices.id"))
    quantity = Column(Integer)
    
    order = relationship("Order", back_populates="details")
    product = relationship("Product", back_populates="details")
    price = relationship("Price", back_populates="details")

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    
    orders = relationship("Order", back_populates="customer")


class Table(Base):
    __tablename__ = "tables"
    id = Column(Integer, primary_key=True)
    table_number = Column(Integer)
    orders = relationship("Order", back_populates="table")


# Creazione delle tabelle
Base.metadata.create_all(engine)


# Creazione di un nuovo ordine
@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    new_order = Order(
        customer_id=data["customer_id"], table_id=data["table_id"], status="in corso"
    )
    session.add(new_order)
    # Creazione dei dettagli dell'ordine
    for detail in data["details"]:
        product = session.query(Product).filter(Product.id == detail["product_id"]).first()
        # Ottieni il prezzo del prodotto prendendo l'ultimo prezzo
        price = (
            session.query(Price)
            .filter(Price.product_id == detail["product_id"])
            .order_by(Price.id.desc())
            .first()
        )
        if not product or not price:
            return jsonify({"message": "Prodotto o prezzo non trovato"}), 404
        new_detail = OrderDetail(
            order=new_order,
            product=product,
            price=price,
            quantity=detail["quantity"],
        )
        session.add(new_detail)
    session.commit()
    return jsonify({"message": "Ordine creato con successo", "order_id": new_order.id})


# Aggiornamento dello stato di un ordine
@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    data = request.get_json()
    order = session.query(Order).filter(Order.id == order_id).first()
    if not order:
        return jsonify({"message": "Ordine non trovato"}), 404
    order.status = data["status"]
    session.commit()
    return jsonify({"message": "Ordine aggiornato con successo"})


# Visualizzazione degli ordini in corso
@app.route("/orders", methods=["GET"])
def get_orders():
    # Visualizza gli ordini in corso facendo JOIN tra le tabelle necessarie
    # Mostrerà anche i prodotti associati a ciascun ordine
    orders = (
        session.query(Order)
        .join(OrderDetail)
        .join(Product)
        .join(Price)
        .filter(Order.status == "in corso")
        .all()
    )
    result = []
    for order in orders:
        order_details = []
        for detail in order.details:
            order_details.append(
                {
                    "product_id": detail.product.id,
                    "product_name": detail.product.name,
                    "price": detail.price.price,
                    "quantity": detail.quantity,
                }
            )
        result.append(
            {
                "order_id": order.id,
                "customer_id": order.customer_id,
                "table_id": order.table_id,
                "status": order.status,
                "details": order_details,
            }
        )
    return jsonify(result)

# Creazione di un nuovo prodotto
@app.route("/products", methods=["POST"])
def create_product():
    data = request.get_json()
    new_product = Product(name=data["name"], category=data["category"])
    session.add(new_product)
    # Aggiunta del prezzo
    new_price = Price(product=new_product, price=data["price"])
    session.add(new_price)
    session.commit()
    return jsonify({"message": "Prodotto creato con successo", "product_id": new_product.id})


# Creazione di un nuovo cliente
@app.route("/customers", methods=["POST"])
def create_customer():
    data = request.get_json()
    new_customer = Customer(name=data["name"], email=data["email"])
    session.add(new_customer)
    session.commit()
    return jsonify({"message": "Cliente creato con successo", "customer_id": new_customer.id})

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
if __name__ == "__main__":
    app.run(debug=True)