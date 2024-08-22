import httpx
from bs4 import BeautifulSoup
import os
import csv
import unicodedata
import time

# Definindo a variável de ambiente para o diretório base
DIR_BD = os.environ.get("DIR_BD", "/caminho/padrao/se/variavel/nao/definida")

def acessar_pagina(url):
    """
    Faz uma requisição GET para a URL fornecida e retorna o conteúdo da página.
    """
    max_tentativas = 5
    tentativa = 1
    while tentativa <= max_tentativas:
        try:
            resposta = httpx.get(url, timeout=60)  # Aumenta o tempo limite
            if resposta.status_code == 200:
                return resposta.text  # Retorna o conteúdo HTML da resposta
            else:
                print(f"Erro ao acessar {url}: {resposta.status_code}. Tentativa {tentativa}/{max_tentativas}")
                tentativa += 1
                time.sleep(5)  # Espera um pouco antes de tentar novamente
        except httpx.RequestError as e:
            print(f"Erro de requisição em {url}: {e}. Tentativa {tentativa}/{max_tentativas}")
            tentativa += 1
            time.sleep(5)  # Espera um pouco antes de tentar novamente
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
    Coleta dados de uma página específica, incluindo links para PDFs,
    corrigindo o protocolo para https e removendo 'www.' se necessário.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    dados = []
    for tabela in soup.find_all('table', height='60'):
        titulo = tabela.find('strong').text.strip()
        link_element = tabela.find('a')
        if link_element:
            link = link_element['href']

            # Corrige o protocolo para https
            if link.startswith('http://'):
                link = link.replace('http://', 'https://')

            # Remove 'www.' se presente para evitar redirecionamento
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
    """
    Baixa um PDF de uma URL e salva no caminho especificado, 
    ignorando erros 404 (Not Found).
    """
    try:
        resposta = httpx.get(url, timeout=60)  # Aumenta o tempo limite
        # Verifica se houve algum erro na resposta HTTP
        resposta.raise_for_status()
        
        caminho_completo = os.path.join(caminho_pasta, nome_arquivo)
        with open(caminho_completo, 'wb') as arquivo:
            arquivo.write(resposta.content)
        print(f"PDF '{nome_arquivo}' baixado com sucesso em '{caminho_pasta}'.")
    except httpx.HTTPStatusError as e:
        # Se o erro for 404 (Not Found), apenas imprime uma mensagem
        if e.response.status_code == 404:
            print(f"PDF não encontrado (404): {url}")
        else:
            # Outros erros HTTP serão lançados novamente
            raise e

def escrever_csv(dados, nome_arquivo):
    """
    Escreve os dados em um arquivo CSV.
    """
    with open(nome_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
        writer = csv.DictWriter(arquivo_csv, fieldnames=['Título', 'link', 'secao/categoria'])
        writer.writeheader()
        for dado in dados:
            writer.writerow({'Título': dado['titulo'], 'link': dado['link'], 'secao/categoria': dado['secao']})

def remover_caracteres_especiais(texto):
    """
    Remove caracteres especiais de um texto, substituindo-os por
    versões ASCII compatíveis.
    """
    texto_normalizado = unicodedata.normalize('NFKD', texto)
    return ''.join([c for c in texto_normalizado if not unicodedata.combining(c)])

def main():
    """
    Função principal do script.
    """
    base_url = "https://monergismo.net.br/"
    nome_site = "Monergismo"  # Nome da pasta principal
    nome_arquivo_csv = "monergismo_links.csv"  # Nome do arquivo CSV

    # Cria a pasta principal se não existir
    caminho_pasta_principal = os.path.join(DIR_BD, nome_site)
    os.makedirs(caminho_pasta_principal, exist_ok=True)

    # Lista para armazenar todos os dados para o CSV
    todos_os_dados = []

    # Coleta informações do menu lateral
    html_content = acessar_pagina(base_url)
    if html_content:
        links_e_titulos = extrair_informacoes(html_content)

        # Itera pelas seções do menu
        for link_e_titulo in links_e_titulos:
            secao = link_e_titulo['secao']
            titulo_secao = remover_caracteres_especiais(link_e_titulo['titulo'])
            print(f"Seção: {titulo_secao}")

            # Cria a pasta da seção dentro da pasta principal (apenas para PDFs)
            caminho_pasta_secao = os.path.join(caminho_pasta_principal, titulo_secao.replace('/', '_'))  # Substitui '/' por '_'
            os.makedirs(caminho_pasta_secao, exist_ok=True)

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
                            titulo_corrigido = remover_caracteres_especiais(dado['titulo'])
                            print(f"  - Título: {titulo_corrigido}")
                            print(f"    Link: {dado['link']}")

                            # Adiciona a seção aos dados
                            dado['secao'] = titulo_secao

                            # Adiciona os dados à lista geral
                            todos_os_dados.append(dado)

                            if dado['tipo'] == 'PDF':
                                nome_arquivo = f"{titulo_corrigido.replace('/', '_')}.pdf"  # Substitui '/' por '_'
                                baixar_pdf(dado['link'], nome_arquivo, caminho_pasta_secao)
                        pagina += 1
                    else:
                        print("-" * 30)
                        break
                else:
                    print("-" * 30)
                    break

        # URLs adicionais (tratamento similar às seções do menu)
        urls_adicionais = [
            {"url": "https://monergismo.net.br/?secao=credos", "titulo": "Credos"},
            {"url": "https://monergismo.net.br/links.htm", "titulo": "Links"}
        ]
        for item in urls_adicionais:
            print(f"Seção: {item['titulo']}")
            caminho_pasta_secao = os.path.join(caminho_pasta_principal, item['titulo'].replace('/', '_'))  # Substitui '/' por '_'
            os.makedirs(caminho_pasta_secao, exist_ok=True)

            html_content = acessar_pagina(item['url'])
            if html_content:
                dados_da_pagina = extrair_dados_da_pagina(html_content)
                if dados_da_pagina:
                    for dado in dados_da_pagina:
                        titulo_corrigido = remover_caracteres_especiais(dado['titulo'])
                        print(f"  - Título: {titulo_corrigido}")
                        print(f"    Link: {dado['link']}")

                        # Adiciona a seção aos dados
                        dado['secao'] = item['titulo'] 

                        # Adiciona os dados à lista geral
                        todos_os_dados.append(dado)

                        if dado['tipo'] == 'PDF':
                            nome_arquivo = f"{titulo_corrigido.replace('/', '_')}.pdf"  # Substitui '/' por '_'
                            baixar_pdf(dado['link'], nome_arquivo, caminho_pasta_secao)

                print("-" * 30)

    # Escreve todos os dados no arquivo CSV
    escrever_csv(todos_os_dados, os.path.join(DIR_BD, nome_arquivo_csv))

if __name__ == "__main__":
    main()