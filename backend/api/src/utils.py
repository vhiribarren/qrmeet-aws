def parse_cookies(headers: dict) -> dict:
    parsed_cookie = {}
    if headers is None:
        return parsed_cookie
    for (key, val) in headers.items():
        if key.lower() == "cookie":
            cookies = val.split(';')
            for cookie in cookies:
                if "=" in cookie:
                    parts = cookie.split("=")
                    parsed_cookie[parts[0]] = parts[1]
                else:
                    parsed_cookie[cookie.strip()] = ''
            break
    else:
        print("No cookie to parse")
    return parsed_cookie
