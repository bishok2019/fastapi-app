from pydantic import BaseModel, ConfigDict, EmailStr


class PostCreate(BaseModel):
    title: str
    content: str
    author_id: int


class PostList(BaseModel):
    title: str
    content: str
    author_id: int
    model_config = ConfigDict(from_attributes=True)


class PostRetrieve(BaseModel):
    title: str
    content: str
    author_id: int
    model_config = ConfigDict(from_attributes=True)


class PostUpdate(BaseModel):
    title: str
    content: str
    author_id: int
