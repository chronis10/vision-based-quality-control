from kafka import KafkaConsumer, KafkaProducer
from PIL import Image
import pytesseract
import io
import base64
import json
import os
from datetime import datetime

KAFKA_BROKER = os.getenv("KAFKA_BROKER","localhost:9092")
INPUT_TOPIC = os.getenv("INPUT_TOPIC","camera2")
OUTPUT_TOPIC = os.getenv("OUTPUT_TOPIC","indexed-frames")
TIMESTAMP_LOCATION = os.getenv("TIMESTAMP_LOCATION","10x440x390x470")
TIME_START_MINUTE = int(os.getenv("TIME_START_MINUTE", 20))  # For example, 0 minute past the hour


consumer = KafkaConsumer(
    INPUT_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group'
)
producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)

def process_image(image_bytes):
    # Convert bytes to image
    base64_encoded_data = message.value.decode('utf-8')
    image_bytes = base64.b64decode(base64_encoded_data)

    image = Image.open(io.BytesIO(image_bytes))
    width, height = image.size

    # Extract datetime from a specific location in the image using pytesseract
    x1, y1, x2, y2 = [int(i) for i in TIMESTAMP_LOCATION.split('x')]
    croped = image.crop((x1, y1, x2, y2))
    date_time = pytesseract.image_to_string(croped)
    return date_time

try:
    print("Waiting for messages. To exit press CTRL+C")
    for message in consumer:
        datetime_string = process_image(message.value)
        print(datetime_string)
        if not datetime_string:
            continue
        try:
            dt = datetime.strptime(datetime_string.strip(), '%d-%m-%Y %H:%M:%S')  # adjust format if necessary
            ct = datetime.now() - dt
            # Extra check to make sure the datetime is within the time range
            if ct.seconds/60 > TIME_START_MINUTE or dt > datetime.now() :
                print(f"Expired frame {ct.seconds/60}")
                continue
        except ValueError:  # Raised when datetime_string cannot be converted
            print(f"Bad frame")
            continue

        # Prepare the output message
        output_data = {
            'image': message.value.decode('utf-8'),
            'datetime': datetime_string,
            'source': INPUT_TOPIC  # Assuming you store the last part in the message key
        }

        # Send the output message to the output topic
        print('sending message to output topic')
        producer.send(OUTPUT_TOPIC, value=json.dumps(output_data).encode('utf-8'))

except KeyboardInterrupt:
    print("\nStopping consumer.")
finally:
    consumer.close()
    producer.close()
    print("Kafka producer and consumer closed.")