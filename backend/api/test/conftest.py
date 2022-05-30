import os
import sys
from urllib.parse import urlparse, parse_qs
from os.path import abspath, join, dirname

import pytest
import boto3
from moto import mock_dynamodb

sys.path.insert(0, abspath((join(dirname(__file__), '../src'))))

DYNAMO_TABLENAME_CODE = "test-table-code"
DYNAMO_TABLENAME_MEET = "test-table-meet"
DYNAMO_TABLENAME_USER = "test-table-user"

MEET_URL_PREFIX = "https://example.com/meet"


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
    os.environ["MEET_URL_PREFIX"] = MEET_URL_PREFIX


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
def code_service(code_store):
    from uc.code_generation import CodeGeneratorService
    return CodeGeneratorService(MEET_URL_PREFIX, code_store)


@pytest.fixture
def user_service(code_service, user_store):
    from uc.user_registration import UserRegistrationService
    return UserRegistrationService(code_service, user_store, code_store)