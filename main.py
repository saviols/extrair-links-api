from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
import time
import re
from urllib.parse import urlparse

app = FastAPI()

class URLRequest(BaseModel):
    url: str

def montar_url_base(url: str, codigo: str) -> str:
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}/Leilao.asp?zz={codigo}"
    return base_url

def extrair_links_leilao(url: str) -> List[str]:
    options = Options()
    options.add_argument("--headless")  # executa sem abrir janela
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(3)

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
