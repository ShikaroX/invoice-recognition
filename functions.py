# functions file 
import numpy as np
import cv2
from pdf2image import convert_from_path
import os

def resizeImage(image):
    width = 800
    height = 1000

    return cv2.resize(image, (width, height))

def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def preProcessingDigitalReceipt(image):
    img = cv2.imread(image)

    resized_img = resizeImage(img)
    grayscale_img = grayscale(resized_img)

    return grayscale_img

def preProcessingDigitalizedReceipt(image):
    img = cv2.imread(image)

    resized_img = resizeImage(img)
    grayscale_img = grayscale(resized_img)

    median = cv2.medianBlur(grayscale_img, 5)

    thresh = cv2.adaptiveThreshold(median, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 2)

    kernel = np.ones((5, 5), np.uint8)
    eroded_img = cv2.erode(thresh, kernel, iterations=7)

    edges = cv2.Canny(eroded_img, 100, 200)

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

            points = contour.reshape(-1, 2)

            top_left = min(points, key=lambda p: p[0] + p[1]) 
            top_right = max(points, key=lambda p: p[0] - p[1]) 
            bottom_left = min(points, key=lambda p: p[0] - p[1])
            bottom_right = max(points, key=lambda p: p[0] + p[1])

            top_left = tuple(top_left)
            top_right = tuple(top_right)
            bottom_left = tuple(bottom_left)
            bottom_right = tuple(bottom_right)

            points = np.array([top_left, top_right, bottom_left, bottom_right])
            
            center = np.mean(points, axis=0)
            rect = cv2.minAreaRect(points)
            angle = rect[2]

            if 45 > angle > 0:
                angle_rotation = angle
            else:
                angle_rotation = -(90 - angle)

            rotation_matrix  = cv2.getRotationMatrix2D(center, angle_rotation, 1.0)

            rotated_img = cv2.warpAffine(resized_img, rotation_matrix, (resized_img.shape[0], resized_img.shape[1]), borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))

            print(angle)
            print(angle_rotation)
            print(angle + angle_rotation)

            cv2.circle(resized_img, top_left, 5, (0, 255, 0), -1)
            cv2.circle(resized_img, top_right, 5, (0, 255, 0), -1)
            cv2.circle(resized_img, bottom_left, 5, (0, 255, 0), -1)
            cv2.circle(resized_img, bottom_right, 5, (0, 255, 0), -1)
            cv2.circle(resized_img, (int(center[0]), int(center[1])), 5, (255, 0, 0), -1)

            bounding_box = (x, y, w, h)

    if bounding_box:
        cropped_img = rotated_img[y:y + h, x:x+w]
        return cropped_img
    else:
        print("Error founding bounding box!")

    return

def pdf2Image(pdf_path):
    images = convert_from_path(pdf_path)

    output_folder = "receipts"

    for i, image in enumerate(images):
        image.save(os.path.join(output_folder ,f"fatura_pagina_{i + 1}.jpg"), "JPEG")