from __future__ import print_function
from categories import (
    CMSSW_CATEGORIES,
    CMSSW_L2,
    CMSSW_L1,
    TRIGGER_PR_TESTS,
    CMSSW_ISSUES_TRACKERS,
    PR_HOLD_MANAGERS,
    EXTERNAL_REPOS,
    CMSDIST_REPOS,
)
import categories
from releases import (
    RELEASE_BRANCH_MILESTONE,
    RELEASE_BRANCH_PRODUCTION,
    RELEASE_BRANCH_CLOSED,
    CMSSW_DEVEL_BRANCH,
)
from releases import RELEASE_MANAGERS, SPECIAL_RELEASE_MANAGERS
from cms_static import (
    VALID_CMSDIST_BRANCHES,
    NEW_ISSUE_PREFIX,
    NEW_PR_PREFIX,
    ISSUE_SEEN_MSG,
    BUILD_REL,
    GH_CMSDIST_REPO,
    CMSBOT_IGNORE_MSG,
    VALID_CMS_SW_REPOS_FOR_TESTS,
)
from cms_static import BACKPORT_STR, GH_CMSSW_ORGANIZATION
from repo_config import GH_REPO_ORGANIZATION, GH_CMSSW_REPO
import re, time, os
from datetime import datetime
from os.path import join, exists
from os import environ
from github_utils import get_token, edit_pr, api_rate_limits
from socket import setdefaulttimeout
from _py2with3compatibility import run_cmd
from github import Github

print("""

    .::   .::       .::  .:: ::        .:: .::       .::::     .::: .::::::
 .::   .::.: .::   .:::.::    .::      .:    .::   .::    .::       .::
.::       .:: .:: . .:: .::            .:     .::.::        .::     .::
.::       .::  .::  .::   .::    .:::::.::: .:   .::        .::     .::
.::       .::   .:  .::      .::       .:     .::.::        .::     .::
 .::   .::.::       .::.::    .::      .:      .:  .::     .::      .::
   .::::  .::       .::  .:: ::        .:::: .::     .::::          .::

.::       .::
.: .::   .:::         .:::.:
.:: .:: . .::.::  .::.:    .:   .::
.::  .::  .::.::  .::    .::  .:   .::
.::   .:  .::.::  .::  .::   .::::: .::
.::       .::.::  .::.::     .:
.::       .::  .::.::.:::::::  .::::

""")

try:
    from categories import COMMENT_CONVERSION
except:
    COMMENT_CONVERSION = {}
setdefaulttimeout(300)

CMSDIST_REPO_NAME = join(GH_REPO_ORGANIZATION, GH_CMSDIST_REPO)
CMSSW_REPO_NAME = join(GH_REPO_ORGANIZATION, GH_CMSSW_REPO)

PR_SALUTATION =  """Hi @{pr_author},
You have proposed changes to files in these packages:
{changed_folders}

which require these tests: {tests_required}.

{watchers}
{tests_triggered_msg}

<a href="https://mu2ewiki.fnal.gov/wiki/Jenkins">cms-bot/mu2e commands are explained here</a>
"""

TESTS_TRIGGERED_CONFIRMATION = """:hourglass: The following tests have been triggered for ref {commit_link}: {test_list} {tests_already_running_msg}"""
TESTS_ALREADY_TRIGGERED = """:x: Those tests have already run or are running for ref {commit_link} ({triggered_tests})"""

TEST_WAIT_GAP = 720


# Mu2e triggering statements are in 'test_suites.py'
import test_suites

def check_test_cmd_mu2e(full_comment, repository):
    # we have a suite of regex statements to support triggering all kinds of tests.
    # each item in this list matches a trigger statement in a github comment

    # each 'trigger event' function should return:
    # (testnames to run: list, master+branchPR merge result to run them on)

    # tests:
    # desc: code checks -> mu2e/codechecks (context name) -> [jenkins project name]
    # desc: integration build tests -> mu2e/buildtest -> [jenkins project name]
    # desC: physics validation -> mu2e/validation -> [jenkins project name]

    for regex, handler in test_suites.TESTS:
        # returns the first match in the comment
        match = regex.search(full_comment)
        print (regex, full_comment, match)

        if match is None:
            continue
        return handler(match)

    return None


def get_last_commit(pr):
    last_commit = None
    try:
        # This requires at least PyGithub 1.23.0. Making it optional for the moment.
        last_commit = pr.get_commits().reversed[0].commit
    except:
        # This seems to fail for more than 250 commits. Not sure if the
        # problem is github itself or the bindings.
        try:
            last_commit = pr.get_commits()[pr.commits - 1].commit
        except IndexError:
            print("Index error: May be PR with no commits")
    return last_commit


