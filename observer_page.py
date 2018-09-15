from flask import Flask, render_template
import json


app = Flask(__name__)


@app.route('/occurrences')
def occurrences():
    with open('config.json') as file:
        config = json.load(file)
    return render_template('index.html', data=config['occurrences'])


if __name__ == '__main__':
    app.run(port=8888)
