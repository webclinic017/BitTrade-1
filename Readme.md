
#### DEV

```
brew install pyenv pipenv
pyenv install 3.7.12
pipenv install
pipenv run ./manage.py migrate

```


#### Deploy

```
apt-get update
apt-get install libpq-dev supervisor redis-server git python3.7 nginx
pythsupervisorctl status
supervisorctl reload
pipenv run fab prod deploy
```
After deploy, you should create local_settings.py in bdd/

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bittrade',
        'USER': 'bdd',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
DingDingUrl = ''
```

The homepage is: http://localhost:8000/coins/