# Read a yaml file
def read_repo_file(repo_config, repo_file, default=None):
    import yaml

    file_path = join(repo_config.CONFIG_DIR, repo_file)
    contents = default
    if exists(file_path):
        contents = yaml.load(open(file_path,'r'), Loader=yaml.FullLoader)
        if not contents:
            contents = default
    return contents

#
# creates a properties file to trigger the test of the pull request
#
def create_properties_file_tests(
    repository,
    pr_number,
    cmsdist_pr,
    cmssw_prs,
    dryRun,
    abort=False,
    req_type="tests",
    repo_config=None,
    extra_prop=None,
    new_tests=True,
    head_sha='',
):
    if abort:
        req_type = "abort"
    repo_parts = repository.split("/")
    if req_type in "tests":
        try:
            if not repo_parts[0] in EXTERNAL_REPOS:
                req_type = "user-" + req_type
            elif not repo_config.CMS_STANDARD_TESTS:
                req_type = "user-" + req_type
        except:
            pass
    repo_partsX = repository.replace("/", "-")
    out_file_name = "trigger-%s-%s-%s.properties" % (req_type, repo_partsX, pr_number)
    parameters = {}
    parameters["REPOSITORY"] = repository
    parameters["PULL_REQUEST"] = pr_number
    parameters["COMMIT_SHA"] = head_sha
    if extra_prop:
        for x in extra_prop:
            parameters[x] = extra_prop[x]
    if new_tests:
        prs = ["%s#%s" % (repository, pr_number)]
        for pr in [p for p in cmssw_prs.split(",") if p]:
            if "#" not in pr:
                pr = "%s#%s" % (repository, pr)
            prs.append(pr)
        parameters["PULL_REQUESTS"] = ",".join(prs)
        parameters["USE_MULTIPLE_PRS_JOB"] = "true"
    else:
        parameters["PUB_USER"] = repo_parts[0]
        if repo_parts[1] == GH_CMSDIST_REPO:
            parameters["CMSDIST_PR"] = pr_number
        else:
            parameters["PULL_REQUEST"] = pr_number
            parameters["CMSDIST_PR"] = cmsdist_pr
            parameters["ADDITIONAL_PULL_REQUESTS"] = cmssw_prs
    try:
        if repo_config.JENKINS_SLAVE_LABEL:
            parameters["RUN_LABEL"] = repo_config.JENKINS_SLAVE_LABEL
    except:
        pass
    print("PropertyFile: ", out_file_name)
    print("Data:", parameters)
    create_property_file(out_file_name, parameters, dryRun)


def create_property_file(out_file_name, parameters, dryRun):
    if dryRun:
        print("Not creating cleanup properties file (dry-run): %s" % out_file_name)
        return
    print("Creating properties file %s" % out_file_name)
    out_file = open(out_file_name, "w")
    for k in parameters:
        out_file.write("%s=%s\n" % (k, parameters[k]))
    out_file.close()


# Update the milestone for a given issue.
def updateMilestone(repo, issue, pr, dryRun):
    milestoneId = RELEASE_BRANCH_MILESTONE.get(pr.base.label.split(":")[1], None)
    if not milestoneId:
        print("Unable to find a milestone for the given branch")
        return
    if pr.state != "open":
        print("PR not open, not setting/checking milestone")
        return
    if issue.milestone and issue.milestone.id == milestoneId:
        return
    milestone = repo.get_milestone(milestoneId)
    print("Setting milestone to %s" % milestone.title)
    if dryRun:
        return
    issue.edit(milestone=milestone)


