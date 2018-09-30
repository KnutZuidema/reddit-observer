import json
import logging
import re
from asyncio import sleep, get_event_loop, gather

from praw import Reddit

from database import Mention, get_session

logging.basicConfig(filename='observer.log', level=logging.INFO, filemode='w',
                    format='%(asctime)s:%(levelname)s: %(message)s')


async def observe(subreddit: str):
    while True:
        try:
            for comment in reddit.subreddit(subreddit).stream.comments(pause_after=2):
                if comment is None:
                    await sleep(5)
                    continue
                observe_keywords(comment)
        except Exception as error:
            logging.error(error)


async def save():
    while True:
        session.commit()
        await sleep(config['parameters']['save_interval'])


async def reload_config():
    global config
    while True:
        with open('config.json') as file:
            config = json.load(file)
        await sleep(config['parameters']['config_update_interval'])


def observe_keywords(comment):
    for keyword, synonyms in config['parameters']['keywords'].items():
        if re.search(fr'(^{keyword}\s)|(\s{keyword}\s)|(\s{keyword}\.)', comment.body):
            logging.info(f'Found {keyword} in comment {comment.id}')
            session.add(Mention(keyword=keyword,
                                timestamp=int(comment.created_utc),
                                permalink=comment.permalink,
                                subreddit=comment.subreddit.display_name,
                                commenter=comment.author.name))
            continue
        for synonym in synonyms:
            if re.search(fr'(^{synonym}\s)|(\s{synonym}\s)|(\s{synonym}\.)', comment.body):
                logging.info(f'Found {keyword} by synonym {synonym} in comment {comment.id}')
                session.add(Mention(keyword=keyword,
                                    timestamp=int(comment.created_utc),
                                    permalink=comment.permalink,
                                    subreddit=comment.subreddit.display_name,
                                    commenter=comment.author.name))
                break


if __name__ == '__main__':
    with open('config.json') as file:
        config = json.load(file)
    reddit = Reddit(client_id=config['credentials']['client_id'],
                    client_secret=config['credentials']['client_secret'],
                    user_agent='Reddit Observer v0.1 by SgtBlackScorp')
    session = get_session(config['database'])
    try:
        loop = get_event_loop()
        subreddit_coroutines = [observe(subreddit) for subreddit
                                in config['parameters']['subreddits']]
        loop.run_until_complete(gather(*subreddit_coroutines, save(), reload_config()))
    except KeyboardInterrupt:
        logging.info('Keyboard interrupt, shutting down')
