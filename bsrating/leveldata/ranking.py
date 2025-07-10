import time
import requests as rq
import os
from http import HTTPStatus

from bsrating.leveldata.levelinfo import OnlineLevelInfo
from bsrating.utils.difficulty import diff_from_str
from .exceptions import *

def load_scoresaber_by_hash(hash: str, difficulty: str, attempt : int) -> dict:
    """Load information from ScoreSaber, from a difficulty for the map with a certain hash.

    Args:
        hash (str): The Beat Saver hash of the level.
        difficulty (str): The string representing the difficulty (e.g. Easy, Normal, Hard, Expert, ExpertPlus)
        attempt (int): The fetching attempt.

    Raises:
        MapNotFoundError: If the map is not found, this exception will be raised
        TimeOutError: If the map can be found but an error occurred, a timeout error
        will be raised, containing the amount of time to wait (exponential backoff)

    Returns:
        dict: The information fetched from the ScoreSaber API about this particular difficulty. 
    """
    
    diff_num = diff_from_str(difficulty)

    ss_rq_path = f"{os.getenv("SCORESABER_API_URL")}/leaderboard/by-hash/{hash}/info?difficulty={diff_num}"
    ss_r = rq.get(ss_rq_path, timeout=5)
    ss_r_code = ss_r.status_code
    ss_r_body = ss_r.json()

    if HTTPStatus(ss_r_code) == HTTPStatus.NOT_FOUND:
        raise MapNotFoundError(f"{hash} Not found")
    elif not HTTPStatus(ss_r_code).is_success:
        raise TimeOutError(ss_r_body["errorMessage"], min(2 ** attempt, 60))
    
    return {
        "songHash" : ss_r_body["songHash"],
        "stars" : ss_r_body["stars"] if ss_r_body["ranked"] else None
    }
    
def load_beatsaver_by_hash(hash: str, attempt : int) -> dict:
    """Load information from BeatSaver, for the map with a certain hash.

    Args:
        hash (str): The Beat Saver hash of the level.
        difficulty (str): The string representing the difficulty (e.g. Easy, Normal, Hard, Expert, ExpertPlus)
        attempt (int): The fetching attempt.

    Raises:
        MapNotFoundError: If the map is not found, this exception will be raised
        TimeOutError: If the map can be found but an error occurred, a timeout error
        will be raised, containing the amount of time to wait (exponential backoff)

    Returns:
        dict: The information fetched from the BeatSaver API. 
    """

    bs_rq_path = f"{os.getenv("BEATSAVER_API_URL")}/maps/hash/{hash}"
    bs_r = rq.get(bs_rq_path, timeout=5)
    bs_r_code = bs_r.status_code
    bs_r_body = bs_r.json()

    if HTTPStatus(bs_r_code) == HTTPStatus.NOT_FOUND:
        raise MapNotFoundError(f"{hash} Not found")
    elif not HTTPStatus(bs_r_code).is_success:
        raise TimeOutError(bs_r_body["errorMessage"], min(2 ** attempt, 60))
    
    return {
        "id" : bs_r_body["id"],
        "name" : bs_r_body["name"],
        "updatedAt" : bs_r_body["updatedAt"]
    }

def load_beatleader_by_hash(hash: str, difficulty : str, attempt : int):
    """Load information from BeatLeader, from a difficulty for the map with a certain hash.

    Args:
        hash (str): The Beat Saver hash of the level.
        difficulty (str): The string representing the difficulty (e.g. Easy, Normal, Hard, Expert, ExpertPlus)
        attempt (int): The fetching attempt.

    Raises:
        MapNotFoundError: If the map is not found, this exception will be raised
        TimeOutError: If the map can be found but an error occurred, a timeout error
        will be raised, containing the amount of time to wait (exponential backoff)

    Returns:
        dict: The information fetched from the BeatLeader API about this particular difficulty. 
    """

    bl_rq_path = f"{os.getenv("BEATLEADER_API_URL")}/leaderboard/{hash}/{difficulty}/Standard"
    bl_r = rq.get(bl_rq_path, timeout=5)
    bl_r_code = bl_r.status_code
    bl_r_body = bl_r.json()

    if HTTPStatus(bl_r_code) == HTTPStatus.NOT_FOUND:
        raise MapNotFoundError(f"{hash} Not found")
    elif not HTTPStatus(bl_r_code).is_success:
        raise TimeOutError(bl_r_body["errorMessage"], min(2 ** attempt, 60))
    
    return {
        "stars" : bl_r_body["difficulty"]["stars"]
    }

def fetch_with_retry(fetcher, max_retries):
    result = None
    retries = 0
    while retries < max_retries:
        try: 
            result = fetcher(retries)
            break
        except MapNotFoundError:
            return None
        except TimeOutError as te:
            print(f"{te} Retrying ({retries} / {max_retries})...")
            retries += 1
            time.sleep(te.time)

    if retries >= max_retries and result is None:
        raise MapNotFoundError("Couldn't retrieve map information")
    
    return result

def load_info_by_hash(hash: str, difficulty : str, max_retries = 5, use_bl : bool = False) -> OnlineLevelInfo:

    # load scoresaber info
    ss_data = fetch_with_retry(lambda t : load_scoresaber_by_hash(hash, difficulty, t), max_retries)

    # load beatleader info
    bl_data = None
    if use_bl:
        bl_data = fetch_with_retry(lambda t : load_beatleader_by_hash(hash, difficulty, t), max_retries) if use_bl else None

    # load beatsaver info
    bs_data = fetch_with_retry(lambda t : load_beatsaver_by_hash(hash, t), max_retries)
    
    return OnlineLevelInfo(
        bs_data["id"], 
        hash, 
        bs_data["name"],
        difficulty, 
        bl_data["stars"] if use_bl else None,
        ss_data["stars"] if ss_data is not None else None,
        bs_data["updatedAt"]
    )