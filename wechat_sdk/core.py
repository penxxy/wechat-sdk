from bs4 import BeautifulSoup

def extract_html_images(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    return [img["src"] for img in soup.find_all("img") if "src" in img.attrs]

# wechat_sdk/core.py
import os
import time
import requests
from typing import List
from io import BytesIO
from .article_types import Article
from .image import download_image, compress_image, get_filename_from_url
from .markdown_utils import extract_markdown_images
from .html_utils import extract_html_images
from .exceptions import WeChatSDKException

class WeChatPublisher:
    BASE_URL = "https://api.weixin.qq.com/cgi-bin"

    def __init__(self, appid, secret, token_cache_path=".token_cache"):
        self.appid = appid
        self.secret = secret
        self.token_cache_path = token_cache_path
        self._access_token = None
        self._token_expires_at = 0

    def get_access_token(self):
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token
        if os.path.exists(self.token_cache_path):
            with open(self.token_cache_path, "r") as f:
                data = f.read().strip().split(",")
                if len(data) == 2 and time.time() < float(data[1]):
                    self._access_token = data[0]
                    self._token_expires_at = float(data[1])
                    return self._access_token
        url = f"{self.BASE_URL}/token?grant_type=client_credential&appid={self.appid}&secret={self.secret}"
        resp = requests.get(url)
        data = resp.json()
        if "access_token" not in data:
            raise WeChatSDKException(f"Token fetch failed: {data}")
        self._access_token = data["access_token"]
        self._token_expires_at = time.time() + data["expires_in"] - 60
        with open(self.token_cache_path, "w") as f:
            f.write(f"{self._access_token},{self._token_expires_at}")
        return self._access_token

    def upload_image(self, path_or_url: str) -> str:
        if path_or_url.startswith("http"):
            stream = download_image(path_or_url)
            filename = get_filename_from_url(path_or_url)
        else:
            with open(path_or_url, "rb") as f:
                stream = BytesIO(f.read())
            filename = os.path.basename(path_or_url)
        compressed = compress_image(stream)
        url = f"{self.BASE_URL}/media/uploadimg?access_token={self.get_access_token()}"
        files = {"media": (filename, compressed)}
        resp = requests.post(url, files=files)
        data = resp.json()
        if "url" not in data:
            raise WeChatSDKException(f"Upload image failed: {data}")
        return data["url"]

    def create_draft_from_articles(self, articles: List[Article], base_dir=".") -> str:
        payload = []
        for art in articles:
            html = art["content"]
            if art["type"] == "markdown":
                import markdown
                html = markdown.markdown(html)
            # if art["type"] == "markdown":
            #     imgs = extract_markdown_images(art["content"])
            #     html_imgs = [self.upload_image(os.path.join(base_dir, path)) for _, path in imgs]
            #     # 保存原始图片路径用于封面
            #     original_img_paths = [os.path.join(base_dir, path) for _, path in imgs]
            # else:
            html_imgs = []
            original_img_paths = []
            for src in extract_html_images(html):
                # 判断是HTTP URL还是本地路径
                if src.startswith("http"):
                    # HTTP URL直接使用
                    image_path = src
                    original_path = src
                else:
                    # 本地路径需要和base_dir拼接
                    image_path = os.path.join(base_dir, src)
                    original_path = os.path.join(base_dir, src)
                
                uploaded_url = self.upload_image(image_path)
                html = html.replace(src, uploaded_url)
                html_imgs.append(uploaded_url)
                original_img_paths.append(original_path)
            thumb_id = art.get("thumb_media_id")
            if not thumb_id and original_img_paths:
                # 使用原始图片路径而不是上传后的URL
                thumb_id = self._upload_image_to_media_id(original_img_paths[0])
            
            # 确保thumb_media_id不为None，微信API不接受None值
            if thumb_id is None:
                thumb_id = ""
            
            payload.append({
                "title": art["title"],
                "author": art.get("author", ""),
                "digest": "",
                "content": html,
                "thumb_media_id": thumb_id,
                "show_cover_pic": 1 if thumb_id else 0,  # 如果没有封面就不显示封面
                "need_open_comment": 0,
                "only_fans_can_comment": 0
            })
        
        url = f"{self.BASE_URL}/draft/add?access_token={self.get_access_token()}"
        # 修复编码问题：手动序列化JSON并设置ensure_ascii=False
        import json
        data_json = json.dumps({"articles": payload}, ensure_ascii=False)
        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }
        resp = requests.post(url, data=data_json.encode('utf-8'), headers=headers)
        data = resp.json()
        if "media_id" not in data:
            raise WeChatSDKException(f"Create draft failed: {data}")
        return data["media_id"]

    def _upload_image_to_media_id(self, image_path_or_url: str) -> str:
        """
        上传图片到微信服务器获取永久素材media_id
        用于草稿封面图片，必须使用永久素材接口而不是临时素材接口
        """
        if image_path_or_url.startswith("http"):
            # 处理URL
            stream = download_image(image_path_or_url)
            filename = get_filename_from_url(image_path_or_url)
        else:
            # 处理本地文件
            if not os.path.exists(image_path_or_url):
                raise WeChatSDKException(f"Image file not found: {image_path_or_url}")
            
            with open(image_path_or_url, "rb") as f:
                stream = BytesIO(f.read())
            
            # 确保文件名有正确的扩展名
            filename = os.path.basename(image_path_or_url)
            name, ext = os.path.splitext(filename)
            filename = f"{name}.jpg"  # 统一使用jpg扩展名
        
        # 压缩图片
        compressed = compress_image(stream)
        
        # 关键修复：使用永久素材接口而不是临时素材接口
        url = f"{self.BASE_URL}/material/add_material?access_token={self.get_access_token()}&type=image"
        files = {"media": (filename, compressed, "image/jpeg")}  # 明确指定MIME类型
        resp = requests.post(url, files=files)
        data = resp.json()
        if "media_id" not in data:
            raise WeChatSDKException(f"Upload cover failed: {data}")
        return data["media_id"]
