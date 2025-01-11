import requests

def fetch_products_by_token(token):
    url = "http://localhost:3000/graphql"  # Replace with your actual GraphQL server URL


    token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJLdjRVRzdSRUx6c3p0aFQwU1A3cGlGVXY1TlZNTnF2NWdqSDVHcFNYajRVIn0.eyJleHAiOjE3MzY1NDU3NjIsImlhdCI6MTczNjU0MjE2MiwianRpIjoiMjFkMTIwZTEtNGEwMy00NmJjLTkzMjEtMjE5MTVkZGU2YzFkIiwiaXNzIjoiaHR0cDovL2tleWNsb2FrOjgwODAvcmVhbG1zL215cmVhbG0iLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiMDJhODRhYzAtMGZiZS00OTk5LTlhZTYtYmVmOGJmZTczYzkyIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoibXljbGllbnQiLCJzaWQiOiIyZTg2ZWVkYS01NTk2LTRjYTktODk1ZC1mNGJjMDI1ODA0ZGEiLCJhY3IiOiIxIiwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbImRlZmF1bHQtcm9sZXMtbXlyZWFsbSIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iLCJ1c2VyIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsibXljbGllbnQiOnsicm9sZXMiOlsic2VmZ2FsIl19LCJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCBlbWFpbCBwcm9maWxlIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJuYW1lIjoiR2FsIE1lbmHFoWUiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJnYWxrbzEyMyIsImdpdmVuX25hbWUiOiJHYWwiLCJmYW1pbHlfbmFtZSI6Ik1lbmHFoWUiLCJlbWFpbCI6ImdhbGtvLm1lbmFzZUBnbWFpbC5jb20ifQ.or_PNtnUlU8Wxbexy8ATlX6MJO8eKYe9DZ7qFBXZ_avzWno-u6P-TEj1yTt3sRdduFGCpSizVh9gb7FH9gwUNh1YE5I39ltmoKwJPWJ5cafPXNBj-byacb7ZeUxTmdQPZBggeoxBLTryN6drb71miAS7pMCaOrfCdyWcZ7Qwd6MTcMAg0OrlhS-1TJf1KYb585ocwh-_bOdYabaIWPjaFU2dv5hR9imOMIAW1o_OGwYAVSfZWTpP-YUZEOKah1A68wYpEswaCYup7vAZmTv9isD-rQfXKnCpcg_KKBEI4qZuOUGzoIvBiWp65_apOVsSTeQo-zkB1ynL54oLXiXOhg"
    query = f"""
    query {{
        productsByToken(token: "{token}") {{
            id
            name
            description
            quantity
            ownerEmail
        }}
    }}
    """   
    headers = {
        "Content-Type": "application/json"
    }
    
    # Make the request
    response = requests.post(url, json={"query": query}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if "data" in data:
            return data["data"]["productsByToken"]
        else:
            print("Error in response:", data.get("errors", "No data"))
            return None
    else:
        print(f"Failed to fetch products. Status code: {response.status_code}")
        return None

# Example usage:
products = fetch_products_by_token(None)  # You can pass None here since the token is embedded in the query itself
if products:
    for product in products:
        print(f"Product ID: {product['id']}, Name: {product['name']}, Quantity: {product['quantity']}")
else:
    print("No products found or error in fetching products.")
