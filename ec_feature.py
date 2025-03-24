import pytesseract

def extract_text_from_image(image_path):
    try:
        text = pytesseract.image_to_string(image_path, lang="por")
        return text
    except Exception as e:
        print(f"Erro ao processar a imagem {image_path}: {e}")
        return ""
