import httpx
from bs4 import BeautifulSoup

def acessar_pagina(url):
    max_tentativas = 5
    tentativa = 1
    while tentativa <= max_tentativas:
        try:
            resposta = httpx.get(url, timeout=30)
            if resposta.status_code == 200:
                return resposta.json()  # Retorna os dados JSON da resposta
            else:
                print(f"Erro ao acessar {url}: {resposta.status_code}. Tentativa {tentativa}/{max_tentativas}")
                tentativa += 1
        except httpx.RequestError as e:
            print(f"Erro de requisição em {url}: {e}. Tentativa {tentativa}/{max_tentativas}")
            tentativa += 1
    print(f"Excedido o número máximo de tentativas para {url}.")
    return None

def extrair_informacoes(json_data):
    dados = []
    for item in json_data:
        if item.get('language') == 'EN':
            # Informações do livro principal em inglês
            code = item.get('code')
            title = item.get('title')
            description = item.get('description', '')
            pdf_url = f"https://www.chapellibrary.org/api/books/download?code={code}&format=pdf"
            
            # Remove tags HTML da descrição usando BeautifulSoup
            soup = BeautifulSoup(description, 'html.parser')
            description_cleaned = soup.get_text(separator='\n')
            
            # Verifica se há autores definidos
            authors = item.get('authors', [])
            author_name = authors[0]['name'] if authors else 'Autor Desconhecido'
            
            dados.append({
                "code": code,
                "title": title,
                "author": author_name,
                "description": description_cleaned.strip(),  # Remove espaços em branco extras
                "pdf_url": pdf_url
            })
    
    return dados  # Retorna a lista de informações extraídas

def main():
    base_url = 'https://www.chapellibrary.org/api/books'
    page_count = 3
    
    for page in range(1, page_count + 1):
        url = f'{base_url}?pageSize=10&pageCount={page}&language=EN&sortby=title'
        
        # Acessa a página e obtém os dados JSON
        json_data = acessar_pagina(url)
        
        if json_data:
            # Extrai as informações relevantes do JSON
            informacoes = extrair_informacoes(json_data)
            
            # Imprime as informações formatadas
            for item in informacoes:
                print("-" * 50)
                print(f"Código: {item['code']}")
                print(f"Título: {item['title']}")
                print(f"Autor: {item['author']}")
                print(f"Descrição: {item['description']}")
                print(f"Link PDF: {item['pdf_url']}")
                print()  # Adiciona uma linha em branco entre cada livro

if __name__ == '__main__':
    main()
