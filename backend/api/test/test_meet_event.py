import json

from urllib.parse import urlparse, parse_qs


API_MEET = "/meet"


def test_api_meet_with_get_method_must_be_redirected(api_get):
    meet_id = "anything"
    result = api_get(f"{API_MEET}/{meet_id}")
    assert result["statusCode"] == 302
    location_url = result["headers"]["Location"]
    parsed_location_url = urlparse(location_url)
    parsed_query = parse_qs(parsed_location_url.query)
    assert parsed_location_url.path == "/"
    assert meet_id == parsed_query["meet_id"][0]


def test_api_meet_post_event_with_registered_phone_and_meet_id_valid(api_post, new_user, meet_store):
    user_1 = new_user("user1")
    user_2 = new_user("user2")
    assert not meet_store.check_if_already_met(user_1.phone_id, user_2.meet_id)
    meet_event = {
        "meet_id": user_2.meet_id,
        "phone_id": user_1.phone_id,
    }
    result = api_post("API_MEET", json.dumps(meet_event))
    assert result["statusCode"] == 200
    assert not meet_store.check_if_already_met(user_1.phone_id, user_2.meet_id)


def test_api_meet_post_event_without_registered_phone_id_is_invalid(api_post, new_user):
    user_1 = new_user("user1")
    meet_event = {
        "meet_id": user_1.meet_id,
        "phone_id": "any-phone-id",
    }
    result = api_post("API_MEET", json.dumps(meet_event))
    assert result["statusCode"] == 400


def test_api_meet_post_event_without_registered_meet_id_is_invalid(api_post, new_user):
    user_1 = new_user("user1")
    meet_event = {
        "meet_id": user_1.meet_id,
        "phone_id": "any-meet-id",
    }
    result = api_post("API_MEET", json.dumps(meet_event))
    assert result["statusCode"] == 400


def test_api_meet_post_event_already_done_is_invalid(api_post, new_user):
    user_1 = new_user("user1")
    user_2 = new_user("user2")
    meet_event = {
        "meet_id": user_2.meet_id,
        "phone_id": user_1.phone_id,
    }
    result = api_post("API_MEET", json.dumps(meet_event))
    assert result["statusCode"] == 200
    result = api_post("API_MEET", json.dumps(meet_event))
    assert result["statusCode"] == 400


def test_api_double_meet_event_must_increase_overall_score():
    assert False


def test_api_after_meet_score_is_returned():
    assert False
