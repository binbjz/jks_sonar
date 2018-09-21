#!/bin/bash
#filename: job_dispatcher.sh
#
#desc: access sonar by jenkins with manual, crontab, push or pull request to trigger.
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
export jenkinsUrl="http://ci.sankuai.com/job/qcs/job/Sonar/view"

# Check parm
if [ $# -ne 1 ]; then
   echo "Usage: ${BASH_SOURCE[0]} pu|prm|prt"
   exit ${NOARGS}
fi

# Specify config template
configSwitch=$1
puConfigTemplate="puInitConfigTemplate.xml"
prmConfigTemplate="prmInitConfigTemplate.xml"
prtConfigTemplate="prtInitConfigTemplate.xml"

case "$configSwitch" in
"pu")
    # using pu config template
    configTemplate=${puConfigTemplate}
    ;;
"prm")
    # using pr master config template
    configTemplate=${prmConfigTemplate}
    ;;
"prt")
    # using pr test config template
    configTemplate=${prtConfigTemplate}
    ;;
* )
    echo "Please specify valid config template type."
    exit ${NOMATCH}
    ;;
esac

# Job suffix and cur dir
bashExec=`which bash`
curDir=$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# Replace kw with specified parm
function replace_kw(){
    sed -re "s#<repo_name>#${1}#g; \
             s#<misid>#${misId}#g; \
             s#(<repositoryName>).*(</repositoryName>)#\1${1}\2#g; \
             s#(<url>).*(</url>)#\1${2}\2#g; \
             s#(sonar.projectKey=).*#\1${3}#g; \
             s#(sonar.projectName=).*#\1${4}#g" \
    ${curDir}/conf/${configTemplate} > ${curDir}/${configTemplate}.$$
}

# Define repo template, project prefix and trigger job with specified action
rt="repoTemplate.txt"
cs="com.sankuai"
qcs_repo="ssh://git@git.sankuai.com/qcs/"
pjk_suffix=":test"

while read git_repo_name;
do
    # specify sonar project prefix
    if [[ "$configSwitch" == "pu" ]]; then
        projectNamePrefix="qcs_push_"
    else
        projectNamePrefix="qcs_pull_request_"
    fi

    #if [[ ${git_repo_name/qcs_repo_name/} != $git_repo_name ]]; then
    #    continue
    #fi

    # define job parm and job list to access sonar
    declare -A array_var

    array_var[repo_name]="$git_repo_name"
    array_var[git_repo]="${qcs_repo}${array_var[repo_name]}.git"
    array_var[project_key]="${cs}:${projectNamePrefix}${array_var[repo_name]}"
    array_var[project_name]="${projectNamePrefix}${array_var[repo_name]}"

    # sonar with pr test branch
    if [[ "$configSwitch" == "prt" ]]; then
        array_var[project_key]="${cs}:${projectNamePrefix}${array_var[repo_name]}${pjk_suffix}"
        array_var[project_name]="${projectNamePrefix}${array_var[repo_name]}${pjk_suffix}"
    fi

    # perform access action
    replace_kw ${array_var[repo_name]} ${array_var[git_repo]} ${array_var[project_key]} ${array_var[project_name]}

    # specify job suffix
    if [[ "$configSwitch" == "pu" ]]; then
        jobSuf="_static-analyze-push"
    elif [[ "$configSwitch" == "prm" ]]; then
        jobSuf="_static-analyze-pr"
    else
        jobSuf="_test_static-analyze-pr"
    fi

    # create job to access sonar
    jobName=${array_var[repo_name]}${jobSuf}

    echo "accessing $git_repo_name to sonar."
    ${bashExec} ${curDir}/job_handler.sh -c ${jobName} -f ${curDir}/${configTemplate}.$$ \
    || exit ${E_CERROR}

    sleep ${STIME}

    # just build with pu job
    if [[ "$configSwitch" == "pu" ]]; then
        # we will not trigger it by manual or crontab for the moment
        :
        # sleep ${STIME}

        # build
        # ${bashExec} ${curDir}/job_handler.sh -s ${jobName}

        # build with parameters
        # ${bashExec} ${curDir}/job_handler.sh -s ${jobName} -p test
    fi

    # cleanup env
    rm -rf ${curDir}/${configTemplate}.$$ &> /dev/null
    echo "op $jobName done.."
    echo

done < ${curDir}/source/${rt}
