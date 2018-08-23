#!/bin/bash
#filename: job_update_msg.sh
#
#desc: Configure dx recipient and sonar info dynamically.
#

E_RERROR=61
E_UERROR=62
S_TIME=0.5

# Git auth
export misId="<misid>"
export apiToken="<api token>"
export viewName="<view name>"
export jenkinsUrl="http://ci.sankuai.com/job/qcs/job/Sonar/view"
export jobsUrl="http://ci.sankuai.com/job/qcs/job/Sonar/view/${viewName}/api/json?tree=jobs[name]"

# dx recipients list, the separator must be a comma
rl="zhaobin11,liying60"

# Project and sonar msg prefix
projectNamePrefix=( qcs_push_ qcs_pull_request_ )
pbPrefix="http:\/\/sonar.ep.sankuai.com\/dashboard\/index\/com.sankuai"

# parser and cur dir
bashExec=`which bash`
curDir=$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# Job list with specified view
job_list(){
    curl -s -u ${misId}:${apiToken} -X POST ${jobsUrl} -o ${curDir}/${viewName}.json
    view_list=`jq -r .jobs ${viewName}.json | jq -r .[].name`
}

# Acquire job list
job_list

for job in ${view_list}
do
    # acquire job config
    ${bashExec} ${curDir}/job_handler.sh -r ${job} || exit ${E_RERROR}
    sleep ${S_TIME}

    srv_name=`awk 'BEGIN {FS="_"} {print $1}' <<< ${job}`

    if [[ ${job/-push/} != ${job} ]]; then
        pbName="${projectNamePrefix[0]}${srv_name}:\${GIT_BRANCH}"
    elif [[ ${job/_test_/} != ${job} ]]; then
        pbName="${projectNamePrefix[1]}${srv_name}:\${GIT_BRANCH}"
    else
        pbName="${projectNamePrefix[1]}${srv_name}"
    fi

    # update sonar info
    msg_cmd="echo \"${pbPrefix}:${pbName}\" > sonar_info"
    sed -ri "1,/<\/?command.*/{s/<\/?command.*/<command>${msg_cmd}<\/command>/}" \
    ${curDir}/${job}_config.xml

    # update dx recipients
    sed -ri "1,/<\/?recipients.*/{s/<\/?recipients.*/<recipients>${rl}<\/recipients>/}" \
    ${curDir}/${job}_config.xml

    # update job
    ${bashExec} ${curDir}/job_handler.sh -u ${job} -f ${curDir}/${job}_config.xml \
    && echo "op ${job} done.." || exit ${E_UERROR}
    echo

    # cleanup tmpl env
    rm -rf ${curDir}/${job}_config.xml &> /dev/null
done

# Cleanup Lst Env
rm -rf ${curDir}/${viewName}.json &> /dev/null
