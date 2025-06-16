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
from .image import download_image, process_image, get_filename_from_url
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

    def upload_image(self, path_or_url: str) -> str | None:
        try:
            # 1. 读取图片文件
            if path_or_url.startswith("http"):
                stream = download_image(path_or_url)
                original_filename = get_filename_from_url(path_or_url)
            else:
                if not os.path.exists(path_or_url):
                    return None
                with open(path_or_url, "rb") as f:
                    content = f.read()
                    if len(content) == 0:
                        return None
                    stream = BytesIO(content)
                original_filename = os.path.basename(path_or_url)
            
            # 2. 处理图片（格式转换和压缩）
            result = process_image(stream)
            if result is None:
                # 不是有效图片，跳过
                return None
            
            processed_image, ext = result
            
            # 3. 生成最终文件名
            name = os.path.splitext(original_filename)[0]
            final_filename = f"{name}.{ext}"
            
            # 4. 上传到微信
            url = f"{self.BASE_URL}/media/uploadimg?access_token={self.get_access_token()}"
            files = {"media": (final_filename, processed_image)}
            resp = requests.post(url, files=files)
            data = resp.json()
            if "url" not in data:
                return None
            return data["url"]
            
        except Exception:
            # 任何异常都返回None，跳过这个图片
            return None

    def create_draft_from_articles(self, articles: List[Article], base_dir=".") -> str:
        payload = []
        for art in articles:
            html = art["content"]
            if art["type"] == "markdown":
                import markdown
                html = markdown.markdown(html)
                
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
                if uploaded_url:  # 只有上传成功才替换
                    html = html.replace(src, uploaded_url)
                    html_imgs.append(uploaded_url)
                    original_img_paths.append(original_path)
                # 如果上传失败，跳过这个图片，HTML中保持原样
            thumb_id = art.get("thumb_media_id")
            if not thumb_id and original_img_paths:
                # 使用原始图片路径而不是上传后的URL
                thumb_id = self._upload_image_to_media_id(original_img_paths[0])
            
            # 确保thumb_media_id不为None，微信API不接受None值
            if not thumb_id:
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

    def _upload_image_to_media_id(self, image_path_or_url: str) -> str | None:
        """
        上传图片到微信服务器获取永久素材media_id
        用于草稿封面图片，必须使用永久素材接口而不是临时素材接口
        """
        try:
            # 1. 读取图片文件
            if image_path_or_url.startswith("http"):
                stream = download_image(image_path_or_url)
                original_filename = get_filename_from_url(image_path_or_url)
            else:
                if not os.path.exists(image_path_or_url):
                    return None
                with open(image_path_or_url, "rb") as f:
                    content = f.read()
                    if len(content) == 0:
                        return None
                    stream = BytesIO(content)
                original_filename = os.path.basename(image_path_or_url)
            
            # 2. 处理图片（格式转换和压缩）
            result = process_image(stream)
            if result is None:
                # 不是有效图片，跳过
                return None
            
            processed_image, ext = result
            
            # 3. 生成最终文件名
            name = os.path.splitext(original_filename)[0]
            final_filename = f"{name}.{ext}"
            
            # 4. 上传到微信永久素材接口
            url = f"{self.BASE_URL}/material/add_material?access_token={self.get_access_token()}&type=image"
            mime_type = "image/png" if ext == "png" else "image/jpeg"
            files = {"media": (final_filename, processed_image, mime_type)}
            resp = requests.post(url, files=files)
            data = resp.json()
            if "media_id" not in data:
                return None
            return data["media_id"]
            
        except Exception:
            # 任何异常都返回None，跳过这个图片
            return None
