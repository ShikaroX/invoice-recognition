# functions file 
import numpy as np
import cv2
from pdf2image import convert_from_path
import os

def resizeImage(image):
    width = 900
    height = 1200

    return cv2.resize(image, (width, height))

def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def preProcessingDigitalReceipt(image):
    img = cv2.imread(image)

    resized_img = resizeImage(img)
    final_img = grayscale(resized_img)

    return final_img

def preProcessingDigitalizedReceipt(image):
    img = cv2.imread(image)

    resized_img = resizeImage(img)
    final_img = grayscale(resized_img)

    return final_img

def pdf2Image(pdf_path):

    images = convert_from_path(pdf_path)

    output_folder = "receipts"

    for i, image in enumerate(images):
        image.save(os.path.join(output_folder ,f"fatura_pagina_{i + 1}.jpg"), "JPEG")