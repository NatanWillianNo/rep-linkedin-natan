import httpx
from bs4 import BeautifulSoup

def extrair_informacoes_livro(livro_html):
    """
    Extrai informações de um livro a partir de um elemento HTML.

    Args:
    - livro_html: Elemento BeautifulSoup representando um livro.

    Returns:
    - Tupla contendo (nome_do_livro, autor, link_do_recurso).
    """
    nome_livro = livro_html.find('span', class_='field-content').find('strong').text.strip()
    link_recurso = livro_html.find('a', href=True).get('href')
    autor_elemento = livro_html.find('div', class_='views-field-field-link-format').find('small')
    autor = autor_elemento.text.strip().replace('PDF by ', '') if autor_elemento else "Autor não encontrado"
    return nome_livro, autor, link_recurso

def verificar_link(link):
    """
    Verifica se o link leva a um arquivo PDF. Se não, tenta encontrar
    uma versão em PDF usando o Wayback Machine.

    Args:
    - link: URL a ser verificado.

    Returns:
    - URL final apontando para a versão em PDF (original ou do Wayback Machine).
    """
    try:
        resposta = httpx.get(link, timeout=10.0)
        resposta.raise_for_status()

        # Verifica se o conteúdo é um PDF
        if 'application/pdf' in resposta.headers.get('content-type', '').lower():
            return link  # Link original é um PDF

        # Se não for um PDF, tenta Wayback Machine
        link_wayback = f"https://web.archive.org/web/{link}"
        return link_wayback

    except httpx.HTTPError:
        # Em caso de erro HTTP, tenta Wayback Machine
        link_wayback = f"https://web.archive.org/web/{link}"
        return link_wayback

    except Exception as e:
        # Trata outras exceções
        print(f"Ocorreu um erro ao verificar o link {link}: {str(e)}")
        return None

def raspar_pagina_monergism(url_base, numero_pagina):
    """
    Raspa informações de livros de uma página específica dos resultados de busca do Monergism.

    Args:
    - url_base: URL base para a busca no Monergism.
    - numero_pagina: Número da página a ser raspada.

    Returns:
    - Lista de tuplas (nome_do_livro, autor, link_do_recurso) dos livros encontrados na página.
    """
    url = f"{url_base}&page={numero_pagina}"
    
    try:
        resposta = httpx.get(url)
        resposta.raise_for_status()
        soup = BeautifulSoup(resposta.content, 'html.parser')
        livros = soup.find_all('li', class_='views-row')
        return [extrair_informacoes_livro(livro) for livro in livros]
    
    except httpx.HTTPError as http_err:
        print(f"Erro HTTP ocorrido ao acessar {url}: {http_err}")
        return []
    
    except Exception as err:
        print(f"Erro ocorrido ao raspar a página {numero_pagina}: {err}")
        return []

def main():
    """
    Função principal para executar a raspagem de dados do Monergism.
    """
    url_base = "https://www.monergism.com/search?sort=field_link_title_sortable&order=asc&keywords=&format=46"

    for numero_pagina in range(0, 150):
        livros = raspar_pagina_monergism(url_base, numero_pagina)
        
        for nome, autor, link in livros:
            link_final = verificar_link(link)
            print(f"Nome: {nome}\nAutor: {autor}\nLink: {link_final}\n{'--'*20}")

if __name__ == "__main__":
    main()
