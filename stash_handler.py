#!/usr/bin/env python
# filename: stash_handler.py
#
# desc: collect and analyze stash info
#

import sys
import functools
import traceback as tb
from requests.auth import HTTPBasicAuth
from jenkins_sonar.jks_logger import logger
from jenkins_sonar.jks_utils import AuthHeaders, UtilityTools

# Set up a specific logger
logger = logger()


class StashHandleException(Exception):
    pass


class Stash(object):
    def __init__(self):
        self.auth = AuthHeaders()
        self.utils = UtilityTools()
        self.timeout = (12.06, 26)
        self.rest_api_prefix = "http://git.sankuai.com/rest/api/2.0"
        self.s = self.auth.requests_retry_session()
        self.req_auth = HTTPBasicAuth(username="<misid>", password="<password>")
        self.get = functools.partial(self.s.get, auth=self.req_auth, timeout=self.timeout)
        self.post = functools.partial(self.s.post, auth=self.req_auth, timeout=self.timeout)
        self.put = functools.partial(self.s.put, auth=self.req_auth, timeout=self.timeout)

    def get_branches(self, project, repos):
        """
        Branches info in the specified repos, default size and limit are 25
        :param project: qcs
        :param repos: qcs.fe.c
        :return:
        """
        query_url = "{}/projects/{}/repos/{}/branches".format(self.rest_api_prefix, project, repos)
        r = self.get(query_url)
        return r.json()

    def is_git_exists(self, git):
        """
        :param git: http://git.sankuai.com/rest/api/2.0/projects/qcs/repos/qcs.fe.c
        :return:
        """

        """
        if "git.sankuai.com" not in git:
            prefix = "http://git.dianpingoa.com/rest/api/1.0"
        else:
            prefix = self.rest_api_prefix
        """
        prefix = self.rest_api_prefix
        projects, repos = self.utils.git_split(git)
        api = "{}/projects/{}/repos/{}".format(prefix, projects, repos)
        r = self.get(api).json()
        if r.get("errors") is None:
            return True
        if r.get("errors")[0].get("exceptionName", "") == "com.atlassian.stash.exception.NoSuchRepositoryException":
            return False
        return True

    def get_all_branches(self, project, repos):
        """
        All branch info (id) in the specified repos
        :param project: qcs
        :param repos: qcs.fe.c
        :return:
        """
        query_url = "{}/projects/{}/repos/{}/branches".format(self.rest_api_prefix, project, repos)
        params = {
            "start": 0,
            "limit": 100
        }
        r = self.get(query_url, params=params).json()
        branch_list = []
        try:
            while True:
                for item in r["values"]:
                    branch_list.append(item["id"])
                if r["isLastPage"]:
                    break
                params["start"] += params["limit"]
                r = self.get(query_url, params=params).json()
        finally:
            return branch_list

    def get_branch_commit(self, project, repos, branch_id, param_dict=None):
        """
        Branch commit info in the specified repos branch, default size and limit are 25
        :param project: qcs
        :param repos: qcs.fe.c
        :param branch_id: master
        :param param_dict: {"start": 0, "limit": 100}
        :return:
        """
        if param_dict is None:
            param_dict = {}
        query_url = "{}/projects/{}/repos/{}/commits".format(self.rest_api_prefix, project, repos)
        params = {"until": branch_id}
        params.update(param_dict)
        r = self.get(query_url, params=params)
        return r.json()

    def get_most_n_committer(self, project, repos, branch_id, n=10, recent=20, flag=False):
        """
        N most frequent committer and the number of commits in the specified repos branch
        :param project: qcs
        :param repos: qcs.fe.c
        :param branch_id: master
        :param n: n most frequent committer
        :param recent: Extract the number of submitted records
        :param flag: True/committer mis, False/committer email
        :return: committer list
        """
        commiter_list = self.get_branch_commit(project, repos, branch_id)
        committer_map = {}
        try:
            # It is possible that an earlier committer might have left,
            # so consider only the most recent submitter.
            commiter_list = commiter_list["values"][:recent]
            for commit in commiter_list:
                if not flag:
                    committer = commit["author"]["emailAddress"]
                else:
                    _committer = commit["author"]["emailAddress"]
                    committer = _committer[:_committer.rfind("@")]
                count = committer_map.get(committer, 0) + 1
                committer_map[committer] = count
        except KeyError:
            pass
        most_committer = sorted(committer_map, key=lambda m: committer_map[m], reverse=True)
        return most_committer[:n]

    def get_branches_before_days(self, project, repos, delta_time=5):
        """
        Active branches info (id/displayId) within selectable delta time
        :param project: qcs
        :param repos: qcs.fe.c
        :param delta_time:
        :return:
        """
        query_url = "{}/projects/{}/repos/{}/branches?base=refs/heads/master&details=true&start=0&limit=20" \
                    "&orderBy=MODIFICATION".format(self.rest_api_prefix, project, repos)
        r = self.get(query_url)
        branches = []
        try:
            for item in r.json()["values"]:
                authorTimestamp = item["metadata"]["com.atlassian.stash.stash-branch-utils:latest-changeset-metadata"][
                    "authorTimestamp"]
                if self.utils.milliseconds_delta(authorTimestamp) > delta_time:
                    break
                branches.append({"id": item["id"], "displayId": item["displayId"]})
        except:
            tb.print_exc()
        finally:
            return branches

    def get_recent_commit_in_days(self, project, repos, delta_time=5):
        """
        Commit info in specified repo within a selectable recent delta time
        :param project: qcs
        :param repos: qcs.fe.c
        :param delta_time:
        :return: a list containing multiple tuple (email, branch, time)
        """
        branches = self.get_branches_before_days(project, repos, delta_time)
        committer_map = dict()
        for branch in branches:
            self.get_recent_commitor_by_time(project, repos, branch["id"], branch["displayId"],
                                             committer_map, delta_time)
        return [(key, value["branch"], self.utils.convert_milliseconds_to_time(value["time"]))
                for key, value in committer_map.items()]

    def get_recent_commitor_by_time(self, project, repos, branch_id, branch_name, committer_map, delta_time=5):
        """
        Committer info in the specified repos branch within a selectable delta time
        :param project: qcs
        :param repos: qcs.fe.c
        :param branch_id: master
        :param branch_name:
        :param committer_map:
        :param delta_time:
        :return: a dictionary containing multiple sub-dictionaries (email : branch, time)
        """
        params = {"start": 0, "limit": 100}
        greater_than_delta_time = False
        try:
            while True:
                commitor_list = self.get_branch_commit(project, repos, branch_id, params)
                for commit in commitor_list["values"]:
                    if self.utils.milliseconds_delta(commit["authorTimestamp"]) > delta_time:
                        greater_than_delta_time = True
                        break
                    # commitor = "{}({})".format(commit["author"]["emailAddress"],
                    #                            convert_milliseconds_to_time(commit["authorTimestamp"]))
                    commitor = commit["author"]["emailAddress"]
                    commit_info = committer_map.get(commitor, {})
                    recent_time = commit["authorTimestamp"]
                    if not commit_info:
                        committer_map[commitor] = commit_info
                        commit_info["time"] = recent_time
                        commit_info["branch"] = branch_name
                    if recent_time > commit_info["time"]:
                        commit_info["time"] = recent_time
                        commit_info["branch"] = branch_name
                if greater_than_delta_time or commitor_list["size"] < params["limit"]:
                    break
                params["start"] += params["limit"]

        except KeyError:
            pass
        return committer_map

    def get_max_commits_branch(self, project, repos):
        """
        Branches's name with the most commits, it's based on master
        :param project:
        :param repos:
        :return:
        """
        max_commits = 0
        max_branch = ("refs/heads/master", "master")
        branches = self.get_branches(project, repos)
        try:
            branches_list = branches["values"]
            for branch in branches_list:
                branch_commit = self.get_branch_commit(project, repos, branch["id"])
                size = branch_commit["size"]
                if size > max_commits:
                    max_commits = size
                    max_branch = (branch["id"], branch["displayId"])
        except KeyError:
            error_desc = sys._getframe().f_code.co_name + ": " + \
                         "project: {} repos {} error: {} ".format(project, repos, str(branches["errors"]))
            logger.error(error_desc)
            raise StashHandleException(error_desc)

        return max_branch

    def get_max_commits(self, project, repos):
        """
        Commit record for the most committed branch
        :param project:
        :param repos:
        :return:
        """
        max_commits = 0
        max_branch_commit = None
        branches = self.get_branches(project, repos)
        branches_list = branches["values"]
        for branch in branches_list:
            branch_commit = self.get_branch_commit(project, repos, branch["id"])
            size = branch_commit["size"]
            if size > max_commits:
                max_commits = size
                max_branch_commit = branch_commit

        return max_branch_commit

    def get_recent_pull_request(self, project, repos):
        """
        Recent pull request branch
        :param project:
        :param repos:
        :return:
        """
        query_url = "{}/projects/{}/repos/{}/pull-requests".format(
            self.rest_api_prefix, project, repos)
        params = {"state": "merged"}
        pull_info = self.get(query_url, params=params).json()
        try:
            if 0 == pull_info["size"]:
                return None
            return pull_info["values"][0]["toRef"]["id"], pull_info["values"][0]["toRef"]["displayId"]
        except KeyError:
            error_desc = sys._getframe().f_code.co_name + ": " + \
                         "project: {} repos {} error: {} ".format(project, repos, str(pull_info["errors"]))
            logger.error(error_desc)
            raise StashHandleException(error_desc)

    def get_max_pull_request(self, project, repos):
        """
        Most frequent pull request branch
        :param project:
        :param repos:
        :return:
        """
        query_url = "{}/projects/{}/repos/{}/pull-requests".format(
            self.rest_api_prefix, project, repos)
        params = {"state": "merged"}
        pull_info = self.get(query_url, params=params).json()
        merge_dict = {}
        try:
            if 0 == pull_info["size"]:
                return None
            for merge_info in pull_info["values"]:
                count = merge_dict.get(merge_info["toRef"]["id"], [merge_info["toRef"]["displayId"], 0])
                count[1] += 1
                merge_dict[merge_info["toRef"]["id"]] = count
            # Search the most frequent pull request merge
            max_key = max(merge_dict, key=lambda m: merge_dict[m][1])
            return max_key, merge_dict[max_key][0]  # return id, displayid
        except KeyError:
            error_desc = sys._getframe().f_code.co_name + ": " + \
                         "project: {} repos {} error: {} ".format(project, repos, str(pull_info))
            logger.error(error_desc)
            raise StashHandleException(error_desc)

    def get_pull_request(self, project, repos, params=None):
        """
        Pull request info
        :param project:
        :param repos:
        :param params:
        :return:
        """
        if params is None:
            params = {}
        query_url = "{}/projects/{}/repos/{}/pull-requests".format(
            self.rest_api_prefix, project, repos)
        params["state"] = "merged"
        return self.get(query_url, params=params).json()

    def get_max_pull_request_v2(self, project, repos):
        params = {"start": 0, "limit": 3000}
        branch_list = self.get_all_branches(project, repos)
        pull_info = self.get_pull_request(project, repos, params)
        merge_branch_info = {}
        try:
            while True:
                for item in pull_info["values"]:
                    # Merge into another branch and the branch is effective
                    if item["fromRef"]["id"] != item["toRef"]["id"] and item["toRef"]["id"] in branch_list:
                        merge_branch_info[item["toRef"]["id"]] = merge_branch_info.get(item["toRef"]["id"], 0) + 1
                if pull_info["isLastPage"]:
                    break
                params["start"] += params["limit"]
                pull_info = self.get_pull_request(project, repos, params)
        except KeyError:
            error_desc = sys._getframe().f_code.co_name + ": " + \
                         "project: {} repos {} error: {} ".format(project, repos, str(pull_info))
            logger.error(error_desc)
            raise StashHandleException(error_desc)
        finally:
            branch_id_sorted = sorted(merge_branch_info, reverse=True)
            if 0 == len(branch_id_sorted):
                return None
            branch_id = branch_id_sorted[0]
            display_id = branch_id[branch_id.rfind("/") + 1:]
            return branch_id, display_id

    def get_most_possible_branch(self, project, repos):
        """
        Get the branch info that most likely to be on-line branch
        :param project: refs/heads/master
        :param repos: master
        :return:
        """
        return "refs/heads/master", "master"

    def get_hook_stash_status(self, git_address):
        """
        Check hook stash status
        :param git_address: ssh://git@git.sankuai.com/qcs/qcs.fe.c.git
        :return: enable:1 | disable:0
        """
        git_info = git_address.split("/")
        repos_end = git_info[-1].rfind(".")
        repos_name = git_info[-1][:repos_end]
        project = git_info[-2]
        hook_name = "com.nerdwin15.stash-stash-webhook-jenkins:jenkinsPostReceiveHook"
        sonar_hook_status_url = "{}/projects/{}/repos/{}/settings/hooks".format(
            self.rest_api_prefix, project, repos_name)
        hook_status = self.get(sonar_hook_status_url).json()
        try:
            for plugin in hook_status["values"]:
                # It will not be set if it has been set
                if hook_name == plugin["details"]["key"]:
                    if plugin["enabled"]:
                        return 1
                    else:
                        return 0
                    # break
        except KeyError:
            return -1

    def set_hook_code_push_event(self, project, repos):
        """
        Configure Stash Push Event
        :param project:
        :param repos:
        """
        old_rule = "http%3A%2F%2Fci.ee.test.sankuai.com%2Fgitlab%2Fbuild_now"
        new_rule = "http%3A%2F%2Fci.ee.test.sankuai.com%2Fgitlab%2Fbuild_now"
        event_rule_url = "webhook/create/1?url={}".format(new_rule)
        hook_code_push_event_url = "{}/projects/{}/repos/{}/{}".format(self.rest_api_prefix, project,
                                                                       repos, event_rule_url)
        try:
            self.post(hook_code_push_event_url)

        except Exception as err:
            raise StashHandleException(err)
        return True

    def set_sonar_hook(self, project, repos, git_address):
        """
        Config sonar hook to trigger static code scans when you commit code
        :param project:
        :param repos:
        :param git_address: ssh://git@git.sankuai.com/qcs/qcs.fe.c.git
        :return:
        """
        hook_name = "com.nerdwin15.stash-stash-webhook-jenkins:jenkinsPostReceiveHook"
        sonar_hook_status_url = "{}/projects/{}/repos/{}/settings/hooks".format(
            self.rest_api_prefix, project, repos)
        hook_status = self.get(sonar_hook_status_url).json()
        try:
            for plugin in hook_status["values"]:
                # If it is already set, it will not be set
                if hook_name == plugin["details"]["key"]:
                    if plugin["enabled"]:
                        return True
                    break
        except KeyError:
            raise StashHandleException(hook_status["errors"])
        sonar_hook_url = "{}/projects/{}/repos/{}/settings/hooks/{}/enabled".format(
            self.rest_api_prefix, project, repos, hook_name)
        json_content = {
            "jenkinsBase": "http://ci.ee.test.sankuai.com",
            "gitRepoUrl": git_address,
            "ignoreCommitters": "",
            "branchOptions": "",
            "branchOptionsBranches": ""
        }
        r = self.put(sonar_hook_url, json=json_content).json()
        if "errors" in r:
            raise StashHandleException(str(r))
        return True

    def get_latest_commit_time(self, project, repos):
        """
        Latest commit time
        :param project:
        :param repos:
        :return:
        """
        query_url = "{}/projects/{}/repos/{}/branches?details=true&" \
                    "orderBy=MODIFICATION&limit=1".format(self.rest_api_prefix, project, repos)
        r = self.get(query_url).json()
        try:
            return r["values"][0]["metadata"]["com.atlassian.stash.stash-branch-utils:"
                                              "latest-changeset-metadata"]["authorTimestamp"]
        except IndexError:
            logger.error("project: {}, repos: {} get lateset commit time error".format(project, repos))
            return 0
        except KeyError:
            logger.error("project: {}, repos: {} get lateset commit time error".format(project, repos))
            return 0

    def get_create_time(self, project, repos):
        """
        Initial repo create time
        :param project:
        :param repos:
        :return:
        """
        query_url = "{}/projects/{}/repos/{}/commits".format(self.rest_api_prefix, project, repos)
        params = {
            "until": "refs/heads/master",
            "start": 0,
            "limit": 6000
        }
        r = self.get(query_url, params=params).json()
        try:
            while not r["isLastPage"]:
                params["start"] += params["limit"]
                r = self.get(query_url, params=params).json()
            return r["values"][-1]["authorTimestamp"]
        except IndexError as e:
            if "errors" in r:
                logger.error("get create time error: {} - {}".format(e, r["errors"]))
            else:
                logger.error("get create time error: {}".format(e))
            return 0
        except KeyError as e:
            if "errors" in r:
                logger.error("get create time error: {} - {}".format(e, r["errors"]))
            else:
                logger.error("get create time error: {}".format(e))
            return 0

    def get_total_pull_request(self, project, repos):
        """
        The total number of pull request
        :param project:
        :param repos:
        :return:
        """
        query_url = "{}/projects/{}/repos/{}/pull-requests".format(
            self.rest_api_prefix, project, repos)
        params = {"state": "merged", "start": 0, "limit": 100}
        pull_info = self.get(query_url, params=params).json()
        size = 0
        try:
            while True:
                size += pull_info["size"]
                if pull_info["isLastPage"]:
                    break
                params["start"] += params["limit"]
                pull_info = self.get(query_url, params=params).json()
        except KeyError:
            error_desc = sys._getframe().f_code.co_name + ": " + \
                         "project: {} repos {} error: {} ".format(project, repos, str(pull_info))
            logger.error(error_desc)
            raise StashHandleException(error_desc)
        finally:
            return size
