from flask import Flask
import graphene
from graphene import ObjectType, String, List
from pymongo import MongoClient
from bson import ObjectId
import os
from flask import request, jsonify
import requests
from fastapi import FastAPI, HTTPException
import jwt

# Flask App
app = Flask(__name__)

# MongoDB Setup (replace with your own MongoDB URI)
AUTH_URL = os.getenv("AUTHENTICATION_URL")
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client.inventory_db  # Name of your database
users_collection = db.users  # Name of your collection
products_collection = db.products  # Name of your products collection

# Graphene Schema

class UserType(graphene.ObjectType):
    id = graphene.String()  # Treat id as a String in GraphQL
    email = graphene.String()

class ProductType(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()
    description = graphene.String()
    quantity = graphene.Float()
    ownerEmail = graphene.String()

class CreateUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)

    user = graphene.Field(UserType)

    def mutate(self, info, email):
        # Create the user
        new_user = {
            "email": email
        }
        print(email)
        result = users_collection.insert_one(new_user)
        # print(result)
        print(f"Creating a new user: {email}")
        # Return success message and the new user's ID
        print(f"User created successfully, user_id: {str(result.inserted_id)}")

        # Fetch the newly added user from the database
        created_user = users_collection.find_one({"_id": result.inserted_id})
        
        # Convert ObjectId to string
        created_user['id'] = str(created_user['_id'])
        
        return CreateUser(user=created_user)
    

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        quantity = graphene.Float(required=True)
        owner_email = graphene.String(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, description, quantity, owner_email):
        # Create the product
        new_product = {
            "name": name,
            "description": description,
            "quantity": quantity,
            "owner_email": owner_email
        }

        # Insert the new product into MongoDB
        result = products_collection.insert_one(new_product)
        print(f"Creating a new product: {name}")
        print(f"Product created successfully, product_id: {str(result.inserted_id)}")

        # Fetch the newly added product from the database
        created_product = products_collection.find_one({"_id": result.inserted_id})
        
        # Convert ObjectId to string
        created_product['id'] = str(created_product['_id'])

        # Return the newly created product
        return CreateProduct(product=created_product)
    
class UpdateProductQuantity(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)  # The ID of the product to update
        quantity = graphene.Float(required=True)  # The new quantity to set

    product = graphene.Field(ProductType)

    def mutate(self, info, id, quantity):
        # Find the product by id and update its quantity
        print()
        print()
        print(f"id: {id}")
        print(f"quan: {quantity}")
        result = products_collection.update_one(
            {"_id": ObjectId(id)},  # Find the product by ID
            {"$set": {"quantity": quantity}}  # Set the new quantity
        )
        print(result)
        print()
        print()
        
        if result.matched_count == 0:
            print(f"No product found with id: {id}")
            return UpdateProductQuantity(product=None)

        # Fetch the updated product from the database
        updated_product = products_collection.find_one({"_id": ObjectId(id)})
        
        # Convert ObjectId to string
        updated_product['id'] = str(updated_product['_id'])

        # Return the updated product
        return UpdateProductQuantity(product=updated_product)
    

class DeleteProduct(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)  # The ID of the product to delete

    success = graphene.Boolean()  # Boolean flag indicating if the deletion was successful

    def mutate(self, info, id):
        # Attempt to delete the product from MongoDB
        result = products_collection.delete_one({"_id": ObjectId(id)})

        if result.deleted_count == 0:
            print(f"No product found with id: {id}")
            return DeleteProduct(success=False)

        print(f"Product with id: {id} has been deleted")
        return DeleteProduct(success=True)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_product = CreateProduct.Field()
    update_product_quantity = UpdateProductQuantity.Field()
    delete_product = DeleteProduct.Field()

