## Setting up Pull Requests and/or Push CI testing for your organizations repositories

### Notify scisoft-team@listserv.fnal.gov
- This will ensure that the appropriate people are aware that you want to start testing pull requests and/or pushes for your repos and the Jenkins jobs can be configured for this.

### Setup your repository
- Make a Pull Request to add your repository configuration in `cms-bot/repos/your_github_user/your_repository`
  - If you have `-` in your github user or repository name then replace it with `_`
- It is better to copy an existing configuration and change it accordingly e.g. copy `repos/LArSoft/larsoft` into `repos/(your github user or organization)/(your repo name)` and make changes to reflect your repositories.
- Add these repository directories with 'git add' and create a pull request to have them added to the master branch.
- Allow `@FNALbot` to update your repository
  - If you have a github organization then please add github user `@FNALbot` into a team with write (or admin) rights
  - If it is not an organization then please add `@FNALbot` to the Collaborators group (under the Settings of your repository).
- Add github webhook so that bot can get notifications.
  - If you have given admin rights to `FNALbot` and set `ADD_WEB_HOOK=True` in `repos/you_or_org/your_repo/repo_config.py` then webhook can be added to your repo automatically.
  - If `FNALbot` does not have admin rights to your repository then please the github webhook (under Settings of your repository) manaully and send scisoft-team@listserv.fnal.gov the "Secret" pass phrase so that your web hooks can be validated. The webhook should have the following properties.
    - Payload URL: https://scd-ci.fnal.gov/cgi-bin/github_webhook
    - Content type: application/json
    - Secret: any password of your choice
    - Let me select individual events: Select
    - Issues, Issue comment, Pull request 
    - Pushes (for push based events)

### Pull request Testing:
- You can have your repository set up to trigger the tests whenever you create or update a pull request with new commits to a branch. In this case, please make sure that github webhook for *Pull requests* is active.

### Push based testsing
- You can have your repository set up to trigger the tests whenever you push some changes to your repo. In this case, please make sure that github webhook for *Pushes* is active.

