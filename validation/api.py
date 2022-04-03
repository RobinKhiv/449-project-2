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

from datetime import datetime
from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseModel, BaseSettings


class Settings(BaseSettings):
    database: str
    logging_config: str

    class Config:
        env_file = ".env"


class words(BaseModel):
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


@app.get("/validate/{word}")
def validate_word(
    word: str, response: Response, db: sqlite3.Connection = Depends(get_db)
):
    if len(word) != 5:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="allowed word length is 5")

    cur = db.execute("SELECT * FROM words WHERE word = ? LIMIT 1", [word])
    words = cur.fetchall()
    if not words:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="entered word is not a valid word"
        )
    return {"words": words}


if __name__ == "__main__":
