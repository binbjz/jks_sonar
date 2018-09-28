#!/bin/bash
#filename: view_handler.sh
#
#desc: This is a very dangerous script, it will enable or disable or remove all jobs with qcs view concurrently.
#prm - pull request to master, prt - pull request to test
#

NOARGS=65
NOMATCH=122
NOMATCH2=123
E_CERROR=129

# Check parm
if [ $# -ne 2 ]; then
    echo "Usage: ${BASH_SOURCE[0]} (pu|prm|prt) (enable|disable|delete)"
    exit ${NOARGS}
fi

# Global var
export misId="<misid>"
export apiToken="<api token>"
export viewName="<view name>"
export jenkinsUrl="http://ci.sankuai.com/job/qcs/job/Sonar/view"
export jobsUrl="http://ci.sankuai.com/job/qcs/job/Sonar/view/${viewName}/api/json?tree=jobs[name]"

# Job exec and ops path
triggerType=$1
actionType=$2
bashExec=`which bash`
curDir=$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Job trigger type
case "$triggerType" in
    "pu")
        trigger_type="_static-analyze-push"
    ;;
    "prm")
        trigger_type="_static-analyze-pr"
    ;;
    "prt")
        trigger_type="_test_static-analyze-pr"
    ;;
    *)
        echo "Please specify valid trigger type (pu|prm|prt)."
        exit ${NOMATCH}
    ;;
esac

# Job action type
case "$actionType" in
    "enable")
        action_type="enable"
        action_opt="-e"
    ;;
    "disable")
        action_type="disable"
        action_opt="-k"
    ;;
    "delete")
        action_type="delete"
        action_opt="-d"
    ;;
    *)
        echo "Please specify valid action type (enable|disable|delete)."
        exit ${NOMATCH2}
    ;;
esac

# Job list with specified view
function job_list() {
    curl -s -u ${misId}:${apiToken} -X POST ${jobsUrl} -o ${curDir}/${viewName}.json
    view_list=`jq -r .jobs ${viewName}.json | jq -r .[].name`
}

# Acquire job list
job_list

# Trigger job with specified action
for job in ${view_list}
do
    if [[ ${job/${trigger_type}/} != ${job} ]]; then
        echo "$action_type $job to sonar."
        ${bashExec} ${curDir}/job_handler.sh ${action_opt} ${job} || exit ${E_CERROR}
        echo "op $job done.."
        echo
    fi
done