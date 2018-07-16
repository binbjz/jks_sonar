#!/bin/bash
#filename: job_dispatcher.sh
#
#desc: access sonar by jenkins with manual, crontab, push or pull request to trigger. 
#

NOARGS=65
NOMATCH=122 
E_CERROR=129

# check parm num
if [ $# -ne 1 ]; then
   echo "Usage: ${BASH_SOURCE[0]} pu|pr"
   exit $NOARGS
fi

# specify config template
configSwitch=$1
puConfigTemplate=puInitConfigTemplate.xml
prConfigTemplate=prInitConfigTemplate.xml

case "$configSwitch" in
"pu")
    # using pu config template
    configTemplate=$puConfigTemplate
    ;;
"pr")
    # using pull request config template
    configTemplate=$prConfigTemplate
    ;;
* )
    echo "Please specify valid config template type"
    exit $NOMATCH
    ;;
esac

# misid, job suffix and cur dir
misId=zhaobin11
bashExec=`which bash`
jobSuf="_static-analyze"
curDir="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# replace kw with specified parm
replace_kw(){
    sed -re "s#<repo_name>#${1}#g; \
             s#<misid>#${misId}#g; \
             s#(<repositoryName>).*(</repositoryName>)#\1${1}\2#g; \
             s#(<url>).*(</url>)#\1${2}\2#g; \
             s#(sonar.projectKey=).*#\1${3}#g; \
             s#(sonar.projectName=).*#\1${4}#g" \
    $configTemplate > $curDir/$configTemplate.$$
}

# define job parm and job list
declare -A array1 array2 array3

array1[repo_name]="qcs.settle.c.account"
array1[git_repo]="ssh://git.sankuai.com/qcs/qcs.settle.c.account.git"
array1[project_key]="com.sankuai:qcs_settle_c-account"
array1[project_name]="qcs_settle_c-account"

array2[repo_name]="qcs.r.settle.invoice"
array2[git_repo]="ssh://git@git.sankuai.com/qcs/qcs.r.settle.invoice.git"
array2[project_key]="com.sankuai:qcs_r_settle-invoice"
array2[project_name]="qcs_r_settle-invoice"

array3[repo_name]="qcs.budget.server"
array3[git_repo]="ssh://git@git.sankuai.com/qcs/qcs.budget.server.git"
array3[project_key]="com.sankuai:qcs_budget-server"
array3[project_name]="qcs_budget-server"

parm_list1="${array1[repo_name]} ${array1[git_repo]} ${array1[project_key]} ${array1[project_name]}"
parm_list2="${array2[repo_name]} ${array2[git_repo]} ${array2[project_key]} ${array2[project_name]}"
parm_list3="${array3[repo_name]} ${array3[git_repo]} ${array3[project_key]} ${array3[project_name]}"

#jobList="parm_list1 parm_list2 parm_list3"
jobList="parm_list3"

# perform action
for job in $jobList;
do
    set -- ${!job}
    replace_kw $1 $2 $3 $4
    
    # create job with sonar
    jobName=${1}${jobSuf}
    $bashExec ${curDir}/job_handler.sh -c $jobName -f ${curDir}/${configTemplate}.$$ \
    || exit $E_CERROR
    echo
    
    # just build with pu job
    if [[ "$configSwitch" == "pu" ]]; then
        sleep 2
    
        # build
        #$bashExec ${curDir}/job_handler.sh -s $jobName
    
        # build with parameters
        $bashExec ${curDir}/job_handler.sh -s $jobName -p test
    fi
    
    # cleanup env
    rm -rf ${curDir}/${configTemplate}.$$ &> /dev/null
    echo "op $jobName done.."
    echo
done
