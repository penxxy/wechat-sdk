from bs4 import BeautifulSoup


def extract_html_images(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    return [img["src"] for img in soup.find_all("img") if "src" in img.attrs]


def process_html_for_wechat(html: str) -> str:
    """
    处理HTML格式，适配微信公众号显示
    """
    import re

    # 1. 转换标题标签为带样式的段落标签（微信公众号不支持标准h标签样式）
    # H1 - 大标题：24px，加粗
    html = re.sub(r'<h1[^>]*>(.*?)</h1>',
                  r'<p style="font-size: 24px; font-weight: bold; margin: 16px 0 12px 0;">\1</p>', html)

    # H2 - 二级标题：20px，加粗
    html = re.sub(r'<h2[^>]*>(.*?)</h2>',
                  r'<p style="font-size: 20px; font-weight: bold; margin: 14px 0 10px 0;">\1</p>', html)

    # H3 - 三级标题：18px，加粗
    html = re.sub(r'<h3[^>]*>(.*?)</h3>',
                  r'<p style="font-size: 18px; font-weight: bold; margin: 12px 0 8px 0;">\1</p>', html)

    # H4 - 四级标题：16px，加粗
    html = re.sub(r'<h4[^>]*>(.*?)</h4>',
                  r'<p style="font-size: 16px; font-weight: bold; margin: 10px 0 6px 0;">\1</p>', html)

    # H5, H6 - 小标题：14px，加粗
    html = re.sub(r'<h[56][^>]*>(.*?)</h[56]>',
                  r'<p style="font-size: 14px; font-weight: bold; margin: 8px 0 4px 0;">\1</p>', html)

    # 2. 处理超链接标签（微信公众号不支持外部链接）
    # 将 <a href="url">text</a> 转换为 text 🔗 url 的格式
    def replace_link(match):
        url = match.group(1)
        text = match.group(2)
        # 如果链接文本就是URL，只显示一次
        if text.strip() == url.strip():
            return f'🔗 {url}'
        else:
            return f'{text} 🔗 {url}'

    html = re.sub(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', replace_link, html)

    # 3. 清理列表项之间的多余换行符
    # 匹配 </li> 后面跟着换行符和空白字符，然后是 <li>
    html = re.sub(r'</li>\s*\n\s*<li>', '</li><li>', html)

    # 4. 清理列表开始和结束标签周围的空白
    html = re.sub(r'<ul>\s*\n\s*<li>', '<ul><li>', html)
    html = re.sub(r'</li>\s*\n\s*</ul>', '</li></ul>', html)
    html = re.sub(r'<ol>\s*\n\s*<li>', '<ol><li>', html)
    html = re.sub(r'</li>\s*\n\s*</ol>', '</li></ol>', html)

    # 5. 清理表格标签周围的多余换行
    html = re.sub(r'<table>\s*\n\s*', '<table>', html)
    html = re.sub(r'\s*\n\s*</table>', '</table>', html)
    html = re.sub(r'<tr>\s*\n\s*', '<tr>', html)
    html = re.sub(r'\s*\n\s*</tr>', '</tr>', html)

    # 6. 清理段落标签之间的多余空白，但保留一个换行
    html = re.sub(r'</p>\s*\n\s*\n\s*<p>', '</p>\n<p>', html)

    # 7. 清理块引用标签周围的空白
    html = re.sub(r'<blockquote>\s*\n\s*', '<blockquote>', html)
    html = re.sub(r'\s*\n\s*</blockquote>', '</blockquote>', html)

    return html
