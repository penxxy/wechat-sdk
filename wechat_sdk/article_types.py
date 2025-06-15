from typing import Literal, TypedDict, Optional

class Article(TypedDict):
    title: str
    author: str
    content: str
    type: Literal["markdown", "html"]
    thumb_media_id: Optional[str]
