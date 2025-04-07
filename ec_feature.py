import re
import json
import spacy

nlp = spacy.load("pt_core_news_lg")

def extract_entities_spacy(text):
    doc = nlp(text)
    entities = {
        "data": "Desconhecido",
        "hora": "Desconhecido",
        "empresa": "Desconhecido"
    }

    for ent in doc.ents:
        if ent.label_ == "DATE" and entities["data"] == "Desconhecido":
            entities["data"] = ent.text.strip()
        elif ent.label_ == "TIME":
            entities["hora"] = ent.text.strip()
        elif ent.label_ == "ORG":
            if "lda" in ent.text.lower() or "s.a." in ent.text.lower():
                entities["empresa"] = ent.text.strip()

    # Ajuste extra: tentar extrair data da compra manualmente se Spacy falhar
    if entities["data"] == "Desconhecido":
        match = re.search(r'Data da compra[:\s]*([0-9]{2}/[0-9]{2}/[0-9]{4})', text, re.IGNORECASE)
        if match:
            entities["data"] = match.group(1).strip()

    return entities

def extract_with_regex(text):
    results = {
        "numero_fatura": "Desconhecido",
        "nif": "Desconhecido",
        "iva_total": "Desconhecido",
        "total": "0.00 €",
        "metodo_pagamento": "Desconhecido"
    }

    # Empresa (caso Spacy falhe)
    match = re.search(r'\n\s*([A-ZÁÉÍÓÚÇ].*?(lda|LDA|s\.a\.|S\.A\.))', text)
    if match:
        results["empresa_override"] = match.group(1).strip()

    # Nº da Fatura
    patterns_fatura = [
        r'Fatura/Recibo\s+N[.ºº]?\s*[:\-]?\s*([A-Z0-9\/\-]+)',  # NOVO padrão
        r'FATURA\s*[/:]?\s*([A-Z0-9\/\-]+)',
        r'Fatura\s+[Nn][.ºº]?\s*[:\-]?\s*([A-Z0-9\/\-]+)',
        r'Fatura.*?([\d]{6,})',
    ]
    for pat in patterns_fatura:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            results["numero_fatura"] = match.group(1).strip()
            break

    # NIF
    patterns_nif = [
        r'NIF[:\s]*PT?(\d{9})',
        r'NIF[:\s]*?(\d{9})',
        r'Nº\s+contribuinte[:\s]*?(\d{9})',
        r'Contribuinte\s*N[ºo]?\s*:?(\d{9})',
        r'Contribuinte\s*:?\s*(\d{9})',  # NOVO padrão
    ]
    for pat in patterns_nif:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            results["nif"] = match.group(1)
            break

    # IVA total
    patterns_iva = [
        r'TOTAL\s+DE\s+IVA[:\s€]*([\d.,]+)',
        r'Total\s+IVA[:\s€]*([\d.,]+)',
        r'Total\s*I\.V\.A\.[:\s€]*([\d.,]+)',
        r'IVA\s+Total[:\s€]*([\d.,]+)',
        r'Isento\(.*?\)\s*\|\s*([\d.,]+)',  # caso do isento
    ]
    for pat in patterns_iva:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            valor = match.group(1).replace('.', '').replace(',', '.')
            try:
                results["iva_total"] = f"{float(valor):.2f} €"
            except:
                pass
            break

    # Total geral
    patterns_total = [
        r'VALOR\s+TOTAL\s+DA\s+FATURA[:\s€]*([\d.,]+)',
        r'Total\s+a\s+pagar[:\s€]*([\d.,]+)',
        r'Total\s*[:€]*\s*([\d.,]+)',
        r'Total\s+Final[:€]*\s*([\d.,]+)',
        r'Valor\s+Total[:€]*\s*([\d.,]+)',
        r'\|\s*[^|\n]+\|\s*\d+\s*\|\s*[^|\n]+\s*\|\s*[\d.,]+\s*€\s*\|\s*[^|\n]+\s*\|\s*([\d.,]+)\s*€'
    ]
    for pat in patterns_total:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            valor = match.group(1).replace('.', '').replace(',', '.')
            try:
                results["total"] = f"{float(valor):.2f} €"
            except:
                pass
            break

    # Método de pagamento
    metodos = ["visa", "mb way", "mbway", "multibanco", "paypal", "dinheiro", "cartão", "cartao", "sequra", "paygate"]
    for metodo in metodos:
        if metodo in text.lower():
            results["metodo_pagamento"] = metodo.title().replace("Mbway", "Mb Way")
            break

    return results

def extract_products(text):
    produtos = []

    # Limitar à secção da tabela (melhor precisão)
    start = text.find("Resumo dos Artigos/Serviços")
    end = text.find("Detalhes da Compra")

    if start != -1 and end != -1:
        tabela_produtos = text[start:end]
    else:
        tabela_produtos = text  # fallback

    # Procurar linhas tipo tabela
    for line in tabela_produtos.splitlines():
        match = re.search(r'\|\s*(.*?)\s*\|\s*(\d+)\s*\|\s*\w+\s*\|\s*([\d.,]+)\s*€\s*\|\s*\w+\s*\|\s*([\d.,]+)\s*€', line)
        if match:
            descricao = match.group(1).strip()
            quantidade = match.group(2).strip()
            preco_unit = match.group(3).replace('.', '').replace(',', '.')
            try:
                preco = f"{float(preco_unit):.2f} €"
            except:
                preco = "Desconhecido"
            produtos.append({
                "descricao": descricao,
                "quantidade": quantidade,
                "valor_unitario": preco
            })

    return produtos

def extract_receipt_fields(text):
    text = re.sub(r'\*+', '', text)  # remove markdown
    entities = extract_entities_spacy(text)
    values = extract_with_regex(text)
    produtos = extract_products(text)

    empresa_final = values.get("empresa_override", entities["empresa"])

    resultado = {
        "empresa": empresa_final,
        "data": entities["data"],
        "hora": entities["hora"],
        "numero_fatura": values["numero_fatura"],
        "nif": values["nif"],
        "iva_total": values["iva_total"],
        "total": values["total"],
        "metodo_pagamento": values["metodo_pagamento"],
        "produtos": produtos
    }

    return resultado
