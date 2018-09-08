import json
import time
from collections import defaultdict
import logging
from prawcore import PrawcoreException

from praw import Reddit

logging.basicConfig(filename='observer.log', level=logging.INFO)

if __name__ == '__main__':
    logging.info('Initializing from config...')
    with open('config.json') as file:
        config = json.load(file)
    logging.info('Success')
    logging.info('Initializing Reddit client...')
    reddit = Reddit(client_id=config['credentials']['client_id'],
                    client_secret=config['credentials']['client_secret'],
                    user_agent='Reddit Observer v0.1 by SgtBlackScorp')
    logging.info('Success')
    subreddits = config['parameters']['subreddits']
    keywords = config['parameters']['keywords']
    interval = config['parameters']['interval']
    depth_submissions = config['parameters']['depth']['submission']
    depth_comments = config['parameters']['depth']['comment']
    occurences = defaultdict(int)
    occurences.update(config['occurences'])
    cache = config['cache']
    iterations = config.get('iterations', 0)
    try:
        while True:
            try:
                iterations += 1
                logging.info(f'Observer iteration {iterations}')
                for subreddit in subreddits:
                    logging.info(f'  Observing subreddit {subreddit}')
                    for submission in reddit.subreddit(subreddit).new(
                            limit=depth_submissions):
                        logging.info(
                            f'    Observing submission "{submission.title}"')
                        submission.comment_sort = 'new'
                        try:
                            submission.comments.replace_more(limit=depth_comments)
                        except:
                            logging.debug(f'  Cannot get more comments '
                                          f'on submission {submission.id}')
                        for comment in submission.comments.list():
                            if comment.id not in cache:
                                cache.append(comment.id)
                                for keyword in keywords:
                                    keyword = keyword.lower()
                                    try:
                                        if re.search(
                                                f'(^{keyword} )|( {keyword} )',
                                                comment.body):
                                            logging.info(
                                                f'      found {keyword} in '
                                                f'comment {comment.id}')
                                            occurences[keyword] += 1
                                    except:
                                        logging.debug(
                                            f'      Comment {comment.id} in '
                                            f'submission {submission.id} '
                                            f'doesn\'t have a body')
                                        break
                            else:
                                logging.debug(
                                    f'      Skipping comment {comment.id} '
                                    f'(exists in cache)')
                config['occurences'] = occurences
                config['cache'] = cache
                config['iterations'] = iterations
                with open('config.json', 'w') as file:
                    json.dump(config, file, indent=2)
                time.sleep(interval)
            except PrawcoreException:
                logging.info(f'PRAW exception... Waiting 60 seconds')
                time.sleep(60)
    except KeyboardInterrupt:
        config['occurences'] = occurences
        config['cache'] = cache
        config['iterations'] = iterations
        with open('config.json', 'w') as file:
            json.dump(config, file, indent=2)
        logging.info('Shutting down')
