from __future__ import print_function
from datetime import datetime
import os
import base64
import twitter
import urllib.request
import json

# IF SCRIPT DOES NOT WORK PROBABLY DATE RANGE ARE NOT LONGER SUPPORTED (THEY ARE STALED)
# TO FIX IT JUST SET A PROPER DATE RATE (MAX LAST 30 DAYS)
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
COUNT = 500
KEYWORD = "@playstation"
PLACE = ""
SINCE = "2019-10-17T13:58:00.000Z"
UNTIL = "2019-10-17T23:59:59.999Z"


def request_data(url, payload, headers):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers=headers
    )
    response = urllib.request.urlopen(req)
    return response


def get_bearer_token(basic_auth):
    url = 'https://api.twitter.com/oauth2/token'
    req = urllib.request.Request(
        url,
        data=str('grant_type=client_credentials').encode(),
        headers={
            'Authorization': "Basic %s" % basic_auth
        }
    )
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode())['access_token']


def main():
    twitter_key = os.getenv('TWITTER_CONSUMER_KEY')
    twitter_secret = os.getenv('TWITTER_CONSUMER_SECRET')
    api = twitter.Api(consumer_key=twitter_key,
                      consumer_secret=twitter_secret,
                      access_token_key=os.getenv(
                          'TWITTER_ACCESS_TOKEN_KEY'),
                      access_token_secret=os.getenv(
                          'TWITTER_ACCESS_TOKEN_KEY'))
    api.sleep_on_rate_limit = False
    basic_auth = base64.encodebytes(
        ('%s:%s' % (twitter_key, twitter_secret)).encode()).decode().replace('\n', '')

    query = KEYWORD

    utc_local_since = datetime.strptime(SINCE, DATE_FORMAT)
    utc_local_until = datetime.strptime(UNTIL, DATE_FORMAT)

    # create parameters for search
    initialPayload = {
        'query': query,
        'maxResults': COUNT,
        'fromDate': utc_local_since.strftime("%Y%m%d%H%M"),
        'toDate': utc_local_until.strftime("%Y%m%d%H%M"),
    }
    headers = {
        'Authorization': "Bearer %s" % get_bearer_token(basic_auth),
        'Content-Type': 'application/json'
    }
    url = os.getenv('TWITTER_SEARCH_URI')

    tweets = []
    try:
        print('### request batch started ###')
        response = json.loads(request_data(
            url, initialPayload, headers).read().decode())
        tweets += response['results']
        if 'next' in response:
            while 'next' in response:
                token = response['next']
                print('# doing extra request with token ', token)
                payload = {
                    'query': query,
                    'maxResults': COUNT,
                    'next': token,
                    'fromDate': utc_local_since.strftime("%Y%m%d%H%M"),
                    'toDate': utc_local_until.strftime("%Y%m%d%H%M"),
                }
                response = json.loads(request_data(
                    url, payload, headers).read().decode())
                tweets += response['results']
                print('current number of tweets retrieved', len(tweets))
        print('### request batch ended ### ')
    except urllib.error.HTTPError as error:
        print('error', error)

    print('number of tweets retrieved: ', len(tweets))


if __name__ == '__main__':
    main()
