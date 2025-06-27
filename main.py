from fastapi import FastAPI # type: ignore
from pydantic import BaseModel
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from urllib.parse import urlparse, urlunparse

app = FastAPI()

class URLRequest(BaseModel):
    url: str

def montar_url_base(url: str, codigo: str) -> str:
    # Extrai domínio raiz (ex: https://www.ricardocorrealeiloes.com.br/)
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}/Leilao.asp?zz={codigo}"
    return base_url

def extrair_links_leilao(url: str) -> List[str]:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(10)

        divs = driver.find_elements(By.XPATH, "//*[@onclick]")
        urls = []

        for div in divs:
            onclick = div.get_attribute("onclick")
            if onclick and "abrirDetalhesLeilao" in onclick:
                match = re.search(r"abrirDetalhesLeilao\('(\d+)'\)", onclick)
                if match:
                    codigo = match.group(1)
                    url_final = montar_url_base(url, codigo)
                    urls.append(url_final)

        return urls

    finally:
        driver.quit()

@app.post("/extrair")
def extrair_leiloes(request: URLRequest):
    urls = extrair_links_leilao(request.url)
    return {"urls": urls}
