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

    thresh = cv2.adaptiveThreshold(grayscale_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 2)
    kernel_2 = np.ones((2, 2), np.uint8)
    dilate = cv2.dilate(thresh, kernel_2)
    kernel_9 = np.ones((9, 9), np.uint8)
    erode = cv2.erode(dilate, kernel_9, iterations=7)
    edge_det = cv2.Canny(erode, 150, 200)

    final_edge_det = cv2.dilate(edge_det, kernel_2, iterations=2)

    contours, _ = cv2.findContours(final_edge_det, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)

        x, y, w, h = cv2.boundingRect(largest_contour)

        #cv2.rectangle(resized_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cropped_img = grayscale_img[y:y+h, x:x+w]    
    else:
        print("Contours not found!")

    return cropped_img

def pdf2Image(pdf_path):

    images = convert_from_path(pdf_path)

    output_folder = "receipts"

    for i, image in enumerate(images):
        image.save(os.path.join(output_folder ,f"fatura_pagina_{i + 1}.jpg"), "JPEG")