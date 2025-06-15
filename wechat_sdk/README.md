## WeChatPublisher SDK

这是一个用于自动化发布微信公众号图文的 Python SDK，支持 Markdown 和 HTML 格式，具备以下功能：

- 远程或本地图片上传，并自动压缩
- Markdown 转 HTML 自动替换图片地址
- 支持草稿创建，批量图文上传
- 自动封面图生成
- Token 缓存管理

### 安装

```bash
pip install -r requirements.txt
```

依赖项：
- requests
- markdown
- beautifulsoup4
- pillow

### 使用示例

```python
from wechat_sdk import WeChatPublisher

publisher = WeChatPublisher(appid="你的appid", secret="你的secret")

articles = [
    {
        "title": "AI 周报：GPT-5 传闻再起",
        "author": "author",
        "content": "## 大模型

![](images/img.png)",
        "type": "markdown",
        "thumb_media_id": None,
    },
    {
        "title": "图文测试",
        "author": "小助手",
        "content": "<h1>图文标题</h1><img src='images/demo.jpg' />",
        "type": "html",
        "thumb_media_id": None
    }
]

media_id = publisher.create_draft_from_articles(articles, base_dir=".")
print("草稿 media_id:", media_id)
```