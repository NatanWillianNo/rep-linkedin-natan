## Coleta Legado Reformado

Este script Python coleta os nomes e links para download de livros gratuitos disponíveis no site [Legado Reformado](https://legadoreformado.com).

### Requisitos

- Python 3.7 ou superior
- Bibliotecas: `httpx`, `beautifulsoup4`

### Instalação

1. **Clone este repositório:**
   ```bash
   git clone https://github.com/NatanWillianNo/coleta_legadoreformado.git
   cd coleta_legadoreformado
   ```

2. **Instale as bibliotecas necessárias:**
   ```bash
   pip install -r requirements.txt
   ```

### Uso

1. **Execute o script:**
   ```bash
   python coleta_legadoreformado.py
   ```

2. **A saída do script exibirá uma lista dos livros gratuitos e seus respectivos links para download, formatados da seguinte maneira:**

   ```
   Lista de livros gratuitos:
   Nome: [Nome do Livro]
   Link: [Link para Download]
   ------------------------------
   Nome: [Nome do Livro]
   Link: [Link para Download]
   ------------------------------
   ...
   ```

3. **Opcional:** Redirecione a saída para um arquivo de texto:
   ```bash
   python coleta_legadoreformado.py > livros_gratuitos.txt
   ```

### Como Funciona

O script utiliza as bibliotecas `httpx` e `beautifulsoup4` para:

1. **Acessar a página de categoria "Livros Gratuitos" do site Legado Reformado.**
2. **Extrair os links para as páginas individuais de cada livro.**
3. **Acessar a página de cada livro e extrair o nome e o link para download do PDF.**
4. **Imprimir os resultados na tela ou salvar em um arquivo de texto.**

### Observações

- O script foi desenvolvido considerando a estrutura atual do site Legado Reformado. Alterações na estrutura do site podem afetar o funcionamento do script.
- O script coleta apenas os livros marcados como "gratuitos" no site.

### Autor

- Feito por [Natan Willian de Souza Noronha](https://github.com/NatanWillianNo)

---
