import spacy
import re
import json

def extract_receipt_fields(text):
    nlp = spacy.load("pt_core_news_sm")
    doc = nlp(text)
    
    fields = {}
    lines = text.split('\n')
    fields["supermercado"] = lines[0].strip() if lines else "Desconhecido"
    
    date_pattern = re.compile(r'\b(\d{2}[/-]\d{2}[/-]\d{2,4})\b')
    date_match = date_pattern.search(text)
    fields["data"] = date_match.group(1) if date_match else "Desconhecido"
    
    time_pattern = re.compile(r'\b(\d{2}:\d{2}(?::\d{2})?)\b')
    time_match = time_pattern.search(text)
    fields["hora"] = time_match.group(1) if time_match else "Desconhecido"
    
    invoice_pattern = re.compile(r'(?i)fatura simplificada\s*nro[:\s]*([\w\d\-/]+)')
    invoice_match = invoice_pattern.search(text)
    fields["numero_fatura"] = invoice_match.group(1) if invoice_match else "Desconhecido"
    
    nif_pattern = re.compile(r'\bNIF[:\s]*(\d{9})\b', re.IGNORECASE)
    nif_match = nif_pattern.search(text)
    fields["nif_supermercado"] = nif_match.group(1) if nif_match else "Desconhecido"
    
    total_pattern = re.compile(r'(?i)total\s*[a-z]*[:\s]+(\d+[.,]\d{2})')
    total_match = total_pattern.search(text)
    fields["total"] = total_match.group(1) if total_match else "Desconhecido"
    
    troco_pattern = re.compile(r'(?i)troco[:\s]+(\d+[.,]\d{2})')
    troco_match = troco_pattern.search(text)
    fields["troco"] = troco_match.group(1) if troco_match else "Desconhecido"
    
    payment_methods = ["Visa", "Multibanco", "Cartão Crédito", "Dinheiro", "Cartão Cliente"]
    fields["metodo_pagamento"] = next((method for method in payment_methods if method.lower() in text.lower()), "Desconhecido")
    
    products_pattern = re.compile(r'(?i)(?:\d{6,})?\s*([A-Za-z0-9 .,-]+)\s+(\d+[.,]\d{2})')
    products = products_pattern.findall(text)
    fields["produtos"] = [{"descricao": p[0].strip(), "valor": p[1]} for p in products] if products else []
    
    return fields

if __name__ == "__main__":
    with open("extracted_text.txt", "r", encoding="utf-8") as f:
        text = f.read()
    
    fields_extracted = extract_receipt_fields(text)
    
    with open("receipt_data.json", "w", encoding="utf-8") as json_file:
        json.dump(fields_extracted, json_file, ensure_ascii=False, indent=4)
    
    print("Dados extraídos salvos em receipt_data.json")