class Query(ObjectType):
    # This allows querying all users
    users = graphene.List(UserType)
    products = graphene.List(ProductType)

    # This allows querying a user by email
    user_by_email = graphene.Field(UserType, email=graphene.String(required=True))
    products_by_token = graphene.List(ProductType, token=graphene.String(required=True))
    product_by_id = graphene.Field(ProductType, id=graphene.String(required=True))

    # Resolver for querying a product by its ID
    def resolve_product_by_id(self, info, id):
        try:
            # Convert the string id to an ObjectId for MongoDB
            product_id = ObjectId(id)
            product = products_collection.find_one({"_id": product_id})
            # print(id)
            # print(product_id)
            # print(product)
            
            if product:
                # Convert _id to string and return the product as a ProductType object
                product["id"] = str(product["_id"])
                return product
            else:
                print(f"No product found with id: {id}")
                return None
        except Exception as e:
            print(f"Error in resolve_product_by_id: {e}")
            return None

    def resolve_products_by_token(self, info, token):
        print("fetching products...")
        print(token[:10])
        url = AUTH_URL + "/user-info"
        headers = {"Authorization": f"Bearer {token}"}
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        roles = decoded_token.get("resource_access", {}).get("myclient", {}).get("roles", [])
        
        if "sefgal" in roles:
            print("User has the 'sefgal' role!")
            products = products_collection.find()
            product_list = [{"id": str(product["_id"]),
                            "name": product["name"],
                            "description": product["description"],
                            "quantity": product["quantity"],
                            "owner_email": product["owner_email"]} for product in products]
            
            print(f"Products found: {product_list}")  # Debugging the returned products
       
            return product_list
        else:
            print("User does not have the 'sefgal' role.")
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()  

                user_info = response.json()
                products = products_collection.find({"owner_email": user_info['email']})
                print(f"Products found: {product_list}")

                return [
                    {
                        "id": str(product["_id"]),
                        "name": product["name"],
                        "description": product["description"],
                        "quantity": product["quantity"],
                        "ownerEmail": product["owner_email"]
                    }
                    for product in products
                ]
            except Exception as e:
                print("Error:", e)
                return jsonify({"error": "Error processing the token or fetching user info"}), 500

    def resolve_products(self, info):
    # Fetch all products
        print("Fetching products...")
        products = products_collection.find()
        product_list = [{"id": str(product["_id"]),
                        "name": product["name"],
                        "description": product["description"],
                        "quantity": product["quantity"],
                        "owner_email": product["owner_email"]} for product in products]
        
        print(f"Products found: {product_list}")  # Debugging the returned products
        
        return product_list


    def resolve_users(self, info):
        try:
            users = users_collection.find()
            return [{"id": str(user['_id']), "email": user['email']} for user in users]
        except Exception as e:
            print(f"Error in resolve_users: {e}")
            return []

    def resolve_user_by_email(self, info, email):
        try:
            user = users_collection.find_one({"email": email})
            if user:
                return UserType(id=str(user['_id']), email=user['email'])
            else:
                print(f"No user found with email: {email}")
                return None
        except Exception as e:
            print(f"Error in resolve_user_by_email: {e}")
            return None

schema = graphene.Schema(query=Query, mutation=Mutation)


# GraphQL Endpoint
@app.route("/inventory/graphql", methods=["GET", "POST"])
def graphql_server():
    from flask import request, jsonify
    if request.method == "GET":
        # Serve the GraphiQL interface (you can add more specific UI for testing)
        return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>GraphQL Playground</title>
                <script src="https://unpkg.com/graphql-playground-react/build/static/js/middleware.js"></script>
            </head>
            <body>
                <div id="root"></div>
                <script>
                    window.addEventListener('DOMContentLoaded', function() {
                        GraphQLPlayground.init(document.getElementById('root'), {
                            endpoint: '/inventory/graphql',
                        });
                    });
                </script>
            </body>
            </html>
        """
    elif request.method == "POST":
        from graphene import Schema
        print("haha")
        data = request.get_json()
        query = data.get('query')
        print(query)
        result = schema.execute(query)
        print(result)
        return jsonify(result.data)
    

@app.get("/inventory/healthz")
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

if __name__ == '__main__':
    print("ok")
    app.run(host='0.0.0.0', port=3001)
