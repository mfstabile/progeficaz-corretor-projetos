import os
import sys
from github import Github

def push_issue(git_username, repository, release, text):
    token = os.getenv('GITHUB_TOKEN', '...')
    g = Github(token)
    repo = g.get_repo('{}/{}'.format(git_username, repository))
    print("Creating issue for {}/{}:\n{}".format(git_username, repository, text))
    i = repo.create_issue(title="Problemas na {}".format(release),
                            body=text,
                            assignee='')