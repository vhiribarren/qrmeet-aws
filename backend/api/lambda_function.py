import uuid
import utils
from lambdarest import lambda_handler


@lambda_handler.handle("get", path="/api")
def author(event):
    return "Powered by TEX Team technology"


@lambda_handler.handle("get", path="/api/debug")
def echo(event):
    print(event)
    return {"event": str(event)}


@lambda_handler.handle("get", path="/api/meet/<id>")
def meet_event(event):
    print(event)
    headers = event["headers"]
    cookies = utils.parse_cookies(headers)
    print(cookies)
    meet = cookies.get("meet", str(uuid.uuid4()))
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': "text/plain",
             'Set-Cookie': 'meet='+meet+"; Expires=Wed, 21 Oct 2023 07:28:00 GMT",
        },
        'body': meet
    }


@lambda_handler.handle("post", path="/api/register")
def register_name(event):
    pass


@lambda_handler.handle("get", path="/api/ranking")
def board_list(event):
    return []


@lambda_handler.handle("get", path="/api/my_contacts")
def user_list(event):
    return []
