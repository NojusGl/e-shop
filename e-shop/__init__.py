import re
import random
import werkzeug as tool
import pymongo as mongo
from flask import (Flask, request, jsonify, abort)

def create_app():
    app = Flask(__name__)
    app.json.sort_keys = False
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
    def reg_prod ():
        reqBody = request.json

        id = reqBody.get("id")
        name = reqBody.get("name")
        category = reqBody.get("category")
        price = reqBody.get("price")

        if ((id is None) or (name is None) or (category is None) or (price is None)):
            return {"message": "Invalid data, or some of the values are missing"}, 400
        elif (products.find_one({"id": id})):
            return {"message": "This ID is already taken"}, 400
        else:
            product = {
                "id": id,
                "name": name,
                "category": category,
                "price": price
            }

            products.insert_one(product)
            return {"message": "Product is registered"}, 200

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

    # put – Register a new product.
    @app.route('/products', methods=['PUT'])
    def reg_prod ():
        reqBody = request.json
        
        id = reqBody.get("id")
        name = reqBody.get("name")
        category = reqBody.get("category")
        price = reqBody.get("price")

        if ((name is None) or (category is None) or (price is None)):
            return {"message": "Invalid data, or some of the values are missing"}, 400
        elif (id is None):
            id = random.randint(0, 65536)
            while (products.find_one({"id": id})):
                id = random.randint(0, 65536)
        else:
            if (products.find_one({"id": id})):
                return {"message": "The ID is already taken"}, 400
            
        product = {
            "id": id,
            "name": name,
            "category": category,
            "price": price
        }
        products.insert_one(product)
        return {"message": "Product is registered"}, 200

    # get – List all products, optionally in category.
    @app.route('/products', methods=['GET'])
    def list_prod ():
        reqBody = request.get_json(silent=True)
        if (reqBody is not None):
            category = reqBody.get("category")
            if (category is None):
                return {"message": "JSON passed, without category (don't pass the JSON in order to see all the products)"}, 400
            else:
                prods = list(products.find({"category": category}))
        else:
            prods = list(products.find())
        
        for prod in prods:
            prod.pop("_id")
        return jsonify(prods)

    # get – Get product details
    @app.route('/products/<productId>', methods=['GET'])
    def get_prod_info (productId):
        prod = products.find_one({"id": str(productId)})
        if (prod is None):
            return {"message": "Product not found"}, 404
        else:
            _prod = {
                "id": prod["id"],
                "name": prod["name"],
                "category": prod["category"],
                "description": "",
                "price": prod["price"]
            }
        return _prod, 200

    # del – Delete a product
    @app.route('/products/<productId>', methods=['DELETE'])
    def del_prod (productId):
        prod = products.find_one({"id": str(productId)})
        if (prod is None):
            return {"message": "Product not found"}, 404
        else:
            products.delete_one({"id": str(productId)})
            return {"message": "Product deleted"}, 204

    # get – Get top 10 clients by number of orders placed.
    @app.route('/statistics/top/clients', methods=['GET'])
    def top_clients ():
        # pasiimu visus klientus (panašu, tiesiog nueinu į db.clients, ir ten jau po vieną imu)
        # pasižiūriu, kiek kiekvienas klientas turi užsakymų get_client_orders()
        # surikiuoju pagal užsakymus
        # pasiimu dešimt nuo viršaus
        pass

    # get – Get top 10 products by total quantity ordered.
    @app.route('/statistics/top/products', methods=['GET'])
    def top_prod ():
        # kaip susisieti produktą su užsakymu kiekiu?
        # eiti per visus order'ius, ir kiekvienam produktui skaičiuoti, kiek kartų jis buvo užsakytas?
        # (aš galiu žinoti, kiek apskritai yra užsakymų iškviesdamas get_orders_count())
        # bet ar man apskritai to reikia?
        pass

    # post – Delete all data from the database
    @app.route('/cleanup', methods=['POST'])
    def cleanup ():
        mongoClient.drop_database('e_shop_database')
        return {"message": "Data deleted"}, 204
      
    return app
