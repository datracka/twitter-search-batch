from __future__ import print_function
from datetime import datetime
import os
import base64
import twitter
import urllib.request
import json

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
COUNT = 15
KEYWORD = "@nasa"
PLACE = ""
SINCE = "2019-09-15T22:00:00.000Z"
UNTIL = "2019-10-15T21:59:59.999Z"

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
    basic_auth = base64.encodestring(('%s:%s' % (twitter_key, twitter_secret)).encode()).decode().replace('\n', '')

    remaining_count = int(COUNT)
    max_results = 500
    if remaining_count < 500:
        max_results = remaining_count
    values = []
    query = KEYWORD
    if PLACE:
        query = query + ' place:' + PLACE
    # query = query + f'' <- point_radius

    # - since and until date casting
    utc_local_since = datetime.strptime(SINCE, DATE_FORMAT)
    utc_local_until = datetime.strptime(UNTIL, DATE_FORMAT)

    data = {
        'query': query,
        'maxResults': max_results,
        'fromDate': utc_local_since.strftime("%Y%m%d%H%M"),
        'toDate': utc_local_until.strftime("%Y%m%d%H%M"),
    }
    url = os.getenv('TWITTER_SEARCH_URI')
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers={
            'Authorization': "Bearer %s" % get_bearer_token(basic_auth),
            'Content-Type': 'application/json'
        }
    )
    while remaining_count > 0:
        response = urllib.request.urlopen(req)
        values += json.loads(response.read().decode())['results']
        remaining_count -= max_results
        if remaining_count < 500:
            max_results = remaining_count

    print(values)

if __name__ == '__main__':
    main()
