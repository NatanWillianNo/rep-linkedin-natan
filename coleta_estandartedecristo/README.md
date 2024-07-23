## Coleta Estandarte de Cristo

Este script Python extrai informações sobre ebooks e postagens de blog do site [O Estandarte de Cristo](https://oestandartedecristo.com/).

### Funcionalidades:

- Extrai título, link da página e link de download de cada ebook disponível na página de ebooks.
- Extrai título, link e autor de cada postagem de blog, navegando por todas as páginas do blog.

### Requisitos:

- Python 3.6 ou superior
- Bibliotecas `httpx` e `BeautifulSoup4`

### Instalação:

1. Instale as bibliotecas necessárias:

   ```bash
   pip install httpx beautifulsoup4
   ```

### Utilização:

1. Salve o script como `coleta_estandartedecristo.py`
2. Execute o script:

   ```bash
   python coleta_estandartedecristo.py
   ```

   O script irá exibir as informações extraídas no console.

### Estrutura do código:

- **`acessar_pagina(url)`:** Faz uma requisição HTTP GET para a URL especificada e retorna o conteúdo HTML da página.
- **`extrair_infos_ebooks(conteudo_html)`:** Extrai dados dos ebooks do HTML da página principal de ebooks, incluindo acessar as páginas individuais para obter os links de download.
- **`extrair_link_download_ebook(conteudo_html)`:** Extrai o link de download do ebook do HTML da página individual do ebook.
- **`extrair_infos_blog(conteudo_html)`:** Extrai dados das postagens de blog do HTML da página do blog.
- **`main()`:** Função principal que orquestra o processo de scraping de ebooks e postagens de blog.

### Observações:

- Este script foi projetado especificamente para a estrutura atual do site O Estandarte de Cristo. Qualquer alteração no site pode requerer modificações no código.
- É importante respeitar os termos de uso do site e não sobrecarregá-lo com muitas requisições em um curto período de tempo.

## Autor

- Feito por [Natan Willian de Souza Noronha](https://github.com/NatanWillianNo)

---


