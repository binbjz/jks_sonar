#!/bin/bash
#filename: hook_event.sh
#
#desc: This script will configure user with repo permission, configure Stash Webhook and
#Events to Jenkins. It can only be used with cookie.
#

# define cookie, Just for convenience
cookie_var=`cat <<-SETVAR
<input your cookie here>
SETVAR`

# user with repo permission
user_account="sonar"
user_permission=( REPO_READ REPO_WRITE REPO_ADMIN )

# hook rest url
qcs_repo="http://git.sankuai.com/beijing/rest/api/2.0/projects/qcs/repos"
hook_key_ap="settings/hooks/com.nerdwin15.stash-stash-webhook-jenkins%3AjenkinsPostReceiveHook"


user_access(){
    # required -> -H "Accept: application/json, text/javascript, */*; q=0.01"
    echo_ "adding $user_account into $repo_name with permission:${user_permission[0]}"
    curl -s -X PUT "${qcs_repo}/${repo_name}/permissions/users?permission=${user_permission[0]}&name=${user_account}" -H "${cookie_var}" -H "Accept: application/json, text/javascript, */*; q=0.01"
    echo -e "op $repo_name done..\n"
}

cu_hooks_StashWebhookToJenkins(){
    echo_ "disabling $repo_name Stash Webhook to Jenkins"
    # Disabled -X DELETE, Enabled -X PUT
    curl -s -X DELETE "${qcs_repo}/${repo_name}/${hook_key_ap}/enabled" -H "${cookie_var}"
    echo -e "\nop $repo_name done..\n"
}

config_hooks_StashWebhookToJenkins(){
    # required -> -H 'Content-Type: application/json'
    echo_ "configuring $repo_name Stash Webhook to Jenkins"
    curl -s -X PUT "${qcs_repo}/${repo_name}/${hook_key_ap}/settings" -H "${cookie_var}" -H "Content-Type: application/json" --data-binary "${payload_json}"
    echo -e "\nop $repo_name done..\n"
}

config_hooks_code_events(){
    echo_ "configuring $repo_name Webhook with event to Jenkins"
    curl -s -X POST "${qcs_repo}/${repo_name}/webhook/create/1?url=http%3A%2F%2Fci.sankuai.com%2Fgitlab%2Fbuild_now" -H "Content-Type: application/json" -H "${cookie_var}"
    echo -e "\nop $repo_name done..\n"
}

hook_config_proc(){
    # http payload
    jenkinsBase="http://ci.sankuai.com/"
    gitRepoUrl="ssh://git@git.sankuai.com/qcs/${repo_name}.git"
    ignoreCommitters=""
    branchOptions="blacklist"
    branchOptionsBranches="master test"

    payload='{"jenkinsBase":"%s","gitRepoUrl":"%s","ignoreCommitters":"%s","branchOptions":"%s","branchOptionsBranches":"%s"}'
    payload_json=$(printf "$payload" "$jenkinsBase" "$gitRepoUrl" "$ignoreCommitters" "$branchOptions" "$branchOptionsBranches")

    # repo permission
    user_access

    # Stash Webhook to Jenkins
    cu_hooks_StashWebhookToJenkins
    #config_hooks_StashWebhookToJenkins

    # Webhook with event
    config_hooks_code_events
}

echo_(){
    echo -e "\033[2;36m$1\033[0m"
}

# execution flow
rt="repoTemplate.txt"
while read repo_name;
do
    hook_config_proc
done < ${rt}
