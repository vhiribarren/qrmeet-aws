import pytest
import json


API_GENERATE = "/api/generate"


# MAC Code Behavior
###################

def test_generated_meet_id_is_valid(code_service):
    meet_id = code_service._generate_meet_id()
    assert code_service._verify_meet_id(meet_id)


def test_known_working_meet_id_is_valid(code_service):
    """May break if current implementation change, but also fix the current implementation"""
    meet_id = "3uOdP0Z1gQ4z1wV"
    assert code_service._verify_meet_id(meet_id)


def test_modified_meet_id_is_invalid(code_service):
    mut_meet_id = list(code_service._generate_meet_id())
    mut_meet_id[0] = chr(ord(mut_meet_id[0]) + 1)
    new_meet_id = "".join(mut_meet_id)
    assert not code_service._verify_meet_id(new_meet_id)


@pytest.mark.parametrize("meet_id", ["0", "BAD_MEET_ID", "123456789123456789123456789", "4uOdP0Z1gQ4z1wV"])
def test_forged_meet_id_is_invalid(code_service, meet_id):
    assert not code_service._verify_meet_id(meet_id)


# Generator Service
###################

@pytest.mark.parametrize("code_count", [1, 10, 100])
def test_generated_meet_id_with_service_is_referenced_and_valid(code_service, code_store, code_count):
    assert code_store.count_codes() == 0
    result = code_service.generate_meet_urls(code_count)
    assert code_store.count_codes() == code_count
    for url in result:
        meet_id = code_service.meet_id_from_url(url)
        assert code_service.check_meet_id_validity(meet_id)
        assert code_service.check_meet_url_validity(url)
        assert code_store.code_exists(meet_id)


# API
#####

def test_valid_api_qrcode_generation(api_get, code_service, code_store):
    result = api_get(API_GENERATE)
    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert isinstance(body, list)
    assert len(body) == 1
    assert code_store.count_codes() == 1
    assert code_service.check_meet_url_validity(body[0])


@pytest.mark.parametrize("count", [1, 5, 10, 99])
def test_valid_api_qrcode_generation_with_count(api_get, code_service,code_store, count):
    result = api_get(f"{API_GENERATE}?count={count}")
    assert result["statusCode"] == 200
    print(result)
    body = json.loads(result["body"])
    assert isinstance(body, list)
    assert len(body) == count
    for url in body:
        assert code_service.check_meet_url_validity(url)


@pytest.mark.parametrize("count", [100, 10_000])
def test_invalid_api_qrcode_generation_with_excessive_count(api_get, code_store, count):
    result = api_get(f"{API_GENERATE}?count={count}")
    print(result)
    assert result["statusCode"] == 400
    assert code_store.count_codes() == 0


@pytest.mark.parametrize("count", ["foobar", "-1", 0])
def test_invalid_api_qrcode_generation_with_invalid_count(api_get, code_store, count):
    result = api_get(f"{API_GENERATE}?count={count}")
    assert result["statusCode"] == 400
    assert code_store.count_codes() == 0
