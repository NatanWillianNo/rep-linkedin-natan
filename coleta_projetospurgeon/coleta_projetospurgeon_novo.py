import httpx
from bs4 import BeautifulSoup
import re

LIVROS_BIBLIA = [
    "Gênesis", "Êxodo", "Levítico", "Números", "Deuteronômio",
    "Josué", "Juízes", "Rute", "1 Samuel", "2 Samuel", "1 Reis", "2 Reis",
    "1 Crônicas", "2 Crônicas", "Esdras", "Neemias", "Ester", "Jó", "Salmos",
    "Provérbios", "Eclesiastes", "Cantares de Salomão", "Isaías", "Jeremias",
    "Lamentações", "Ezequiel", "Daniel", "Oseias", "Joel", "Amós", "Obadias",
    "Jonas", "Miquéias", "Naum", "Habacuque", "Sofonias", "Ageu", "Zacarias",
    "Malaquias", "Mateus", "Marcos", "Lucas", "João", "Atos", "Romanos",
    "1 Coríntios", "2 Coríntios", "Gálatas", "Efésios", "Filipenses",
    "Colossenses", "1 Tessalonicenses", "2 Tessalonicenses", "1 Timóteo",
    "2 Timóteo", "Tito", "Filemom", "Hebreus", "Tiago", "1 Pedro",
    "2 Pedro", "1 João", "2 João", "3 João", "Judas", "Apocalipse"
]

def extrair_sermoes(conteudo_html):
    """Extrai informações sobre os sermões do conteúdo HTML."""
    soup = BeautifulSoup(conteudo_html, 'html.parser')
    sermoes = []

    for tag_p in soup.find_all('p'):
        link = tag_p.find('a')
        if link:
            numero_sermao = tag_p.text.split('–')[0].strip()
            if numero_sermao.isdigit():
                titulo_sermao = link.text.strip()
                link_sermao = link['href']
                sermoes.append({'Número': numero_sermao, 'Título': titulo_sermao, 'Link': link_sermao})

    return sermoes

def extrair_versiculo_base(conteudo_html):
    """Extrai a referência bíblica, tratando anomalias e formatação."""
    soup = BeautifulSoup(conteudo_html, 'html.parser')

    for tag_p in soup.find_all('p'):
        for livro in LIVROS_BIBLIA:
            match = re.search(fr'\b{livro}\s+\d+[:.;]\s*\d+(?:-\d+)?[\s,;:]*\d*[a-z]?\b', tag_p.text)
            if match:
                referencia = match.group(0)
                # Formatando a referência:
                referencia = re.sub(r';', ':', referencia)
                referencia = re.sub(r',', '-', referencia)
                referencia = re.sub(r'\s+', ' ', referencia)
                return referencia
    return "Não tem referência bíblica base"

def main():
    """Função principal."""
    url = 'https://www.projetospurgeon.com.br/sermoes/sermoesprovisorio/'
    cabecalhos = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        resposta = httpx.get(url, headers=cabecalhos)
        resposta.raise_for_status()
        sermoes = extrair_sermoes(resposta.content)

        for sermao in sermoes:
            print(f"Número: {sermao['Número']}")
            print(f"Título: {sermao['Título']}")
            print(f"Link: {sermao['Link']}")

            resposta_sermao = httpx.get(sermao['Link'], headers=cabecalhos)
            resposta_sermao.raise_for_status()
            referencia_biblica = extrair_versiculo_base(resposta_sermao.content)
            print(f"Referência Bíblica: {referencia_biblica}")
            print("-" * 30)

    except httpx.HTTPError as exc:
        print(f"Erro ao buscar a página: {exc}")

if __name__ == "__main__":
    main()