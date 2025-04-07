# main para testes do ec_feature
import numpy as np
import cv2
import pytesseract
from pdf2image import convert_from_path
import os
from sys import exit
import functions
import ec_feature
import dt_feature
import deepseek
import re


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
    image = "pdf_files/fatura_digital_2.pdf"

    if os.path.splitext(image)[1].lower() == ".pdf":
        functions.pdf2Image(image)
        image = "receipts/fatura_pagina_1.jpg"

    img = cv2.imread(image)

    final_image = functions.preProcessingDigitalReceipt(img)

#elif opc == 2:
   #image = "receipts/fatura_digitalizada_7_inv.jpg"

   #if os.path.splitext(image)[1].lower() == ".pdf":
        #functions.pdf2Image(image)
        #image = "receipts/fatura_pagina_1.jpg"

        #img = cv2.imread(image)

        #final_image = functions.preProcessingDigitalizedReceipt(img)

#orientation = pytesseract.image_to_osd(final_image)
#print(orientation)
#if orientation[39:42] == '180':
    #final_image = cv2.rotate(final_image, cv2.ROTATE_180)

#extracted_text = pytesseract.image_to_string(final_image, lang="por")

#system_prompt = "Corrige me este texto: "

#enhanced_text = deepseek.ask_deepseek(extracted_text, system_prompt)
    
#if extracted_text:
    #print("Texto extraído salvo em extracted_text.txt")
    #with open("extracted_text.txt", "w", encoding="utf-8") as f:
        #f.write(enhanced_text)
#else:
    #print("Nenhum texto foi extraído.")

#cv2.imwrite('original_image.jpg', img)
#cv2.imwrite('preprocessed_image.jpg', final_image)
#cv2.waitKey(0)

with open("extracted_text.txt", "r", encoding="utf-8") as f:
    text = f.read()
    
fields_extracted = ec_feature.extract_receipt_fields(text)
    
with open("receipt_data.json", "w", encoding="utf-8") as json_file:
    ec_feature.json.dump(fields_extracted, json_file, ensure_ascii=False, indent=4)
    
print("Dados extraídos salvos em receipt_data.json")