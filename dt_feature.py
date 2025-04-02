import pytesseract
import cv2

def extract_text_from_image(image_path):
    try:
        custom_config = '--oem 1 --psm 4 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789,.€@()/"'
        text = pytesseract.image_to_string(image_path, lang="por", config=custom_config)
        return text.strip()
    except Exception as e:
        print(f"Erro ao processar a imagem {image_path}: {e}")
        return ""