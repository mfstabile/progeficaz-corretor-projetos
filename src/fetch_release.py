from git import Repo, Git
import sys
import os
import shutil
import re
import json

CLONE_BASE_PATH = os.environ.get('CLONE_BASE_PATH')
GIT_BASE_URL = os.environ.get('GIT_BASE_URL')
GIT_SSH_KEY_FILE = os.environ.get('GIT_SSH_KEY_FILE')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

# get ssh key
git_ssh_identity_file = os.path.expanduser(GIT_SSH_KEY_FILE)
git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file
old_env = Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd) #make git use said ssh key


def update_repos(git_username, repository, release):
    clone_path = f"{CLONE_BASE_PATH}/{git_username}/{repository}"
    git_path = f"https://{GITHUB_TOKEN}@github.com/{git_username}/{repository}.git"

    if (not os.path.isdir(f"{clone_path}/.git")):
        Repo.clone_from(git_path, clone_path)
    
    else:
        print(clone_path)
        cur_repo = Repo(clone_path)
        cur_repo.git.reset('--hard')
        cur_repo.remotes.origin.pull("master")
    
    Git(clone_path).checkout(release)

def create_src(git_username):
    if not (os.path.isdir(CLONE_BASE_PATH)):
        os.mkdir(CLONE_BASE_PATH)
    if not (os.path.isdir(os.path.join(CLONE_BASE_PATH, git_username))):
        os.mkdir(os.path.join(CLONE_BASE_PATH, git_username))

def delete_old_src(git_username, repository):
    rep = os.path.join(CLONE_BASE_PATH, git_username, repository)
    if os.path.isdir(rep):
        shutil.rmtree(rep)

def fetch_release(git_username, repository, release):
    create_src(git_username)
    delete_old_src(git_username, repository)
    update_repos(git_username, repository, release)