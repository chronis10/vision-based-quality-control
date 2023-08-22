from kafka import KafkaConsumer, KafkaProducer
from PIL import Image
import base64
import json
import io
import os
import torch
from torchvision import transforms
import numpy as np
from utils import extract_masks,extract_coverage,return_image_with_contours
import cv2
import time

KAFKA_BROKER = os.getenv("KAFKA_BROKER","localhost:9092")
INPUT_TOPIC = os.getenv("INPUT_TOPIC","synchronized-frames")
MODEL_PATH = os.getenv("MODEL_PATH","models/maskrcnn_model_full.pth")
SCORE_THRESHOLD = os.getenv("SCORE_THRESHOLD",0.5)
DEDUG = os.getenv("DEBUG","False").strip().lower()

consumer = KafkaConsumer(
    INPUT_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)

def make_final_image(processed_frames,percentages,timestamp,sources):
    # Calculate the total width and the maximum height of the stitched image
    image_list = [cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR) for pil_img in processed_frames]
    total_width = sum(img.shape[1] for img in image_list)
    max_height = max(img.shape[0] for img in image_list)

    # Create an empty canvas
    stitched_image = np.zeros((max_height, total_width, 3), dtype=np.uint8)

    # Place each image on the canvas and add text
    x_offset = 0
    for i, img in enumerate(image_list):
        stitched_image[: img.shape[0], x_offset : x_offset + img.shape[1]] = img
        
        # Add two lines of text to the top right of each image
        if i < 3:
            
            text1 = f"Source: {sources[i]}, coverage {percentages[i]*100:.2f}%"
        
            position1 = (x_offset + img.shape[1] -500, 50)  # adjust -200 as per the length of your text and font size
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            color = (0, 0, 255)  # Green color
            thickness = 2
            cv2.putText(stitched_image, text1, position1, font, font_scale, color, thickness)
        
        
        x_offset += img.shape[1]

    # Save the final stitched image
    cv2.imwrite('stitched_image.jpg', stitched_image)


device =  torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
model = torch.load(MODEL_PATH)
model.to(device)
model.eval()
transform = transforms.Compose([transforms.ToTensor()])

def main():  
    
    for message in consumer:
        packet = message.value          
        timestamp = packet["datetime"]
        frame_list = packet["frames"]
        sources = packet["sources"]
        
        processed_frames = []
        percentages = []
        masks_areas = [] 
        with torch.no_grad():            
            for i,frame in enumerate(frame_list[:3]):
                frame = base64.b64decode(frame)
                frame = Image.open(io.BytesIO(frame))    
                image_tensor = transform(frame).to(device)
                prediction = model(image_tensor.unsqueeze(0))
                if len(prediction) == 0:
                    continue
                extracted_predictions,masks = extract_masks(prediction,SCORE_THRESHOLD)
                coverage,contours,selected_masks_area = extract_coverage(extracted_predictions,frame)
                masks_areas.append(selected_masks_area)
                image_with_contours = return_image_with_contours(frame,contours)
                processed_frames.append(image_with_contours)
                percentages.append(coverage)
                print(f"Source {i}, coverage: {round(coverage*100,2)}%")

        print(f"Source1: {round(percentages[0]*100,2)}%, Source2: {round(percentages[1]*100,2)}%, Source3: {round(percentages[2]*100,2)}")
       
        if DEDUG == "true":
            frame = base64.b64decode(frame_list[-1])
            frame = Image.open(io.BytesIO(frame))    
            processed_frames.append(frame) 
            make_final_image(processed_frames,percentages,timestamp[0],sources)

        
        # base64_encoded_images = [base64.b64encode(img).decode('utf-8') for img in processed_frames]
        # base64_encoded_images.append(frame_list[-1])

        # output_data = {
        #     "datetime":timestamp[0],
        #     "sources":sources,
        #     "frames":base64_encoded_images,
        #     "coverage":percentages
        # }
        
if __name__ == "__main__":
    main()
