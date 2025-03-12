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

    median = cv2.medianBlur(grayscale_img,5)

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
        if cv2.contourArea(contour) > min_area:
            cv2.drawContours(mask, [contour], -1, 255, thickness=cv2.FILLED)

            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(mask, (x, y), (x + w, y + h), 255, thickness=2)

            bounding_box = (x, y, w, h)

    if bounding_box:
        x, y, w, h = bounding_box
        cropped_img = resized_img[y:y + h, x:x+w]
        return cropped_img
    else:
        print("Error founding bounding box!")

    return resized_img

def pdf2Image(pdf_path):
    images = convert_from_path(pdf_path)

    output_folder = "receipts"

    for i, image in enumerate(images):
        image.save(os.path.join(output_folder ,f"fatura_pagina_{i + 1}.jpg"), "JPEG")