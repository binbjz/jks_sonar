#!/usr/bin/env python
#filename: repo_handler.py
#

import os
import sys
import json
import logging
import requests
import multiprocessing
from datetime import datetime


# define logger
logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s",
        )

# define auth
username=<misid>
passwd=<password>
url="http://git.sankuai.com/rest/api/2.0/projects/qcs/repos?start=0&limit=1000"

# define json and template file
json_file="repoJson.txt"
repo_template="repoTemplate.txt"
time_format="{0}_{1}".format(datetime.now().strftime("%m-%d_%H-%S"), datetime.now().microsecond)
repos_file="data_{0}.txt".format(time_format)


def write_json_to_file(filename, data):
    """write json data into file"""
    des_file = os.path.expanduser(filename)
    with open(des_file, "w+", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2)

def write_data_to_file(filename, data_lst):
    """write normal data into file"""
    des_file = os.path.expanduser(filename)
    with open(des_file, "a+", encoding="utf-8") as fp:
        for data in data_lst:
            fp.write(data + '\n')

def handle_requests_status(res):
    """handle http response status"""
    if res.status_code == requests.codes.ok:
        logging.info("response status code: {:d}".format(res.status_code))
        return True
    elif res.status_code >= 500:
        logging.info("request {0:s}: [{1:d}] {2:s}".format(res.url, res.status_code, res.content))
        return False
    elif res.status_code >= 400:
        logging.info("request {0:s}: [{1:d}] {2:s}" % (res.url, res.status_code, res.content))
        return False

def get_qcs_repo_data(url):
    """sends a GET request and get json data"""
    try:
        res = requests.get(url, auth=(username, passwd), timeout = 12)
    except BaseException as e:
        logging.info("Exception occurred while connecting {}\n".format(url))
        sys.exit(1)

    if not handle_requests_status(res):
    	return None

    res_data = res.json()
    return res_data

def get_qcs_repo_list(repo_res_data, repo_list = None):
    """get repo list which contains qcs all repos"""
    if repo_list is None:
        repo_list = []

    repo_list = [l["slug"] for l in repo_res_data["values"]]
    return repo_list

def mul_proc_exec(filename, repo_list, argfunc):
    jobs = []
    p = multiprocessing.Process(target=argfunc, args=(filename, repo_list))
    jobs.append(p)
    p.start()


if __name__ == "__main__":
    repo_data = get_qcs_repo_data(url)

    # write json data into json file
    #write_json_to_file(json_file, repo_data)

    # fetch all repo name in qcs and write them into repo template
    repo_lst = get_qcs_repo_list(repo_data)
    mul_proc_exec(repo_template, repo_lst, write_data_to_file)
