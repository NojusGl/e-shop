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

    #Register a new client.
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
    
    return app