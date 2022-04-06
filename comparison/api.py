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

class AnswerDef(object):
    def __init__(self, answerid, answer):
        self.answerid = answerid
        self.answer  = answer


def get_db():
    with contextlib.closing(sqlite3.connect(settings.database)) as db:
        db.row_factory = sqlite3.Row
        yield db


def get_logger():
    return logging.getLogger(__name__)


settings = Settings()
app: FastAPI = FastAPI()

logging.config.fileConfig(settings.logging_config)


def retrieve_game_date(worddate: int):
    return worddate if worddate else int(datetime.now().strftime('%m%d%Y'))

def retrieve_hash_id(worddate: int):
    # wordDay = worddate if worddate else int(datetime.now().strftime('%m%d%Y'))
    idForDay = round(((worddate* 3 / 13)* 23) % 2308)
    return idForDay


# word of day service
def wod_retrieval_service(id: int, db: sqlite3.Connection):
    try:
        cur = db.execute("SELECT * FROM answer WHERE answerid = ? LIMIT 1", [id])
        query = cur.fetchall()
        for row in query:
            result = AnswerDef(*row)

    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )

    return result.answer


# update word by id
def wod_update_service(id: int, newWord: str, db: sqlite3.Connection):
    try:
        print(newWord, id)
        cur = db.execute("UPDATE answer SET answer = ? WHERE answerid = ?", (newWord, id))
        db.commit()
        print('here')
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )



#compare answer with input
def letter_find(answer: str, user_input:str):
        word_of_day = answer
        one = word_of_day[0]
        two = word_of_day[1]
        three = word_of_day[2]
        four = word_of_day[3]
        five = word_of_day[4]
        yellow = []
        green = []
        gray = []
        vars = [False,False,False,False,False]
        char_index = 1

        for index in range(0, len(user_input)):

            if user_input[index] == one and not vars[0]:
              if char_index == 1:
                  green.append(index)
                  char_index += 1
                  vars[0] = True
                  continue
              else:
                  yellow.append(index)
                  char_index += 1
                  continue

            if user_input[index] == two and not vars[1]:
                if char_index == 2:
                      green.append(index)
                      char_index += 1
                      vars[1] = True
                      continue
                else:
                    yellow.append(index)
                    char_index += 1
                    continue

            if user_input[index] == three and not vars[2]:
                if char_index == 3:
                      green.append(index)
                      char_index += 1
                      vars[2] = True
                      continue
                else:
                    yellow.append(index)
                    char_index += 1
                    continue

            if user_input[index] == four and not vars[3]:
                if char_index == 4:
                      green.append(index)
                      char_index += 1
                      vars[3] = True
                      continue
                else:
                    yellow.append(index)
                    char_index += 1
                    continue

            if user_input[index] == five and not vars[4]:
                if char_index == 5:
                      green.append(index)
                      char_index += 1
                      vars[0] = True
                      continue
                else:
                    yellow.append(index)
                    char_index += 1
                    continue
            gray.append(index)
            char_index += 1
            continue

        constructed = {
        "correct":green,
        "WrongPosition":yellow,
        "wrong":gray
       }
        return constructed


@app.post("/compare/")
def validate_word_and_return_indexes_of_correct_and_incorrect(word: str, response: Response, db: sqlite3.Connection = Depends(get_db), gameday: Optional[int] = Query(None, description="Enter date in MMDDYYY to check word against that specific date")):
    gamedate = retrieve_game_date(gameday)
    id = retrieve_hash_id(gamedate)
    answer = wod_retrieval_service(id, db)
    compare = letter_find(answer, word)
    return compare


@app.put("/check/update")
def update_answer(word: str,  response: Response, db: sqlite3.Connection = Depends(get_db), gameday: Optional[int] = Query(None, description="Enter date in MMDDYYY to change word for that specific date" )):
    gamedate = retrieve_game_date(gameday)
    id = retrieve_hash_id(gamedate)
    wod_update_service(id, word, db)
    return 'Successfully updated word'



if __name__ == "__main__":
    uvicorn.run("validate:app", host="0.0.0.0", port=5000, log_level="info")
