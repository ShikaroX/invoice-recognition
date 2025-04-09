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
        elif ent.label_ == "TIME" and entities["hora"] == "Desconhecido":
            entities["hora"] = ent.text.strip()
        elif ent.label_ == "ORG":
            if "lda" in ent.text.lower() or "s.a." in ent.text.lower():
                entities["empresa"] = ent.text.strip()

    if entities["data"] == "Desconhecido":
        match = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', text)
        if not match:
            match = re.search(r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})', text, re.IGNORECASE)
        if match:
            entities["data"] = match.group(1).strip()

    if entities["hora"] == "Desconhecido":
        match = re.search(r'(\d{1,2}:\d{2}(?::\d{2})?)', text)
        if match:
            entities["hora"] = match.group(1).strip()

    return entities


def calcular_iva_total(iva_reduzido, iva_normal):
    try:
        iva_reduzido_valor = float(iva_reduzido.replace(",", ".").replace("€", "").strip())
        iva_normal_valor = float(iva_normal.replace(",", ".").replace("€", "").strip())
        iva_total = iva_reduzido_valor + iva_normal_valor
        return f"{iva_total:.2f} €"
    except ValueError:
        return "Desconhecido"


def extract_with_regex(text):
    results = {
        "numero_fatura": "Desconhecido",
        "nif": "Desconhecido",
        "iva_total": "Desconhecido",
        "total": "0.00 €",
        "metodo_pagamento": "Desconhecido"
    }

    match = re.search(r'^\s*(?:FATURA)?\s*([A-Z\s]{3,})\s*$', text, re.MULTILINE)
    if match:
        results["empresa_override"] = match.group(1).strip()

    patterns_fatura = [
        r'Fatura.*?[Nn][º°.]?\s*(\S+)',
        r'Fatura/Recibo\s+N[.ºº]?\s*[:\-]?\s*([A-Z0-9\/\-]+)',
        r'FATURA\s*[/:]?\s*([A-Z0-9\/\-]+)',
        r'Fatura\s+[Nn][.ºº]?\s*[:\-]?\s*([A-Z0-9\/\-]+)',
        r'Fatura.*?([\d]{6,})',
        r'N[ºº]?\s*[\-]?\s*(\d{6,})'
    ]
    for pat in patterns_fatura:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            numero = match.group(1).strip()
            if not numero.lower().startswith("recibo"):
                results["numero_fatura"] = numero
                break

    patterns_nif = [
        r'NIF[:\s]*PT?(\d{9})',
        r'NIF[:\s]*?(\d{9})',
        r'Nº\s+contribuinte[:\s]*?(\d{9})',
        r'Contribuinte\s*N[ºo]?\s*:?(\d{9})',
        r'Contribuinte\s*:?\s*(\d{9})',
        r'Nº\s+contribuinte\s*(\d{9})',
        r'Número\s+de\s+Contribuinte[:\s]*(\d{9})',
    ]
    for pat in patterns_nif:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            results["nif"] = match.group(1)
            break

    if results["nif"] == "Desconhecido":
        match = re.search(r'\b(\d{9})\b', text)
        if match:
            results["nif"] = match.group(1)

    iva_reduzido = "0.00"
    iva_normal = "0.00"
    patterns_iva = [
        r'TOTAL\s+DE\s+IVA[:\s€]*([\d.,]+)',
        r'Total\s+IVA[:\s€]*([\d.,]+)',
        r'Total\s*I\.V\.A\.[:\s€]*([\d.,]+)',
        r'IVA\s+Total[:\s€]*([\d.,]+)',
        r'Isento\(.*?\)\s*\|\s*([\d.,]+)',
        r'IVA\s+incluído[:\s€]*([\d.,]+)',
        r'IVA\s+cobrado[:\s€]*([\d.,]+)',
        r'IVA\s+não\s+tributário\s+\(taxa\s+reduzida\s+em\s+vigor\):\s*([\d.,]+)',
        r'IVA\s+não\s+tributário\s+\(taxa\s+normal\s+em\s+vigor\):\s*([\d.,]+)',
    ]
    for pat in patterns_iva:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            valor = match.group(1).replace('.', '').replace(',', '.')
            try:
                if "reduzida" in pat:
                    iva_reduzido = f"{float(valor):.2f}"
                elif "normal" in pat:
                    iva_normal = f"{float(valor):.2f}"
            except:
                pass

    iva_total = calcular_iva_total(iva_reduzido, iva_normal)
    results["iva_total"] = iva_total if iva_total != "0.00 €" else "Desconhecido"

    if results["iva_total"] == "Desconhecido":
        match = re.search(r'Taxa\s+de\s+IVA\s*:\s*(\d+)%', text, re.IGNORECASE)
        if match:
            results["iva_total"] = f"Taxa: {match.group(1)}%"

    patterns_total = [
        r'Total\s+pago\s+em\s+Euros[:\s€]*([\d.,]+)',
        r'VALOR\s+TOTAL\s+DA\s+FATURA[:\s€]*([\d.,]+)',
        r'Total\s+a\s+pagar[:\s€]*([\d.,]+)',
        r'Total\s*a\s+pagar.*?([\d.,]+)',
        r'Total\s*[:€]*\s*([\d.,]+)',
        r'Total\s+Final[:€]*\s*([\d.,]+)',
        r'Total\s+c\/?\s*IVA[:\s€]*([\d.,]+)',
        r'Total\s+com\s+IVA[:\s€]*([\d.,]+)',
        r'Valor\s+Total[:€]*\s*([\d.,]+)',
        r'Pago\s+[:\s€]*([\d.,]+)',
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

    metodos = ["visa", "mb way", "mbway", "multibanco", "paypal", "dinheiro", "cartão", "cartao", "sequra", "paygate"]
    for metodo in metodos:
        if metodo in text.lower():
            results["metodo_pagamento"] = metodo.title().replace("Mbway", "Mb Way")
            break

    return results


def extract_products(text):
    produtos = []
    produto_encontrado = False

    pattern_produto = re.compile(
        r'\d+\.\s+(.*?)\s{2,}(\d+)\s*/\s*([\d.,]+)\s*€\s*/\s*\d+%?\s*/\s*([\d.,]+)\s*€', re.IGNORECASE)

    for match in pattern_produto.finditer(text):
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
        produto_encontrado = True

    if not produto_encontrado:
        pattern_alt = re.compile(
            r'\|\s*(.*?)\s*\|\s*(\d+)\s*\|\s*\w+\s*\|\s*([\d.,]+)\s*€\s*\|\s*\w+\s*\|\s*([\d.,]+)\s*€'
        )
        for match in pattern_alt.finditer(text):
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
            produto_encontrado = True

    if not produto_encontrado:
        produtos.append({
            "descricao": "Pagamento de Serviço",
            "quantidade": "1",
            "valor_unitario": "0.00 €"
        })

    return produtos


def extract_receipt_fields(text):
    text = re.sub(r'\*+', '', text)
    entities = extract_entities_spacy(text)
    values = extract_with_regex(text)
    produtos = extract_products(text)

    if produtos and len(produtos) > 0:
        try:
            soma = sum([float(p['valor_unitario'].replace('€', '').strip()) for p in produtos])
            values["total"] = f"{soma:.2f} €"
        except:
            pass

    empresa_final = values.get("empresa_override", entities["empresa"]).split('\n')[0].strip()

    if values["numero_fatura"].upper() == empresa_final.upper():
        padroes_fatura = [
            r'FATURA[\s:]*([A-Z]+\d+/\d+)',
            r'FATURA([A-Z]+\d+/\d+)',
            r'FATURA.*?([A-Z]{2,}\d{2,}/\d{5,})',
            r'N[ºº]?\s*[:\-]?\s*([A-Z0-9]+/\d+)',
            r'FATURA\s*N[ºº]?\s*[:\-]?\s*([A-Z0-9/\-]+)'
        ]
        for pat in padroes_fatura:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                numero_corrigido = match.group(1).strip()
                if numero_corrigido.upper() != empresa_final.upper():
                    values["numero_fatura"] = numero_corrigido
                    break

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
