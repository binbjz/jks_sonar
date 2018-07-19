#!/bin/bash
#filename: parmTemplate.sh
#

# define owner
# example: misId=zhaobin11
misId=<misid>

# define prefix
cs=com.sankuai
qcs_repo=ssh://git.sankuai.com/qcs

if [[ "$configSwitch" == "pu" ]]; then
	projectNamePrefix=qcs_push_
else
	projectNamePrefix=qcs_pull_request_
fi

# define job parm and job list to access sonar
declare -A array1 array2 array3 array4

array1[repo_name]="qcs.settle.c.account12"
array1[git_repo]="${qcs_repo}/${array1[repo_name]}.git"
array1[project_key]="${cs}:${projectNamePrefix}${array1[repo_name]}"
array1[project_name]="${projectNamePrefix}${array1[repo_name]}"

array2[repo_name]="qcs.r.settle.invoice12"
array2[git_repo]="${qcs_repo}/${array2[repo_name]}.git"
array2[project_key]="${cs}:${projectNamePrefix}${array2[repo_name]}"
array2[project_name]="${projectNamePrefix}${array2[repo_name]}"

array3[repo_name]="qcs.budget.server12"
array3[git_repo]="${qcs_repo}/${array3[repo_name]}.git"
array3[project_key]="${cs}:${projectNamePrefix}${array3[repo_name]}"
array3[project_name]="${projectNamePrefix}${array3[repo_name]}"

array4[repo_name]="qcs.r.settle.server12"
array4[git_repo]="${qcs_repo}/${array4[repo_name]}.git"
array4[project_key]="${cs}:${projectNamePrefix}${array4[repo_name]}"
array4[project_name]="${projectNamePrefix}${array4[repo_name]}"

parm_list1="${array1[repo_name]} ${array1[git_repo]} ${array1[project_key]} ${array1[project_name]}"
parm_list2="${array2[repo_name]} ${array2[git_repo]} ${array2[project_key]} ${array2[project_name]}"
parm_list3="${array3[repo_name]} ${array3[git_repo]} ${array3[project_key]} ${array3[project_name]}"
parm_list4="${array4[repo_name]} ${array4[git_repo]} ${array4[project_key]} ${array4[project_name]}"

# confirm which service will be accessed.
# exmaple: jobList="parm_list1 parm_list2 parm_list3 parm_list4" or jobList="parm_list3"
jobList=<>
