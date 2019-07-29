#!/usr/bin/env python
from __future__ import print_function
from github import Github
from os.path import expanduser
from repo_config import GH_TOKEN


def main():
    from os import environ
    gh = Github(login_or_token=environ['GITHUBTOKEN'])
    print("GitHub API rate limit: {0}".format(gh.get_rate_limit()))


if __name__ == '__main__':
    main()
