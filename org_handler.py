#!/usr/bin/env python
# filename: org_handler.py
#
# desc: MT org architecture
#

import logging
from jenkins_sonar.utils_tools import AuthHeaders, UtilityTools

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s",
)

API_MAP = {
    "emp_info": "/api/v3/currentempinfo/get",
    "base_info": "/api/orgemp/getEmpBaseInfo",
    "complete_info": "/api/v3/getCompleteInfo",
    "direct_header": "/api/2/employee/getDirectHeaderById",
    "direct_lower": "/api/2/employee/getDirectLowersById",
}


class OrgInfoException(Exception):
    pass


class OrgInfo(object):
    """
    Collect MT Org Info with specified mis
    """

    def __init__(self):
        self.auth = AuthHeaders()
        self.utils = UtilityTools()
        self.timeout = (16.06, 26)
        self.host = "http://api.org-in.sankuai.com"

    def parms_tmpl(self, mis):
        """
        Specified data in a POST request
        :param mis:
        """
        params = {
            # "leaveOfficeDays": 5000,
            "login": mis,
            "name": mis
        }
        return params

    def get_base_info(self, mis):
        """
        Base info with specified mis
        :param mis: mis id
        :return:
        """
        api = API_MAP["base_info"]
        params = self.parms_tmpl(mis)
        headers = self.auth.get_auth_headers(api)
        response = self.auth.requests_retry_session().get(self.host + api, params=params,
                                                          headers=headers, timeout=self.timeout)
        try:
            ret = response.json()
        except:
            logging.error("json decode error {}".format(response.text))
            ret = {}
        return ret

    def get_complete_info(self, mis):
        """
        Completed info with specified mis
        :param mis: mis id
        :return:
        """
        api = API_MAP["complete_info"]
        params = self.parms_tmpl(mis)
        headers = self.auth.get_auth_headers(api)
        response = self.auth.requests_retry_session().get(self.host + api, params=params,
                                                          headers=headers, timeout=self.timeout)
        try:
            ret = response.json()
        except:
            logging.error("json decode error {}".format(response.text))
            ret = {}
        return ret

    def get_base_info_by_id(self, id_list):
        """
        :param id_list: mis id list
        :return:
        """
        api = API_MAP["base_info"]
        id_list = [str(i) for i in id_list]
        params = {
            "userIds": ",".join(id_list)
        }
        headers = self.auth.get_auth_headers(api)
        response = self.auth.requests_retry_session().get(self.host + api, params=params,
                                                          headers=headers, timeout=self.timeout)
        return response.json()

    def get_direct_header_id(self, mis):
        api = API_MAP["direct_header"]
        emp_id = self.get_base_info(mis)["data"][0]["id"]
        params = {
            "empId": emp_id
        }
        headers = self.auth.get_auth_headers(api)
        response = self.auth.requests_retry_session().get(self.host + api, params=params,
                                                          headers=headers, timeout=self.timeout).json()
        return response["data"]

    def get_direct_header_info(self, mis):
        header_id = self.get_direct_header_id(mis)
        return self.get_base_info_by_id([str(header_id)])

    def get_direct_header_mis(self, mis):
        header_info = self.get_direct_header_info(mis)
        return header_info["data"][0]["login"]

    def get_direct_header_email(self, mis):
        try:
            header_info = self.get_direct_header_info(mis)
            return header_info["data"][0]["email"]
        except (KeyError, IndexError, Exception):
            return None

    def get_direct_lower_id(self, emp_id):
        api = API_MAP["direct_lower"]
        params = {
            "empId": emp_id
        }
        headers = self.auth.get_auth_headers(api)
        response = self.auth.requests_retry_session().get(self.host + api, params=params,
                                                          headers=headers, timeout=self.timeout).json()
        return response

    def get_same_level_email(self, mis):
        try:
            leader_id = self.get_direct_header_id(mis)
            lower_ids = self.get_direct_lower_id(leader_id)["data"]
            base_infos = self.get_base_info_by_id(lower_ids)["data"]
            return [base_info["email"] for base_info in base_infos]
        except IndexError:
            return None

    def get_direct_header_name(self, mis):
        if mis is None:
            raise OrgInfoException("mis can not be None")
        info = self.get_direct_header_info(mis)
        return "{}({})".format(info["data"][0]["name"], info["data"][0]["login"])

    def get_direct_header_name_list(self, email_list):
        headers_map = {}
        for email in email_list:
            pos = email.rfind("@")
            if -1 != pos:
                mis = email[:email.rfind("@")]
            else:
                mis = email
            if not self.has_lower_by_mis(mis):
                try:
                    header_name = self.get_direct_header_name(mis)
                    headers_map[header_name] = headers_map.get(header_name, 0) + 1
                except IndexError:
                    logging.error("OrgInfo error: can not find mis: {} in org".format(mis))
                except KeyError:
                    logging.error("OrgInfo error: can not find mis: {} in org".format(mis))
        return sorted(headers_map.items(), key=lambda d: d[1], reverse=True)

    def has_lower_by_mis(self, mis):
        try:
            emp_id = self.get_base_info(mis)["data"][0]["id"]
            data = self.get_direct_lower_id(emp_id)
            return 0 != len(data["data"])
        except (KeyError, IndexError):
            return False

    def get_lower_by_mis(self, mis):
        try:
            emp_id = self.get_base_info(mis)["data"][0]["id"]
            data = self.get_direct_lower_id(emp_id).get("data", [])
            emp_infos = self.get_base_info_by_id(data)
            emp_mises = [emp["login"] for emp in emp_infos.get("data", [])]
            return emp_mises
        except (KeyError, IndexError):
            return []

    def get_low_same_level_by_mis(self, mis):
        """
        Get their own and subordinate mis list according to mis
        :param mis:
        :return:
        """
        data = self.get_lower_by_mis(mis)
        data.append(mis)
        return data

    def get_low_level_by_mis(self, mis):
        """
        Get their own and subordinate mis list according to mis
        :param mis:
        :return:
        """
        data = self.get_lower_by_mis(mis)
        return data

    def get_join_date_by_mis(self, mis):
        data = self.get_base_info(mis)
        try:
            secs = data.get("data", [])[0].get("joinDate")
            return self.utils.convert_milliseconds_to_time(secs)
        except (KeyError, IndexError)as e:
            logging.error("Failed to obtain info for \"{}\": {}".format(mis, e))
            return None

    def get_left_date_by_mis(self, mis):
        data = self.get_base_info(mis)
        try:
            secs = data.get("data", [])[0].get("leftDate")
            if secs is not None:
                return self.utils.convert_milliseconds_to_time(secs)
            return "Still on the job."
        except (KeyError, IndexError)as e:
            logging.error("Failed to obtain info for \"{}\": {}".format(mis, e))
            return None

    def get_birthday_by_mis(self, mis):
        data = self.get_complete_info(mis)
        try:
            secs = data.get("data", [])[0].get("birthday")
            if secs is not None:
                return self.utils.convert_milliseconds_to_time(secs)
        except (KeyError, IndexError)as e:
            logging.error("Failed to obtain info for \"{}\": {}".format(mis, e))
            return None

    def get_org_full_name(self, mis):
        """
        Full org tree with specified mis
        IPH-集团-出行事业部-X项目组-技术研发部-结算组
        :param mis:
        :return:
        """
        data = self.get_complete_info(mis)
        try:
            full_info = data.get("data", [])[0].get("orgFullName")
            return full_info
        except (KeyError, IndexError)as e:
            logging.error("Failed to obtain org info for \"{}\": {}".format(mis, e))
            return None

    def get_org_dep_name(self, mis, depth):
        """
        Full department tree with specified mis
        技术研发部-结算组
        :param mis:
        :param depth:
        :return:
        """
        data = self.get_complete_info(mis)
        try:
            full_info = data.get("data", [])[0].get("orgFullName")
            dep_info = full_info.split("-", 4)[depth]
            return dep_info
        except (KeyError, IndexError, AttributeError)as e:
            logging.error("Failed to obtain department info for \"{}\": {}".format(mis, e))
            return None

