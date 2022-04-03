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


@app.post("/compare/{word}")
def validate_word(
 word: str, response: Response, db: sqlite3.Connection = Depends(get_db)
):
    idForDay = round(((int(datetime.today().strftime('%Y%d%m'))* 3 / 13)* 23) % 2308)
    try:
        cur = db.execute("SELECT * FROM answer WHERE answerid = ? LIMIT 1", [idForDay])
        wordOfDay = cur.fetchall()
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )

    return wordOfDay


if __name__ == "__main__":
    uvicorn.run("validate:app", host="0.0.0.0", port=5000, log_level="info")
