import httpx
from bs4 import BeautifulSoup

def acessar_pagina(url):
    """Acessa a página da web e retorna o conteúdo HTML."""
    try:
        resposta = httpx.get(url)
        resposta.raise_for_status()
        return resposta.text
    except httpx.HTTPError as exc:
        print(f"Erro ao acessar {exc.request.url!r}: {exc}")
        return None

def extrair_infos_ebooks(conteudo_html):
    """Extrai informações sobre ebooks da página da web."""
    ebooks = []
    sopa = BeautifulSoup(conteudo_html, 'html.parser')
    itens = sopa.find_all('li', class_='product')

    for item in itens:
        titulo = item.find('h2', class_='woocommerce-loop-product__title').text.strip()
        link_pagina = item.find('a', class_='woocommerce-LoopProduct-link')['href']

        # Acessa a página individual do ebook para extrair o link de download
        conteudo_pagina_ebook = acessar_pagina(link_pagina)
        link_download = extrair_link_download_ebook(conteudo_pagina_ebook)

        ebooks.append({'titulo': titulo, 'link_pagina': link_pagina, 'link_download': link_download})

    return ebooks

def extrair_link_download_ebook(conteudo_html):
    """Extrai o link de download do ebook da página individual."""
    sopa = BeautifulSoup(conteudo_html, 'html.parser')
    botao_download = sopa.find('div', class_='elementor-widget-button').find('a')
    if botao_download:
        return botao_download['href']
    return None

def extrair_infos_blog(conteudo_html):
  """Extrai informações sobre postagens de blog da página da web."""
  postagens = []
  sopa = BeautifulSoup(conteudo_html, 'html.parser')
  artigos = sopa.find_all('article', class_='elementor-post')

  for artigo in artigos:
    titulo_elemento = artigo.find('h3', class_='elementor-post__title').find('a')
    titulo = titulo_elemento.text.strip() if titulo_elemento else ''
    link = titulo_elemento['href'] if titulo_elemento else ''

    autor_elemento = artigo.find('span', class_='elementor-post-author')
    autor = autor_elemento.text.strip() if autor_elemento else ''

    postagens.append({'titulo': titulo, 'link': link, 'autor': autor})

  return postagens

def main():
    """Função principal que executa a extração de dados."""
    # Extrair informações de ebooks
    url_ebooks = 'https://oestandartedecristo.com/ebooks-orderbydate/'
    conteudo_ebooks = acessar_pagina(url_ebooks)
    if conteudo_ebooks:
        ebooks = extrair_infos_ebooks(conteudo_ebooks)
        print("----- Ebooks -----")
        for ebook in ebooks:
            print(f"Título: {ebook['titulo']}")
            print(f"Link da Página: {ebook['link_pagina']}")
            print(f"Link de Download: {ebook['link_download']}")
            print("-" * 20)

    # Extrair informações de postagens de blog
    print("\n----- Postagens de Blog -----")

    # Primeira página (estrutura diferente)
    url_blog = 'https://oestandartedecristo.com/blog/'
    conteudo_blog = acessar_pagina(url_blog)
    if conteudo_blog:
        postagens = extrair_infos_blog(conteudo_blog)
        for postagem in postagens:
            print(f"Título: {postagem['titulo']}")
            print(f"Link: {postagem['link']}")
            print(f"Autor: {postagem['autor']}")
            print("-" * 20)

    # Demais páginas (estrutura padrão)
    for pagina in range(2, 55):
        url_blog = f'https://oestandartedecristo.com/blog/page/{pagina}/'
        conteudo_blog = acessar_pagina(url_blog)
        if conteudo_blog:
            postagens = extrair_infos_blog(conteudo_blog)
            for postagem in postagens:
                print(f"Título: {postagem['titulo']}")
                print(f"Link: {postagem['link']}")
                print(f"Autor: {postagem['autor']}")
                print("-" * 20)

if __name__ == "__main__":
    main()  # Chama a função main() quando o script é executado