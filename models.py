from pydantic import BaseModel
from datetime import datetime

class Post(BaseModel):
    id: int
    author: str
    title: str
    content: str
    date_posted: str = datetime.now().strftime("%B %d, %Y")