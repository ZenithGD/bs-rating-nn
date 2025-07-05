import requests as rq
import os
from http import HTTPStatus

from bsrating.utils.difficulty import diff_from_str
from .exceptions import *

def ss_load_info_by_hash(hash: str, difficulty : str):

    diff_num = diff_from_str(difficulty)

    # load scoresaber info
    ss_rq_path = f"{os.getenv("SCORESABER_API_URL")}/leaderboard/by-hash/{hash}/info?difficulty={diff_num}"
    ss_r = rq.get(ss_rq_path)
    ss_r_code = ss_r.status_code
    ss_r_body = ss_r.json()

    if not HTTPStatus(ss_r_code).is_success:
        raise SSTimeOutError(ss_r_body["errorMessage"], 60)
    
    # load beatsaver info
    bs_rq_path = f"{os.getenv("BEATSAVER_API_URL")}/maps/hash/{hash}"
    bs_r = rq.get(bs_rq_path)
    bs_r_code = bs_r.status_code
    bs_r_body = bs_r.json()

    if not HTTPStatus(bs_r_code).is_success:
        raise MapNotFoundError(f"{hash} Not found")
    
    return {
        "id" : bs_r_body["id"],
        "difficulty" : difficulty,
        "hash" : ss_r_body["songHash"],
        "name" : ss_r_body["songName"],
        "stars" : ss_r_body["stars"],
        "created_date" : ss_r_body["createdDate"]
    }