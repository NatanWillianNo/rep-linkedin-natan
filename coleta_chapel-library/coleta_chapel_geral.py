import httpx
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import time
from colorama import Fore, Style
from tqdm import tqdm

load_dotenv()
DIR_BD = os.getenv("DIR_BD")
if not DIR_BD:
    raise ValueError("A variável de ambiente DIR_BD não está definida.")

livros_baixados = set()

def acessar_pagina(url, max_tentativas=5, tempo_espera=5):
    """Acessa a página da URL e retorna o conteúdo em JSON."""
    for tentativa in range(1, max_tentativas + 1):
        try:
            resposta = httpx.get(url, timeout=30)
            resposta.raise_for_status()
            return resposta.json()
        except httpx.RequestError as e:
            print(f"Erro de requisição em {url}: {e}. Tentativa {tentativa}/{max_tentativas}")
            time.sleep(tempo_espera)
    print(f"Excedido o número máximo de tentativas para {url}.")
    return None

def extrair_informacoes(dados_json):
    """Extrai informações relevantes do JSON."""
    lista_livros = []
    for item in dados_json:
        codigo = item.get('code')
        titulo = item.get('title')
        descricao = item.get('description', '')
        preco = item.get('price', 0.00)
        preco = f'{preco:.2f}'.replace('.', ',') if isinstance(preco, (float, int)) else '0,00'

        # Links de download corrigidos
        url_pdf = f"https://www.chapellibrary.org/api/books/download?code={codigo}&format=pdf"
        url_epub = f"https://www.chapellibrary.org/api/books/download?code={codigo}&format=epub"
        url_livro = f"https://www.chapellibrary.org/book/{codigo}/"
        tem_versao_imprimivel = item.get('hasPrintableVersion', False)

        soup = BeautifulSoup(descricao, 'html.parser')
        descricao_limpa = soup.get_text(separator='\n').strip()

        autores = item.get('authors', [])
        nome_autor = autores[0]['name'] if autores else 'Autor Desconhecido'

        nome_arquivo = f"{titulo} - {nome_autor}".translate({ord(c): '' for c in "\\/:*?\"<>|"})

        livro = {
            "codigo": codigo,
            "titulo": titulo,
            "autor": nome_autor,
            "descricao": descricao_limpa,
            "preco": preco,
            "url_pdf": url_pdf,
            "url_epub": url_epub,
            "url_livro": url_livro,
            "nome_arquivo": nome_arquivo,
            "tem_versao_imprimivel": tem_versao_imprimivel
        }

        lista_livros.append(livro)

    return lista_livros

def coletar_arquivos(link_pdf, link_epub, nome_arquivo, idioma):
    """Baixa PDFs e EPUBs."""
    caminho_pasta = os.path.join(DIR_BD, f"coleta_chapel_{idioma}")
    os.makedirs(caminho_pasta, exist_ok=True)

    caminho_pdf = os.path.join(caminho_pasta, "pdf")
    os.makedirs(caminho_pdf, exist_ok=True)

    caminho_epub = os.path.join(caminho_pasta, "epub")
    os.makedirs(caminho_epub, exist_ok=True)

    local_pdf = os.path.join(caminho_pdf, f"{nome_arquivo}.pdf")
    local_epub = os.path.join(caminho_epub, f"{nome_arquivo}.epub")

    baixou_algo = False

    if link_pdf:
        if tentar_baixar_arquivo(link_pdf, local_pdf, "PDF", nome_arquivo):
            baixou_algo = True

    if link_epub:
        if tentar_baixar_arquivo(link_epub, local_epub, "EPUB", nome_arquivo):
            baixou_algo = True

    if not baixou_algo:
        print(Fore.YELLOW + f"Nenhum arquivo PDF/EPUB encontrado para '{nome_arquivo}'" + Style.RESET_ALL)

    return local_pdf if os.path.exists(local_pdf) else None, local_epub if os.path.exists(local_epub) else None

def tentar_baixar_arquivo(link, caminho_arquivo, tipo_arquivo, nome_arquivo):
    """Tenta baixar um arquivo e lida com erros."""
    try:
        with httpx.stream("GET", link, timeout=60) as resposta:
            resposta.raise_for_status()
            with open(caminho_arquivo, "wb") as arquivo:
                for chunk in tqdm(resposta.iter_bytes(), desc=f"Baixando {nome_arquivo}.{tipo_arquivo.lower()}", unit="B", unit_scale=True):
                    arquivo.write(chunk)
        print(Fore.GREEN + f"Arquivo .{tipo_arquivo.lower()}: '{nome_arquivo}' baixado com sucesso em '{caminho_arquivo}'" + Style.RESET_ALL)
        return True
    except httpx.HTTPError as http_err:
        print(Fore.RED + f"Erro HTTP ao baixar {tipo_arquivo}: {http_err}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Erro ao baixar {tipo_arquivo}: {e}" + Style.RESET_ALL)
    return False


def main():
    """Função principal."""
    url_base = 'https://www.chapellibrary.org/api/books?pageSize=10&pageCount={pagina}&language={idioma}&sortby=title'
    idiomas_paginas = {
        'EN': 122,
        'ES': 27,
        'FR': 4,
        'PT': 2,
        'IT': 2
    }

    for idioma, page_count in idiomas_paginas.items():
        for pagina in range(0, page_count + 1):
            url = url_base.format(idioma=idioma, pagina=pagina)
            dados_json = acessar_pagina(url)

            if dados_json:
                informacoes_livros = extrair_informacoes(dados_json)

                for livro in informacoes_livros:
                    chave_livro = (livro['titulo'], idioma)
                    if chave_livro in livros_baixados:
                        print(Fore.GREEN + f"Livro '{livro['titulo']}' ({idioma}) já foi baixado. Pulando..." + Style.RESET_ALL)
                        continue

                    print("-" * 50)
                    print(f"Título: {livro['titulo']}")
                    print(f"Autor: {livro['autor']}")
                    print(f"Idioma: {idioma}")
                    print(f"Tem Versão Imprimível: {'SIM' if livro['tem_versao_imprimivel'] else 'NÃO'}") 
                    print(f"PDF: {livro['url_pdf']}")
                    print(f"EPUB: {livro['url_epub']}") 

                    local_pdf, local_epub = coletar_arquivos(livro['url_pdf'], livro['url_epub'],
                                                        livro['nome_arquivo'], idioma)

                    if local_pdf or local_epub:
                        livros_baixados.add(chave_livro)

if __name__ == '__main__':
    main()