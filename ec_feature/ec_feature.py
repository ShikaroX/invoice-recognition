import cv2
import pytesseract
from pdf2image import convert_from_path
import os

def extract_text_from_image(image_path):
    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        text = pytesseract.image_to_string(thresh, lang="por")
        return text
    except Exception as e:
        print(f"Erro ao processar a imagem {image_path}: {e}")
        return ""

def extract_text_from_pdf(pdf_path, poppler_path=None):
    try:
        # Configurar Poppler no Windows se necessário
        if poppler_path:
            images = convert_from_path(pdf_path, poppler_path=poppler_path)
        else:
            images = convert_from_path(pdf_path)
        
        all_text = ""
        for i, image in enumerate(images):
            temp_image_path = f"temp_page_{i}.jpg"
            image.save(temp_image_path, "JPEG")
            text = extract_text_from_image(temp_image_path)
            all_text += text + "\n"
            os.remove(temp_image_path)
        
        return all_text
    except Exception as e:
        print(f"Erro ao processar o PDF {pdf_path}: {e}")
        return ""

if __name__ == "__main__":
    file_path = r"C:\Users\guilh\OneDrive\Ambiente de Trabalho\ProjFinal\ec_feature\receipts\receipt_1.jpeg"
    
    if not os.path.exists(file_path):
        print(f"Erro: O arquivo {file_path} não foi encontrado.")
        exit(1)
    
    extracted_text = extract_text_from_pdf(file_path) if file_path.endswith(".pdf") else extract_text_from_image(file_path)
    
    if extracted_text:
        print("Texto extraído:")
        print(extracted_text)
        with open("extracted_text.txt", "w", encoding="utf-8") as f:
            f.write(extracted_text)
    else:
        print("Nenhum texto foi extraído.")