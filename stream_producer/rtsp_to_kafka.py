from kafka import KafkaProducer
import cv2
import base64
import time
import os

RTSP_URL = os.getenv("RTSP_URL")
KAFKA_BROKER = os.getenv("KAFKA_BROKER","localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC","stream_topic")
RETRY_INTERVAL = int(os.getenv("RETRY_INTERVAL","5"))

while True:
    cap = cv2.VideoCapture(RTSP_URL)
    
    if not cap.isOpened():
        print("Failed to connect to RTSP stream. Retrying in {} seconds...".format(RETRY_INTERVAL))
        time.sleep(RETRY_INTERVAL)
        continue

    producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER, retries=RETRY_INTERVAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Stream interrupted. Attempting to reconnect...")
            break

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_base64 = base64.b64encode(buffer)
        
        try:
            producer.send(KAFKA_TOPIC, frame_base64)
        except Exception as e:
            print(f"Error sending message to Kafka: {e}. Attempting to continue...")
            # Add any necessary handling or logging for Kafka-specific exceptions

    cap.release()
