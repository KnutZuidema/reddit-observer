# reddit-observer

An app for observing Subreddits on Reddit for keywords.
If a keyword is mentioned in a comment, that mention will be saved to a SQLite3 database alongside some meta information.

It also comes with a small Flask web-app for displaying found content  
See http://observer.knutzuidema.de for an example

## Install

```bash
git clone https://github.com/KnutZuidema/reddit-observer
cd reddit-observer
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
```

## Configure

Copy the `example.config.json` and rename it to `config.json`
Then configure your application as outlined below.

### Credentials
You will have to acquire a client ID and a client secret for the Reddit API.  
Go to https://www.reddit.com/prefs/apps and create a new app or use a previously created one.

##### client_id
Your client ID

##### client_secret
Your client secret

### Parameters
##### subreddits
List of subreddits by their name (without `/r/` in front) that should be observed.

##### keywords
List of keywords that should yield a match. These are matched only if they are a separate word in the comment but are not case-sensitive.

##### save_interval
Time in seconds that should pass between each commit to the database.

##### config_update_interval
Time in seconds that should pass between each reload of the config file.  
Updates will only take effect after the config file was reloaded.

## Run
```bash
. venv/bin/activate
python observer.py & python observer_page.py
```
