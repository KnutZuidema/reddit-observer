from flask import Flask, render_template
import json
import sqlite3
from collections import defaultdict
import time
from pprint import pprint

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
    for keyword in keywords:
        try:
            cursor.execute('select count(*) from keywords where keyword=?',
                           (keyword.lower(),))
            data[keyword]['all'] = cursor.fetchone()[0]
            cursor.execute(f'select count(*) from keywords where keyword=? '
                           f'and timestamp > {yesterday}',
                           (keyword.lower(),))
            data[keyword]['day'] = cursor.fetchone()[0]
            cursor.execute(f'select count(*) from keywords where keyword=? '
                           f'and timestamp between {yesteryesterday} '
                           f'and {yesterday}',
                           (keyword.lower(),))
            change = data[keyword]['day'] - cursor.fetchone()[0]
            data[keyword]['change'] = change
            send = sorted(data.items(), key=lambda item: item[1]['day'],
                          reverse=True)
        except sqlite3.OperationalError:
            continue
    return render_template('index.html', data=send)


# @app.route('/create')
# def create():


if __name__ == '__main__':
    app.run(port=8888, debug=True)
