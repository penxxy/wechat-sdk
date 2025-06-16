# WeChat SDK

一个简单易用的微信公众号开发 Python SDK，支持文章发布、图片上传、草稿管理等功能。

## 功能特性

- 🚀 支持从 Markdown 和 HTML 创建微信草稿
- 🖼️ 自动处理图片上传和压缩
- 📝 支持多篇文章批量发布
- 💾 Token 自动缓存和刷新
- 🛡️ 完善的错误处理

## 安装

### 从 GitHub 安装

```bash
pip install git+https://github.com/penxxy/wechat-sdk.git
```

### 从 PyPI 安装（如果已发布）

```bash
pip install wechat-sdk
```

## 使用方法

### 基本使用

```python
from wechat_sdk import WeChatPublisher, Article

# 初始化发布器
publisher = WeChatPublisher(
    appid="your_appid",
    secret="your_secret"
)

# 创建文章
articles: list[Article] = [{
    "title": "我的第一篇文章",
    "content": "这是文章内容",
    "type": "html",  # 或 "markdown"
    "author": "作者名",
    "thumb_media_id": None  # 可选，封面图片ID
}]

# 创建草稿
media_id = publisher.create_draft_from_articles(articles)
print(f"草稿创建成功，media_id: {media_id}")
```

### 高级使用

```python
# 上传单独图片
image_url = publisher.upload_image("path/to/image.jpg")
print(f"图片上传成功: {image_url}")

# 从 URL 上传图片
image_url = publisher.upload_image("https://example.com/image.jpg")
```

## 配置说明

- `appid`: 微信公众号的 AppID
- `secret`: 微信公众号的 AppSecret  
- `token_cache_path`: Access Token 缓存文件路径（可选，默认 ".token_cache"）

## 文章格式

文章对象支持以下字段：

```python
from wechat_sdk import Article

article: Article = {
    "title": "文章标题",           # 必填：字符串
    "content": "文章内容",         # 必填：字符串
    "type": "html",              # 必填: "html" 或 "markdown"
    "author": "作者名",           # 必填：字符串
    "thumb_media_id": None,      # 可选：封面图片ID，字符串或None
}
```

## 注意事项

1. 需要在微信公众平台开启开发者模式
2. 确保服务器IP在微信白名单中
3. 图片大小建议小于2MB，支持 jpg、png 格式
4. Access Token 会自动缓存，有效期7200秒


## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！ 