import sys
from os.path import abspath, join, dirname

import pytest
import boto3
from moto import mock_dynamodb

sys.path.insert(0, abspath((join(dirname(__file__), '../src'))))

DYNAMO_TABLENAME_CODE = "test-table-code"


@pytest.fixture
def handler():
    from lambda_function import lambda_handler
    return lambda_handler


@pytest.fixture
def api_get(handler):
    def req(url_path: str):
        event = {
            "httpMethod": "GET",
            "resource": url_path,
        }
        return handler(event=event, context=None)
    return req


@pytest.fixture
def api_post(handler):
    def req(url_path: str, json_payload: str):
        event = {
            "httpMethod": "POST",
            "resource": url_path,
            "body": json_payload,
        }
        return handler(event=event, context=None)
    return req


@pytest.fixture(autouse=False, scope="session")
def mock_boto():
    with mock_dynamodb():
        dynamo = boto3.resource("dynamodb")
        # create table
        yield


@pytest.fixture
def code_store():
    from adapter.code_store import DynamoCodeStore
    return DynamoCodeStore(DYNAMO_TABLENAME_CODE)


@pytest.fixture
def code_service(code_store):
    from uc.code_generation import CodeGeneratorService
    return CodeGeneratorService(code_store)