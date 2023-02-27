import orjson
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class CharacterModel(BaseModel):
    name: str
    image_url: str
    actor: str
    familys: list[str]
    first_episode_name: str
    first_episode_year: int
    character_description: str

    @staticmethod
    def from_dict(data: dict):
        record = CharacterModel(**data)
        return record


class Problem(BaseModel):
    detail: str


class Database:
    def __init__(self):
        self._data: list = []

    def load_from_filename(self, filename: str):
        with open(filename, "rb") as f:
            data = orjson.loads(f.read())
            for record in data:
                obj = CharacterModel.from_dict(record)
                self._data.append(obj)
 
    def get_all(self) -> list[CharacterModel]:
        object_with_data = {}
        for i in range(len(self._data)):
            object_with_data[i] = self._data[i]
        return object_with_data

    def get(self, id_character: int):
        if 0 < id_character >= len(self._data):
            return
        return self._data[id_character]

    def add(self, character: CharacterModel):
        self._data.append(character)

    def update(self, id_character: int, character: CharacterModel):
        if 0 < id_character >= len(self._data):
            return
        self._data[id_character] = character

    def delete(self, id_character: int):
        if 0 < id_character >= len(self._data):
            return
        self._data.pop(id_character)

    def count(self) -> int:
        return len(self._data)

db = Database()
db.load_from_filename('characters.json')

app = FastAPI(title="Game of thrones Rest API", version="0.1", docs_url="/docs")

app.is_shutdown = False

@app.get("/characters", response_model=dict[int, CharacterModel], description="Returns list of characters")
async def get_characters():
    return db.get_all()


@app.get("/characters/{id_character}", response_model=CharacterModel, description="Returns character by id")
async def get_character(id_character: int):
    return db.get(id_character)


@app.post("/characters", response_model=CharacterModel, description="Adds character to DB")
async def post_characters(character: CharacterModel):
    db.add(character)
    return character


@app.delete("/characters/{id_character}", description="Delets character from DB", responses={
    404: {'model': Problem}
})
async def delete_character(id_character: int):
    character = db.get(id_character)
    if character is None:
        raise HTTPException(404, "Character does not exist")
    db.delete(id_character)
    return {'status': 'smazano'}


@app.patch("/characters/{id_character}", description="Upadates character from DB", responses={
    404: {'model': Problem}
})
async def update_character(id_character: int, updated_character: CharacterModel):
    character = db.get(id_character)
    if character is None:
        raise HTTPException(404, "Character does not exist")
    db.update(id_character, updated_character)
    return {'old': character, 'new': updated_character}