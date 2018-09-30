import json
from datetime import datetime
from itertools import zip_longest

from flask import Flask, render_template

from database import Mention, SQLSession

app = Flask(__name__)

DAY = 86400


@app.route('/')
def occurrences():
    session = SQLSession(config['database'])
    now = int(datetime.utcnow().timestamp())
    data = dict()
    all_all_time = session.counts(Mention.keyword)
    all_today = session.counts_between(Mention.keyword, now - DAY, now)
    all_yesterday = session.counts_between(Mention.keyword, now - 2 * DAY, now - DAY)
    for (keyword, all_time), today, yesterday in zip_longest(all_all_time.items(),
                                                             all_today.values(),
                                                             all_yesterday.values(), fillvalue=0):
        data[keyword] = {
            'all': all_time,
            'day': today,
            'change': today - yesterday
        }

    total = {
        'all': sum(keyword['all'] for keyword in data.values()),
        'day': sum(keyword['day'] for keyword in data.values()),
        'change': sum(keyword['change'] for keyword in data.values())
    }
    session.close()
    return render_template('index.html', data=data, total=total)


@app.route('/<keyword>')
def keywords(keyword: str):
    session = SQLSession(config['database'])
    upper = int(datetime.utcnow().timestamp())
    lower = upper - DAY
    data = list()
    for _ in range(7):
        data = [session.count_between(Mention.keyword, lower, upper, keyword)] + data
        upper = lower - 1
        lower -= DAY
    session.close()
    return render_template('keyword.html', keyword=keyword, data=data)


if __name__ == '__main__':
    with open('config.json') as file:
        config = json.load(file)
    app.run(port=8888, debug=True)
