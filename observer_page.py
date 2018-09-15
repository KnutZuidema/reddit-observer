from flask import Flask, render_template
import json
from collections import OrderedDict

app = Flask(__name__)


@app.route('/')
def occurrences():
    with open('config.json') as file:
        config = json.load(file)
    data = OrderedDict(
        reversed(sorted(config['occurences'].items(), key=lambda x: x[1])))
    return render_template('index.html', data=data)


if __name__ == '__main__':
    app.run(port=8888, debug=True)
