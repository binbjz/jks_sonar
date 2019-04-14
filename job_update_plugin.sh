#!/bin/bash
#filename: job_update_plugin.sh
#
#desc: Update stash post build comment plugin dynamically.
#note: just for pull request.
#

set -e

E_RERROR=61
E_UERROR=62
S_TIME=0.2

# Please uncomment the code block and update these parms
# if you need to use this script alone.
: << COMMENTBLOCK
# Git auth
export misId="<misid>"
export apiToken="<api token>"
export viewName="<view name>"
export jenkinsUrl="http://ci.sankuai.com/job/qcs/job/Sonar/view"
export jobsUrl="http://ci.sankuai.com/job/qcs/job/Sonar/view/${viewName}/api/json?tree=jobs[name]"
COMMENTBLOCK

# Stash post build comment plugin
stash_pr_plugin_var=`cat <<- SETVAR
    <stashpullrequestbuilder.stashpullrequestbuilder.StashPostBuildComment plugin=\"stash-pullrequest-builder@1.6.0\">\n\
      <buildSuccessfulComment/>\n\
      <buildFailedComment/>\n\
    </stashpullrequestbuilder.stashpullrequestbuilder.StashPostBuildComment>
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

for job in ${view_list}
do
    # acquire job config
    ${bashExec} ${curDir}/job_handler.sh -r ${job} || exit ${E_RERROR}
    sleep ${S_TIME}

    # remove stash pr plugin with comments
    sed -ri "/<.*\.StashPostBuildComment/,/<\/.*\.StashPostBuildComment>/d" ${curDir}/${job}_config.xml
    sleep ${S_TIME}

    # add stash pr plugin
    sed -ri "/<publishers>/a\\${stash_pr_plugin_var}" ${curDir}/${job}_config.xml

    # update job
    ${bashExec} ${curDir}/job_handler.sh -u ${job} -f ${curDir}/${job}_config.xml \
    && echo "op ${job} done.." || exit ${E_UERROR}
    echo

    # cleanup tmpl env
    rm -rf ${curDir}/${job}_config.xml &> /dev/null
done

# Cleanup Lst Env
rm -rf ${curDir}/${viewName}.json &> /dev/null
