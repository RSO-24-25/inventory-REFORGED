FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install flask pymongo

ENV MONGO_URI=mongodb+srv://mongodb:galjetaksef123!@mongoloidgal.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000

EXPOSE 5000

CMD ["python", "app.py"]
