from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "your-mongo-connection-string")  # Replace with your Azure MongoDB connection string
client = MongoClient(MONGO_URI)
db = client.inventory_db

users_collection = db.users
products_collection = db.products

# Helper Function
def serialize_doc(doc):
    """Converts MongoDB document ObjectId to string for JSON serialization."""
    doc["_id"] = str(doc["_id"])
    return doc

# Routes
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    if 'email' not in data:
        return jsonify({'error': 'Email is required'}), 400

    if users_collection.find_one({"email": data['email']}):
        return jsonify({'error': 'Email already exists'}), 400

    user = {"email": data['email']}
    users_collection.insert_one(user)
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/products', methods=['POST'])
def create_product():
    data = request.json
    required_fields = ['name', 'description', 'owner_email']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Name, description, and owner_email are required'}), 400

    if not users_collection.find_one({"email": data['owner_email']}):
        return jsonify({'error': 'Owner email does not exist'}), 404

    product = {
        "name": data['name'],
        "description": data['description'],
        "quantity": 0,
        "owner_email": data['owner_email']
    }
    result = products_collection.insert_one(product)
    return jsonify({'message': 'Product created successfully', 'id': str(result.inserted_id)}), 201

@app.route('/products/<string:product_id>/update_quantity', methods=['POST'])
def update_product_quantity(product_id):
    data = request.json
    if 'quantity' not in data:
        return jsonify({'error': 'Quantity is required'}), 400

    product = products_collection.find_one({"_id": ObjectId(product_id)})
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    new_quantity = product.get("quantity", 0) + data['quantity']
    products_collection.update_one({"_id": ObjectId(product_id)}, {"$set": {"quantity": new_quantity}})
    return jsonify({'message': 'Product quantity updated successfully'}), 200

@app.route('/products', methods=['GET'])
def list_products():
    products = products_collection.find()
    result = [serialize_doc(p) for p in products]
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
