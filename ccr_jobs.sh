#!/bin/bash
#filename: ccr_jobs.sh
#
#desc: This is a very dangerous script, it will remove all jobs with qcs concurrently.
#

NOARGS=65
NOMATCH=122
E_CERROR=129

# check parm num
if [ $# -ne 1 ]; then
   echo "Usage: ${BASH_SOURCE[0]} pu|pr"
   exit ${NOARGS}
fi

# global var
export misId="<misid>"
export apiToken="<api token>"
export viewName="<view name>"
export jenkinsUrl="http://ci.sankuai.com/job/qcs/job/Sonar/view"

# job exec and ops path
configSwitch=$1
bashExec=`which bash`
curDir=$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# repo template
#rt="repoTemplate.txt"
rt="repoTemplate_newer.txt"

# job suffix
case "$configSwitch" in
"pu")
    jobSuf=_static-analyze-push
    ;;
"pr")
    jobSuf=_static-analyze-pr
    ;;
* )
    echo "Please specify valid action."
    exit ${NOMATCH}
    ;;
esac

while read git_repo_name;
do
    (
        echo "deleting $git_repo_name to sonar."
        ${bashExec} ${curDir}/job_handler.sh -d ${git_repo_name}${jobSuf} || exit $E_CERROR
        echo "op $git_repo_name done.."
        echo
    ) &
done < ${rt}

wait
