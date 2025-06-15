import requests
from PIL import Image
from io import BytesIO
import os
from urllib.parse import urlparse
from .exceptions import WeChatSDKException

def download_image(url: str) -> BytesIO:
    resp = requests.get(url)
    if resp.status_code != 200:
        raise WeChatSDKException(f"Failed to download image: {url}")
    return BytesIO(resp.content)

def compress_image(image: BytesIO, max_size: int = 1 * 1024 * 1024) -> BytesIO:
    """
    压缩图片并确保格式符合微信要求
    微信支持的图片格式：JPG, PNG
    """
    img = Image.open(image)
    
    # 转换为RGB模式以确保兼容性
    if img.mode in ('RGBA', 'LA', 'P'):
        # 对于有透明度的图片，创建白色背景
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    output = BytesIO()
    
    # 统一使用JPEG格式，微信更好支持
    img.save(output, format='JPEG', optimize=True, quality=85)
    
    # 如果文件太大，降低质量
    if output.tell() > max_size:
        output = BytesIO()
        img.save(output, format='JPEG', optimize=True, quality=75)
    
    # 如果还是太大，调整尺寸
    if output.tell() > max_size:
        # 计算新尺寸
        width, height = img.size
        ratio = (max_size / output.tell()) ** 0.5
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        output = BytesIO()
        img_resized.save(output, format='JPEG', optimize=True, quality=75)
    
    output.seek(0)
    return output

def get_filename_from_url(url: str) -> str:
    filename = os.path.basename(urlparse(url).path)
    # 确保文件名有正确的扩展名
    if not filename or '.' not in filename:
        return 'image.jpg'
    
    # 将扩展名统一为jpg
    name, ext = os.path.splitext(filename)
    return f"{name}.jpg"
