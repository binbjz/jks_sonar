#!/bin/bash
#filename: parmTemplate.sh
#

# define owner
# example: misId=zhaobin11
misId=<misid>

# define job parm and job list to access sonar
declare -A array1 array2 array3

array1[repo_name]="qcs.settle.c.account12"
array1[git_repo]="ssh://git.sankuai.com/qcs/qcs.settle.c.account12.git"
array1[project_key]="com.sankuai:qcs_settle_c-account12"
array1[project_name]="qcs_settle_c-account12"

array2[repo_name]="qcs.r.settle.invoice12"
array2[git_repo]="ssh://git@git.sankuai.com/qcs/qcs.r.settle.invoice12.git"
array2[project_key]="com.sankuai:qcs_r_settle-invoice12"
array2[project_name]="qcs_r_settle-invoice12"

array3[repo_name]="qcs.budget.server12"
array3[git_repo]="ssh://git@git.sankuai.com/qcs/qcs.budget.server12.git"
array3[project_key]="com.sankuai:qcs_budget-server12"
array3[project_name]="qcs_budget-server12"

parm_list1="${array1[repo_name]} ${array1[git_repo]} ${array1[project_key]} ${array1[project_name]}"
parm_list2="${array2[repo_name]} ${array2[git_repo]} ${array2[project_key]} ${array2[project_name]}"
parm_list3="${array3[repo_name]} ${array3[git_repo]} ${array3[project_key]} ${array3[project_name]}"

# confirm which service will be accessed.
# exmaple: jobList="parm_list1 parm_list2 parm_list3" or jobList="parm_list3"
jobList=<job list>
