import json
import time
from collections import defaultdict
import logging
import re

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
depth_submissions = config['parameters']['depth']['submission']
depth_comments = config['parameters']['depth']['comment']
occurrences = defaultdict(int)
occurrences.update(config['occurences'])
cache = config['cache']
iterations = config.get('iterations', 0)


def observe():
    global subreddits, iterations
    iterations += 1
    logging.info(f'Observer iteration {iterations}')
    try:
        for subreddit in subreddits:
            observe_submissions(subreddit)
    except PrawcoreException:
        logging.debug('PRAW exception, waiting 60 seconds')
        time.sleep(60)


def observe_submissions(subreddit):
    global reddit, depth_submissions, depth_comments
    logging.info(f'Observing subreddit {subreddit}')
    for submission in reddit.subreddit(subreddit).new(limit=depth_submissions):
        submission.comment_sort = 'new'
        # noinspection PyBroadException
        try:
            submission.comments.replace_more(limit=depth_comments)
        except:
            logging.debug(f'Failed to get more comments for '
                          f'submission {submission.id}')
        observe_comments(submission)


def observe_comments(submission):
    global cache
    logging.info(f'Observing submission {submission.id}: {submission.title}')
    for comment in submission.comments.list():
        if comment.id not in cache:
            cache.append(comment.id)
        else:
            logging.debug(f'Skipping comment {comment.id}')
            continue
        observe_keywords(comment)


def observe_keywords(comment):
    global keywords, occurrences
    for keyword in keywords:
        keyword = keyword.lower()
        try:
            if re.search(f'(^{keyword} )|( {keyword} )', comment.body):
                logging.info(f'Found {keyword} in comment {comment.id}')
                occurrences[keyword] += 1
        except AttributeError:
            logging.debug(f'Comment {comment.id} doesn\'t have a body')
            break


def save_observations():
    config['occurences'] = occurrences
    config['cache'] = cache
    config['iterations'] = iterations
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=2)


if __name__ == '__main__':
    try:
        while True:
            observe()
            save_observations()
            time.sleep(interval)
    except KeyboardInterrupt:
        logging.info('Keyboard interrupt, shutting down')
        save_observations()
