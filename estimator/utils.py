import cv2
import numpy as np

def filter_objects(objects, size_threshold):
    filtered_objects = [obj for obj in objects if obj.size >= size_threshold]
    return filtered_objects

def extract_coverage(extracted_predictions,image):
    total_contours = []
    total_mask_area = []
    total_blob_area = []
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    for prediction in extracted_predictions:
        mask = prediction['mask']
        mask = mask.squeeze()  
        mask = (mask > 0.5).astype(np.float32)
        mask = mask.astype(np.uint8)
        roi = cv2.bitwise_and(image, image, mask=mask)
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        _, binary_mask = cv2.threshold(roi_gray, 75, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)        

        size_threshold = 20  # change this to the minimum contour size you want
        contours = filter_objects(contours, size_threshold)
        blob_area = sum(cv2.contourArea(contour) for contour in contours)
        mask_area = cv2.countNonZero(mask)
        total_mask_area.append(mask_area)
        total_contours.append(contours)
        total_blob_area.append(blob_area)
    
    max_mask = max(total_mask_area)
    w_mask = [w/max_mask for w in total_mask_area]
    coverage_list = [c/m for c,m in zip(total_blob_area,total_mask_area)]
    weighted_sum = sum([w*c for w,c in zip(w_mask,coverage_list)])
    return weighted_sum,contours,sum(total_mask_area)


def extract_masks(prediction,score_threshold=0.5):    
    masks = prediction[0]['masks'].cpu().detach().numpy()
    labels = prediction[0]['labels'].cpu().detach().numpy()
    scores = prediction[0]['scores'].cpu().detach().numpy()
    extracted_predictions = []
    if 2 in labels:
        array = np.array(labels)
        indices = np.where(array == 2)[0]
        rocks_positions = list(indices)
        for pos in rocks_positions:
            if scores[pos] >= score_threshold:
                temp = {'score':scores[pos],'mask':masks[pos]}
                extracted_predictions.append(temp)
    selected_masks = [pred['mask'] for pred in extracted_predictions]
    return extracted_predictions,masks

def return_image_with_contours(image,contours):
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    mask = np.zeros_like(image)
    cv2.drawContours(mask, contours, -1, (0,255,0), thickness=-1)
    result = cv2.addWeighted(image, 0.7, mask, 1, 0)
    return result