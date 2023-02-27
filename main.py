import orjson
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class MovieRecord(BaseModel):
    name: str
    description: str
    imageUrl: str
    actor: str
    gender: str
    origin: str
    firstEpisodeName: str
    firstEpisodeYear: int

    @staticmethod
    def from_dict(data: dict):
        record = MovieRecord(**data)
        return record


class Problem(BaseModel):
    detail: str


class Database:
    def __init__(self):
        self._data: list = []

    def load_from_filename(self, filename: str):
        with open(filename, "r") as f:
            data = orjson.loads(f.read())
            for record in data:
                obj = MovieRecord.from_dict(record)
                self._data.append(obj)

    def delete(self, id_movie: int):
        if 0 < id_movie >= len(self._data):
            return
        self._data.pop(id_movie)

    def add(self, movie: MovieRecord):
        self._data.append(movie)

    def get(self, id_movie: int):
        if 0 < id_movie >= len(self._data):
            return
        return self._data[id_movie]

    def get_all(self) -> list[MovieRecord]:
        return self._data

    def update(self, id_movie: int, movie: MovieRecord):
        if 0 < id_movie >= len(self._data):
            return
        self._data[id_movie] = movie

    def count(self) -> int:
        return len(self._data)
