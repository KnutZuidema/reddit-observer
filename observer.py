import json
import time
from collections import defaultdict
import logging
import re
from asyncio import sleep, get_event_loop, gather

from praw import Reddit
from prawcore import PrawcoreException

logging.basicConfig(filename='observer.log', level=logging.INFO, filemode='w',
                    format='%(asctime)s:%(levelname)s: %(message)s')

with open('config.json') as file:
    config = json.load(file)
reddit = Reddit(client_id=config['credentials']['client_id'],
                client_secret=config['credentials']['client_secret'],
                user_agent='Reddit Observer v0.1 by SgtBlackScorp')
subreddits = config['parameters']['subreddits']
keywords = config['parameters']['keywords']
interval = config['parameters']['interval']
cache = config.get('cache', [])
comments_observed = config.get('comments_observed', 0)
occurrences = defaultdict(int)
occurrences.update(config['occurences'])


async def observe(subreddit: str):
    global comments_observed
    while True:
        for comment in reddit.subreddit(subreddit).stream.comments(
                pause_after=2):
            if comment is None:
                print('waiting')
                await sleep(5)
                continue
            comments_observed += 1
            observe_keywords(comment)
            print(f'observing {comment.id}')


async def save_every(seconds):
    while True:
        config['occurences'] = occurrences
        config['comments_observed'] = comments_observed
        with open('config.json', 'w') as config_file:
            json.dump(config, config_file, indent=2)
        await sleep(seconds)


def observe_keywords(comment):
    for keyword in keywords:
        keyword = keyword.lower()
        try:
            if re.search(f'(^{keyword} )|( {keyword} )', comment.body):
                logging.info(f'Found {keyword} in comment {comment.id}')
                occurrences[keyword] += 1
        except AttributeError:
            logging.debug(f'Comment {comment.id} doesn\'t have a body')
            break


if __name__ == '__main__':
    try:
        loop = get_event_loop()
        subreddit_coroutines = [observe(subreddit) for subreddit in subreddits]
        loop.run_until_complete(
            gather(*subreddit_coroutines, save_every(interval)))
    except KeyboardInterrupt:
        logging.info('Keyboard interrupt, shutting down')
