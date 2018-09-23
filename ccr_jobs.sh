#!/bin/bash
#filename: ccr_jobs.sh
#
#desc: This is a very dangerous script, it will remove all jobs with qcs concurrently.
#prm - pull request to master, prt - pull request to test
#

NOARGS=65
NOMATCH=122
E_CERROR=129

# Check parm
if [ $# -ne 1 ]; then
    echo "Usage: ${BASH_SOURCE[0]} pu|prm|prt"
    exit ${NOARGS}
fi

# Global var
export misId="<misid>"
export apiToken="<api token>"
export viewName="<view name>"
export jenkinsUrl="http://ci.sankuai.com/job/qcs/job/Sonar/view"

# Job exec and ops path
configSwitch=$1
bashExec=`which bash`
curDir=$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Repo template
#rt="repoTemplate.txt"
rt="repoTemplate_newer.txt"

# Job suffix
case "$configSwitch" in
    "pu")
        jobSuf="_static-analyze-push"
    ;;
    "prm")
        jobSuf="_static-analyze-pr"
    ;;
    "prt")
        jobSuf="_test_static-analyze-pr"
    ;;
    *)
        echo "Please specify valid action."
        exit ${NOMATCH}
    ;;
esac

while read git_repo_name;
do
    (
    echo "deleting $git_repo_name to sonar."
    ${bashExec} ${curDir}/job_handler.sh -d ${git_repo_name}${jobSuf} || exit ${E_CERROR}
    echo "op $git_repo_name done.."
    echo
    ) &
done < ${curDir}/source/${rt}

wait
