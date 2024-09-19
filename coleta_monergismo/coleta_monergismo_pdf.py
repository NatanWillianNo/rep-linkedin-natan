import httpx
from bs4 import BeautifulSoup
import os
import csv
import unicodedata
import time
import re

# Definindo a variável de ambiente para o diretório base
DIR_BD = os.environ.get("DIR_BD", "/caminho/padrao/se/variavel/nao/definida")

def acessar_pagina(url):
    """Faz uma requisição GET para a URL fornecida e retorna o conteúdo da página."""
    max_tentativas = 5
    tentativa = 1
    while tentativa <= max_tentativas:
        try:
            resposta = httpx.get(url, timeout=60)
            if resposta.status_code == 200:
                return resposta.text
            else:
                print(f"Erro ao acessar {url}: {resposta.status_code}. Tentativa {tentativa}/{max_tentativas}")
                tentativa += 1
                time.sleep(5)
        except httpx.RequestError as e:
            print(f"Erro de requisição em {url}: {e}. Tentativa {tentativa}/{max_tentativas}")
            tentativa += 1
            time.sleep(5)
    print(f"Excedido o número máximo de tentativas para {url}.")
    return None

def extrair_informacoes(html_content):
    """Extrai links e títulos do menu lateral do site usando BeautifulSoup."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Encontra a tabela desejada (ajuste se a estrutura do site mudar)
    table = soup.find("td", bgcolor="#7BA4CD").find_all("table", class_=["menu", "menu_sub_inicio", "menu_sub_fim"])

    links_e_titulos = []
    for item in table:
        rows = item.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) > 1:
                link = cells[1].find("a")
                href = link["href"].split("?")[1]
                links_e_titulos.append({
                    "href": href,
                    "titulo": link.text.strip(),
                    "secao": href.split("&")[0].split("=")[1]
                })
    return links_e_titulos

def extrair_dados_da_pagina(html_content):
    """Coleta dados de uma página específica, incluindo links para PDFs."""
    soup = BeautifulSoup(html_content, 'html.parser')
    dados = []
    for tabela in soup.find_all('table', height='60'):
        titulo_element = tabela.find('strong')
        if titulo_element:
            titulo = titulo_element.text.strip()
            link_element = tabela.find('a')
            if link_element:
                link = link_element['href']

                if link.startswith('http://'):
                    link = link.replace('http://', 'https://')
                link = link.replace("https://www.", "https://")

                if link.endswith('.pdf'):
                    tipo = 'PDF'
                else:
                    tipo = 'Página'

                dados.append({
                    'titulo': titulo,
                    'link': link,
                    'tipo': tipo,
                })
    return dados

def baixar_pdf(url, nome_arquivo, caminho_pasta):
    """Baixa um PDF de uma URL e salva no caminho especificado."""
    try:
        resposta = httpx.get(url, timeout=60)
        resposta.raise_for_status()
        caminho_completo = os.path.join(caminho_pasta, nome_arquivo)
        with open(caminho_completo, 'wb') as arquivo:
            arquivo.write(resposta.content)
        print(f"PDF '{nome_arquivo}' baixado com sucesso em '{caminho_pasta}'.")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print(f"PDF não encontrado (404): {url}")
        else:
            raise e

def escrever_csv(dados, nome_arquivo):
    """Escreve os dados em um arquivo CSV."""
    with open(nome_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
        writer = csv.DictWriter(arquivo_csv, fieldnames=['Título', 'link', 'secao/categoria'])
        writer.writeheader()
        for dado in dados:
            writer.writerow({'Título': dado['titulo'], 'link': dado['link'], 'secao/categoria': dado['secao']})

def limpar_nome_arquivo(nome):
    """Remove caracteres inválidos e a string "(codificação inválida)" de um nome de arquivo."""
    # Remove caracteres inválidos usando expressão regular
    nome = re.sub(r'[\\/*?:"<>|]', "", nome)
    # Remove a string "(codificação inválida)"
    nome = nome.replace("(codificação inválida)", "")
    # Substitui caracteres especiais por equivalentes ASCII
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')
    return nome.strip()


def main():
    """Função principal do script."""
    base_url = "https://monergismo.net.br/"
    nome_site = "Monergismo"
    nome_arquivo_csv = "monergismo_links.csv"

    caminho_pasta_principal = os.path.join(DIR_BD, nome_site)
    os.makedirs(caminho_pasta_principal, exist_ok=True)

    todos_os_dados = []

    html_content = acessar_pagina(base_url)
    if html_content:
        links_e_titulos = extrair_informacoes(html_content)

        for link_e_titulo in links_e_titulos:
            secao = link_e_titulo['secao']
            titulo_secao = limpar_nome_arquivo(link_e_titulo['titulo'])
            print(f"Seção: {titulo_secao}")

            caminho_pasta_secao = os.path.join(caminho_pasta_principal, titulo_secao.replace('/', '_'))
            os.makedirs(caminho_pasta_secao, exist_ok=True)

            pagina = 0
            while True:
                url_completa = base_url + f"?pg={pagina}&secao={secao}&campo=titulo&ordem=asc"
                print(f"URL Completa: {url_completa}")

                html_content = acessar_pagina(url_completa)
                if html_content:
                    dados_da_pagina = extrair_dados_da_pagina(html_content)
                    if dados_da_pagina:
                        for dado in dados_da_pagina:
                            titulo_corrigido = limpar_nome_arquivo(dado['titulo'])
                            print(f"  - Título: {titulo_corrigido}")
                            print(f"    Link: {dado['link']}")

                            dado['secao'] = titulo_secao
                            todos_os_dados.append(dado)

                            if dado['tipo'] == 'PDF':
                                nome_arquivo = f"{titulo_corrigido.replace('/', '_')}.pdf"
                                baixar_pdf(dado['link'], nome_arquivo, caminho_pasta_secao)
                        pagina += 1
                    else:
                        print("-" * 30)
                        break
                else:
                    print("-" * 30)
                    break

        urls_adicionais = [
            {"url": "https://monergismo.net.br/?secao=credos", "titulo": "Credos"},
            {"url": "https://monergismo.net.br/links.htm", "titulo": "Links"}
        ]
        for item in urls_adicionais:
            print(f"Seção: {item['titulo']}")
            caminho_pasta_secao = os.path.join(caminho_pasta_principal, item['titulo'].replace('/', '_'))
            os.makedirs(caminho_pasta_secao, exist_ok=True)

            html_content = acessar_pagina(item['url'])
            if html_content:
                dados_da_pagina = extrair_dados_da_pagina(html_content)
                if dados_da_pagina:
                    for dado in dados_da_pagina:
                        titulo_corrigido = limpar_nome_arquivo(dado['titulo'])
                        print(f"  - Título: {titulo_corrigido}")
                        print(f"    Link: {dado['link']}")

                        dado['secao'] = item['titulo']
                        todos_os_dados.append(dado)

                        if dado['tipo'] == 'PDF':
                            nome_arquivo = f"{titulo_corrigido.replace('/', '_')}.pdf"
                            baixar_pdf(dado['link'], nome_arquivo, caminho_pasta_secao)

                print("-" * 30)

    escrever_csv(todos_os_dados, os.path.join(DIR_BD, nome_arquivo_csv))

if __name__ == "__main__":
    main()