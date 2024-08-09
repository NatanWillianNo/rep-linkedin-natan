import httpx
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

def acessar_pagina(url):
    """
    Acessa a página da URL fornecida e retorna o conteúdo em formato JSON.

    Args:
        url (str): A URL da página a ser acessada.

    Returns:
        dict/None: Um dicionário contendo o conteúdo da página em formato JSON 
                   ou None se a página não puder ser acessada.
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
                tentativa += 1
        except httpx.RequestError as e:
            print(f"Erro de requisição em {url}: {e}. Tentativa {tentativa}/{max_tentativas}")
            tentativa += 1
    print(f"Excedido o número máximo de tentativas para {url}.")
    return None

def extrair_informacoes(dados_json):
    """
    Extrai informações relevantes dos dados JSON.

    Args:
        dados_json (dict): Um dicionário contendo dados em formato JSON.

    Returns:
        list: Uma lista de dicionários, cada um representando um livro 
              com informações como título, autor, descrição, etc.
    """
    lista_livros = []
    for item in dados_json:
        codigo = item.get('code')
        titulo = item.get('title')
        descricao = item.get('description', '')
        url_pdf = f"https://www.chapellibrary.org/api/books/download?code={codigo}&format=pdf"
        url_epub = f"https://www.chapellibrary.org/api/books/download?code={codigo}&format=epub"
        tem_versao_imprimivel = item.get('hasPrintableVersion', False)

        # Remove tags HTML da descrição
        soup = BeautifulSoup(descricao, 'html.parser')
        descricao_limpa = soup.get_text(separator='\n')

        autores = item.get('authors', [])
        nome_autor = autores[0]['name'] if autores else 'Autor Desconhecido'
        nome_arquivo = titulo + ' - ' + nome_autor

        livro = {
            "codigo": codigo,
            "titulo": titulo,
            "autor": nome_autor,
            "descricao": descricao_limpa.strip(),
            "url_pdf": url_pdf,
            "url_epub": url_epub,
            "nome_arquivo": nome_arquivo,
            "tem_versao_imprimivel": tem_versao_imprimivel
        }

        lista_livros.append(livro)

    return lista_livros

def coletar_arquivos(link_pdf, link_epub, nome_arquivo, idioma):
    """
    Cria as pastas para salvar PDFs e EPUBs e baixa os arquivos dos links fornecidos.

    Args:
        link_pdf (str): URL do PDF a ser baixado.
        link_epub (str): URL do EPUB a ser baixado.
        nome_arquivo (str): Nome do arquivo a ser salvo (sem extensão).
        idioma (str): Idioma do conteúdo.

    Returns:
        tuple: Caminhos completos dos arquivos PDF e EPUB salvos localmente, ou None se não foram baixados.
    """
    # Carregar variáveis de ambiente do arquivo .env
    load_dotenv()

    # Obter a variável de ambiente DIR_BD
    DIR_BD = os.getenv("DIR_BD")
    
    if not DIR_BD:
        raise ValueError("A variável de ambiente DIR_BD não está definida.")

    # Definir diretórios de destino
    caminho_pasta = os.path.join(DIR_BD, f"coleta_chapel_{idioma}")
    os.makedirs(caminho_pasta, exist_ok=True)
    
    caminho_pdf = os.path.join(caminho_pasta, "pdf")
    os.makedirs(caminho_pdf, exist_ok=True)
    
    caminho_epub = os.path.join(caminho_pasta, "epub")
    os.makedirs(caminho_epub, exist_ok=True)

    # Definir os caminhos completos para salvar os arquivos
    local_pdf = os.path.join(caminho_pdf, f"{nome_arquivo}.pdf")
    local_epub = os.path.join(caminho_epub, f"{nome_arquivo}.epub")

    try:
        # Baixar o PDF
        if link_pdf:
            resposta_pdf = httpx.get(link_pdf)
            if resposta_pdf.status_code == 200:
                with open(local_pdf, "wb") as arquivo_pdf:
                    arquivo_pdf.write(resposta_pdf.content)
                print(f"PDF '{nome_arquivo}' baixado com sucesso para '{local_pdf}'")
            else:
                local_pdf = None
        else:
            local_pdf = None

        # Baixar o EPUB
        if link_epub:
            resposta_epub = httpx.get(link_epub)
            if resposta_epub.status_code == 200:
                with open(local_epub, "wb") as arquivo_epub:
                    arquivo_epub.write(resposta_epub.content)
                print(f"EPUB '{nome_arquivo}' baixado com sucesso para '{local_epub}'")
            else:
                local_epub = None
        else:
            local_epub = None

        return local_pdf, local_epub

    except httpx.HTTPError as http_err:
        print(f"Erro HTTP ao baixar '{nome_arquivo}': {http_err}")
        return None, None
    except Exception as e:
        print(f"Erro ao baixar '{nome_arquivo}': {e}")
        return None, None

def verificar_link(url):
    """
    Verifica se o link fornecido é acessível.

    Args:
        url (str): URL a ser verificada.

    Returns:
        bool: True se o link for acessível (status_code 200), False caso contrário.
    """
    try:
        resposta = httpx.get(url, timeout=10)
        return resposta.status_code == 200
    except httpx.RequestError:
        return False

def main():
    """
    Função principal que orquestra o processo de raspagem de dados e download de PDFs e EPUBs.
    """
    url_base = 'https://www.chapellibrary.org/api/books'
    idiomas = ['EN', 'ES', 'FR']
    total_paginas = 121

    for idioma in idiomas:
        for pagina in range(1, total_paginas + 1):
            url = f'{url_base}?pageSize=10&pageCount={pagina}&language={idioma}&sortby=title'
            dados_json = acessar_pagina(url)

            if dados_json:
                informacoes_livros = extrair_informacoes(dados_json)

                for livro in informacoes_livros:
                    print("-" * 50)
                    print(f"Código: {livro['codigo']}")
                    print(f"Título: {livro['titulo']}")
                    print(f"Autor: {livro['autor']}")
                    print(f"Descrição: {livro['descricao']}")
                    if livro['url_pdf']:
                        print(f"Link PDF: {livro['url_pdf']}")

                    # Verificar se o link EPUB é acessível e imprimir apenas se for válido
                    if livro.get('url_epub') and verificar_link(livro['url_epub']):
                        print(f"Link EPUB: {livro['url_epub']}")
                    
                    print(f"Nome do arquivo: {livro['nome_arquivo']}")
                    print(f"Tem Versão Imprimível: {'SIM' if livro['tem_versao_imprimivel'] else 'NÃO'}")

                    # Coletar os arquivos se os links forem válidos
                    local_pdf, local_epub = coletar_arquivos(livro['url_pdf'], livro.get('url_epub'), livro['nome_arquivo'], idioma)

                    # Apenas imprimir se os arquivos foram baixados com sucesso
                    if local_pdf or local_epub:
                        print(f"Arquivos baixados com sucesso:")
                        if local_pdf:
                            print(f"  PDF: {local_pdf}")
                        if local_epub:
                            print(f"  EPUB: {local_epub}")
                        print()
                    else:
                        print("Nenhum arquivo foi baixado.\n")

if __name__ == '__main__':
    main()
