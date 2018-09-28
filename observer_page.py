import json
from collections import defaultdict

import sqlalchemy.exc
from flask import Flask, render_template

from database import get_session, Keyword, get_max, count, count_between

app = Flask(__name__)

DAY = 86400


@app.route('/')
def occurrences():
    with open('config.json') as file:
        config = json.load(file)
    keywords = config['parameters']['keywords']
    session = get_session(config['database'])
    data = defaultdict(dict)
    now = get_max(session, Keyword.timestamp)
    yesterday = now - DAY
    yesteryesterday = yesterday - DAY
    send = tuple()
    for keyword in keywords.keys():
        try:
            data[keyword]['all'] = count(session, Keyword.keyword, keyword)
            data[keyword]['day'] = count_between(session, Keyword.keyword,
                                                 yesterday, now, keyword)
            change = data[keyword]['day'] - count_between(session,
                                                          Keyword.keyword,
                                                          yesteryesterday,
                                                          yesterday, keyword)
            data[keyword]['change'] = change
            send = sorted(data.items(), key=lambda item: item[1]['day'],
                          reverse=True)
        except sqlalchemy.exc.OperationalError:
            continue
    total = {
        'all': count(session, Keyword),
        'day': count_between(session, Keyword, yesterday, now)
    }
    total['change'] = total['day'] - count_between(session, Keyword,
                                                   yesteryesterday, yesterday)
    return render_template('index.html', data=send, total=total)


@app.route('/<keyword>')
def keywords(keyword: str):
    with open('config.json') as file:
        config = json.load(file)
    session = get_session(config['database'])
    upper = get_max(session, Keyword.timestamp)
    lower = upper - DAY
    data = list()
    for _ in range(7):
        data = [count_between(session, Keyword.keyword, lower, upper, keyword)] + data
        upper = lower - 1
        lower -= DAY
    return render_template('keyword.html', keyword=keyword, data=data)


if __name__ == '__main__':
    app.run(port=8888, debug=True)
