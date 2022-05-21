import uuid
from lambdarest import lambda_handler

@lambda_handler.handle("get", path="/api")
def author(event):
    return "Powered by TEX Team technology"


def register_name(event):
    pass


def meet_event(event):
    pass


def board_list(event):
    pass


def user_list(event):
    pass



@lambda_handler.handle("get", path="/api/reg")
def my_own(event):
    print(event)
    headers = event["headers"]
    cookies = parse_cookies(headers)
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



def parse_cookies(headers):
    parsed_cookie = {}
    if headers is None:
        return parsed_cookie
    if headers.get('cookie'):
        cookies = headers['cookie'].split(';')
        for cookie in cookies:
            if "=" in cookie:
                parts = cookie.split("=")
                parsed_cookie[parts[0]] = parts[1]
            else:
                parsed_cookie[cookie.strip()] = ''
    else:
        print("No cookie to parse")
    return parsed_cookie