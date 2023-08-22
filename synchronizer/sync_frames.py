from kafka import KafkaConsumer, KafkaProducer
import json
import base64
from datetime import datetime,timedelta
from collections import deque
from PIL import Image
import io
import os

KAFKA_BROKER = os.getenv("KAFKA_BROKER","localhost:9092")
INPUT_TOPIC = os.getenv("INPUT_TOPIC","indexed-frames")
OUTPUT_TOPIC = os.getenv("OUTPUT_TOPIC","synchronized-frames")
DEDUG = os.getenv("DEBUG","False").strip().lower()

# Initialize queues for each camera
queue1 = deque()
queue2 = deque()
queue3 = deque()
queue4 = deque()

# Map the source names to the respective queues
queues_map = {
    "camera1": queue1,
    "camera2": queue2,
    "camera3": queue3,
    "camera4": queue4
}

# Kafka Consumer setup
consumer = KafkaConsumer(
    INPUT_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    group_id='my-group',
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)

def join_images_side_by_side(images_list, output_name):
    images = [Image.open(io.BytesIO(img)) for img in images_list]
    
    # Calculate total width and max height
    total_width = sum(img.width for img in images)
    max_height = max(img.height for img in images)

    # Create a new blank image with the calculated width and height
    new_image = Image.new('RGB', (total_width, max_height))

    # Paste each image into the new image
    x_offset = 0
    for img in images:
        new_image.paste(img, (x_offset, 0))
        x_offset += img.width

    # Save the new image
    new_image.save(output_name +'.jpg')

def process_message(data):
    
    # Decode the image from base64
    image_data = base64.b64decode(data['image'])
    source_name = data['source']

    # Add data to the respective queue
    if source_name in queues_map:
        queues_map[source_name].appendleft((datetime.strptime(data['datetime'].strip(), "%d-%m-%Y %H:%M:%S"), image_data))
    
    # Logic to synchronize and display images
    print(len(queue1), len(queue2), len(queue3), len(queue4))

    # Get the last datetime from all queues
    
    last_datetime = datetime.now() - timedelta(days=30)
    if len(queue1)>0:
        last_datetime = max(last_datetime, queue1[-1][0])
        # print(queue1[-1][0] )
    if len(queue2)>0:
        last_datetime = max(last_datetime, queue2[-1][0])
        # print(queue2[-1][0] )
    if len(queue3)>0:
        last_datetime = max(last_datetime, queue3[-1][0])
        # print(queue3[-1][0] )
    if len(queue4)>0:
        last_datetime = max(last_datetime, queue4[-1][0])
        # print(queue4[-1][0] )
    
    print('-----------------------------------------------')

    while len(queue1)>0:
        if queue1[-1][0] < last_datetime:
            queue1.pop()
        else:
            break
    while len(queue2)>0:
        if queue2[-1][0] < last_datetime:
            queue2.pop()
        else:
            break
    while len(queue3)>0:
        if queue3[-1][0] < last_datetime:
            queue3.pop()
        else:
            break
    while len(queue4)>0:
        if queue4[-1][0] < last_datetime:
            queue4.pop()
        else:
            break           
    if len(queue1)>0 and len(queue2)>0 and len(queue3)>0 and len(queue4)>0:
        if queue1[-1][0] == last_datetime and queue2[-1][0] == last_datetime and queue3[-1][0] == last_datetime and queue4[-1][0] == last_datetime:
            print("Synced")
            imgelist = [queue1[-1][1],queue2[-1][1],queue3[-1][1],queue4[-1][1]]
            base64_encoded_images = [base64.b64encode(img).decode('utf-8') for img in imgelist]
            output_data = {
            'sources': list(queues_map.keys()),
            'frames': base64_encoded_images,
            'datetime': last_datetime.strftime('%Y-%m-%d %H:%M:%S'),
             }

            # Send the output message to the output topic
            producer.send(OUTPUT_TOPIC, value=json.dumps(output_data).encode('utf-8'))
            if DEDUG == "true":
                join_images_side_by_side(imgelist, last_datetime.strftime('%Y-%m-%d_%H:%M:%S'))
            if len(queue1)>0:
                queue1.pop()
            if len(queue2)>0:
                queue2.pop()
            if len(queue3)>0:
                queue3.pop()
            if len(queue4)>0:
                queue4.pop()

    

for message in consumer:
    process_message(message.value)

consumer.close()