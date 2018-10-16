import json
from datetime import datetime

from flask import Flask, render_template

from database import Mention, SQLSession

app = Flask(__name__)

DAY = 86400


@app.route('/')
def occurrences():
    session = SQLSession(config['database'])
    now = int(datetime.now().timestamp())
    data = dict()
    all_time = session.counts(Mention.keyword)
    today = session.counts_between(Mention.keyword, now - DAY, now)
    yesterday = session.counts_between(Mention.keyword, now - 2 * DAY, now - DAY)
    for keyword in all_time.keys():
        data[keyword] = {
            'all': all_time.get(keyword, 0),
            'day': today.get(keyword, 0),
            'change': today.get(keyword, 0) - yesterday.get(keyword, 0)
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
    upper = int(datetime.now().timestamp())
    lower = upper - DAY
    data = list()
    for _ in range(7):
        data = [session.count_between(Mention.keyword, lower, upper, keyword)] + data
        upper = lower - 1
        lower -= DAY
    submissions = session.get_submissions(keyword)
    commenters = session.get_commenters(keyword)
    session.close()
    return render_template('keyword.html', keyword=keyword, data=data, submissions=submissions,
                           commenters=commenters)


if __name__ == '__main__':
    with open('config.json') as file:
        config = json.load(file)
    app.run(port=8888, debug=True)
