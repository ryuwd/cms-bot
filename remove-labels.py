#!/bin/env python
from github import Github
from github_utils import api_rate_limits
from os import environ

def clean_labels(repo):
    deflabels=['bug','documentation','duplicate','enhancement','good first idea','help wanted', 'invalid', 'question', 'wontfix']
    api_rate_limits(gh)
    print repo.name
    api_rate_limits(gh)
    for label in repo.get_labels():
        if not label.name in deflabels:
            print label.name
            label.delete()
        api_rate_limits(gh)
        
if __name__ ==  "__main__":
    gh = Github(login_or_token=environ['GITHUBTOKEN'])
    repo=gh.get_repo("gartung/cms-bot")
    print repo
    clean_labels(repo)
    user = gh.get_user('LArSoft')
    repos = user.get_repos()
    for r in repos:
        clean_labels(r)
