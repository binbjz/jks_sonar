#!/bin/bash
#filename: stash_hook_event.sh
#
#desc: This script will configure user with repo permission,
# configure Stash Webhook and Events to Jenkins.
#

# Define Auth
username="<misid>"
passwd="<password>"

# User with repo permission, Stash webhook switch.
user_account="sonar"
user_permission=( REPO_READ REPO_WRITE REPO_ADMIN )
swh_switch=( PUT DELETE )

# Hook rest url
qcs_repo="http://git.sankuai.com/beijing/rest/api/2.0/projects/QCS/repos"
hook_key_ap="settings/hooks/com.nerdwin15.stash-stash-webhook-jenkins%3AjenkinsPostReceiveHook"

# Hook event rule
old_rule="http%3A%2F%2Fci.sankuai.com%2Fgitlab%2Fbuild_now"
new_rule="http%3A%2F%2Fqcs.ci.ee.test.sankuai.com%2Fgitlab%2Fbuild_now"

function user_access() {
    # Required -> -H "Accept: application/json, text/javascript, */*; q=0.01"
    echo_ "adding ${1} into $repo_name with permission:${2}"
    curl -s -u ${username}:${passwd} -X PUT "${qcs_repo}/${repo_name}/permissions/users?permission=${2}&name=${1}" -H "Accept: application/json, text/javascript, */*; q=0.01"
    echo -e "op $repo_name done..\n"
}

function cu_hooks_StashWebhookToJenkins() {
    # Disabled -X DELETE, Enabled -X PUT
    act=`((${#1} < 6)) && echo "enabling" || echo "disabling"`
    echo_ "$act $repo_name Stash Webhook to Jenkins"
    curl -s -u ${username}:${passwd} -X ${1} "${qcs_repo}/${repo_name}/${hook_key_ap}/enabled" -H "Content-Type: application/json"
    echo -e "\nop $repo_name done..\n"
}

function config_hooks_StashWebhookToJenkins() {
    # Required -> -H 'Content-Type: application/json'
    echo_ "configuring $repo_name Stash Webhook to Jenkins"
    curl -s -u ${username}:${passwd} -X PUT "${qcs_repo}/${repo_name}/${hook_key_ap}/settings" -H "Content-Type: application/json" --data-binary "${payload_json}"
    echo -e "\nop $repo_name done..\n"
}

function config_hooks_code_events() {
    echo_ "configuring $repo_name Webhook with event to Jenkins"
    curl -s -u ${username}:${passwd} -X POST "${qcs_repo}/${repo_name}/webhook/create/1?url=${new_rule}" -H "Content-Type: application/json"
    echo -e "\nop $repo_name done..\n"
}

function echo_() {
    echo -e "\033[2;36m$1\033[0m"
}

function hook_config_proc() {
    # Http payload
    jenkinsBase="http://ci.sankuai.com/"
    gitRepoUrl="ssh://git@git.sankuai.com/qcs/${repo_name}.git"
    ignoreCommitters=""

    # Stash Webhook for Build from
    #branchOptions:"whitelist"
    #branchOptionsBranches:"master test"

    # Stash Webhook for Build all
    #branchOption:""
    #branchOptionsBranches:""

    # Stash Webhook for Ignore from
    branchOptions="blacklist"
    branchOptionsBranches="master test"

    payload='{"jenkinsBase":"%s","gitRepoUrl":"%s","ignoreCommitters":"%s","branchOptions":"%s","branchOptionsBranches":"%s"}'
    payload_json=$(printf "$payload" "$jenkinsBase" "$gitRepoUrl" "$ignoreCommitters" "$branchOptions" "$branchOptionsBranches")

    # Repo permission
    user_access ${user_account} ${user_permission[0]}

    # Stash Webhook to Jenkins
    cu_hooks_StashWebhookToJenkins ${swh_switch[1]}
    #config_hooks_StashWebhookToJenkins

    # Webhook with event
    config_hooks_code_events
}

# Executing Process
rt="repo_template_newer.txt"
while read repo_name;
do
    hook_config_proc
done < ${rt}
