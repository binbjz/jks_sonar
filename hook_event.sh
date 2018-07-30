#!/bin/bash
#filename: hook_event.sh
#
#desc: This script will configure user with repo permission, configure Stash Webhook and
#Events to Jenkins. It can only be used with cookie.
#

# define cookie, Just for convenience
cookie_var=`cat <<-SETVAR
Cookie: u=1116923364; uu=4be07e30-3713-11e8-934d-d9b8c00eab8a; cid=1; ai=1; _lxsdk_cuid=1628a79e52cc8-00ecf3d42e751-336c7b05-13c680-1628a79e52cc8; _lxsdk=1628a79e52cc8-00ecf3d42e751-336c7b05-13c680-1628a79e52cc8; userInfoInCode={%22name%22:%22%E8%B5%B5%E6%96%8C%22%2C%22account%22:%22zhaobin11%22%2C%22id%22:156877%2C%22emailAddress%22:%22zhaobin11@meituan.com%22}; _ga=GA1.2.1045501110.1524496289; sso.saveRequest=http%3A%2F%2Fgit.sankuai.com%2Fapi-wm%2Fimage%2Fvisible%3Fr%3D150%26g%3D150%26b%3D150%26deg%3D-20%26type%3D3; misId=zhaobin11; misId.sig=9zuVzbSovVyF8XvV2SwrCvZjv3Y; userId=2111863; userId.sig=MBrpLbAGY6kyVmDmKI84iKcVeMs; userName=%E8%B5%B5%E6%96%8C; userName.sig=kTU_ZzfsuxK9cUd1pqzb56E0H-Q; role=staff; UM_distinctid=1646996082a798-05316b61a5e8e6-16386952-13c680-1646996082b9db; skmtutc=c4B3PNJIcnAYORwEtKLNrXwfnlOEqyuiKlmbglLR/d+AFtUhM0B3/xPr7RuAEgor-a+LDOC1pxtR940eKoMgtzaozewA=; al=clrkmplcmqzcazqfrwhbzdmqbwjizpgw; beijing_sessionid=85B1AD2E3BC0E21C0B4DF37F69EAEA3A
SETVAR`

# user with repo permission
user_account="sonar"
user_permission=( REPO_READ REPO_WRITE REPO_ADMIN )

# hook rest url
qcs_repo="http://git.sankuai.com/beijing/rest/api/2.0/projects/qcs/repos"
hook_key_ap="settings/hooks/com.nerdwin15.stash-stash-webhook-jenkins%3AjenkinsPostReceiveHook"
hook_code_events="${qcs_repo}/${repo_name}/webhook/create/1?url=http%3A%2F%2Fci.sankuai.com%2Fgitlab%2Fbuild_now"


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

cr_hooks_code_events(){
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
    cr_hooks_code_events
}

echo_(){
    echo -e "\033[2;36m$1\033[0m"
}

# execution flow
rt="repoTemplate_temp.txt"
while read repo_name;
do
    hook_config_proc
done < ${rt}
