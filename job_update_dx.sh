#!/bin/bash
#filename: job_update_dx.sh
#
#desc: update dx recipient in batches.
#

E_RERROR=61
E_UERROR=62
STIME=1

# Git auth
export misId="<misid>"
export apiToken="<api token>"
export viewName="<view name>"
export jenkinsUrl="http://ci.sankuai.com/job/qcs/job/Sonar/view"
export jobsUrl="http://ci.sankuai.com/job/qcs/job/Sonar/view/${viewName}/api/json?tree=jobs[name]"

# dx recipients list
rl="zhaobin11,liying60"

# Job list with specified view
job_list(){
    curl -s -u ${misId}:${apiToken} -X POST ${jobsUrl} -o ${viewName}.json
    view_list=`jq -r .jobs ${viewName}.json | jq -r .[].name`
}

# Job suffix and cur dir
bashExec=`which bash`
curDir=$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# Acquire job list
job_list

for job in ${view_list}
do
    # acquire job config
    ${bashExec} ${curDir}/job_handler.sh -r ${job} || exit ${E_RERROR}
    sleep ${STIME}

    # update config template
    sed -ri "1,/<\/?recipients.*/{s/<\/?recipients.*/<recipients>${rl}<\/recipients>/}" \
    ${curDir}/${job}_config.xml

    # update job config
    ${bashExec} ${curDir}/job_handler.sh -u ${job} -f ${curDir}/${job}_config.xml \
    || exit ${E_UERROR}

    # Cleanup Env
    rm -rf ${viewName}.json ${curDir}/${job}_config.xml &> /dev/null
done
