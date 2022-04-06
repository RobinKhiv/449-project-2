# Science Fiction Novel API - FastAPI Edition
#
# Adapted from "Creating Web APIs with Python and Flask"
# <https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask>.
#


import contextlib
import logging.config
import sqlite3


import uvicorn
from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseSettings


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


# validate guess
@app.post("/validate/guess")
def validate_word(
        word: str, response: Response, db: sqlite3.Connection = Depends(get_db)
):
    logging.info("validate word::" + word)
    if len(word) != 5:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="allowed word length is 5")
    cur = db.execute("SELECT * FROM words WHERE UPPER(word) = UPPER(?) LIMIT 1", [word])
    words = cur.fetchall()
    if not words:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail={"entered word is not in the wordlist": word}
        )
    return {"isValidWord": "true"}


# add new word to words db
@app.post("/add/guess", status_code=status.HTTP_201_CREATED)
def create_word(
        word: str, response: Response, db: sqlite3.Connection = Depends(get_db)
):
    logging.info("adding word::" + word)
    if len(word.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="word is empty")
    try:
        cur = db.execute(
            """
            INSERT INTO WORDS(word)
            VALUES(:word)
            """,
            [word],
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )
    return {"New word added : " + word}


# remove existing word from words db
@app.post("/remove/guess", status_code=status.HTTP_200_OK)
def remove_word(
        word: str, response: Response, db: sqlite3.Connection = Depends(get_db)
):
    logging.info("deleting word::" + word)
    cur = db.execute(
        """
           DELETE FROM words WHERE word=:word
            """,
        [word],
    )
    print(cur.rowcount)
    if cur.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail={"no record exists for the word ": word}
        )

    db.commit()
    return {"Word deleted ": word}


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, log_level="info")
