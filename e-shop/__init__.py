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

        if len(id) != 0 and len(name) != 0 and len(email) != 0:
            client = {
                "id": id,
                "name": name,
                "email": email
            }
            clients.insert_one(client)
            return {"id": id}, 201
        return {"message": "Invalid input, missing name or email"}, 400
    
    # Get client details.
    #NOTE there is a problem with how it displays client info
    @app.route('/clients/<clientId>', methods=['GET'])
    def get_client(clientId):
        client = clients.find_one({"id": str(clientId)})
        if client != None:
            clientInfo = {
                "id": int(client["id"]),
                "name": client["name"],
                "email": client["email"]
            }

            return clientInfo, 200
        return {"message": "Client not found"}, 404

    # Delete a client and its associated orders.
    @app.route('/clients/<clientId>', methods=['DEL'])
    def delete_client(clientId):
        client = clients.find_one({"id": str(clientId)})
        if client != None:
             orders.delete_many({"clientId": str(clientId)})
             clients.delete_one({"id": str(clientId)})  
             return {"message": "Client deleted"}, 204
        return {"message": "Client not found"}, 404

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
        reqBody = request.json
        clientId = reqBody.get("clientId")
        items = reqBody.get("items")
        client = clients.find_one({"id": str(clientId)})
        if client != None:
            if len(clientId) != 0 and len(items) != 0:
                order = {
                    "clientId": clientId,
                    "items": items
                }

                orderId = orders.insert_one(order).inserted_id
                return {"id": str(orderId)}, 201
            return {"message": "Invalid input, missing clientId or items"}, 400
        return {"message": "Client not found"}, 404

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
        ordersCount = orders.count_documents({})
        return {"total": ordersCount}, 200

    # Get total value of orders placed.
    #NOTE need products for proper testing
    @app.route('/statistics/orders/totalValue', methods=['GET'])
    def get_orders_value():
        cursor = orders.find({})
        totalValue = 0.0

        for order in cursor:
            items = order[items]
            for item in items:
                price = float(products.find_one({"id": item["productId"]})["price"])
                totalValue += price * int(item["quantity"])

        return {"totalValue": totalValue}, 200

    # Delete all data from the database.
    @app.route('/cleanup', methods=['POST'])
    def delete_database():
        pass
    
    return app

