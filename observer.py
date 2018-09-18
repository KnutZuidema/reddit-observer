import json
from collections import defaultdict
import logging
import re
from asyncio import sleep, get_event_loop, gather
import sqlite3

from praw import Reddit

logging.basicConfig(filename='observer.log', level=logging.INFO, filemode='w',
                    format='%(asctime)s:%(levelname)s: %(message)s')

with open('config.json') as file:
    config = json.load(file)
reddit = Reddit(client_id=config['credentials']['client_id'],
                client_secret=config['credentials']['client_secret'],
                user_agent='Reddit Observer v0.1 by SgtBlackScorp')
subreddits = config['parameters']['subreddits']
keywords = config['parameters']['keywords']
mentions = defaultdict(list)


def create_database():
    connection = sqlite3.connect('keywords.db')
    cursor = connection.cursor()
    cursor.execute('create table if not exists keywords('
                   'id integer primary key autoincrement,'
                   'keyword text,'
                   'timestamp integer,'
                   'permalink text,'
                   'subreddit text,'
                   'commenter text)')
    connection.commit()
    connection.close()


async def observe(subreddit: str):
    while True:
        for comment in reddit.subreddit(subreddit).stream.comments(
                pause_after=2):
            if comment is None:
                print('waiting')
                await sleep(5)
                continue
            observe_keywords(comment)
            print(f'observing {comment.id}')


async def save():
    while True:
        connection = sqlite3.connect('keywords.db')
        cursor = connection.cursor()
        for keyword, data in mentions.items():
            cursor.execute('insert into keywords values (?, ?, ?, ?, ?)',
                           (keyword, data['timestamp'], data['permalink'],
                            data['subreddit'], data['commenter']))
        connection.commit()
        connection.close()
        await sleep(config['parameters']['save_interval'])


def observe_keywords(comment):
    for keyword in keywords:
        keyword = keyword.lower()
        try:
            if re.search(f'(^{keyword} )|( {keyword} )', comment.body):
                logging.info(f'Found {keyword} in comment {comment.id}')
                mentions[keyword] += [{
                    'timestamp': comment.created,
                    'permalink': comment.permalink,
                    'subreddit': comment.subreddit.display_name,
                    'commenter': comment.author.name
                }]
        except AttributeError:
            logging.debug(f'Comment {comment.id} doesn\'t have a body')
            break


if __name__ == '__main__':
    create_database()
    try:
        loop = get_event_loop()
        subreddit_coroutines = [observe(subreddit) for subreddit in subreddits]
        loop.run_until_complete(
            gather(*subreddit_coroutines, save()))
    except KeyboardInterrupt:
        logging.info('Keyboard interrupt, shutting down')
