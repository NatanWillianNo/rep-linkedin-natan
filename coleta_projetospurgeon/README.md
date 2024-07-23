# Script de Coleta de Sermões do Projeto Spurgeon

Este script em Python foi desenvolvido para coletar informações de sermões disponíveis no site do Projeto Spurgeon e extrair referências bíblicas associadas a esses sermões.

### Funcionalidades

1. **extrair_sermoes(conteudo_html)**: Extrai informações sobre sermões a partir do conteúdo HTML fornecido, incluindo número, título e link.
   
2. **extrair_versiculo_base(conteudo_html)**: Extrai a referência bíblica base do conteúdo HTML fornecido, buscando por referências específicas nos livros da Bíblia.

3. **main()**: Função principal que realiza o fluxo principal do programa:
   - Acessa a página principal dos sermões no site do Projeto Spurgeon.
   - Coleta e exibe informações de cada sermão encontrado, incluindo número, título, link e referência bíblica associada.

### Dependências

- `httpx` para realizar requisições HTTP de forma assíncrona.
- `BeautifulSoup` (bs4) para fazer parsing e manipulação de HTML.
- `re` (expressões regulares) para encontrar e formatar referências bíblicas.

### Uso

Para executar o script, certifique-se de ter as bibliotecas necessárias instaladas:

```bash
pip install httpx beautifulsoup4
```

Em seguida, execute o script `coleta_projetospurgeon_novo.py`:

```bash
python coleta_projetospurgeon_novo.py
```

### Autor

- Feito por [Natan Willian de Souza Noronha](https://github.com/NatanWillianNo)

---

