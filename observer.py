import json
import time
from collections import defaultdict
import logging

from praw import Reddit


if __name__ == '__main__':
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
    occurences = defaultdict(int)
    occurences.update(config['occurences'])
    cache = config['cache']
    while True:
        for subreddit in subreddits:
            for submission in reddit.subreddit(subreddit).new(
                    limit=depth_submissions):
                if submission.id not in cache:
                    cache.append(submission.id)
                    submission.comment_sort = 'new'
                    try:
                        submission.comments.replace_more(limit=depth_comments)
                    except:
                        logging.error(f'Cannot get more comments '
                                      f'on submission {submission.id}')
                    for comment in submission.comments.list():
                        for keyword in keywords:
                            try:
                                if keyword in comment.body:
                                    occurences[keyword] += 1
                            except:
                                logging.error(f'Comment {comment.id} in '
                                              f'submission {submission.id} '
                                              f'doesn\'t have a body')
        config['occurences'] = occurences
        config['cache'] = cache
        with open('config.json', 'w') as file:
            json.dump(file, 'config.json')
        time.sleep(interval)
