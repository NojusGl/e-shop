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
    
    def generateId(container):
        id = None
        while (id == None or container.find_one({"id": id})):
            id = str(random.randint(0, 65536))
        return id

    # Register a new client.
    @app.route('/clients', methods=['PUT'])
    def set_client():
        reqBody = request.json
        id = reqBody.get("id")
        name = reqBody.get("name")
        email = reqBody.get("email")

        if name != None and email != None:
            if id == None:
                id = generateId(clients)
            client = {
                "id": id,
                "name": name,
                "email": email
            }
            clients.insert_one(client)
            return {"id": int(id)}, 201
        return {"message": "Invalid input, missing name or email"}, 400
 
    # Get client details.
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
    @app.route('/clients/<clientId>', methods=['DELETE'])
    def delete_client(clientId):
        client = clients.find_one({"id": str(clientId)})
        if client != None:
             orders.delete_many({"clientId": str(clientId)})
             clients.delete_one({"id": str(clientId)})  
             return {"message": "Client deleted"}, 204
        return {"message": "Client not found"}, 404
    
    # Create a new order.
    @app.route('/orders', methods=['PUT'])
    def set_order():
        reqBody = request.json
        clientId = reqBody.get("clientId")
        items = reqBody.get("items")
        client = clients.find_one({"id": str(clientId)})
        if client != None:
            if clientId != None and items != None:
                order = {
                    "clientId": str(clientId),
                    "items": items
                }

                orderId = orders.insert_one(order).inserted_id
                return {"id": str(orderId)}, 201
            return {"message": "Invalid input, missing clientId or items"}, 400
        return {"message": "Client not found"}, 404

    # Get client orders.
    @app.route('/clients/<clientId>/orders', methods=['PUT'])
    def get_client_orders(clientId):
        client = clients.find_one({"id": str(clientId)})
        if client != None:
            cursor = orders.find({"clientId": str(clientId)})
            items = []
            for order in cursor:
                items.append(order["items"])

            order = {
                    "clientId": clientId,
                    "items": items
            }

            return order, 200

        return {"message": "Client not found"}, 404
    
    # Get number of orders placed.
    @app.route('/statistics/orders/total', methods=['GET'])
    def get_orders_count():
        ordersCount = orders.count_documents({})
        return {"total": ordersCount}, 200

    # Get total value of orders placed.
    @app.route('/statistics/orders/totalValue', methods=['GET'])
    def get_orders_value():
        cursor = orders.find({})
        totalValue = 0.0

        for order in cursor:
            items = order["items"]
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
            id = generateId(products)
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
        return {"id": id}, 201

    # get – List all products, optionally in category.
    @app.route('/products', methods=['GET'])
    def list_prod ():
        category = request.args.get('category')
        if (category is None):
            prods = list(products.find())
        else:
            prods = list(products.find({"category": category}))
        
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
        pipeline = [
            {
                "$group": {
                    "_id": "$clientId",
                    "totalOrders": {
                        "$sum": 1
                        }
                }
            },
            {
                "$sort": {
                    "totalOrders": -1
                }
            },
            {
                "$limit": 10
            },
            {
                "$lookup": {
                    "from": "clients",
                    "localField": "_id",
                    "foreignField": "id",
                    "as": "client_info"
                }
            },
            {
                "$unwind": "$client_info"
            },
            {
                "$project": {
                    "_id": False,
                    "id": "$_id",
                    "name": "$client_info.name",
                    "totalOrders": 1
                }
            }
        ]

        top_clients = list(orders.aggregate(pipeline))

        formatted_clients = [
            {
                "id": client["id"],
                "name": client["name"],
                "totalOrders": client["totalOrders"]
            } for client in top_clients
        ]

        return jsonify(formatted_clients)

    # get – Get top 10 products by total quantity ordered.
    @app.route('/statistics/top/products', methods=['GET'])
    def top_prod ():
        pipeline = [
            {
                "$unwind": "$items"
            },
            {
                "$group": {
                    "_id": "$items.productId",
                    "quantity": {
                        "$sum": "$items.quantity"
                    }
                }
            },
            {
                "$sort": {
                    "quantity": -1
                }
            },
            {
                "$limit": 10
            },
            {
                "$lookup": {
                    "from": "products",
                    "localField": "_id",
                    "foreignField": "id",
                    "as": "product_info"
                }
            },
            {
                "$unwind": "$product_info"
            },
            {
                "$project": {
                    "_id": False,
                    "productId": "$_id",
                    "name": "$product_info.name",
                    "quantity": 1
                }
            }
        ]

        top_products = list(orders.aggregate(pipeline))

        formatted_prods = [
            {
                "productId": prod["productId"],
                "name": prod["name"],
                "quantity": prod["quantity"]
            } for prod in top_products
        ]

        return jsonify(formatted_prods)

    # post – Delete all data from the database
    @app.route('/cleanup', methods=['POST'])
    def cleanup ():
        mongoClient.drop_database('e_shop_database')
        return {"message": "Data deleted"}, 204
      
    return app