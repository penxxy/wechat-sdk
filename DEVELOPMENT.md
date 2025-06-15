# 开发说明

## 项目结构

```
wechat-sdk/
├── wechat_sdk/          # 核心 SDK 代码（会被打包发布）
│   ├── __init__.py
│   ├── core.py          # 主要功能实现
│   ├── image.py         # 图片处理
│   ├── html_utils.py    # HTML 工具
│   ├── markdown_utils.py # Markdown 工具
│   ├── article_types.py  # 文章类型定义
│   └── exceptions.py     # 异常定义
├── example_publish.py   # 使用示例（不会被打包）
├── article.md           # 测试文章（不会被打包）
├── cover.png            # 测试封面（不会被打包）
├── preview.html         # 预览文件（不会被打包）
├── .token_cache         # Token 缓存（不会被打包）
├── setup.py             # 包配置
├── requirements.txt     # 依赖
├── README.md            # 项目说明
└── .gitignore           # Git 忽略文件
```

## 发布内容

只有 `wechat_sdk/` 目录中的代码会被打包发布，其他文件都是开发测试用的。

## 本地开发

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 可编辑模式安装：
```bash
pip install -e .
```

3. 运行测试示例：
```bash
python example_publish.py
```

## 发布新版本

1. 修改 `setup.py` 中的版本号
2. 提交代码到 GitHub
3. 用户可通过以下方式安装：
   ```bash
   pip install git+https://github.com/yourusername/wechat-sdk.git
   ``` 