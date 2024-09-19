import httpx
from bs4 import BeautifulSoup
import os
import time
import csv
import json
from dotenv import load_dotenv
from tqdm import tqdm
from colorama import Fore, Style

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
                print(
                    f"Erro ao acessar {url}: {resposta.status_code}. Tentativa {tentativa}/{max_tentativas}"
                )
                time.sleep(5)
                tentativa += 1
        except httpx.RequestError as e:
            print(
                f"Erro de requisição em {url}: {e}. Tentativa {tentativa}/{max_tentativas}"
            )
            time.sleep(5)
            tentativa += 1
    print(f"Excedido o número máximo de tentativas para {url}.")
    return None


def verificar_link_download(url):
    """
    Verifica a validade de um link de download tentando baixar um pequeno pedaço
    do arquivo.

    Args:
        url (str): A URL do arquivo para download.

    Returns:
        bool: True se o download do pedaço do arquivo for bem-sucedido, False caso contrário.
    """
    try:
        with httpx.stream("GET", url, timeout=10) as resposta:
            if resposta.status_code == 200:
                # Lê um pequeno pedaço de dados da resposta
                _ = resposta.read()  # Remove o argumento '1024' aqui
                return True
            
    except Exception as e:
        print(f"Aviso: Erro ao verificar link de download {url}: {e}")
    return False

def extrair_informacoes(dados_json):
    """
    Extrai informações relevantes dos dados JSON, incluindo o preço,
    e verifica a disponibilidade dos links para download de PDF e EPUB
    tentando baixar um pedaço do arquivo.

    Args:
        dados_json (dict): Um dicionário contendo os dados JSON da página.

    Returns:
        list: Uma lista de dicionários, onde cada dicionário representa um livro
              com suas informações extraídas.
    """
    lista_livros = []
    for item in dados_json:
        codigo = item.get("code")
        titulo = item.get("title")
        descricao = item.get("description", "")
        preco = item.get("price", "Indisponível")
        if isinstance(preco, float) or isinstance(preco, int):
            preco = f"{preco:.2f}"
        url_livro = f"https://www.chapellibrary.org/book/{codigo}/"
        tem_versao_imprimivel = (
            "SIM" if item.get("hasPrintableVersion", False) else "NÃO"
        )

        url_pdf = (
            f"https://www.chapellibrary.org/api/books/download?code={codigo}&format=pdf"
        )
        link_pdf = url_pdf if verificar_link_download(url_pdf) else ""

        url_epub = (
            f"https://www.chapellibrary.org/api/books/download?code={codigo}&format=epub"
        )
        link_epub = url_epub if verificar_link_download(url_epub) else ""

        soup = BeautifulSoup(descricao, "html.parser")
        descricao_limpa = soup.get_text(separator="\n")

        autores = item.get("authors", [])
        nome_autor = autores[0]["name"] if autores else "Autor Desconhecido"

        livro = {
            "codigo": codigo,
            "titulo": titulo,
            "autor": nome_autor,
            "descricao": descricao_limpa.strip(),
            "preco": preco,
            "link_livro": url_livro,
            "link_pdf": link_pdf,
            "link_epub": link_epub,
            "tem_versao_imprimivel": tem_versao_imprimivel,
        }

        lista_livros.append(livro)

    return lista_livros

def salvar_csv(dados, idioma):
    """
    Salva os dados dos livros em um arquivo CSV com o nome do idioma.

    Args:
        dados (list): Uma lista de dicionários, onde cada dicionário representa um livro.
        idioma (str): O idioma dos livros a serem salvos.
    """
    nome_arquivo = os.path.join(DIR_BD, f"livros_chapel_{idioma}.csv")

    campos = [
        "codigo",
        "titulo",
        "autor",
        "descricao",
        "preco",
        "link_livro",
        "link_pdf",
        "link_epub",
        "tem_versao_imprimivel",
    ]

    # Se o arquivo não existir, cria um novo com cabeçalho
    if not os.path.isfile(nome_arquivo):
        with open(nome_arquivo, "w", newline="", encoding="utf-8") as arquivo_csv:
            escritor = csv.DictWriter(arquivo_csv, fieldnames=campos)
            escritor.writeheader()

    # Abre o arquivo em modo 'append' para adicionar dados
    with open(nome_arquivo, "a", newline="", encoding="utf-8") as arquivo_csv:
        escritor = csv.DictWriter(arquivo_csv, fieldnames=campos)
        for livro in dados:
            escritor.writerow(livro)


def salvar_json(dados, idioma):
    """
    Salva os dados dos livros em um arquivo JSON com o nome do idioma.
    Remove as chaves dentro dos livros no arquivo JSON.

    Args:
        dados (list): Uma lista de dicionários, onde cada dicionário representa um livro.
        idioma (str): O idioma dos livros a serem salvos.
    """
    nome_arquivo = os.path.join(DIR_BD, f"livros_chapel_{idioma}.json")
    with open(nome_arquivo, "w", encoding="utf-8") as arquivo_json:
        # Utiliza json.dumps para formatar o JSON em uma string
        json_str = json.dumps(dados, ensure_ascii=False, indent=4)

        # Remove aspas extras ao redor dos valores que não são strings
        json_str = json_str.replace('"true"', 'true').replace('"false"', 'false')

        arquivo_json.write(json_str)


def main():
    """
    Função principal.
    """
    url_base = "https://www.chapellibrary.org/api/books"
    idiomas_paginas = {"EN": 122, "ES": 27, "FR": 4, "PT": 2,  "IT": 2}

    for idioma, total_paginas in idiomas_paginas.items():
        todos_os_livros = []
        print(Fore.BLUE + f"Processando idioma: {idioma}" + Style.RESET_ALL)

        with tqdm(
            total=total_paginas,
            desc=f"Progresso {idioma}",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
        ) as barra_progresso:
            for pagina in range(0, total_paginas + 1):
                url = f"{url_base}?pageSize=10&pageCount={pagina}&language={idioma}&sortby=title"
                dados_json = acessar_pagina(url)

                if dados_json:
                    informacoes_livros = extrair_informacoes(dados_json)
                    todos_os_livros.extend(informacoes_livros)

                barra_progresso.update(1)
                time.sleep(
                    1
                )  # Pausa para não sobrecarregar o servidor

        salvar_csv(todos_os_livros, idioma)
        salvar_json(todos_os_livros, idioma)


if __name__ == "__main__":
    main()