def process_pr(repo_config, gh, repo, issue, dryRun, cmsbuild_user=None, force=False):
    api_rate_limits(gh)

    mu2eorg = gh.get_organization("Mu2e")
    #mu2eteams = mu2eorg.get_teams()
    mu2e_write = ['ryuwd']#mu2eorg.get_team_by_slug('write') TODO: remove after testing
    mu2e_write_mems =['ryuwd']# [mem.login for mem in mu2e_write.get_members()]

    if not issue.pull_request:
        return

    # users authorised to communicate with this bot
    authorised_users = set(mu2e_write_mems)

    not_seen_yet = True
    last_time_seen = None
    labels = []
    # commit test states:
    test_statuses = {}
    test_triggered = {}
    test_status_exists = {} # did we already create a commit status?

    # tests we'd like to trigger on this commit
    tests_to_trigger = []

    # tests we've already triggered
    tests_already_triggered = []
    # top-level folders of the Offline 'monorepo'
    # that have been edited by this PR
    modified_top_level_folders = []

    prId = issue.number
    pr = repo.get_pull(prId)

    if pr.changed_files == 0:
        print("Ignoring: PR with no files changed")
        return

    # get PR and changed libraries / packages
    pr_repo = gh.get_repo(repo.full_name)
    pr_files = pr.get_files()

    for f in pr_files:
        filename, file_extension = os.path.splitext(f.filename)
        print( "Changed file (%s): %s.%s" % (file_extension, filename, file_extension) )

        splits = filename.split('/')
        if len(splits) > 1:
            modified_top_level_folders.append(splits[0])
        else:
            modified_top_level_folders.append('/')

    modified_top_level_folders = set(modified_top_level_folders)
    print ('Build Targets changed:')
    print (
        '\n'.join(['- %s' % s for s in modified_top_level_folders])
    )

    # TODO: print modified monorepo package folders in 'greeting' message
    watchers = read_repo_file(repo_config, "watchers.yaml", {})

    print ('watchers:', watchers )

    # get required tests
    test_requirements = test_suites.get_tests_for(modified_top_level_folders)
    print ('Tests required: ', test_requirements)

    # set their status to 'pending' (will be updated shortly after)
    for test in test_requirements:
        test_statuses[test] = 'pending'
        test_triggered[test] = False
        test_status_exists[test] = False

    # get latest commit
    last_commit = pr.get_commits().reversed[0]
    git_commit = last_commit.commit
    if git_commit is None:
        return

    last_commit_date = git_commit.committer.date
    print(
        "Latest commit by ",
        git_commit.committer.name,
        " at ",
        last_commit_date,
    )
    print("Latest commit message: ", git_commit.message.encode("ascii", "ignore"))
    print("Latest commit sha: ", git_commit.sha)
    print("PR update time", pr.updated_at)
    print("Time UTC:", datetime.utcnow())

    if last_commit_date > datetime.utcnow():
        print("==== Future commit found ====")
        if (not dryRun) and repo_config.ADD_LABELS:
            labels = [x.name for x in issue.labels]
            if not "future commit" in labels:
                labels.append("future commit")
                issue.edit(labels=labels)
        return

    # now get commit statuses
    # this is how we figure out the current state of tests
    # on the latest commit of the PR.
    commit_status = last_commit.get_statuses()

    # we can translate git commit status API 'state' strings if needed.
    state_labels = {
        'error': 'error',
        'failure': 'failed',
        'success': 'succeeded',
    }

    commit_status_time = {}

    for stat in commit_status:
        name = test_suites.get_test_name(stat.context)
        if name == 'unrecognised':
            continue
        if name in commit_status_time:
            if commit_status_time[name] > stat.updated_at:
                continue
        commit_status_time[name] = stat.updated_at

        # error, failure, pending, success
        test_statuses[name] = stat.state
        if stat.state in state_labels:
            test_statuses[name] = state_labels[stat.state]
        test_status_exists[name] = True

        if name in test_triggered:
            if test_triggered[name]: # if already True, don't change it
                continue
        test_triggered[name] = ('has been triggered' in stat.description)

        # some other labels, gleaned from the description (the status API
        # doesn't support states)
        if ('running' in stat.description):
            test_statuses[name] = 'running'



    # now process PR comments that come after when
    # the bot last did something, first figuring out when the bot last commented
    pr_author = issue.user.login
    comments = issue.get_comments()
    for comment in comments:
        # loop through once to ascertain when the bot last commented
        if comment.user.login == repo_config.CMSBUILD_USER:
            not_seen_yet = False
            last_time_seen = comment.created_at

    # we might not have commented, but e.g. changed a label instead...
    for event in pr.get_issue_events():
        if event.actor.login == repo_config.CMSBUILD_USER:
            if event.created_at > last_time_seen:
                last_time_seen = event.created_at


    # now we process comments
    for comment in comments:
        # Ignore all other messages which are before last commit.
        # TODO: we should handle abort messages here that come before the last commit

        if (comment.created_at < last_commit_date):
            continue

        # neglect comments we've already responded to
        if not (comment.created_at > last_time_seen):
            continue

        # neglect comments by un-authorised users
        if not comment.user.login in authorised_users:
            print("IGNORE comment from %s." % comment.user.login)
            continue

        # now look for bot triggers
        # check if the comment has triggered a test
        trigger_search = check_test_cmd_mu2e(comment.body, repo.full_name)
        tests_already_triggered = []

        if trigger_search is not None:
            tests, run_with = trigger_search
            print ("Triggered! Comment: %s" % comment.body)
            print ('current test(s) to trigger: %r' % tests_to_trigger)
            print ('add test(s) to trigger: %r' % tests )

            for test in tests:
                # check that the test has been triggered on this commit first
                if test in test_triggered: # has the test been added?
                    if test_triggered[test]:
                        print ("The test has already been triggered for this ref. It will not be triggered again.")
                        tests_already_triggered.append(test)
                        continue
                else:
                    test_triggered[test] = False

                if not test_triggered[test]: # is the test already running?
                    # ok - now we can trigger the test
                    print ("The test has not been triggered yet. It will now be triggered.")

                    # update the 'state' of this commit
                    test_statuses[test] = 'pending'
                    test_triggered[test] = True

                    # add the test to the queue of tests to trigger
                    tests_to_trigger.append(test)


    # now,
    # - apply labels according to the state of the latest commit of the PR
    # - trigger tests if indicated (for this specific SHA.)
    # - set the current status for this commit SHA
    # - make a comment if required

    for test, state in test_statuses.items():
        labels.append('%s %s' % (test, state))

        if test in tests_to_trigger:
            print ("TEST WILL NOW BE TRIGGERED: %s" % test)
            # trigger the test in jenkins
            # TODO: figure out how these properties files will trigger
            # the mu2e Jenkins jobs
            create_properties_file_tests(
                    repo.full_name,
                    prId,
                    '',
                    '',
                    dryRun,
                    req_type='mu2e-' + test.replace(' ','-'),
                    abort=False,
                    repo_config=repo_config,
                    new_tests=True,
                    head_sha=git_commit.sha
                )
            if not dryRun:
                last_commit.create_status(
                            state="pending",
                            target_url="https://github.com/mu2e/Offline",
                            description="The test has been triggered in Jenkins",
                            context=test_suites.get_test_alias(test)
                        )
            print ("Git status created for SHA %s test %s - since the test has been triggered." % (git_commit.sha, test))
        elif state == 'pending' and test_status_exists[test]:
            print ("Git status unchanged for SHA %s test %s - the existing one is up-to-date." % (git_commit.sha, test))

        elif state == 'pending' and not test_triggered[test] and not test_status_exists[test]:
            print (test_status_exists)
            print ("Git status created for SHA %s test %s - since there wasn't one already." % (git_commit.sha, test))
            # indicate that the test is pending but
            # we're still waiting for someone to trigger the test
            if not dryRun:
                last_commit.create_status(
                            state="pending",
                            target_url="https://github.com/mu2e/Offline",
                            description="This test has not been triggered yet.",
                            context=test_suites.get_test_alias(test)
                        )
        # don't do anything else with commit statuses
        # the script handler that handles Jenkins job results will update the commits accordingly

    commitlink = 'https://github.com/%s/pull/%s/commits/%s' % (repo.full_name, prId, git_commit.sha)
    tests_triggered_msg = ''
    already_running_msg = ''
    if len(tests_to_trigger) > 0:
        if len(tests_already_triggered) > 0:
            already_running_msg = '(already triggered: %s)' % ','.join(tests_already_triggered)
        tests_triggered_msg = TESTS_TRIGGERED_CONFIRMATION.format(commit_link=commitlink, test_list=', '.join(tests_to_trigger), tests_already_running_msg=already_running_msg)

    # check if labels have changed
    labelnames =  [x.name for x in issue.labels]
    for l in labels:
        if l not in labelnames:
            if not dryRun:
                issue.edit(labels=labels)
            print ("labels have changed to: ", labels)
            break

    # check if we have any lingering labels!
    for l in labelnames:
        if l not in labels:
            if not dryRun:
                issue.edit(labels=labels)
            print ("labels have changed to: ", labels)
            break

    if not_seen_yet:
        print ("First time seeing this PR - send the user a salutation!")
        if not dryRun:
            issue.create_comment(PR_SALUTATION.format(
                pr_author=pr_author,
                changed_folders='\n'.join(['- %s' % s for s in modified_top_level_folders]),
                tests_required=', '.join(test_requirements),
                watchers='',
                tests_triggered_msg=tests_triggered_msg
            ))

    elif len(tests_to_trigger) > 0:
        if not dryRun:
            issue.create_comment(tests_triggered_msg)
    elif len(tests_to_trigger) == 0 and len(tests_already_triggered) > 0:
        if not dryRun:
            issue.create_comment(TESTS_ALREADY_TRIGGERED.format(commit_link=commitlink, triggered_tests=', '.join(tests_already_triggered))
)
