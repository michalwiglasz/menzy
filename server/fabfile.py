# -*- coding: utf-8 -*-

from fabric.api import *
from fabric.colors import *
from functools import partial
from platform import system
import time
import re


env.hosts = ['menzy@lugano.michalwiglasz.cz']


# better local
local_run = partial(local, capture=True)

# better warnings
warn = lambda msg: warn(red(msg, bold=True))

# /dev/null
dev_null = 'NUL' if system() == 'Windows' else '/dev/null'


def wait(msg=None, timeout=5):
    """ Allows user to abort operation """
    if msg:
        puts(msg)
    try:
        puts('You have {0} seconds to abort by Ctrl+C.'.format(timeout))
        time.sleep(timeout)
    except KeyboardInterrupt:
        abort('Interrupted.')


class Git(object):
    def __init__(self, local=False):
        super(Git, self).__init__()
        self.do = local_run if local else run

    @property
    def branch(self):
        branches = self.do('git branch --no-color 2>' + dev_null)
        match = re.search(r'\* ([\w\-_]*)', branches)
        if match:
            return match.group(1)
        return None

    @property
    def last_tag(self):
        return self.do('git describe --tags '
                       '`git rev-list --tags --max-count=1`')

    @property
    def last_commit(self):
        return self.do('git rev-parse --verify HEAD')

    @property
    def user(self):
        return self.do('git config --get user.name')

    def tag(self, tag, message):
        self.do('git tag -a "{tag}" -m "{message}"'
                .format(tag=tag, message=message))

    def push(self, branch, tags=False):
        if tags:
            cmd = 'git push --tags origin {0}'
        else:
            cmd = 'git push origin {0}'
        self.do(cmd.format(branch))

    def checkout_branch(self, branch):
        if branch != self.branch:
            self.do('git fetch')
            self.do('git checkout {0}'.format(branch))
        self.do('git reset --hard')

    def pull(self, branch, tags=False):
        if tags:
            cmd = 'git pull --tags origin {0}'
        else:
            cmd = 'git pull origin {0}'
        self.do(cmd.format(branch))


@task
def stop():
    sudo('supervisorctl stop menzy')


@task(alias='start')
def restart():
    sudo('supervisorctl restart menzy')


@task
def deploy():
    local_git = Git(local=True)
    branch = local_git.branch
    puts('\n\nDeploying branch: ' + branch + '\n')
    wait()

    local_git.push(branch)

    execute(stop)
    remote_git = Git(local=False)
    with cd('~/app'):
        remote_git.checkout_branch(branch)
        remote_git.pull(branch)

        prefix = 'source ~/.initenv && workon menzy && '
        run(prefix + 'pip install ./server --upgrade')

    execute(restart)
