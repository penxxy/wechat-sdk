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
    try:
        # 确保BytesIO指针在开始位置
        image.seek(0)
        
        # 检查BytesIO是否有内容
        if image.tell() == len(image.getvalue()):
            image.seek(0)
        
        # 尝试打开图片
        try:
            img = Image.open(image)
            # 验证图片是否有效
            img.verify()
            # 重新打开图片，因为verify()后图片对象不能再使用
            image.seek(0)
            img = Image.open(image)
        except Exception as e:
            raise WeChatSDKException(f"无法识别图片格式或图片已损坏: {e}")
        
        # 转换为RGB模式以确保兼容性
        try:
            if img.mode in ('RGBA', 'LA', 'P'):
                # 对于有透明度的图片，创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
        except Exception as e:
            raise WeChatSDKException(f"图片格式转换失败: {e}")
        
        # 第一次压缩尝试
        try:
            output = BytesIO()
            img.save(output, format='JPEG', optimize=True, quality=85)
            
            # 如果文件太大，降低质量
            if output.tell() > max_size:
                output = BytesIO()
                img.save(output, format='JPEG', optimize=True, quality=75)
            
            # 如果还是太大，调整尺寸
            if output.tell() > max_size:
                try:
                    # 计算新尺寸
                    width, height = img.size
                    if width <= 0 or height <= 0:
                        raise WeChatSDKException("图片尺寸无效")
                    
                    ratio = (max_size / output.tell()) ** 0.5
                    new_width = max(1, int(width * ratio))
                    new_height = max(1, int(height * ratio))
                    
                    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    output = BytesIO()
                    img_resized.save(output, format='JPEG', optimize=True, quality=75)
                    
                    # 如果调整尺寸后还是太大，进一步降低质量
                    if output.tell() > max_size:
                        output = BytesIO()
                        img_resized.save(output, format='JPEG', optimize=True, quality=50)
                    
                except Exception as e:
                    raise WeChatSDKException(f"图片尺寸调整失败: {e}")
            
            # 最终检查
            if output.tell() == 0:
                raise WeChatSDKException("压缩后的图片为空")
            
            output.seek(0)
            return output
            
        except Exception as e:
            if isinstance(e, WeChatSDKException):
                raise
            raise WeChatSDKException(f"图片压缩保存失败: {e}")
    
    except WeChatSDKException:
        raise
    except Exception as e:
        # 最后的回退：如果所有压缩都失败，尝试直接返回原图片
        try:
            image.seek(0)
            original_size = len(image.getvalue())
            if original_size <= max_size:
                image.seek(0)
                return image
            else:
                raise WeChatSDKException(f"图片压缩失败，原图过大({original_size} bytes > {max_size} bytes): {e}")
        except Exception:
            raise WeChatSDKException(f"图片处理完全失败: {e}")

def get_filename_from_url(url: str) -> str:
    filename = os.path.basename(urlparse(url).path)
    # 确保文件名有正确的扩展名
    if not filename or '.' not in filename:
        return 'image.jpg'
    
    # 将扩展名统一为jpg
    name, ext = os.path.splitext(filename)
    return f"{name}.jpg"
