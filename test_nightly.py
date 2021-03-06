import doctest
import os
import json
import re
import sys
import time
from datetime import datetime, timedelta

import requests
import lxml.html


def log(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()


def get_twitter_time_offset():
    # example: '2017-11-25 10:58'
    san_francisco_coords = (37.733795, -122.446747)
    response = requests.get('http://api.geonames.org/timezoneJSON', params={
        'lat': san_francisco_coords[0],
        'lng': san_francisco_coords[1],
        'username': 'honzajavorek'
    })
    san_francisco_time = json.loads(response.content).get('time')
    dt = datetime.strptime(san_francisco_time, '%Y-%m-%d %H:%M')
    return timedelta(hours=dt.hour - datetime.now().hour)


def parse_dt(tweet_timestamp):
    # example: '1:24 PM - 20 Sep 2017'

    # Fix hour & month zero-padding
    tweet_timestamp = re.sub(r'^(\d):', r'0\1:', tweet_timestamp)
    tweet_timestamp = re.sub(r'\- (\d) ', r'- 0\1 ', tweet_timestamp)

    return datetime.strptime(tweet_timestamp, '%I:%M %p - %d %b %Y')


def read_tweets():
    response = requests.get('https://twitter.com/schedule_tw')
    html = lxml.html.fromstring(response.content)

    for tweet in html.cssselect('.stream .tweet'):
        tweet_text = tweet.cssselect('.tweet-text')[0].text_content()
        tweet_timestamp = tweet.cssselect('.tweet-timestamp')[0]
        tweet_timestamp_dt = parse_dt(tweet_timestamp.get('title'))
        yield (tweet_text, tweet_timestamp_dt)


if __name__ == '__main__':
    assert 'PASSWORD' in os.environ, (
        'The PASSWORD environment variable needs to be set'
    )

    # The time Twitter renders to their static HTML is in SF timezone
    log('Getting Twitter time')
    twitter_td = get_twitter_time_offset()

    before_test_dt = datetime.now() + twitter_td
    log(f'About to run the code example from README, '
        f'{before_test_dt.isoformat()} (Twitter time)')
    doctest.testfile('README.rst')
    log(f'The code example has been executed, waiting 4 minutes')
    for i in range(4):
        time.sleep(60)
        log(f'Minute #{i + 1} elapsed')
    after_test_dt = datetime.now() + twitter_td
    log(f'About to do assertions, {after_test_dt.isoformat()} (Twitter time)')

    tweets = read_tweets()
    tweet2 = next(tweets)
    tweet1 = next(tweets)

    log("The tweet #1 starts with 'First Tweet'")
    assert tweet1[0].startswith('First Tweet')
    log("The tweet #1 is within the expected time range")
    assert before_test_dt < tweet1[1] < after_test_dt

    log("The tweet #2 starts with 'Second Tweet'")
    assert tweet2[0].startswith('Second Tweet')
    log("The tweet #1 is within the expected time range")
    assert before_test_dt < tweet2[1] < after_test_dt

    log('The time difference between last two tweets is not more than 1 min')
    assert int((tweet2[1] - tweet1[1]).seconds / 60) <= 1

    log('Done!')
