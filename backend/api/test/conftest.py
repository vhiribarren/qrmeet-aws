import os
import sys
from urllib.parse import urlparse, parse_qs
from os.path import abspath, join, dirname
from dataclasses import dataclass

import pytest
import boto3
from moto import mock_dynamodb

sys.path.insert(0, abspath((join(dirname(__file__), '../src'))))

DYNAMO_TABLENAME_CODE = "test-table-code"
DYNAMO_TABLENAME_USER = "test-table-user"
DYNAMO_TABLENAME_MEET = DYNAMO_TABLENAME_USER
DYNAMO_TABLENAME_RANK = "test-table-ranking"

MEET_URL_PREFIX = "https://example.com/meet"
MEET_REDIRECT_URL = "https://example.com/"

@pytest.fixture
def handler():
    from lambda_function import lambda_handler
    return lambda_handler


def _handler_request(handler, http_method: str, url_path: str, body: str = None):
    parsed_url_path = urlparse(url_path)
    query = parse_qs(parsed_url_path.query)
    query = {k: v[0] for k, v in query.items()}
    event = {
        "httpMethod": http_method,
        "resource": parsed_url_path.path,
        "queryStringParameters": query,
        "body": body,
    }
    return handler(event=event, context=None)


@pytest.fixture
def api_get(handler):
    return lambda url_path: _handler_request(handler, "GET", url_path)


@pytest.fixture
def api_post(handler):
    return lambda url_path, body: _handler_request(handler, "POST", url_path, body)


@pytest.fixture(scope="session", autouse=True)
def init_aws_env_var():
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"


@pytest.fixture(scope="session", autouse=True)
def init_lambda_env_var():
    os.environ["CODE_STORE_TABLE_NAME"] = DYNAMO_TABLENAME_CODE
    os.environ["USER_STORE_TABLE_NAME"] = DYNAMO_TABLENAME_USER
    os.environ["RANK_STORE_TABLE_NAME"] = DYNAMO_TABLENAME_RANK
    os.environ["MEET_URL_PREFIX"] = MEET_URL_PREFIX
    os.environ["MEET_REDIRECT_URL"] = MEET_REDIRECT_URL


@pytest.fixture(autouse=True)
def mock_boto():
    with mock_dynamodb():
        dynamo = boto3.resource("dynamodb")
        dynamo.create_table(
            TableName=DYNAMO_TABLENAME_CODE,
            BillingMode="PAY_PER_REQUEST",
            KeySchema=[{
                "AttributeName": "meet_id",
                "KeyType": "HASH"
            }],
            AttributeDefinitions=[{
                "AttributeName": "meet_id",
                "AttributeType": "S"
            }]
        )
        dynamo.create_table(
            TableName=DYNAMO_TABLENAME_USER,
            BillingMode="PAY_PER_REQUEST",
            KeySchema=[{
                "AttributeName": "phone_id",
                "KeyType": "HASH"
            }],
            AttributeDefinitions=[{
                "AttributeName": "phone_id",
                "AttributeType": "S"
            }
            ])
        yield


@pytest.fixture
def code_store():
    from adapter.code_store import DynamoCodeStore
    return DynamoCodeStore(DYNAMO_TABLENAME_CODE)


@pytest.fixture
def user_store():
    from adapter.user_store import DynamoUserStore
    return DynamoUserStore(DYNAMO_TABLENAME_USER)


@pytest.fixture
def meet_store():
    from adapter.meet_store import DynamoMeetStore
    return DynamoMeetStore(DYNAMO_TABLENAME_MEET)


@pytest.fixture
def ranking_store():
    from adapter.ranking_store import DynamoRankingStore
    return DynamoRankingStore(DYNAMO_TABLENAME_RANK)


@pytest.fixture
def code_service(code_store):
    from uc.code_generation import CodeGeneratorService
    return CodeGeneratorService(MEET_URL_PREFIX, code_store)


@pytest.fixture
def user_service(code_service, user_store, code_store):
    from uc.user_registration import UserRegistrationService
    return UserRegistrationService(code_service, user_store, code_store)


@pytest.fixture
def meet_service(code_service, user_service, meet_store, ranking_store):
    from uc.meet_event import MeetService
    return MeetService(code_service, user_service, meet_store, ranking_store)


@dataclass
class User:
    phone_id: str
    meet_id: str
    username: str


@pytest.fixture
def new_user(user_service, code_service):
    def generate_user(username):
        meet_id = code_service.meet_id_from_url(code_service.generate_meet_urls()[0])
        phone_id = user_service.register_user(meet_id, username)
        return User(phone_id=phone_id, meet_id=meet_id, username=username)
    return generate_user