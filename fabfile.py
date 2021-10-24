from fabric.api import env, run, settings
from fabric.operations import sudo
GIT_REPO = "git@github.com:sharp/BitTrade.git"

def prod():
    env.user = 'root'
    env.hosts = ['xxx.xxx.xxx.xxx']
    env.port = '22'
    env.forward_agent = True
    env.mode = 'production'
    env.branch = 'pro'
    env.source_folder = '/root/bdd_production'
    env.supervisor = 'bdd_production'


def deploy():
    source_folder = env.source_folder
    with settings(warn_only=True):
        if run("test -d %s" % source_folder).failed:
            run("git clone %s %s" % (GIT_REPO, source_folder))
        if run("test -d /var/log/celery").failed:
            run("mkdir /var/log/celery")

    run('cd %s && git fetch && git checkout %s && git pull origin %s' % (source_folder, env.branch, env.branch))
    #sudo('cd %s && pip3 install -r requirements.txt' % source_folder)
    sudo('cd %s && pipenv install' % source_folder)
    sudo("""
        cd {} &&
        MODE={} pipenv run python3.7 manage.py collectstatic --noinput &&
        MODE={} pipenv run python3.7 manage.py migrate
        """.format(source_folder, env.mode, env.mode))
    if env.supervisor:
        sudo("supervisorctl restart %s" % env.supervisor)
    #sudo("supervisorctl restart asgi_daphne")
    #sudo("supervisorctl restart asgi_workers:*")
    sudo("supervisorctl restart celery")
    sudo("supervisorctl restart celerybeat")
