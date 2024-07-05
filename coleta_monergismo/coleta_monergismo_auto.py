import httpx
from bs4 import BeautifulSoup

def acessar_pagina(url):
    """
    Faz uma requisição GET para a URL fornecida e retorna o conteúdo da página.
    """
    max_tentativas = 5
    tentativa = 1
    while tentativa <= max_tentativas:
        try:
            resposta = httpx.get(url, timeout=30)
            if resposta.status_code == 200:
                return resposta.text  # Retorna o conteúdo HTML da resposta
            else:
                print(f"Erro ao acessar {url}: {resposta.status_code}. Tentativa {tentativa}/{max_tentativas}")
                tentativa += 1
        except httpx.RequestError as e:
            print(f"Erro de requisição em {url}: {e}. Tentativa {tentativa}/{max_tentativas}")
            tentativa += 1
    print(f"Excedido o número máximo de tentativas para {url}.")
    return None

def extrair_informacoes(html_content):
    """
    Extrai links e títulos do menu lateral do site monergismo.net.br usando BeautifulSoup.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Encontra a tabela desejada
    table = soup.find("td", bgcolor="#7BA4CD").find_all("table", class_=["menu", "menu_sub_inicio", "menu_sub_fim"])

    links_e_titulos = []
    for item in table:
        rows = item.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) > 1:
                link = cells[1].find("a")
                href = link["href"].split("?")[1]  # Pega a parte após o ?
                links_e_titulos.append({
                    "href": href,
                    "titulo": link.text.strip(),
                    "secao": href.split("&")[0].split("=")[1]  # Extrai a seção do href
                })
    return links_e_titulos

def extrair_dados_da_pagina(html_content):
    """
    Coleta dados de uma página específica.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    dados = []
    for tabela in soup.find_all('table', height='60'):
        titulo = tabela.find('strong').text.strip()
        link = tabela.find('a')['href']
        dados.append({
            'titulo': titulo,
            'link': link,
        })
    return dados

def main():
    """
    Função principal do script.
    """
    base_url = "https://monergismo.net.br/"

    # Coleta informações do menu lateral
    html_content = acessar_pagina(base_url)
    if html_content:
        links_e_titulos = extrair_informacoes(html_content)

        # Itera pelas seções do menu
        for link_e_titulo in links_e_titulos:
            secao = link_e_titulo['secao']
            print(f"Seção: {link_e_titulo['titulo']}")
            
            # Iterando pelas páginas da seção
            pagina = 0
            while True:
                url_completa = base_url + f"?pg={pagina}&secao={secao}&campo=titulo&ordem=asc"
                print(f"URL Completa: {url_completa}")

                html_content = acessar_pagina(url_completa)
                if html_content:
                    dados_da_pagina = extrair_dados_da_pagina(html_content)
                    if dados_da_pagina:
                        for dado in dados_da_pagina:
                            # Corrigindo o título para remover caracteres estranhos
                            titulo_corrigido = dado['titulo'].encode('ascii', 'ignore').decode()
                            print(f"  - Título: {titulo_corrigido}")
                            print(f"    Link: {dado['link']}")
                        pagina += 1
                    else:
                        print("-" * 30)
                        break
                else:
                    print("-" * 30)
                    break

        # Itera pelas URLs adicionais
        urls_adicionais = [
            "https://monergismo.net.br/?secao=livros",
            "https://monergismo.net.br/?secao=meditacoes",
            "https://monergismo.net.br/?secao=credos"
        ]
        for url in urls_adicionais:
            print(f"URL Completa: {url}")
            html_content = acessar_pagina(url)
            if html_content:
                dados_da_pagina = extrair_dados_da_pagina(html_content)
                if dados_da_pagina:
                    for dado in dados_da_pagina:
                        # Corrigindo o título para remover caracteres estranhos
                        titulo_corrigido = dado['titulo'].encode('ascii', 'ignore').decode()
                        print(f"  - Título: {titulo_corrigido}")
                        print(f"    Link: {dado['link']}")

                print("-" * 30)

if __name__ == "__main__":
    main()