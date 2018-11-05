#!/usr/bin/env python
# filename: jks_utils.py
#

import os
import csv
import json
import time
import hmac
import base64
import codecs
import hashlib
import datetime
import fileinput

import requests
from urllib3 import Retry
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from jenkins_sonar.jks_logger import logger

# Set up a specific logger
logger = logger()


class AuthHeaders(object):
    """
    Http Authorized Headers With MT Org
    """

    def get_auth_headers(self, api):
        gmt_time = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        string2sign = "GET {}\n{}".format(api, gmt_time)
        app_key = "<appkey>"
        app_secret = "<secret>"
        signature = base64.encodebytes(hmac.new(app_secret.encode("utf-8"),
                                                string2sign.encode("utf-8"),
                                                hashlib.sha1).digest()).replace(b"\n", b"").decode("utf-8")
        headers = {
            "Date": gmt_time,
            "Authorization": "MWS" + " " + app_key + ":" + signature,
        }
        return headers

    def requests_retry_session(
            self,
            retries=6,
            backoff_factor=0.5,
            status_forcelist=(500, 502, 504),
            session=None,
    ):
        with session or requests.session() as session:
            session.keep_alive = False
            retry = Retry(
                total=retries,
                read=retries,
                connect=retries,
                backoff_factor=backoff_factor,
                status_forcelist=status_forcelist,
            )
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
        return session

    def requests_retry_session_v2(self, session=None):
        with session or requests.Session() as session:
            session.keep_alive = False
            session.mount('http://', HTTPAdapter(max_retries=6))
            session.mount('https://', HTTPAdapter(max_retries=6))
        return session


class SonarTools(object):

    def __init__(self):
        self.td = "http://sonar.sankuai.com/api/tableData"
        self._auth = HTTPBasicAuth("<privileged user>", "<password>")
        self.auth = AuthHeaders()

    def get_group_info(self, filename):
        """
        Collect sonar filter info and write data into file
        :param filename:
        """
        response = self.auth.requests_retry_session().get(self.td, auth=self._auth)
        content = response.json()

        with open(filename, "a+") as csv_file:
            csv_file.write(codecs.BOM_UTF8.decode("utf-8"))
            csv_writer = csv.writer(csv_file, dialect='excel', lineterminator="\n")
            for item in content:
                info = "{},{},{},,".format(item["name"].rstrip("_"), item["showName"],
                                           item["parentKey"].rstrip("_")).split(",")
                csv_writer.writerow(info)


