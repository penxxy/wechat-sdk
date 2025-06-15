from bs4 import BeautifulSoup

def extract_html_images(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    return [img["src"] for img in soup.find_all("img") if "src" in img.attrs]