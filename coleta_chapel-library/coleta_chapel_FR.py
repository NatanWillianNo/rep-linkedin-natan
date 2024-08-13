import httpx  # Para fazer requisições web
from bs4 import BeautifulSoup  # Para extrair dados de HTML

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
        if item.get('language') == 'FR':
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
                "nome_arquivo": nome_arquivo,
                "tem_versao_imprimivel": tem_versao_imprimivel
            }

            # Tenta acessar o EPUB (sem imprimir verificação)
            try:
                with httpx.stream("GET", url_epub, timeout=10) as resposta_epub:
                    if resposta_epub.status_code == 200:
                        livro["url_epub"] = url_epub
            except Exception as e:
                pass  # Ignora erros ao acessar o EPUB

            lista_livros.append(livro)

    return lista_livros

def main():
    """
    Função principal que orquestra o processo de raspagem de dados.
    """
    url_base = 'https://www.chapellibrary.org/api/books'
    total_paginas = 121 

    for pagina in range(0, total_paginas + 1):
        url = f'{url_base}?pageSize=10&pageCount={pagina}&language=FR&sortby=title'
        dados_json = acessar_pagina(url)

        if dados_json:
            informacoes_livros = extrair_informacoes(dados_json)

            if informacoes_livros:
                for livro in informacoes_livros:
                    print("-" * 50)
                    print(f"Código: {livro['codigo']}")
                    print(f"Título: {livro['titulo']}")
                    print(f"Autor: {livro['autor']}")
                    print(f"Descrição: {livro['descricao']}")
                    print(f"Link PDF: {livro['url_pdf']}")
                    if "url_epub" in livro:
                        print(f"Link EPUB: {livro['url_epub']}")
                    print(f"Nome do arquivo: {livro['nome_arquivo']}")
                    print(f"Tem Versão Imprimível: {'SIM' if livro['tem_versao_imprimivel'] else 'NÃO'}") # Mudança aqui
                    print()
            else:
                print(f"Nenhum livro em francês encontrado na página {pagina}.")

if __name__ == '__main__':
    main()