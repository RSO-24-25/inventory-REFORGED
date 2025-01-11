from flask import Flask
import graphene
# from flask_graphql import GraphQLView
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from flask import request, jsonify
import requests
from fastapi import FastAPI, HTTPException

app = Flask(__name__)


AUTH_URL = os.getenv("AUTHENTICATION_URL", "http://localhost:8000")

# MongoDB Configuration
MONGO_URI =os.getenv("MONGO_URL", "mongodb+srv://mongodb:galjetaksef123!@mongoloidgal.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000")  # Replace with your Azure MongoDB connection string
client = MongoClient(MONGO_URI)
db = client.inventory_db

users_collection = db.users
products_collection = db.products

# GraphQL Types
class UserType(graphene.ObjectType):
    id = graphene.String()
    email = graphene.String()


class ProductType(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()
    description = graphene.String()
    quantity = graphene.Int()
    owner_email = graphene.String()


# GraphQL Queries
class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    products = graphene.List(ProductType)
    product_by_id = graphene.Field(ProductType, id=graphene.String(required=True))

    def resolve_users(self, info):
        users = users_collection.find()
        return [UserType(id=str(u["_id"]), email=u["email"]) for u in users]

    def resolve_products(self, info):
        products = products_collection.find()
        return [
            ProductType(
                id=str(p["_id"]),
                name=p["name"],
                description=p["description"],
                quantity=p["quantity"],
                owner_email=p["owner_email"],
            )
            for p in products
        ]

    def resolve_product_by_id(self, info, id):
        product = products_collection.find_one({"_id": ObjectId(id)})
        if product:
            return ProductType(
                id=str(product["_id"]),
                name=product["name"],
                description=product["description"],
                quantity=product["quantity"],
                owner_email=product["owner_email"],
            )
        return None


# GraphQL Mutations
class CreateUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)

    message = graphene.String()

    def mutate(self, info, email):
        if users_collection.find_one({"email": email}):
            return CreateUser(message="Email already exists")
        users_collection.insert_one({"email": email})
        return CreateUser(message="User created successfully")


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        owner_email = graphene.String(required=True)

    message = graphene.String()
    product_id = graphene.String()

    def mutate(self, info, name, description, owner_email):
        if not users_collection.find_one({"email": owner_email}):
            return CreateProduct(message="Owner email does not exist")

        product = {
            "name": name,
            "description": description,
            "quantity": 0,
            "owner_email": owner_email,
        }
        result = products_collection.insert_one(product)
        return CreateProduct(
            message="Product created successfully", product_id=str(result.inserted_id)
        )

# schema = graphene.Schema(mutation=CreateProduct)
class UpdateProductQuantity(graphene.Mutation):
    class Arguments:
        product_id = graphene.String(required=True)
        quantity = graphene.Int(required=True)

    message = graphene.String()

    def mutate(self, info, product_id, quantity):
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            return UpdateProductQuantity(message="Product not found")

        new_quantity = product.get("quantity", 0) + quantity
        products_collection.update_one(
            {"_id": ObjectId(product_id)}, {"$set": {"quantity": new_quantity}}
        )
        return UpdateProductQuantity(message="Product quantity updated successfully")


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_product = CreateProduct.Field()
    update_product_quantity = UpdateProductQuantity.Field()


# Schema
schema = graphene.Schema(query=Query, mutation=Mutation)

@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    print(data)

    if not data or "query" not in data:
        return jsonify({"error": "No query provided"}), 400

    result = schema.execute(data["query"])
    return jsonify(result.data)



# Flask route to accept and print token
@app.route("/post-token", methods=["POST"])
def post_token():
    # Get JSON data from request
    data = request.get_json()

    # Check if token is provided in the request body
    if "token" not in data:
        return jsonify({"error": "Token is required"}), 400

    token = data["token"]

    # For now, print the token
    # print(f"Received token: {token}")

    url = AUTH_URL + "/user-info"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  

        user_info = response.json()

        # print(user_info)
    
        products = products_collection.find({"owner_email": user_info['email']})
        # print("hehe")
        # for product in products:
        #     print(product)
        # products = "jogurt"

        product_list = [serialize_doc(product) for product in products]
        # print("product list:")
        # print(product_list)

        # Return the products associated with the user
        return jsonify({"products": product_list}), 200


    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Error processing the token or fetching user info"}), 500

def serialize_doc(doc):
    """Converts MongoDB document ObjectId to string for JSON serialization."""
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])  # Convert ObjectId to string for easier usage
    return doc
    


@app.get("/healthz")
def health_check():
    """
    Health check endpoint.
    """
    try:
        # Here you can add checks like database connectivity, etc.
        return {"status": "healthy"}
    except Exception as e:
        # If the check fails, raise an HTTPException
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8601)
