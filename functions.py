# functions file 
import numpy as np
import cv2
from pdf2image import convert_from_path
import os

def resizeImage(image, width, height):
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_CUBIC)

def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def preProcessingDigitalReceipt(image):
    resized_img = resizeImage(image, 1600, 2400)    
    grayscale_img = grayscale(resized_img)

    return grayscale_img

def preProcessingDigitalizedReceipt(image):
    """
    This function performs all the necessary preprocessing for digitized invoices.

    :param image: Input image to be processed.

    :return: Preprocessed image.
    """

    resized_img = resizeImage(image, 900, 1100)

    grayscale_img = grayscale(resized_img)

    gaussian_blur = cv2.GaussianBlur(grayscale_img, (3, 3), 0)

    thresh = cv2.threshold(gaussian_blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    kernel = np.ones((30, 30), np.uint8)
    dilate = cv2.dilate(thresh, kernel)

    contours, _ = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    mask = np.zeros_like(dilate)
    min_area = 50000
    for contour in contours:
        if cv2.contourArea(contour) > min_area:
            cv2.drawContours(mask, [contour], -1, 255, thickness=cv2.FILLED)

            x, y, w, h = cv2.boundingRect(contour)
            # cv2.rectangle(resized_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            rect = cv2.minAreaRect(contour)
            center = rect[0]
            angle = rect[2]

            if 45 <= angle <= 90:
                new_angle = -(90 - angle)
            else:
                new_angle = angle

            print(angle)
            print(new_angle)
            
            matrix = cv2.getRotationMatrix2D((center[0], center[1]), new_angle, 1.0)

            rotated_mask = cv2.warpAffine(mask, matrix, (resized_img.shape[1], resized_img.shape[0]), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    
            contours, _ = cv2.findContours(rotated_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            rotated_img = cv2.warpAffine(grayscale_img, matrix, (resized_img.shape[1], resized_img.shape[0]), borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))

            min_area = 50000
            for contour in contours:
                if cv2.contourArea(contour) > min_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    # cv2.rectangle(rotated_img, (x, y), (x + w, y + h), (0, 255, 255), 2)

            # box = np.intp(cv2.boxPoints(rect))

            # cv2.circle(resized_img, (int(center[0]), int(center[1])), 7, (255, 0, 0), -1)
            # cv2.polylines(resized_img, [box], True, (255, 0, 0), 2)

            bounding_box = (x, y, w, h)

            if bounding_box:
                cropped_img = rotated_img[y:y+h, x:x+w]
            else:
                print("Bounding box not found!")
                return

            gaussian_blur = cv2.GaussianBlur(cropped_img, (3, 3), 0)

            _, binary = cv2.threshold(gaussian_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return binary

def pdf2Image(pdf_path):
    images = convert_from_path(pdf_path)

    output_folder = "receipts"

    for i, image in enumerate(images):
        image.save(os.path.join(output_folder ,f"fatura_pagina_{i + 1}.jpg"), "JPEG")