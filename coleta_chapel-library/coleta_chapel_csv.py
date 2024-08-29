import httpx
from bs4 import BeautifulSoup
import os
import time
import csv
import json
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()
DIR_BD = os.getenv("DIR_BD")

if not DIR_BD:
    raise ValueError("A variável de ambiente DIR_BD não está definida.")

def acessar_pagina(url):
    """
    Acessa a página da URL fornecida e retorna o conteúdo em formato JSON.

    Args:
        url (str): A URL da página a ser acessada.

    Returns:
        dict or None: Um dicionário contendo os dados JSON da página,
                      ou None se houver um erro ao acessar a página.
    """
    max_tentativas = 5
    tentativa = 1
    while tentativa <= max_tentativas:
        try:
            resposta = httpx.get(url, timeout=30)
            if resposta.status_code == 200:
                return resposta.json()
            else:
                time.sleep(5)
                tentativa += 1
        except httpx.RequestError as e:
            time.sleep(5)
            tentativa += 1
    return None

def verificar_link(url):
    """
    Verifica se o link fornecido é acessível.

    Args:
        url (str): A URL a ser verificada.

    Returns:
        bool: True se o link for acessível (código de status 200), False caso contrário.
    """
    try:
        resposta = httpx.get(url, timeout=10)
        return resposta.status_code == 200
    except httpx.RequestError:
        return False

def extrair_informacoes(dados_json):
    """
    Extrai informações relevantes dos dados JSON, incluindo o preço,
    e verifica a disponibilidade dos links para download de PDF e EPUB.

    Args:
        dados_json (dict): Um dicionário contendo os dados JSON da página.

    Returns:
        list: Uma lista de dicionários, onde cada dicionário representa um livro
              com suas informações extraídas.
    """
    lista_livros = []
    for item in dados_json:
        codigo = item.get('code')
        titulo = item.get('title')
        descricao = item.get('description', '')
        preco = item.get('price', 'Indisponível')
        if isinstance(preco, float) or isinstance(preco, int):
            preco = f'{preco:.2f}'
        url_livro = f"https://www.chapellibrary.org/book/{codigo}/"
        tem_versao_imprimivel = 'SIM' if item.get('hasPrintableVersion', False) else 'NÃO'

        url_pdf = f"https://www.chapellibrary.org/api/books/download?code={codigo}&format=pdf"
        if verificar_link(url_pdf):
            link_pdf = url_pdf
        else:
            link_pdf = ""

        url_epub = f"https://www.chapellibrary.org/api/books/download?code={codigo}&format=epub"
        if verificar_link(url_epub):
            link_epub = url_epub
        else:
            link_epub = ""

        soup = BeautifulSoup(descricao, 'html.parser')
        descricao_limpa = soup.get_text(separator='\n')

        autores = item.get('authors', [])
        nome_autor = autores[0]['name'] if autores else 'Autor Desconhecido'

        livro = {
            "codigo": f"Código: {codigo}",
            "titulo": f"Título: {titulo}",
            "autor": f"Autor: {nome_autor}",
            "descricao": f"Descrição: {descricao_limpa.strip()}",
            "preco": f"Preço: {preco}",
            "link_livro": f"Link do livro: {url_livro}",
            "link_pdf": f"Link do PDF: {link_pdf}",
            "link_epub": f"Link do EPUB: {link_epub}",
            "tem_versao_imprimivel": f"Tem versão imprimível: {tem_versao_imprimivel}"
        }

        lista_livros.append(livro)

    return lista_livros


def salvar_csv(dados):
    """
    Salva todos os dados dos livros em um único arquivo CSV chamado 'livros_chapel.csv'.

    Args:
        dados (list): Uma lista de dicionários, onde cada dicionário representa um livro.
    """
    nome_arquivo = os.path.join(DIR_BD, 'livros_chapel.csv')

    campos = ["codigo", "titulo", "autor", "descricao", "preco", "link_livro", "link_pdf",
              "link_epub", "tem_versao_imprimivel"]

    # Se o arquivo não existir, cria um novo com cabeçalho
    if not os.path.isfile(nome_arquivo): 
        with open(nome_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
            escritor = csv.DictWriter(arquivo_csv, fieldnames=campos)
            escritor.writeheader()

    # Abre o arquivo em modo 'append' para adicionar dados
    with open(nome_arquivo, 'a', newline='', encoding='utf-8') as arquivo_csv:
        escritor = csv.DictWriter(arquivo_csv, fieldnames=campos)
        for livro in dados:
            escritor.writerow(livro)

def salvar_json(dados):
    """
    Salva todos os dados dos livros em um único arquivo JSON chamado 'livros_chapel.json'.

    Args:
        dados (list): Uma lista de dicionários, onde cada dicionário representa um livro.
    """
    nome_arquivo = os.path.join(DIR_BD, 'livros_chapel.json')
    with open(nome_arquivo, 'w', encoding='utf-8') as arquivo_json:
        json.dump(dados, arquivo_json, ensure_ascii=False, indent=4)

def main():
    """
    Função principal que orquestra o processo de raspagem de dados
    e salvamento em um arquivo CSV.
    """
    url_base = 'https://www.chapellibrary.org/api/books'
    idiomas = ['PT', 'EN', 'ES', 'FR', 'IT']
    total_paginas = 121
    todos_os_livros = [] # Para armazenar todos os livros antes de salvar

    for idioma in idiomas:
        for pagina in range(0, total_paginas + 1):
            url = f'{url_base}?pageSize=10&pageCount={pagina}&language={idioma}&sortby=title'
            dados_json = acessar_pagina(url)

            if dados_json:
                informacoes_livros = extrair_informacoes(dados_json)
                todos_os_livros.extend(informacoes_livros) 

    # Salva todos os livros em CSV e JSON após a raspagem completa
    salvar_csv(todos_os_livros) 
    salvar_json(todos_os_livros)

if __name__ == '__main__':
    main()