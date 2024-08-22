import httpx
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import time
import csv

def acessar_pagina(url):
    """
    Acessa a página da URL fornecida e retorna o conteúdo em formato JSON.
    """
    max_tentativas = 5
    tentativa = 1
    while tentativa <= max_tentativas:
        try:
            resposta = httpx.get(url, timeout=30)
            if resposta.status_code == 200:
                return resposta.json()
            else:
                print(f"Erro ao acessar {url}: {resposta.status_code}. Tentativa {tentativa}/{max_tentativas}")
                time.sleep(5)
                tentativa += 1
        except httpx.RequestError as e:
            print(f"Erro de requisição em {url}: {e}. Tentativa {tentativa}/{max_tentativas}")
            time.sleep(5)
            tentativa += 1
    print(f"Excedido o número máximo de tentativas para {url}.")
    return None

def extrair_informacoes(dados_json):
    """
    Extrai informações relevantes dos dados JSON.
    """
    lista_livros = []
    for item in dados_json:
        codigo = item.get('code')
        titulo = item.get('title')
        url_pdf = f"https://www.chapellibrary.org/api/books/download?code={codigo}&format=pdf"
        url_epub = f"https://www.chapellibrary.org/api/books/download?code={codigo}&format=epub"
        url_livro = f"https://www.chapellibrary.org/book/{codigo}/"  # URL original do livro

        autores = item.get('authors', [])
        nome_autor = autores[0]['name'] if autores else 'Autor Desconhecido'

        livro = {
            "codigo": codigo,
            "titulo": titulo,
            "autor": nome_autor,
            "idioma": item.get('language', 'Desconhecido'),
            "link_pdf": url_pdf if verificar_link(url_pdf) else None,
            "link_epub": url_epub if verificar_link(url_epub) else None,
            "link_original": url_livro
        }

        lista_livros.append(livro)

    return lista_livros

def verificar_link(url):
    """
    Verifica se o link fornecido é acessível.
    """
    try:
        resposta = httpx.get(url, timeout=10)
        return resposta.status_code == 200
    except httpx.RequestError:
        return False

def gerar_csv(lista_livros):
    """
    Gera um arquivo CSV com as informações dos livros.
    """
    load_dotenv()
    DIR_BD = os.getenv("DIR_BD")
    
    if not DIR_BD:
        raise ValueError("A variável de ambiente DIR_BD não está definida.")

    nome_arquivo = os.path.join(DIR_BD, "livros_chapel.csv")

    with open(nome_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
        campos = ['codigo', 'titulo', 'autor', 'idioma', 'link_pdf', 'link_epub', 'link_original']
        escritor = csv.DictWriter(arquivo_csv, fieldnames=campos)
        escritor.writeheader()
        for livro in lista_livros:
            escritor.writerow(livro)

def main():
    """
    Função principal que orquestra o processo de raspagem de dados e geração do CSV.
    """
    url_base = 'https://www.chapellibrary.org/api/books'
    idiomas = ['PT','EN', 'ES', 'FR', 'IT']
    total_paginas = 121

    lista_livros_todos = []

    for idioma in idiomas:
        for pagina in range(0, total_paginas + 1):
            url = f'{url_base}?pageSize=10&pageCount={pagina}&language={idioma}&sortby=title'
            dados_json = acessar_pagina(url)

            if dados_json:
                informacoes_livros = extrair_informacoes(dados_json)
                lista_livros_todos.extend(informacoes_livros)

    # Gera o CSV único com todos os livros
    gerar_csv(lista_livros_todos)
    print(f"CSV 'livros_chapel.csv' gerado com sucesso!")

if __name__ == '__main__':
    main()