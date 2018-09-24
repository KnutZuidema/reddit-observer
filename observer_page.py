import json
import sqlite3
from collections import defaultdict

from flask import Flask, render_template

app = Flask(__name__)

DAY = 86400


def max_timestamp(cursor: sqlite3.Cursor):
    cursor.execute('select max(timestamp) from keywords')
    return cursor.fetchone()[0]


def count_between(cursor: sqlite3.Cursor, keyword, lower: int = 0,
                  upper: int = None):
    upper = upper or max_timestamp(cursor)
    cursor.execute(f'select count(*) from keywords where '
                   f'(keyword=?  collate nocase) '
                   f'and timestamp between {lower} and {upper}',
                   (keyword,))
    return cursor.fetchone()[0]


@app.route('/')
def occurrences():
    with open('config.json') as file:
        config = json.load(file)
    keywords = config['parameters']['keywords']
    connection = sqlite3.connect('keywords.db')
    cursor = connection.cursor()
    data = defaultdict(dict)
    now = max_timestamp(cursor)
    yesterday = now - DAY
    yesteryesterday = yesterday - DAY
    send = tuple()
    for keyword in keywords.keys():
        try:
            data[keyword]['all'] = count_between(cursor, keyword)
            data[keyword]['day'] = count_between(cursor, keyword,
                                                 yesterday, now)
            change = data[keyword]['day'] - count_between(cursor, keyword,
                                                          yesteryesterday,
                                                          yesterday)
            data[keyword]['change'] = change
            send = sorted(data.items(), key=lambda item: item[1]['day'],
                          reverse=True)
        except sqlite3.OperationalError:
            continue
    connection.close()
    total = {
        'all': sum(keyword['all'] for keyword in data.values()),
        'day': sum(keyword['day'] for keyword in data.values()),
        'change': sum(keyword['change'] for keyword in data.values())
    }
    return render_template('index.html', data=send, total=total)


@app.route('/<keyword>')
def keywords(keyword: str):
    connection = sqlite3.connect('keywords.db')
    cursor = connection.cursor()
    upper = max_timestamp(cursor)
    lower = upper - DAY
    data = list()
    for _ in range(7):
        data = [count_between(cursor, keyword, lower, upper)] + data
        upper = lower - 1
        lower -= DAY
    connection.close()
    return render_template('keyword.html', keyword=keyword, data=data)


if __name__ == '__main__':
    app.run(port=8888, debug=True)
