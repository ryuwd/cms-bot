from os.path import basename,dirname,abspath
#from cms_static import GH_CMSSW_ORGANIZATION,GH_CMSSW_REPO,CMSBUILD_GH_USER
GH_CMSSW_ORGANIZATION="LArSoft"
GH_CMSSW_REPO="larwirecell"
CMSBUILD_GH_USER="scdbuild"
#GH read/write token: Use default ~/.github-token-scdbot
GH_TOKEN="~/.github-token-scdbot"
#GH readonly token: Use default ~/.github-token-readonly
GH_TOKEN_READONLY="~/.github-token-readonly"
CONFIG_DIR=dirname(abspath(__file__))
#GH bot user: Use default scdbot
CMSBUILD_USER="scdbot"
GH_REPO_ORGANIZATION=basename(dirname(CONFIG_DIR))
GH_REPO_FULLNAME="LArSoft/larwirecell"
CREATE_EXTERNAL_ISSUE=False
#Jenkins CI server: User default http://cmsjenkins05.cern.ch:8080/cms-jenkins
JENKINS_SERVER="https://buildmaster.fnal.gov/buildmaster"
#GH Web hook pass phrase. This is encrypeted used bot keys.
GITHUB_WEBHOOK_TOKEN="""U2FsdGVkX19akbUO9GV/sfW46u9HUcJxcJtAo1oHRWOzTjeib95IvymrqUUcxCrv
+C0TsoP8i5gHZ3gq/g9bVQ=="""
#Set to True if you want bot to add build/test labels to your repo
ADD_LABELS=False
#Set to True if you want bot to add GH webhooks. scdbot needs admin rights
ADD_WEB_HOOK=False
#List of issues/pr which bot should ignore
IGNORE_ISSUES = [10]
#Set the Jenkins slave label is your tests needs special machines to run.
JENKINS_SLAVE_LABEL=""
#For cmsdist/cmssw repos , set it to False if you do not want to run standard cms pr tests
CMS_STANDARD_TESTS=False
#Map your branches with cmssw branches for tests
#User Branch => CMSSW/CMSDIST Branch
CMS_BRANCH_MAP={
}
#Valid Web hooks e.g. '.+' to match all event
VALID_WEB_HOOKS=['.+']

