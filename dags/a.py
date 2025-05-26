from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from pymongo import MongoClient
from kafka import KafkaProducer
from bson import ObjectId
from confluent_kafka import Consumer
import json

# Default arguments for DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 7, 7),  # Ngày bắt đầu hợp lệ
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Initialize the DAG
dag = DAG(
    dag_id='data',
    default_args=default_args,
    schedule_interval='@once',
    catchup=False
)

run_app_crawler_compose = BashOperator(
    task_id="run_app_crawler_compose",
    bash_command="docker start -ai app_crawler",
    dag=dag
)

def json_serializer(document):
    return json.dumps(document, default=lambda x: str(x) if isinstance(x, ObjectId) else x).encode('utf-8')

def send_mongo_data_to_kafka():
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://mongodb:27017')
        db = client['db_goodread']
        collection = db['tb_book']

        # Connect to Kafka
        producer = KafkaProducer(
            bootstrap_servers='kafka:29092',
            value_serializer=json_serializer
        )

        # Read from MongoDB and send to Kafka
        for document in collection.find():
            producer.send('book', document)
        
        producer.flush()  # Ensure all records are sent
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        producer.close()  # Close producer connection

# Define the task in Airflow
send_data_task = PythonOperator(
    task_id='send_mongo_data_to_kafka_task',
    python_callable=send_mongo_data_to_kafka,
    dag=dag
)

run_spark = BashOperator(
    task_id="run_spark",
    bash_command="docker start spark",
    dag=dag
)

# Kafka Consumer Function
def read_from_kafka_and_save_to_mongo(**kwargs):
    # Kafka Consumer Configuration
    kafka_config = {
        'bootstrap.servers': 'kafka:29092',  # Kafka server
        'group.id': 'Combined Lag',
        'auto.offset.reset': 'earliest',
    }
    topic = "goodread"  # Kafka topic name

    # MongoDB Configuration
    mongo_client = MongoClient("mongodb://mongodb:27017/")  # MongoDB server
    db = mongo_client["db_goodread"]  # MongoDB database
    collection = db["tb_book"]  # MongoDB collection

    # Initialize Kafka Consumer
    consumer = Consumer(kafka_config)
    consumer.subscribe([topic])

    try:
        while True:
            # Poll messages from Kafka
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                break  # Exit loop if no more messages
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue
            
            # Parse Kafka message
            message_value = json.loads(msg.value().decode('utf-8'))
            print(f"Received message: {message_value}")
            
            # Insert into MongoDB
            collection.insert_one(message_value)
            print(f"Inserted into MongoDB: {message_value}")

    finally:
        consumer.close()
        print("Kafka consumer closed.")

kafka_to_mongo_task = PythonOperator(
    task_id='kafka_to_mongo_task',
    python_callable=read_from_kafka_and_save_to_mongo,
    dag=dag
)


# Task execution order
run_app_crawler_compose >> kafka_to_mongo_task >> send_data_task >> run_spark