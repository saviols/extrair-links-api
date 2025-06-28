from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from playwright.sync_api import sync_playwright
import re
from urllib.parse import urlparse

app = FastAPI()

class URLRequest(BaseModel):
    url: str

def montar_url_base(url: str, codigo: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}/Leilao.asp?zz={codigo}"

def extrair_links_leilao(url: str) -> List[str]:
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)

        # Captura todos os elementos com onclick contendo abrirDetalhesLeilao
        divs = page.query_selector_all("[onclick*='abrirDetalhesLeilao']")
        urls = []

        for div in divs:
            onclick = div.get_attribute("onclick")
            if onclick:
                match = re.search(r"abrirDetalhesLeilao\('(\d+)'\)", onclick)
                if match:
                    codigo = match.group(1)
                    urls.append(montar_url_base(url, codigo))

        browser.close()
        return urls

@app.post("/extrair")
def extrair_leiloes(request: URLRequest):
    urls = extrair_links_leilao(request.url)
    return {"urls": urls}
