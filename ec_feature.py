import pytesseract
import cv2

def extract_text_from_image(image_path):
    try:
        custom_config = '--oem 3 --psm 6'
        text = pytesseract.image_to_string(image_path, lang="por", config=custom_config)
        return text.strip()
    except Exception as e:
        print(f"Erro ao processar a imagem {image_path}: {e}")
        return ""