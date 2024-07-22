# Chapellibrary Scraper

Este script Python é um web scraper desenvolvido para acessar e extrair informações de livros do site Chapellibrary (https://www.chapellibrary.org/). Ele utiliza a biblioteca `httpx` para fazer requisições HTTP e `BeautifulSoup` para o parsing de HTML.

## Funcionalidade

O script realiza as seguintes operações:

1. **Acesso à API**: Acessa a API REST do Chapellibrary para obter dados dos livros.
2. **Tratamento de Erros**: Implementa tratamento para erros de requisição HTTP utilizando um máximo de 5 tentativas.
3. **Extração de Dados**: Extrai informações específicas dos livros retornados pela API, como código, título, autor, descrição e link para download do PDF.
4. **Formatação e Impressão**: Formata os dados extraídos e imprime na saída padrão, separados por página.

## Requisitos

- Python 3.x
- Bibliotecas Python: `httpx`, `BeautifulSoup`

## Uso

1. Clone o repositório:

   ```
   git clone https://github.com/seu-usuario/chapellibrary-scraper.git
   ```

2. Instale as dependências:

   ```
   pip install httpx beautifulsoup4
   ```

3. Execute o script:

   ```
   python scraper.py
   ```

## Configuração

- `base_url`: URL base da API do Chapellibrary.
- `page_size`: Número de livros por página a serem requisitados.
- `page_count`: Número total de páginas a serem requisitadas.
- `timeout`: Tempo limite para as requisições HTTP.

## Contribuição

Contribuições são bem-vindas! Se você quiser adicionar novos recursos, resolver problemas ou melhorar a documentação, sinta-se à vontade para enviar um pull request.

## Autor

- Feito por [Natan Willian de Souza Noronha](https://github.com/NatanWillianNo)

---

