# functions file 
import numpy as np
import cv2
from pdf2image import convert_from_path
import os

def resizeImage(image):
    width = 900
    height = 1100

    return cv2.resize(image, (width, height))

def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def preProcessingDigitalReceipt(image):
    img = cv2.imread(image)

    resized_img = resizeImage(img)
    grayscale_img = grayscale(resized_img)

    return grayscale_img

def preProcessingDigitalizedReceipt(image):
    """
    This function performs all the necessary preprocessing for digitized invoices.

    :param image: Input image to be processed.

    :return: Preprocessed image.
    """
    resized_img = resizeImage(image)                                                                            
    grayscale_img = grayscale(resized_img)                                                                      # Converts BGR to grayscale

    median = cv2.medianBlur(grayscale_img, 5)                                                                   # Apply the median filter with a kernel size of 5.

    thresh = cv2.adaptiveThreshold(median, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 2)       # Gaussian threshold with a kernel size of 15.

    kernel = np.ones((5, 5), np.uint8)
    eroded_img = cv2.erode(thresh, kernel, iterations=7)                                                        # Image erode with a kernel size of 5, using 7 iterations.

    edges = cv2.Canny(eroded_img, 100, 200)                                                                     # Edge detection using canny.

    kernel = np.ones((4, 4), np.uint8)
    edges_dilate = cv2.dilate(edges, kernel)

    contours, _ = cv2.findContours(edges_dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    mask = np.zeros_like(edges_dilate)

    min_area = 2500
    for contour in contours:
        if cv2.contourArea(contour) > min_area :
            cv2.drawContours(mask, [contour], -1, 255, thickness=cv2.FILLED)

            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(resized_img, (x, y), (x + w, y + h), (0, 0, 255), thickness=2)

            print(x, y, w, h)

            points = contour.reshape(-1, 2)

            top_left = (min(points, key=lambda p: p[0] + p[1]))
            top_right = (max(points, key=lambda p: p[0] - p[1])) 
            bottom_left = (min(points, key=lambda p: p[0] - p[1]))
            bottom_right = (max(points, key=lambda p: p[0] + p[1]))

            print(top_left)
            print(top_right)
            print(bottom_left)
            print(bottom_right)

            points = np.array([top_left, top_right, bottom_left, bottom_right])
            
            center = np.mean(points, axis=0)
            rect = cv2.minAreaRect(points)
            angle = rect[2]
            need_rotation = True

            if 45 > angle > 0:
                angle_rotation = angle
            else:
                angle_rotation = -(90 - angle)

            if angle >= 85 or angle <= 5:
                need_rotation = False

            print(angle)
            print(angle_rotation)
            print(angle + angle_rotation)
            print(need_rotation)

            if need_rotation:

                (h, w) = resized_img.shape[:2]
                center = (w // 2, h // 2)

                rotation_matrix  = cv2.getRotationMatrix2D(center, angle_rotation, 1.0)

                cos = np.abs(rotation_matrix[0, 0])
                sin = np.abs(rotation_matrix[0, 1])
                new_h = int((h * cos) + (w * sin))  
                new_w = w  

                shift_y = max(0, new_h - h) - 200
                rotation_matrix[1, 2] += shift_y // 2

                rotated_mask = cv2.warpAffine(mask, rotation_matrix, (new_w, new_h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))

                edges = cv2.Canny(rotated_mask, 100, 200)

                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                min_area = 2500
                for contour in contours:
                    if cv2.contourArea(contour) > min_area:
                        x, y, w, h = cv2.boundingRect(contour)

                rotated_img = cv2.warpAffine(grayscale_img, rotation_matrix, (new_w, new_h), borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))

                grayscale_img = rotated_img

            cv2.circle(resized_img, top_left, 5, (0, 255, 0), -1)
            cv2.circle(resized_img, top_right, 5, (0, 255, 0), -1)
            cv2.circle(resized_img, bottom_left, 5, (0, 255, 0), -1)
            cv2.circle(resized_img, bottom_right, 5, (0, 255, 0), -1)
            cv2.circle(resized_img, (int(center[0]), int(center[1])), 5, (255, 0, 0), -1)

            bounding_box = (x, y, w, h)

            print(x, y, w, h)

    if bounding_box:
        cropped_img = grayscale_img[y:y + h, x:x+w]
    else:
        print("Bounding box not found!")
        return 
    
    gaussian_blur = cv2.GaussianBlur(cropped_img, (3, 3), 0)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(5,5))
    enhanced_img = clahe.apply(gaussian_blur)
    
    return enhanced_img

def pdf2Image(pdf_path):
    images = convert_from_path(pdf_path)

    output_folder = "receipts"

    for i, image in enumerate(images):
        image.save(os.path.join(output_folder ,f"fatura_pagina_{i + 1}.jpg"), "JPEG")