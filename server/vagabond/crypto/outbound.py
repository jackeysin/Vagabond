from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime

from base64 import b64encode

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from vagabond.__main__ import VERSION
from vagabond.config import config

import requests

import json

def get_http_datetime():
    now = datetime.now()
    stamp = mktime(now.timetuple())
    return format_date_time(stamp)



def generate_signing_string(host, request_target, method, body, date, content_type):
    method = method.lower()
    digest = b64encode(SHA256.new(bytes(body, 'utf-8')).digest()).decode('utf-8')
    # Single line used to make sure UNIX v.s. NT line endings don't cause any problems.
    return f'(request-target): {method} {request_target}\nhost: {host}\ndate: {date}\ndigest: SHA-256={digest}\ncontent-type: {content_type}'



def signed_request(host, request_target, body, actor, method='POST', content_type='application/activity+json'):

    if method != 'POST':
        raise Exception(f'Only valid HTTP method for signed_request function is POST. \'{method}\' provided.')

    date = get_http_datetime()

    if type(body) is dict:
        body = json.dumps(body)

    signing_string = generate_signing_string(host, request_target, method, body, date, content_type)

    private_key = RSA.importKey(actor.private_key)
    pkcs = pkcs1_15.new(private_key)
    
    sha256_body = SHA256.new(bytes(body, 'utf-8'))
    digest_body = sha256_body.digest()
    b64_digest_body = b64encode(digest_body).decode('utf-8')


    sha256_signing_string = SHA256.new(bytes(signing_string, 'utf-8'))
    b64_sha256_signing_string = b64encode(pkcs.sign(sha256_signing_string)).decode('utf-8')

    api_url = config['api_url']

    headers = {
        'user-agent': f'Vagabond/{VERSION}',
        'host': config['domain'],
        'date': date,
        'digest': f'SHA-256={b64_digest_body}',
        'content-type': content_type,
        'signature': f'keyId="{api_url}/actors/{actor.username}#main-key",algorithm="rsa-sha256",headers="(request-target) host date digest content-type",signature="{b64_sha256_signing_string}"'
    }

    return requests.post(url='https://' + host + request_target, headers=headers, data=body)
