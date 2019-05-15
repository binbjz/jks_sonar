#!/bin/bash
#filename: job_dispatcher.sh
#
#desc: access sonar with grouping by pull request to trigger.
#For now, just accessing and grouping by pull request with master and release branch.
#

NOARGS=65
NOMATCH=122
E_CERROR=129
E_EMP=127
STIME=0.2

# Define global var
export misId="<misid>"
export apiToken="<api token>"
export viewName="<view name>"
export jenkinsUrl="http://ci.sk.com/job/qcs/job/Sonar/view"

# Check parm
if [[ $# -ne 1 ]]; then
    echo "Usage: ${BASH_SOURCE[0]} prm|prr"
    exit ${NOARGS}
fi

# Specify config template and target br
configSwitch=$1
prConfigTemplate="prInitConfigTemplate.xml"

case "$configSwitch" in
    "prm")
        # using pr master config template
        configTemplate=${prConfigTemplate}
        target_br="master"
    ;;
    "prr")
        # using pr release config template
        configTemplate=${prConfigTemplate}
        target_br="release"
    ;;
    *)
        echo "Please specify valid config template type."
        exit ${NOMATCH}
    ;;
esac

# Job suffix and cur dir
bashExec=`which bash`
curDir=$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)

function func_trim() {
    echo "$1" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//'
}

# Replace kw with specified parm
function replace_kw() {
    sed -re "s#repos_name#${1}#g; \
             s#mis_id#${misId}#g; \
             s#(<repositoryName>).*(</repositoryName>)#\1${1}\2#g; \
             s#(<url>).*(</url>)#\1${2}\2#g; \
             s#(<targetBranchesToBuild>).*(</targetBranchesToBuild>)#\1${3}\2#g; \
             s#(sonar.projectKey=).*#\1${4}#g; \
             s#(sonar.projectName=).*#\1${5}#g" \
    ${curDir}/conf/${configTemplate} > ${curDir}/${configTemplate}.$$
}

# Define repo template, project prefix and trigger job with specified action
rt="stash_org_grp_success.csv"
cs="com.sk"
qcs_repo="ssh://git@git.sk.com/qcs/"
pjk_suffix=":release"

while read git_repo_info
do
    # specify sonar project prefix
    # qcs.r.settle.common,gaoyang09,技术研发部-结算组,qcs_trd_settle
    git_repo=$(awk 'NR==1{sub(/^\xef\xbb\xbf/,"")}1' <<< ${git_repo_info})
    git_repo=$(func_trim "${git_repo}")
    git_repo_name=$(awk -F',' '{print $1}' <<< ${git_repo})
    projectNamePrefix=$(awk -F',' '{print $4}' <<< ${git_repo})

    # define job parm and job list to access sonar
    declare -A array_var

    array_var[repo_name]="$git_repo_name"
    array_var[repo_ssh]="${qcs_repo}${array_var[repo_name]}.git"
    array_var[project_key]="${cs}:${projectNamePrefix}_${array_var[repo_name]}"
    array_var[project_name]="${projectNamePrefix}_${array_var[repo_name]}"
    array_var[target_branch]="${target_br}"

    # sonar with pr release branch
    if [[ "$configSwitch" == "prr" ]]; then
        array_var[project_key]="${cs}:${projectNamePrefix}_${array_var[repo_name]}${pjk_suffix}"
        array_var[project_name]="${projectNamePrefix}_${array_var[repo_name]}${pjk_suffix}"
    fi

    # perform access action
    replace_kw ${array_var[repo_name]} ${array_var[repo_ssh]} ${array_var[target_branch]} \
    ${array_var[project_key]} ${array_var[project_name]}

    # specify job suffix
    if [[ "$configSwitch" == "prm" ]]; then
        jobSuf="_static-analyze-pr"
    else
        jobSuf="_release_static-analyze-pr"
    fi

    # create job to access sonar
    jobName=${array_var[repo_name]}${jobSuf}

    echo "accessing $git_repo_name to sonar."
    ${bashExec} ${curDir}/job_handler.sh -c ${jobName} -f ${curDir}/${configTemplate}.$$ \
    || exit ${E_CERROR}

    sleep ${STIME}

    # just build with prm job
    if [[ "$configSwitch" == "prm" ]]; then
        # we will not trigger it by manual or crontab for the moment
        :
        # sleep ${STIME}

        # build
        # ${bashExec} ${curDir}/job_handler.sh -s ${jobName}

        # build with parameters
        # ${bashExec} ${curDir}/job_handler.sh -s ${jobName} -p release
    fi

    # cleanup env
    rm -rf ${curDir}/${configTemplate}.$$ &> /dev/null
    echo "op $jobName done.."
    echo
done < ${curDir}/source/${rt}
