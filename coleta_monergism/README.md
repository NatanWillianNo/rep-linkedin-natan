# Monergism Book Scraper

Este script Python realiza a raspagem de informações de livros do site Monergism (https://www.monergism.com). Ele extrai detalhes como nome do livro, autor e link para o recurso, verificando se o link é para um arquivo PDF ou tentando encontrar uma versão arquivada no Wayback Machine, se não for.

## Funcionalidades

- **raspar_pagina_monergism(url_base, numero_pagina)**: Raspagem de uma página específica de resultados de busca no Monergism, retornando uma lista de tuplas (nome do livro, autor, link do recurso).
  
- **verificar_link(link)**: Verificação se o link é para um arquivo PDF. Se não for, tenta encontrar uma versão no Wayback Machine.
  
- **extrair_informacoes_livro(livro_html)**: Extração de informações de um elemento HTML de um livro, retornando uma tupla com nome do livro, autor e link.

## Dependências

- `httpx`: Biblioteca para requisições HTTP moderna e assíncrona.
- `BeautifulSoup`: Biblioteca para parsing HTML.

## Como usar

1. Instale as dependências:

   ```bash
   pip install httpx beautifulsoup4
   ```

2. Execute o script `main.py`:

   ```bash
   python main.py
   ```

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues relatando problemas encontrados ou propor melhorias no código.

## Autores

- Feito por [Natan Willian de Souza Noronha](https://github.com/NatanWillianNo)

