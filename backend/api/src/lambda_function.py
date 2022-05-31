import json
import logging
import os

from lambdarest import lambda_handler

from adapter.code_store import DynamoCodeStore
from adapter.meet_store import DynamoMeetStore
from adapter.ranking_store import DynamoRankingStore
from adapter.user_store import DynamoUserStore
from uc.code_generation import CodeGeneratorService
from uc.meet_event import MeetService
from uc.ranking import RankingService
from uc.user_registration import UserRegistrationService

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
MEET_SERVICE = MeetService(CODE_SERVICE, CODE_STORE, USER_SERVICE, MEET_STORE, RANK_STORE)
RANK_SERVICE = RankingService(RANK_STORE, USER_STORE)

MAX_CODE_GENERATION_COUNT = 100

logger = logging.getLogger()


@lambda_handler.handle("get", path="/api")
def author(event):
    return "Powered by TEX Team technology"


@lambda_handler.handle("get", path="/meet/<meet_id>")
def meet_event(event, meet_id):
    logger.debug(f"{meet_id} was scanned! Redirecting user to app...")
    return {
        'statusCode': 302,
        'headers': {
            'Location': f"{MEET_REDIRECT_URL}?meet_id={meet_id}",
        },
    }


@lambda_handler.handle("post", path="/meet")
def meet_event(event):
    body = json.loads(event["body"])
    from_phone_id = body.get("from_phone_id")
    encounter_meet_id = body.get("encounter_meet_id")
    if from_phone_id is None or encounter_meet_id is None:
        logger.warning(f"meet/post: bad formatted body, missing from_phone_id or encounter_meet_id: {event['body']}")
        return "Bad request", 400
    try:
        score = MEET_SERVICE.meet_other(body["from_phone_id"], body["encounter_meet_id"])
    except MeetService.UnregisteredPhoneIdException:
        logger.warning(f"meet/post: phone_id: {from_phone_id} does not exist in the database")
        return "Bad request", 400
    except MeetService.UnregisteredMeetIdException:
        logger.warning(f"meet/post: phone_id: {from_phone_id} tried to scan an invalid meet_id: {encounter_meet_id}")
        return "Bad request", 400
    return score.to_json()


@lambda_handler.handle("get", path="/api/generate")
def generate_code(event):
    params = event.get("queryStringParameters") or {}
    count = params.get("count", 1)
    try:
        count = int(count)
    except ValueError:
        logger.warning(f"generate: {count} parameter is not a number")
        return "Bad request", 400
    if count >= MAX_CODE_GENERATION_COUNT or count < 1:
        logger.warning(f"generate: {count} parameter is not in the right range")
        return "Bad request", 400
    logger.debug(f"generate: {count} codes were asked")
    urls = CODE_SERVICE.generate_meet_urls(count)
    return urls


@lambda_handler.handle("post", path="/api/register/new")
def register_name(event):
    request = json.loads(event["body"])
    meet_id = request.get("meet_id")
    username = request.get("username")
    if meet_id is None or username is None:
        logger.warning(f"register/new: bad formatted body, missing phone_id or username: {event['body']}")
        return "Bad request", 400
    try:
        logger.debug(f"register/new: {username} is registering for meet_id: {meet_id}")
        phone_id = USER_SERVICE.register_user(meet_id, username)
        return {"phone_id": phone_id}
    except UserRegistrationService.InvalidMeetIdException as e:
        logger.warning(f"register/new: meet_id: {meet_id} not valid, not registering, reason: {str(e)}")
        return "Bad request", 400


@lambda_handler.handle("post", path="/api/register/update")
def update_name(event):
    request = json.loads(event["body"])
    phone_id = request.get("phone_id")
    username = request.get("username")
    if phone_id is None or username is None:
        logger.warning(f"register/update: bad formatted body, missing phone_id or username: {event['body']}")
        return "Bad request", 400
    try:
        logger.debug(f"register/update: new name: {username} for phone_id: {phone_id}")
        USER_SERVICE.update_user(phone_id, username)
        return
    except UserRegistrationService.PhoneIdNotFoundException:
        logger.warning(f"register/update: error, phone_id does not exist: {phone_id}")
        return "Bad request", 404


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
