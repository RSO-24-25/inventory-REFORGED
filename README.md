# Inventory 

## Overview
The Inventory Microservice manages users and products in a MongoDB database. It exposes a GraphQL API for querying and mutating data and integrates with an external authentication service for role-based access control.

---

## Features
- **GraphQL API**:
  - Manage users and products.
  - CRUD operations on products.
  - Query products by token with role-based filtering.
- **Authentication**:
  - Validates tokens using an external authentication service.
- **Health Check**:
  - Endpoint to monitor the service's status.

---

## Architecture
- **Flask**: Web framework for the microservice.
- **Graphene**: GraphQL implementation for Python.
- **MongoDB**: Stores user and product data.
- **JWT Authentication**: Secures endpoints with token validation.

---

## Setup Instructions

### Prerequisites
- Python 3.9+
- Docker and Docker Compose
- MongoDB cluster

### Installation

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd inventory-microservice
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set environment variables in a `.env` file:
    ```dotenv
    MONGO_URI=mongodb+srv://<your-mongo-uri>
    AUTHENTICATION_URL=http://auth-service-url
    ```

4. Start the service using Docker Compose:
    ```bash
    docker-compose up --build
    ```

---

## Usage

### GraphQL Endpoints
The service exposes GraphQL endpoints for managing users and products.

#### **Endpoint**:
- URL: `/inventory/graphql`

#### **Queries**
- **Fetch All Users**:
  ```graphql
  query {
    users {
      id
      email
    }
  }
