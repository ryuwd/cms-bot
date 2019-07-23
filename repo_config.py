from cms_static import GH_CMSSW_ORGANIZATION,GH_CMSSW_REPO,CMSBUILD_GH_USER
from os.path import dirname,abspath
from os import environ
GH_TOKEN=environ['GITHUBTOKEN']
GH_TOKEN_READONLY=environ['GITHUBTOKEN']
CONFIG_DIR=dirname(abspath(__file__))
CMSBUILD_USER="gartung"
GH_REPO_ORGANIZATION="LArSoft"
GH_CMSSW_REPO="github-bot"
CREATE_EXTERNAL_ISSUE=True
JENKINS_SERVER="https://buildmaster.fnal.gov/buildmaster"
IGNORE_ISSUES = {
  GH_CMSSW_ORGANIZATION+"/"+GH_CMSSW_REPO : [12368],
}
OPEN_ISSUE_FOR_PUSH_TESTS=True
