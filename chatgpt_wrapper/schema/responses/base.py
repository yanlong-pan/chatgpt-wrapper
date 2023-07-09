from pydantic import BaseModel

class Base(BaseModel):
    success: str
    msg: str = None
    detail: dict = None

class Success(Base):
    success: str = 'yes'

class Failure(Base):
    success: str = 'no'