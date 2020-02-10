from github import Github

def comment_gh_pr(repo, pr, msg):
    from os import environ
    gh = Github(login_or_token=environ['GITHUBTOKEN'], retry=3)
    repo = gh.get_repo(repo)
    pr   = repo.get_issue(pr)

    # This script provides the mechanism that reports on
    # job statuses.
    # the message is read from a 'report file' supplied by the Jenkins job.

    # The format should be:
    # line 1: SHA of the tested commit
    # line 2: the job 'context' or the string-identifier for the job
    # line 3: job status: success/failure/error/running
    # line 4: a one-line description of the state
    # line 5: Link to detailed results/information
    # line 6+: The comment to post on the Pull Request, or, if no comment desired, add 'NOCOMMENT'

    lines = msg.split('\n')
    if len(lines) < 6: # need at least six lines.
        # Post instead the msg, and skip the git status.
        pr.create_comment("Error: A Jenkins job did not report output in the correct format. \n\nThe output was as follows:\n%s" % msg)
        return

    test_commit_sha = lines[0]
    context = lines[1]
    state = lines[2]
    desc = lines[3]
    details_link = lines[4]

    pr.get_commit(sha=test_commit_sha).create_status(
        state=state,
        target_url=details_link,
        description=desc,
        context=test_suites.get_test_alias(test)
    )


    comment_msg = '\n'.join(lines[5:])

    if not 'NOCOMMENT' in comment_msg: # some status updates by commenting might not be necessary.
        pr.create_comment(comment_msg)
