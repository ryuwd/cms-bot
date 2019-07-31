#!/bin/env python
from github import Github
from github_utils import api_rate_limits

repos = []
repo_name="LArSoft"
from os import environ
gh = Github(login_or_token=environ['GITHUBTOKEN'])
api_rate_limits(gh)
user = gh.get_user(repo_name)
deflabels=['bug','documentation','duplicate','enhancement','good first idea','help wanted', 'invalid', 'question', 'wontfix']
for repo in user.get_repos(repo_name):
    print repo.name
    api_rate_limits(gh)
    for label in repo.get_labels():
        if not label.name in deflabels:
            print label.name
            label.delete()
        api_rate_limits(gh)
        
