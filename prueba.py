import pandas as pd
import requests
import dns.resolver
from bs4 import BeautifulSoup

# Dominios comunes a ignorar
common_domains = {'gmail.com', 'hotmail.com', 'yahoo.com'}

def extract_domain(email):
    return email.split('@')[-1].strip()

def has_mx_record(domain):
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        return bool(answers)
    except:
        return False

def analyze_web_content(domain):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        for protocol in ['http', 'https']:
            url = f"{protocol}://{domain}"
            response = requests.get(url, allow_redirects=True, timeout=10, headers=headers)
            final_url = response.url
            if "error" in final_url.lower() or "not_found" in final_url.lower():
                continue
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text(strip=True)
                words = text.split()
                if len(words) > 300:
                    return True
        return False
    except requests.RequestException:
        return False

def read_emails_from_file(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            for email in line.split(','):
                yield email.strip()

def main():
    input_file_path = 'lista_correos.txt'
    output_file_path = 'resultados.xlsx'
    results = []

    for email in read_emails_from_file(input_file_path):
        domain = extract_domain(email)
        if domain not in common_domains:
            mx_record_exists = has_mx_record(domain)
            if mx_record_exists:
                website_active = analyze_web_content(domain)
                results.append({
                    'correo': email,
                    'web': 'sí' if website_active else 'no'
                })

    df = pd.DataFrame(results)
    df.to_excel(output_file_path, index=False, sheet_name='Resultados')
    print(f"Los resultados han sido guardados en el archivo {output_file_path}")

if __name__ == '__main__':
    main()
