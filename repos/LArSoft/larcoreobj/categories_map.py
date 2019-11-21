from repo_config import GH_CMSSW_REPO as gh_repo
CMSSW_CATEGORIES = {
  gh_repo: ['%s/%s' % (gh_repo, gh_repo) ,'%s/CMakeLists.txt' % gh_repo,],
  'build': ['%s/ups' % gh_repo,],
}
