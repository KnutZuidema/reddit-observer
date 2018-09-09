from flask import Flask, jsonify
import json


app = Flask(__name__)


@app.route('/occurrences')
def occurrences():
    with open('config.json') as file:
        config = json.load(file)
    return jsonify(config['occurrences'])


if __name__ == '__main__':
    app.run('0.0.0.0', 8888)
