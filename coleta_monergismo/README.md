## Coleta de Dados Automática do Site Monergismo

Este script em Python, chamado `coleta_monergismo_auto.py`, utiliza as bibliotecas `httpx` e `BeautifulSoup` para extrair automaticamente informações do site monergismo.net.br. Ele coleta links, títulos e outros dados do menu lateral, seções, páginas de artigos, livros, meditações e credos.

### Funcionalidades:

- **Coleta de links e títulos do menu lateral:** Extrai os links e títulos das seções do site Monergismo, presentes no menu lateral.
- **Coleta de dados de páginas específicas:** Extrai informações de páginas individuais, como artigos, livros e meditações, buscando por tabelas com `height="60"`.
- **Organização dos dados:** Formata os dados coletados em uma estrutura organizada, mostrando a seção, URL completa, título e link de cada item.

### Como Executar:

1. **Instalar as bibliotecas:**
    - Certifique-se de que as bibliotecas `httpx` e `BeautifulSoup` estão instaladas:
      ```
      pip install httpx beautifulsoup4
      ```

2. **Executar o script:**
    - Execute o script no terminal:
      ```
      python coleta_monergismo_auto.py
      ```

3. **Visualizar os dados:** Os dados coletados do site serão impressos no console.

### Exemplo de Saída:

```
Seção: Antropologia Bíblica
URL Completa: https://monergismo.net.br/?pg=0&secao=antropologia_biblica&campo=titulo&ordem=asc
  - Título: A Imagem de Deus
      Link: https://www.monergismo.com/textos/antropologia_biblica/imagem_deus_genebra.htm
      ...
      Seção: Livros
      URL Completa: https://monergismo.net.br/?pg=3&secao=livros&campo=titulo&ordem=asc
        - Título: Os Sete Brados do Salvador Sobre a Cruz 
            Link: https://www.monergismo.com/textos/livros/sete_brados_salvador_cruz.pdf
            ...
```

### Observações:

- Este script é para fins de demonstração e aprendizado. 
- O código pode precisar ser ajustado se houver alterações na estrutura do site.
- A coleta automática de dados deve ser feita de forma responsável, respeitando as políticas de uso do site e evitando sobrecargas nos servidores. 
- É recomendável utilizar serviços de proxy ou gerenciar as requisições HTTP para anonimizar a sua coleta de dados.

## Contribuição

Contribuições são bem-vindas! Se você quiser adicionar novos recursos, resolver problemas ou melhorar a documentação, sinta-se à vontade para enviar um pull request.

## Autor

Feito por Natan Willian de Souza Noronha (https://github.com/NatanWillianNo).

---




