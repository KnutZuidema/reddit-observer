from flask import Flask, render_template
import json
import sqlite3

app = Flask(__name__)


@app.route('/')
def occurrences():
    with open('config.json') as file:
        config = json.load(file)
    keywords = config['parameters']['keywords']
    connection = sqlite3.connect('keywords.db')
    cursor = connection.cursor()
    data = dict()
    for keyword in keywords:
        try:
            cursor.execute(f'select * from keywords where keyword=?',
                           (keyword.lower(),))
            data[keyword] = len(cursor.fetchall())
        except sqlite3.OperationalError:
            continue
    return render_template('index.html', data=data)


if __name__ == '__main__':
    app.run(port=8888, debug=True)
