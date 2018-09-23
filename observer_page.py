import json
import sqlite3
import time
from collections import defaultdict

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def occurrences():
    with open('config.json') as file:
        config = json.load(file)
    keywords = config['parameters']['keywords']
    connection = sqlite3.connect('keywords.db')
    cursor = connection.cursor()
    data = defaultdict(dict)
    day = 86400
    yesterday = time.time() - day
    yesteryesterday = yesterday - day
    send = tuple()
    for keyword in keywords.keys():
        try:
            cursor.execute('select count(*) from keywords '
                           'where keyword=? collate nocase',
                           (keyword,))
            data[keyword]['all'] = cursor.fetchone()[0]
            cursor.execute(f'select count(*) from keywords where '
                           f'(keyword=?  collate nocase) '
                           f'and timestamp > {yesterday}',
                           (keyword,))
            data[keyword]['day'] = cursor.fetchone()[0]
            cursor.execute(f'select count(*) from keywords '
                           f'where (keyword=?  collate nocase) '
                           f'and timestamp between {yesteryesterday} '
                           f'and {yesterday}',
                           (keyword,))
            change = data[keyword]['day'] - cursor.fetchone()[0]
            data[keyword]['change'] = change
            send = sorted(data.items(), key=lambda item: item[1]['day'],
                          reverse=True)
        except sqlite3.OperationalError:
            continue
    total = {
        'all': sum(keyword['all'] for keyword in data.values()),
        'day': sum(keyword['day'] for keyword in data.values()),
        'change': sum(keyword['change'] for keyword in data.values())
    }
    return render_template('index.html', data=send, total=total)


# @app.route('/create')
# def create():


if __name__ == '__main__':
    app.run(port=8888, debug=True)
