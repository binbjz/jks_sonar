#!/usr/bin/env python
# filename: repo_handler.py
#
# desc: First run, it will generate repo template as initial template,
# after this it will generate latest repo template. and then it will compare
# initial repo template and latest repo template and write differences into html.
#

import os
import sys
import json
import logging
import difflib
import requests
import multiprocessing
from datetime import datetime
from requests.auth import HTTPBasicAuth

# Default log handler
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s",
)

# Git auth
username = "<misid>"
passwd = "<password>"

# Template file
cur_dir = os.path.join(os.getcwd(), "source")
repo_template_path = os.path.join(cur_dir, "repoTemplate.txt")
repo_template_newer_path = os.path.join(cur_dir, "repoTemplate_newer.txt")
time_format = "{0}_{1}".format(datetime.now().strftime("%m-%d_%H-%S"), datetime.now().microsecond)
repos_file = "data_{0}.txt".format(time_format)


class RepoTplGenerator(object):
    """
    Counting and collecting QCS repository data.
    """

    def __init__(self):
        self.timeout = (3.06, 26)
        self.json_file = os.path.join(os.getcwd(), "source", "repoInfo.json")
        self.repo_url = "http://git.sk.com/rest/api/2.0/projects/qcs/repos?start=0&limit=1000"

    def write_json_to_file(self, filename, data):
        """
        Write json data into file
        :param filename:
        :param data: json data
        """
        des_file = os.path.expanduser(filename)
        with open(des_file, "w+", encoding="utf-8") as fp:
            json.dump(data, fp, indent=2)

    def write_data_to_file(self, filename, data):
        """
        Write normal data into file
        :param filename:
        :param data: normal text data
        """
        des_file = os.path.expanduser(filename)
        with open(des_file, "a+", encoding="utf-8") as fp:
            fp.write(data + "\n")

    def handle_requests_status(self, res):
        """
        Handle http response status
        :param res: response data
        :return:
        """
        if res.status_code == requests.codes.ok:
            logging.info("response status code: {:d}".format(res.status_code))
            return True
        elif res.status_code >= 500:
            logging.error("request {:s}: [{:d}] {:s}".format(res.url, res.status_code, res.text))
            return False
        elif res.status_code >= 400:
            logging.error("request {:s}: [{:d}] {:s}".format(res.url, res.status_code, res.text))
            return False

    def get_qcs_repo_data(self, r_url):
        """
        Sends a GET request and get json data
        :param r_url: repo url
        :return:
        """
        try:
            _auth = HTTPBasicAuth(username, passwd)
            res = requests.get(r_url, auth=_auth, timeout=self.timeout)
        except requests.exceptions.RequestException as e:
            logging.error(e)
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
        More than one process be executed concurrently
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

    def main_gen_proc(self):
        repo_data = self.get_qcs_repo_data(self.repo_url)

        # write json data into json file
        # self.write_json_to_file(self.json_file, repo_data)

        # fetch all repo name in qcs and write them into repo template
        repo_lst = self.get_qcs_repo_list(repo_data)
        if not os.path.exists(repo_template_path):
            repo_template_temp = repo_template_path
        else:
            repo_template_temp = repo_template_newer_path
            if os.path.exists(repo_template_newer_path):
                os.remove(repo_template_newer_path)

        self.mul_proc_exec(repo_template_temp, repo_lst, self.write_data_to_file)


class DiffGenerator(object):
    """
    Analyzing and generating discrepant data between older and newer QCS repository.
    """

    def __init__(self):
        self.diff_html = os.path.join(os.getcwd(), "source", "repoDiff.html")

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
                logging.info("Write diff into {0} successfully".format(self.diff_html))
        except IOError as error:
            logging.error("Error writing HTML file: {0}".format(error))

    def read_file(self, filename):
        """Return a list of the lines in the string, breaking at line boundaries"""
        try:
            with open(filename, "r+") as fileHandle:
                text = fileHandle.read().splitlines()
            return text
        except IOError as error:
            logging.error("Read file Error:" + str(error))
            sys.exit(1)

    def main_diff_proc(self):
        # write diff into html
        diff_1 = self.read_file(repo_template_path)
        diff_2 = self.read_file(repo_template_newer_path)
        self.diff_h(diff_1, diff_2)

        # redirect diff to stdout
        # self.diff_u(self.read_file(repo_template_path), self.read_file(repo_template_newer_path))


if __name__ == "__main__":
    RepoTplGenerator().main_gen_proc()
    DiffGenerator().main_diff_proc()
