import re
import werkzeug as tool
import pymongo as mongo
from flask import (Flask, request, Response, jsonify, abort)

def create_app():
    app = Flask(__name__)
    mongoClient = mongo.MongoClient("localhost", 27017)
    db = mongoClient.e_shop_database
    clients = db.clients
    products = db.products
    orders = db.orders

    # Register a new client.
    @app.route('/clients', methods=['PUT'])
    def set_client():
        reqBody = request.json
        id = reqBody.get("id")
        name = reqBody.get("name")
        email = reqBody.get("email")

        client = {
            "id": id,
            "name": name,
            "email": email
        }
        clients.insert_one(client)

        return {"message": "Client is registered"}, 200
    
    # Get client details.
    @app.route('/clients/<clientId>', methods=['GET'])
    def get_client():
        pass

    # Delete a client and its associated orders.
    @app.route('/clients/<clientId>', methods=['DEL'])
    def delete_client():
        pass

    # Register a new product.  
    @app.route('/products', methods=['PUT'])  
    def set_product():
        pass

    # List all products, optionally in category.  
    @app.route('/products', methods=['GET'])  
    def get_products():
        pass

    # Get product details.
    @app.route('/product/<productId>', methods=['GET'])
    def get_product():
        pass
    
    # Delete a product.
    @app.route('/product/<productId>', methods=['DEL'])
    def delete_product():
        pass
    
    # Create a new order.
    @app.route('/orders', methods=['PUT'])
    def set_order():
        pass

    # Get client orders.
    @app.route('/clients/<clientId>/orders', methods=['PUT'])
    def get_client_orders():
        pass
    
    # Get top 10 clients by number of orders placed.
    @app.route('/statistics/top/clients', methods=['GET'])
    def get_top10_clients_by_orders():
        pass
    
    # Get top 10 products by total quantity ordered.
    @app.route('/statistics/top/products', methods=['GET'])
    def get_top10_products_by_ordered_quantity():
        pass
    
    # Get number of orders placed.
    @app.route('/statistics/orders/total', methods=['GET'])
    def get_orders_count():
        pass

    # Get total value of orders placed.
    @app.route('/statistics/orders/totalValue', methods=['GET'])
    def get_orders_value():
        pass

    # Delete all data from the database.
    @app.route('/cleanup', methods=['POST'])
    def delete_database():
        pass
    
    return app

