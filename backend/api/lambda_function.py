import os
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


@lambda_handler.handle("post", path="/api/register")
def register_name(event):
    pass


@lambda_handler.handle("get", path="/api/all_ranking")
def board_list(event):
    return []


@lambda_handler.handle("get", path="/api/my_ranking")
def user_list(event):
    return []
