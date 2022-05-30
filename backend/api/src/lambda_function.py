import os
import json
import uuid
import utils

from lambdarest import lambda_handler

from uc.code_generation import CodeGeneratorService
from uc.user_registration import UserRegistrationService
from uc.meet_event import MeetService
from uc.ranking import RankingService
from adapter.code_store import DynamoCodeStore
from adapter.user_store import DynamoUserStore
from adapter.meet_store import DynamoMeetStore
from adapter.ranking_store import DynamoRankingStore

MEET_REDIRECT_URL = os.environ['MEET_REDIRECT_URL']

CODE_STORE_TABLE_NAME = os.environ["CODE_STORE_TABLE_NAME"]
USER_STORE_TABLE_NAME = os.environ["USER_STORE_TABLE_NAME"]
RANK_STORE_TABLE_NAME = os.environ["RANK_STORE_TABLE_NAME"]
MEET_URL_PREFIX = os.environ["MEET_URL_PREFIX"]

CODE_STORE = DynamoCodeStore(CODE_STORE_TABLE_NAME)
USER_STORE = DynamoUserStore(USER_STORE_TABLE_NAME)
MEET_STORE = DynamoMeetStore(USER_STORE_TABLE_NAME)
RANK_STORE = DynamoRankingStore(RANK_STORE_TABLE_NAME)
CODE_SERVICE = CodeGeneratorService(MEET_URL_PREFIX, CODE_STORE)
USER_SERVICE = UserRegistrationService(CODE_SERVICE, USER_STORE, CODE_STORE)
MEET_SERVICE = MeetService(CODE_SERVICE, USER_SERVICE, MEET_STORE, RANK_STORE)
RANK_SERVICE = RankingService(RANK_STORE)

MAX_CODE_GENERATION_COUNT = 100


@lambda_handler.handle("get", path="/api")
def author(event):
    return "Powered by TEX Team technology"


@lambda_handler.handle("get", path="/meet/<meet_param>")
def meet_event(event, meet_param):
    print(f"Someone scanned {meet_param} but no 'from', redirecting...")
    return {
        'statusCode': 302,
        'headers': {
            'Location': f"{MEET_REDIRECT_URL}?meet_id={meet_param}",
        },
    }


@lambda_handler.handle("post", path="/meet")
def meet_event(event):
    pass


@lambda_handler.handle("get", path="/api/generate")
def generate_code(event):
    params = event.get("queryStringParameters") or {}
    count = params.get("count", 1)
    try:
        count = int(count)
    except ValueError:
        return "Bad parameter value", 400
    if count >= MAX_CODE_GENERATION_COUNT or count < 1:
        return "Bad parameter value", 400
    urls = CODE_SERVICE.generate_meet_urls(count)
    return urls


@lambda_handler.handle("post", path="/api/register/new")
def register_name(event):
    request = json.loads(event["body"])
    if "meet_id" not in request or "username" not in request:
        return "Bad parameter value", 400
    try:
        phone_id = USER_SERVICE.register_user(request["meet_id"], request["username"])
        return { "phone_id": phone_id}
    except UserRegistrationService.InvalidMeetIdException:
        return "Bad parameter value", 400
    except UserRegistrationService.PhoneIdNotFoundException:
        return "Bad parameter value", 404


@lambda_handler.handle("post", path="/api/register/update")
def update_name(event):
    request = json.loads(event["body"])
    if "phone_id" not in request or "username" not in request:
        return "Bad parameter value", 400
    try:
        USER_SERVICE.update_user(request["phone_id"], request["username"])
        return
    except UserRegistrationService.PhoneIdNotFoundException:
        return "Bad parameter value", 404


@lambda_handler.handle("get", path="/api/all_ranking")
def board_list(event):
    return []


@lambda_handler.handle("get", path="/api/my_ranking")
def user_list(event):
    return []


@lambda_handler.handle("get", path="/api/debug")
def echo(event):
    print(event)
    return {"event": str(event)}