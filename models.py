# server/models.py
from pydantic import BaseModel
from typing import List, Optional

class Movie(BaseModel):
    id: Optional[int] = None
    name: str
    year: str
    duration: Optional[str] = ""
    rating: Optional[str] = ""
    description: Optional[str] = ""
    poster: Optional[str] = ""
    genres: List[str] = []
    actors: List[str] = []

class MovieCreate(BaseModel):
    name: str
    year: str
    duration: Optional[str] = ""
    rating: Optional[str] = ""
    description: Optional[str] = ""
    poster: Optional[str] = ""
    genres: List[str] = []
    actors: List[str] = []