class UtilityTools(object):
    def get_git_address_without_user(self, git_address):
        """
        ssh://git@git.sankuai.com/qcs/qcs.fe.c.git
        :param git_address:
        :return: git.sankuai.com/qcs/qcs.fe.c.git
        """
        pos = git_address.find("@")
        if -1 != pos:
            return git_address[pos + 1:]
        return git_address

    def convert_milliseconds_to_time(self, millisecond):
        """
        :param millisecond: 1539830277000
        :return: 2018-10-18
        """
        if 0 == millisecond:
            return ""
        seconds = millisecond / 1000
        local = time.localtime(seconds)
        return time.strftime("%Y-%m-%d", local)

    def convert_milliseconds_to_date(self, millisecond):
        """
        :param millisecond: 1539830277000
        :return: 2018-10-18 00:00:00
        """
        time_date = self.convert_milliseconds_to_time(millisecond)
        convert_date = datetime.datetime.strptime(time_date, "%Y-%m-%d")
        return convert_date

    def get_today_date_time(self):
        """
        :return: 2018-10-18 00:00:00
        """
        time_date = time.strftime("%Y%m%d", time.localtime())
        current_date = datetime.datetime.strptime(time_date, "%Y%m%d")
        return current_date

    def milliseconds_delta(self, millisecond):
        """
        :param millisecond:
        :return: delta days
        """
        return (self.get_today_date_time() - self.convert_milliseconds_to_date(millisecond)).days

    def get_current_week(self):
        return self.get_date_week(datetime.datetime.today())

    def get_last_week(self):
        return self.get_last_date_week(datetime.datetime.today())

    def get_last_date_week(self, date):
        date += datetime.timedelta(days=-7)
        if date.weekday() in (5, 6):
            date += datetime.timedelta(days=-2)
        return self.get_date_week(date)

    def get_date_week(self, date):
        week_day = date.weekday()
        if week_day <= 4:
            start_day = date + datetime.timedelta(days=-week_day - 2)
            end_day = date + datetime.timedelta(4 - week_day)
        else:
            start_day = date + datetime.timedelta(days=-week_day + 5)
            end_day = date + datetime.timedelta(days=-week_day + 11)
        return "{}~{}".format(start_day.strftime("%Y%m%d"), end_day.strftime("%Y%m%d"))

    def git_split(self, git_address):
        git_info = git_address.split("/")
        """
        repos_end = git_info[-1].rfind(".")
        repos = git_info[-1][: repos_end]
        project = git_info[-2]
        """
        repos = git_info[-1]
        project = git_info[-3]
        return project, repos

    def read_file_to_list(self, filename):
        """
        Read file contents into list
        :param filename:
        :return:
        """
        try:
            with open(filename, "r+") as fn:
                repo_list = [line for line in fn]
            return repo_list
        except IOError:
            raise ValueError("Could not open {}".format(filename))

    def inplace_qcs_repo(self, filename, line_append):
        """
        Inplace qcs repo info in qcs repo template
        :param filename:
        :param line_append:
        """
        try:
            with fileinput.input(filename, inplace=True, backup='.bak') as file:
                for line in file:
                    _line = line.rstrip()
                    line = _line.replace(_line, "{}:{}".format(_line, line_append))
                    print(line)
        except IOError:
            raise ValueError("Could not open {}".format(filename))

    def write_json_to_file(self, filename, data):
        """
        Write json data into file
        :param filename:
        :param data: json data
        """
        des_file = os.path.expanduser(filename)
        try:
            with open(des_file, "w+", encoding="utf-8") as fp:
                json.dump(data, fp, indent=2)
        except IOError:
            raise ValueError("Could not open {}".format(filename))

    def write_data_to_file(self, filename, data, lf_flag=True):
        """
        Write normal data into file
        :param filename:
        :param data: normal text data
        :param lf_flag: True/Add a line break at the end of the line, False/Not add
        """
        lf = "\n" if lf_flag else ""
        des_file = os.path.expanduser(filename)
        try:
            with open(des_file, "a+", encoding="utf-8") as fp:
                fp.write(data + lf)
        except IOError:
            raise ValueError("Could not open {}".format(filename))

    def output_data_from_csv(self, filename):
        """
        Output data from cvs
        :param filename: csv file
        # utf-8-sig removes BOM if present
        """
        try:
            with open(filename, "r+", encoding='utf-8-sig') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=",")
                line_count = 0
                for row in csv_reader:
                    logger.info(row)
                    line_count += 1
        except IOError:
            raise ValueError("Could not open {}".format(filename))

    def read_data_from_csv(self, filename):
        """
        Return iterable obj from cvs
        :param filename: csv file
        # utf-8-sig removes BOM if present
        """
        try:
            csv_file = open(filename, "r+", encoding='utf-8-sig')
            csv_reader = csv.reader(csv_file, delimiter=",")
            return csv_reader
        except IOError:
            raise ValueError("Could not open {}".format(filename))

    def write_data_to_csv(self, filename, data):
        """
        Write data into csv, chinese characters need to be decoded
        :param filename: csv file name
        :param data: data list
        """
        try:
            with open(filename, "a+", encoding="utf-8") as csv_file:
                csv_file.write(codecs.BOM_UTF8.decode("utf-8"))
                csv_writer = csv.writer(csv_file, dialect='excel', lineterminator="\n")
                csv_writer.writerow(data)
        except IOError:
            raise ValueError("Could not open {}".format(filename))

    def init_csv_file(self, filename, fieldname):
        """
        Beginning of line already exist in file and write it, otherwise return
        :param filename:
        :param fieldname:
        """
        try:
            with open(filename, "a+", newline="", encoding="utf-8") as fp:
                if 0 == fp.tell():
                    if fieldname[-1] != "\n":
                        fieldname += "\n"
                    fp.write(fieldname)
        except IOError:
            raise ValueError("Could not open {}".format(filename))
