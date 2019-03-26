#!/bin/bash
#filename: job_update_msg.sh
#
#desc: Configure dx recipient, sonar info and post notification dynamically.
#

set -e
set +H

E_RERROR=61
E_UERROR=62
S_TIME=0.2

# Git auth
export misId="<misid>"
export apiToken="<api token>"
export viewName="<view name>"
export jenkinsUrl="http://ci.ee.test.sankuai.com/job/qcs/job/Sonar/view"
export jobsUrl="http://ci.ee.test.sankuai.com/job/qcs/job/Sonar/view/${viewName}/api/json?tree=jobs[name]"

# Dx recipients list, the separator must be a comma
rl="zhaobin11,liying60"

# Sonar msg prefix and repo template
pbPrefix="http:\/\/sonar.ep.sankuai.com\/dashboard\/index\/com.sankuai"
rt="stash_org_grp_success.csv"

# Sonar lang js for qcs.fe.* srv
sonar_lang="js"

# Build success and failure info
bscVar=`cat <<- SETVAR
Static code check success!\n\
Access the url: [qcs_sonar_plat](<sonar_url>)\n\
Check the latest inspection report!
SETVAR`

bfcVar=`cat <<- SETVAR
Static code check failure!\n\
Access the url: [\\${BUILD_TAG}](\\${BUILD_URL})\n\
Check the error reason!
SETVAR`

# Parser and cur dir
bashExec=`which bash`
curDir=$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)


# Job list with specified view
function job_list() {
    curl -sS -u ${misId}:${apiToken} -X POST ${jobsUrl} -o ${curDir}/${viewName}.json
    view_list=`jq -r .jobs ${viewName}.json | jq -r .[].name`
}

# Acquire job list
job_list

# Update job with specified action
for job in ${view_list}
do
    # service name by jks job
    srv_name=`awk 'BEGIN {FS="_"} {print $1}' <<< ${job}`

    while read git_repo
    do
        # repo info from repo template
        #git_repo=$(awk 'NR==1{sub(/^\xef\xbb\xbf/,"")}1' <<< ${git_repo})
        git_repo_name=$(awk -F',' '{print $1}' <<< ${git_repo})
        projectNamePrefix=$(awk -F',' '{print $4}' <<< ${git_repo})

        if [[ ${git_repo_name} != ${srv_name} ]]; then
            continue
        fi

        # acquire job config
        ${bashExec} ${curDir}/job_handler.sh -r ${job} || exit ${E_RERROR}
        sleep ${S_TIME}

        if [[ ${job/_release_/} != ${job} ]]; then
            pbName="${projectNamePrefix}_${srv_name}:\${GIT_BRANCH}"
        else
            pbName="${projectNamePrefix}_${srv_name}"
        fi

        # update sonar info
        msgCmd="echo \"${pbPrefix}:${pbName}\" > sonar_info"
        sed -ri "1,/<\/?command.*/{s/<\/?command.*/<command>${msgCmd}<\/command>/}" \
        ${curDir}/${job}_config.xml

        # update dx recipients
        sed -ri "1,/<\/?recipients.*/{s/<\/?recipients.*/<recipients>${rl}<\/recipients>/}" \
        ${curDir}/${job}_config.xml

        # update stash post build successful comment -> just for pull request
        sed -ri "s/<\/?buildSuccessfulComment.*/<buildSuccessfulComment>${bscVar}<\/buildSuccessfulComment>/" \
        ${curDir}/${job}_config.xml

        # update stash post build failed comment -> just for pull request
        sed -ri "s/<\/?buildFailedComment.*/<buildFailedComment>${bfcVar}<\/buildFailedComment>/" \
        ${curDir}/${job}_config.xml

        # update sonar_url in build successful comment -> just for pull request
        sed -ri "1,/<sonar_url>/{s/<sonar_url>/${pbPrefix}:${pbName}/}" ${curDir}/${job}_config.xml

        # Note: update sonar language, it only works for qcs.fe.* srv
        # You can specify job view that only contains the qcs.fe.* srv and uncomment it
        : sed -ri "/sonar\.inclusions/c\sonar\.language=${sonar_lang}" ${curDir}/${job}_config.xml

        # update job
        ${bashExec} ${curDir}/job_handler.sh -u ${job} -f ${curDir}/${job}_config.xml \
        && echo "op ${job} done.." || exit ${E_UERROR}
        echo

        # cleanup tmpl env
        rm -rf ${curDir}/${job}_config.xml &> /dev/null

        # Break inner template loop
        break
    done < ${curDir}/source/${rt}
done

# Cleanup Lst Env
rm -rf ${curDir}/${viewName}.json &> /dev/null
