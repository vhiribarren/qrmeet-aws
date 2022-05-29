import os
import uuid
import utils

from lambdarest import lambda_handler

from uc.code_generation import CodeGeneratorService
from adapter.code_store import DynamoCodeStore

CODE_STORE_TABLE_NAME = os.environ["CODE_STORE_TABLE_NAME"]
MEET_URL_PREFIX = os.environ["MEET_URL_PREFIX"]

CODE_STORE = DynamoCodeStore(CODE_STORE_TABLE_NAME)
CODE_SERVICE = CodeGeneratorService(MEET_URL_PREFIX, CODE_STORE)

MAX_CODE_GENERATION_COUNT = 100


@lambda_handler.handle("get", path="/api")
def author(event):
    return "Powered by TEX Team technology"


@lambda_handler.handle("get", path="/meet/<meet_param>")
def meet_event(event, meet_param):
    params = event.get("queryStringParameters") or {}
    from_param = params.get("from")
    if from_param:
        print(f"{from_param} scanned {meet_param}")
        return {
            'statusCode': 200
        }
    else:
        print(f"Someone scanned {meet_param} but no 'from', redirecting...")
        return {
            'statusCode': 302,
            'headers': {
                'Location': f"{os.environ['MEET_REDIRECT_URL']}?meet={meet_param}",
            },
        }


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


@lambda_handler.handle("post", path="/api/register")
def register_name(event):
    pass


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