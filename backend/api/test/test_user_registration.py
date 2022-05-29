import pytest
import json


API_REGISTRATION_NEW = "/api/register/new"
API_REGISTRATION_UPDATE = "/api/register/update"


def test_api_unused_and_valid_meet_id_registration_is_valid(api_post, code_service):
    meet_id = code_service.meet_id_from_url(code_service.generate_meet_urls()[0])
    registration_msg = {
        "meet_id": meet_id,
        "username": "Vincent H."
    }
    result = api_post(API_REGISTRATION_NEW, json.dumps(registration_msg))
    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert "phone_id" in body


def test_api_registration_without_name_is_invalid(api_post, code_service):
    meet_id = code_service.meet_id_from_url(code_service.generate_meet_urls()[0])
    registration_msg = {
        "meet_id": meet_id
    }
    result = api_post(API_REGISTRATION_NEW, json.dumps(registration_msg))
    assert result["statusCode"] == 400


def test_api_unused_and_invalid_meet_id_registration_is_invalid(api_post):
    meet_id = "3uOdP0Z1gQ4z1wV"
    registration_msg = {
        "meet_id": meet_id,
        "username": "Vincent H."
    }
    result = api_post(API_REGISTRATION_NEW, json.dumps(registration_msg))
    assert result["statusCode"] == 400


def test_api_already_registered_meet_id_is_invalid(api_post, code_service):
    meet_id = code_service.meet_id_from_url(code_service.generate_meet_urls()[0])
    registration_msg = {
        "meet_id": meet_id,
        "username": "Vincent H."
    }
    result = api_post(API_REGISTRATION_NEW, json.dumps(registration_msg))
    assert result["statusCode"] == 200
    result = api_post(API_REGISTRATION_NEW, json.dumps(registration_msg))
    assert result["statusCode"] == 400


def test_api_update_name_with_valid_user_id_is_valid(api_post, code_service):
    meet_id = code_service.meet_id_from_url(code_service.generate_meet_urls()[0])
    registration_msg = {
        "meet_id": meet_id,
        "username": "Vincent H."
    }
    result = api_post(API_REGISTRATION_NEW, json.dumps(registration_msg))
    assert result["statusCode"] == 200
    result_body = json.loads(result["body"])
    phone_id = result_body["phone_id"]
    update_msg = {
        "phone_id": phone_id,
        "username": "SuperChat"
    }
    result = api_post(API_REGISTRATION_UPDATE, json.dumps(update_msg))
    assert result["statusCode"] == 200


def test_api_update_name_with_unknown_user_id_is_invalid(api_post, user_service):
    update_msg = {
        "phone_id": "phone_id",
        "username": "SuperChat"
    }
    result = api_post(API_REGISTRATION_UPDATE, json.dumps(update_msg))
    assert result["statusCode"] == 404
