# reddit-observer

An app for observing Subreddits on Reddit for keywords.
If a keyword is mentioned in a comment, that mention will be saved in a SQLite3 database along with some meta information.

It also comes with a small Flask web-app for displaying found content

### Install

```bash
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
```

### Run

```bash
. venv/bin/activate
python observer.py & python observer_page.py
```
