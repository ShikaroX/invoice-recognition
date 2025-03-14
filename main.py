# main file 
import numpy as np
import cv2
import pytesseract
from pdf2image import convert_from_path
import os
from sys import exit
import functions

print("~" * 40)
print("\t\tMENU")
print("~" * 40)
print("1- Fatura digital")
print("2- Fatura digitalizada")
print("3- Fatura fotografada")
print("0- Sair")
print("~" * 40)
opc = int(input("Digite a opção: "))

if opc == 0:
    exit()
elif opc == 1:
    file = "pdf_files/fatura_digital_5.pdf"

    if os.path.splitext(file)[1].lower() == ".pdf":
        functions.pdf2Image(file)
        file = "receipts/fatura_pagina_1.jpg"

    final_image = functions.preProcessingDigitalReceipt(file)

elif opc == 2:
    file = "receipts/fatura_digitalizada_7.jpg"

    if os.path.splitext(file)[1].lower() == ".pdf":
        functions.pdf2Image(file)
        file = "receipts/fatura_pagina_1.jpg"

    final_image = functions.preProcessingDigitalizedReceipt(file)

cv2.imshow("Final image", final_image)
cv2.waitKey(0)

    
