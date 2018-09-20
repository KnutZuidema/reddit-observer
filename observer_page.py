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
    # 86400 == 24h in seconds
    yesterday = time.time() - 86400
    send = tuple()
    for keyword in keywords:
        try:
            cursor.execute('select * from keywords where keyword=?',
                           (keyword.lower(),))
            data[keyword]['all'] = len(cursor.fetchall())
            cursor.execute(f'select * from keywords where keyword=? '
                           f'and timestamp > {yesterday}',
                           (keyword.lower(),))
            data[keyword]['day'] = len(cursor.fetchall())
            pprint(data.items())
            send = sorted(data.items(), key=lambda item: item[1]['day'],
                          reverse=True)
        except sqlite3.OperationalError:
            continue
    return render_template('index.html', data=send)


if __name__ == '__main__':
    app.run(port=8888, debug=True)
