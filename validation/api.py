# Science Fiction Novel API - FastAPI Edition
#
# Adapted from "Creating Web APIs with Python and Flask"
# <https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask>.
#

import collections
import contextlib
import logging.config
import sqlite3
import typing

import uvicorn
from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseModel, BaseSettings


class Settings(BaseSettings):
    database: str
    logging_config: str

    class Config:
        env_file = ".env"


class Words(BaseModel):
    id: int
    word: str


def get_db():
    with contextlib.closing(sqlite3.connect(settings.database)) as db:
        db.row_factory = sqlite3.Row
        yield db


def get_logger():
    return logging.getLogger(__name__)


settings = Settings()
app: FastAPI = FastAPI()

logging.config.fileConfig(settings.logging_config)


@app.post("/validate/guess/{word}")
def validate_word(
        word: str, response: Response, db: sqlite3.Connection = Depends(get_db)
):
    if len(word) != 5:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="allowed word length is 5")

    cur = db.execute("SELECT * FROM words WHERE UPPER(word) = UPPER(?) LIMIT 1", [word])
    words = cur.fetchall()
    if not words:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail={"entered word is not a valid word":word}
        )
    return {"isValidWord": "true"}


@app.post("/add/guess", status_code=status.HTTP_201_CREATED)
def create_word(
        words: Words, response: Response, db: sqlite3.Connection = Depends(get_db)
):
    w = dict(words)
    try:
        cur = db.execute(
            """
            INSERT INTO WORDS(wordid, word)
            VALUES(:id,:word)
            """,
            w,
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )
    w["id"] = cur.lastrowid
    response.headers["Location"] = f"/words/{w['id']}"
    return w


@app.post("/remove/guess", status_code=status.HTTP_200_OK)
def remove_word(
        words: Words, response: Response, db: sqlite3.Connection = Depends(get_db)
):
    w = dict(words)
    cur = db.execute(
        """
           DELETE  FROM words WHERE wordid = :id and word=:word
            """,
        w,
    )
    if cur.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"no record exists for the id and word": w}
        )
    db.commit()
    return w


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, log_level="info")
