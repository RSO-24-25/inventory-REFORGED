from flask import Flask, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint
from pymongo import MongoClient
from bson.json_util import dumps

# MongoDB Connection
MONGO_URI = "mongodb+srv://mongodb:galjetaksef123!@mongoloidgal.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"  # Replace with your MongoDB URI
client = MongoClient(MONGO_URI)

db = client.inventory_db

users_collection = db.users
products_collection = db.products

# Flask App
app = Flask(__name__)

# Swagger Setup
SWAGGER_URL = '/api-docs'  # Swagger UI path
API_DEFINITION = '/static/swagger.json'  # Swagger file path
swagger_ui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_DEFINITION)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

def serialize_doc(doc):
    """Converts MongoDB document ObjectId to string for JSON serialization."""
    if '_id' in doc:
        doc['_id'] = str(doc['_id']) 
    return doc


@app.route('/users', methods=['GET'])
def get_users():
    """Fetch all data from MongoDB"""
    try:
        data = list(users_collection.find())

        users_list = [serialize_doc(user) for user in data]

        return jsonify({"users": users_list}), 200
    except Exception as e:  
        print("Error:", e)
        return jsonify({"error": "Error processing the token or fetching user info"}), 500

@app.route('/products', methods=['GET'])
def get_products():
    """Fetch all data from MongoDB"""
    try:
        data = list(products_collection.find())

        product_list = [serialize_doc(product) for product in data]

        return jsonify({"products": product_list}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Error processing the token or fetching user info"}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
