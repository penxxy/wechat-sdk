from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wechat-sdk",
    version="0.1.0",
    author="penxxy",
    author_email="mkhu3638@gmail.com",
    description="微信公众号开发 SDK - 支持文章发布、图片上传等功能",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/penxxy/wechat-sdk",
    packages=["wechat_sdk"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "Pillow>=8.0.0",
        "markdown>=3.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 