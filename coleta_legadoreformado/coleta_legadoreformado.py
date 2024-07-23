import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = 'https://legadoreformado.com'

def extrair_links_livros(soup):
    """Extrai os links dos livros da página de categoria."""
    links_livros = []
    produtos = soup.find_all('li', class_='product')
    for produto in produtos:
        link_livro = produto.find('a', class_='woocommerce-LoopProduct-link')['href']
        links_livros.append(link_livro)
    return links_livros

def raspar_pagina_livro(url):
    """Coleta o link do PDF e o nome do livro na página individual do livro."""
    url = urljoin(BASE_URL, url)
    response = httpx.get(url, follow_redirects=True)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    # Encontrar o link do PDF dentro do span com classe 'Y2IQFc'
    span_download = soup.find('span', class_='Y2IQFc')
    if span_download:
        link_a = span_download.find('a') 
        if link_a:  
            link_pdf = link_a['href']
        else:
            link_pdf = None
    else:
        link_pdf = None

    # Encontrar o nome do livro
    nome_livro = soup.find('h1', class_='product_title').text.strip()

    return link_pdf, nome_livro

def raspar_livros_gratuitos():
    """Coleta os links dos PDFs e os nomes dos livros gratuitos."""
    livros = []
    pagina_atual = 1

    while True:
        if pagina_atual == 1:
            url = 'https://legadoreformado.com/categoria-produto/livros/?view=list'
        else:
            url = f'https://legadoreformado.com/categoria-produto/livros/page/{pagina_atual}/?view=list'

        response = httpx.get(url, follow_redirects=True)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        links_livros = extrair_links_livros(soup)
        for link_livro in links_livros:
            link_pdf, nome_livro = raspar_pagina_livro(link_livro)
            if link_pdf:
                livros.append((nome_livro, link_pdf))

        # Verifica se há próxima página
        proxima_pagina = soup.find('a', class_='next page-link')
        if proxima_pagina:
            pagina_atual += 1
        else:
            break

    return livros

def main():
    """Função principal que executa o web scraping."""
    livros = raspar_livros_gratuitos()
    
    print("Lista de livros gratuitos:")
    for nome, link in livros:
        print(f'Nome: {nome}')
        print(f'Link: {link}')
        print('-' * 30)  # Separador entre os livros

if __name__ == '__main__':
    main()