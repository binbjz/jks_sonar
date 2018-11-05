#!/usr/bin/env python
# filename: stash_repo_builder.py
#
# desc: First run, it will generate repo template as initial template,
# after this it will generate latest repo template. and then it will compare
# initial repo template and latest repo template and write differences into html.
#

import os
import sys
import difflib

import requests
import multiprocessing
from functools import partial
from datetime import datetime
from requests.auth import HTTPBasicAuth
from jenkins_sonar.jks_logger import logger
from jenkins_sonar.jks_utils import AuthHeaders, UtilityTools

# Set up a specific logger
logger = logger()

# Git auth
username = "<misid>"
passwd = "<password>"

# Template file
cur_dir = os.path.join(os.getcwd(), "source")
repo_template_init = os.path.join(cur_dir, "repo_template_init.txt")
repo_template_newer = os.path.join(cur_dir, "repo_template_newer.txt")
time_format = "{0}_{1}".format(datetime.now().strftime("%m-%d_%H-%S"), datetime.now().microsecond)
repos_file = "data_{0}.txt".format(time_format)


class RepoTplGenerator(object):
    """
    Counting and collecting QCS repository data.
    """

    def __init__(self):
        self.auth = AuthHeaders()
        self.utils = UtilityTools()
        self.timeout = (12.06, 26)
        self.json_file = os.path.join(os.getcwd(), "source", "repo_info.json")
        self.repo_url = "http://git.sankuai.com/rest/api/2.0/projects/qcs/repos?start=0&limit=1000"

    def handle_requests_status(self, res):
        """
        Handle http response status
        :param res: response data
        :return:
        """
        if res.status_code == requests.codes.ok:
            logger.info("response status code: {:d}".format(res.status_code))
            return True
        elif res.status_code >= 500:
            logger.error("request {:s}: [{:d}] {:s}".format(res.url, res.status_code, res.text))
            return False
        elif res.status_code >= 400:
            logger.error("request {:s}: [{:d}] {:s}".format(res.url, res.status_code, res.text))
            return False

    def get_qcs_repo_data(self, r_url):
        """
        Sends a GET request and get json data
        :param r_url: repo url
        :return:
        """
        try:
            _auth = HTTPBasicAuth(username, passwd)
            res = self.auth.requests_retry_session().get(r_url, auth=_auth, timeout=self.timeout)
        except requests.exceptions.RequestException as e:
            logger.error(e)
            sys.exit(1)

        if not self.handle_requests_status(res):
            return None

        res_data = res.json()
        return res_data

    def get_qcs_repo_list(self, repo_res_data, repo_list=None):
        """
        Get repo list which contains qcs all repos
        :param repo_res_data: repo response data
        :param repo_list:
        :return:
        """
        if repo_list is None:
            repo_list = []

        if repo_res_data is None:
            return

        rl = [l["slug"] for l in repo_res_data["values"]]
        repo_list.extend(rl)
        return repo_list

    def mul_proc_exec(self, filename, repo_list, arg_func):
        """
        More than one process be executed concurrently by using multiprocessing basics
        :param filename: store repo list into filename
        :param repo_list: qcs repo list
        :param arg_func: Concurrent processing func
        """
        jobs = []
        if repo_list is None:
            return

        for rl in repo_list:
            p = multiprocessing.Process(target=arg_func, args=(filename, rl))
            jobs.append(p)
            p.start()

    def mul_proc_exec_v2(self, filename, repo_list, arg_func):
        """
        More than one process be executed concurrently by using processing pool
        :param filename: store repo list into filename
        :param repo_list: qcs repo list
        :param arg_func: Concurrent processing func
        """
        pool_size = multiprocessing.cpu_count() * 3
        pool = multiprocessing.Pool(
            processes=pool_size,
        )
        if repo_list is None:
            return

        pool.map(partial(arg_func, filename), repo_list)
        pool.close()
        pool.join()

    def main_gen_proc(self):
        repo_data = self.get_qcs_repo_data(self.repo_url)

        # write json data into json file
        # self.utils.write_json_to_file(self.json_file, repo_data)

        # fetch all repo name in qcs and write them into repo template
        repo_lst = self.get_qcs_repo_list(repo_data)
        if not os.path.exists(repo_template_init):
            repo_template_temp = repo_template_init
        else:
            repo_template_temp = repo_template_newer
            if os.path.exists(repo_template_newer):
                os.remove(repo_template_newer)

        self.mul_proc_exec(repo_template_temp, repo_lst, self.utils.write_data_to_file)
        # self.mul_proc_exec_v2(repo_template_temp, repo_lst, self.utils.write_data_to_file)


class DiffGenerator(object):
    """
    Analyzing and generating discrepant data between older and newer QCS repository.
    """

    def __init__(self):
        self.utils = UtilityTools()
        self.diff_html = os.path.join(os.getcwd(), "source", "repo_diff.html")

    def diff_u(self, text1_lines, text2_lines):
        """
        Show only includes modified lines and a bit of context
        :param text1_lines:
        :param text2_lines:
        """
        diff = difflib.unified_diff(
            text1_lines,
            text2_lines,
            lineterm="",
        )
        print("\n".join(diff))

    def diff_h(self, text1_lines, text2_lines):
        """Produces HTML output with the different information into Diff file
        :param text1_lines:
        :param text2_lines:
        """
        d = difflib.HtmlDiff()
        result = d.make_file(text1_lines, text2_lines)
        try:
            with open(self.diff_html, "w+") as result_file:
                result_file.write(result)
                logger.info("Write diff into {0} successfully".format(self.diff_html))
        except IOError as error:
            logger.error("Error writing HTML file: {0}".format(error))

    def main_diff_proc(self):
        # write diff into html
        diff_1 = self.utils.read_file_to_list(repo_template_init)
        diff_2 = self.utils.read_file_to_list(repo_template_newer)
        self.diff_h(diff_1, diff_2)

        # redirect diff to stdout
        # self.diff_u(self.utils.read_file_to_list(repo_template_init),
        #             self.utils.read_file_to_list(repo_template_newer))


if __name__ == "__main__":
    RepoTplGenerator().main_gen_proc()
    DiffGenerator().main_diff_proc()
