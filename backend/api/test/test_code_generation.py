import pytest


API_GENERATE = "/api/generate"


# MAC Code Behavior
###################

def test_valid_generated_meet_id(code_service):
    meet_id = code_service._generate_meet_id()
    assert code_service._verify_meet_id(meet_id)


def test_invalid_modified_meet_id(code_service):
    mut_meet_id = list(code_service._generate_meet_id())
    mut_meet_id[0] += 1
    new_meet_id = "".join(mut_meet_id)
    assert not code_service._verify_meet_id(new_meet_id)


def test_invalid_forged_meet_id(code_service):
    meet_id = "BAD_MEET_ID"
    assert not code_service._verify_meet_id(meet_id)


# Generator Service
###################

def test_valid_generate_and_check(code_service, code_store):
    code_count = 10
    assert code_store.count_codes() == 0
    result = code_service.generate_meet_urls(code_count)
    assert code_store.count_codes() == code_count
    for url in result:
        meet_id = code_service.meet_id_from_url(url)
        assert code_service.check_meet_url_validity(url)
        assert code_service.check_meet_id_validity(meet_id)
        assert code_store.code_exists(meet_id)


# API
#####

def test_valid_api_qrcode_generation(api_get, code_service, code_store):
    result = api_get(API_GENERATE)
    body = result["body"]
    assert result["statusCode"] == 200
    assert isinstance(body, list)
    assert len(body) == 1
    assert code_store.count_codes() == 1
    assert code_service.check_meet_url_validity(body[0])


@pytest.mark.parametrize("count", [1, 5, 10, 99])
def test_valid_api_qrcode_generation_with_count(api_get, code_service,code_store, count):
    result = api_get(f"{API_GENERATE}?count={count}")
    body = result["body"]
    assert result["statusCode"] == 200
    assert isinstance(body, list)
    assert len(body) == count
    for url in body:
        assert code_service.check_meet_url_validity(url)


@pytest.mark.parametrize("count", [100, 10_000])
def test_invalid_api_qrcode_generation_with_excessive_count(api_get, code_store, count):
    result = api_get(f"{API_GENERATE}?count={count}")
    assert result["statusCode"] == 400
    assert not result["body"]
    assert code_store.count_codes() == 0


@pytest.mark.parametrize("count", ["foobar"])
def test_invalid_api_qrcode_generation_with_invalid_count(api_get, code_store, count):
    result = api_get(f"{API_GENERATE}?count={count}")
    assert result["statusCode"] == 400
    assert not result["body"]
    assert code_store.count_codes() == 0
