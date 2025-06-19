import requests
from PIL import Image
from io import BytesIO
import os
from urllib.parse import urlparse


def download_image(url: str) -> BytesIO:
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception(f"Failed to download image: {url}")
    return BytesIO(resp.content)


def process_image(image: BytesIO, max_size: int = 10 * 1024 * 1024) -> tuple[BytesIO, str] | None:
    """
    处理图片：检查格式、转换格式、压缩大小
    微信支持格式：bmp/png/jpeg/jpg/gif，大小限制10M
    返回：(处理后的图片BytesIO, 文件扩展名) 或 None（如果不是有效图片）
    """
    try:
        image.seek(0)
        img = Image.open(image)
        
        # 验证图片是否有效
        img.verify()
        # 重新打开图片，因为verify()后图片对象不能再使用
        image.seek(0)
        img = Image.open(image)
        
        # 获取原始格式
        original_format = img.format
        if not original_format:
            return None
        
        # 检查图片大小是否需要压缩
        image.seek(0)
        original_size = len(image.getvalue())
        
        # 如果原图小于10M且格式支持，直接返回
        if original_size <= max_size and original_format in ['BMP', 'PNG', 'JPEG', 'GIF']:
            image.seek(0)
            ext = 'jpg' if original_format == 'JPEG' else original_format.lower()
            return image, ext
        
        # 需要转换格式或压缩大小
        # 对于有透明度的图片，转为PNG；其他转为JPEG
        if img.mode in ('RGBA', 'LA') or original_format == 'PNG':
            output_format = 'PNG'
            ext = 'png'
            output = BytesIO()
            img.save(output, format='PNG', optimize=True)
        else:
            output_format = 'JPEG'
            ext = 'jpg'
            # 转换为RGB模式
            if img.mode != 'RGB':
                img = img.convert('RGB')
            output = BytesIO()
            img.save(output, format='JPEG', optimize=True, quality=85)
        
        # 如果还是太大，进行压缩
        if output.tell() > max_size and output_format == 'JPEG':
            # 降低质量
            output = BytesIO()
            img.save(output, format='JPEG', optimize=True, quality=75)
            
            # 如果还是太大，调整尺寸
            if output.tell() > max_size:
                width, height = img.size
                if width <= 0 or height <= 0:
                    return None
                ratio = (max_size / output.tell()) ** 0.5
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                if new_width <= 0 or new_height <= 0:
                    return None
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                output = BytesIO()
                img_resized.save(output, format='JPEG', optimize=True, quality=75)
        
        output.seek(0)
        return output, ext
        
    except Exception:
        # 如果任何步骤失败，返回None表示这不是有效图片
        return None


def get_filename_from_url(url: str) -> str:
    filename = os.path.basename(urlparse(url).path)
    # 确保文件名有正确的扩展名
    if not filename or '.' not in filename:
        return 'image.jpg'
    
    # 保持原始扩展名，不强制转换
    return filename


