#!/bin/bash
#filename: parmTemplate.sh
#

# define owner
# example: misId=zhaobin11
misId=<misid>

# define job parm and job list to access sonar
declare -A array1 array2 array3 array4

array1[repo_name]="qcs.settle.c.account12"
array1[git_repo]="ssh://git.sankuai.com/qcs/qcs.settle.c.account12.git"
array1[project_key]="com.sankuai:qcs_settle_c-account12"
array1[project_name]="qcs_settle_c-account12"

array2[repo_name]="qcs.r.settle.invoice12"
array2[git_repo]="ssh://git@git.sankuai.com/qcs/qcs.r.settle.invoice.git12"
array2[project_key]="com.sankuai:qcs_settle_r-settle-invoice12"
array2[project_name]="qcs_settle_r-settle-invoice12"

array3[repo_name]="qcs.budget.server12"
array3[git_repo]="ssh://git@git.sankuai.com/qcs/qcs.budget.server12.git"
array3[project_key]="com.sankuai:qcs_settle_budget-server12"
array3[project_name]="qcs_settle_budget-server12"

array4[repo_name]="qcs.r.settle.server12"
array4[git_repo]="ssh://git@git.sankuai.com/qcs/qcs.r.settle.server12.git"
array4[project_key]="com.sankuai:qcs_settle_r-settle-server12"
array4[project_name]="qcs_settle_r-settle-server12"

parm_list1="${array1[repo_name]} ${array1[git_repo]} ${array1[project_key]} ${array1[project_name]}"
parm_list2="${array2[repo_name]} ${array2[git_repo]} ${array2[project_key]} ${array2[project_name]}"
parm_list3="${array3[repo_name]} ${array3[git_repo]} ${array3[project_key]} ${array3[project_name]}"
parm_list4="${array4[repo_name]} ${array4[git_repo]} ${array4[project_key]} ${array4[project_name]}"

# confirm which service will be accessed.
# exmaple: jobList="parm_list1 parm_list2 parm_list3 parm_list4" or jobList="parm_list3"
jobList=<job list>
