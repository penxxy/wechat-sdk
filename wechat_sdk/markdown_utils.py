import re
from bs4 import BeautifulSoup


def extract_markdown_images(md: str) -> list[tuple[str, str]]:
    return re.findall(r"!\[(.*?)\]\((.*?)\)", md)


def extract_html_images(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    return [img["src"] for img in soup.find_all("img") if "src" in img.attrs]
