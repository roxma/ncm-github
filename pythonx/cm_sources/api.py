import os
from urllib.request import Request

token = os.getenv('GITHUB_TOKEN')

def create_request(url):
    req = url

    if token:
        req = Request(url, headers={'Authorization': 'token %s' % token})

    return req
