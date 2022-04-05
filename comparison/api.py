# Science Fiction Novel API - FastAPI Edition
#
# Adapted from "Creating Web APIs with Python and Flask"
# <https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask>.
#

import collections
import contextlib
import logging.config
import sqlite3

from typing import Optional
from datetime import datetime
from fastapi import FastAPI, Depends, Response, HTTPException, status, Query
from pydantic import BaseModel, BaseSettings


class Settings(BaseSettings):
    database: str
    logging_config: str

    class Config:
        env_file = ".env"


def get_db():
    with contextlib.closing(sqlite3.connect(settings.database)) as db:
        db.row_factory = sqlite3.Row
        yield db


def get_logger():
    return logging.getLogger(__name__)


settings = Settings()
app: FastAPI = FastAPI()

logging.config.fileConfig(settings.logging_config)


def retrieve_hash_id(worddate: int):
    print('here', worddate)
    wordDay = worddate if worddate else int(datetime.now().strftime('%m%d%Y'))

    idForDay = round(((wordDay* 3 / 13)* 23) % 2308)
    return idForDay


# word of day service
def wod_retrieval_service(id: int, db: sqlite3.Connection):
    try:
        cur = db.execute("SELECT * FROM answer WHERE answerid = ? LIMIT 1", [id])
        word = cur.fetchall()
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )
    return word


# update word by id
def wod_update_service(id: int, newWord: str, db: sqlite3.Connection):
    try:
        cur = db.execute("UPDATE answer SET Answer = ? WHERE answerid = ?", (newWord, id))
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )
    return "Successfully updated word to '" + newWord + "'"


@app.post("/compare/")
def validate_word(word: str, response: Response, db: sqlite3.Connection = Depends(get_db), gameday: Optional[int] = Query(None, description="Enter date in MMDDYYY to check word against that specific date")):
    id = retrieve_hash_id(gameday)
    answer = wod_retrieval_service(id, db)
    return answer


@app.put("/check/update")
def update_word(word: str,  response: Response, db: sqlite3.Connection = Depends(get_db), gameday: Optional[int] = Query(None, description="Enter date in MMDDYYY to change word for that specific date" )):
    id = retrieve_hash_id(gameday)
    return wod_update_service(id, word, db)


if __name__ == "__main__":
    uvicorn.run("validate:app", host="0.0.0.0", port=5000, log_level="info")
