#!/usr/bin/env python
# filename: stash_org_grouping_builder.py
#
# desc: Configure repository template with Group relations of stash and org
#

import os
import multiprocessing
from functools import partial

from jenkins_sonar.jks_logger import logger
from jenkins_sonar.org_handler import OrgInfo
from jenkins_sonar.stash_handler import Stash
from jenkins_sonar.org_sonar_mapping import mapping_tmpl
from jenkins_sonar.jks_utils import UtilityTools, SonarTools
from jenkins_sonar.stash_repo_builder import repo_template_newer
from jenkins_sonar.stash_repo_builder import cur_dir, RepoTplGenerator, DiffGenerator

# Set up a specific logger
logger = logger()

# Project name and Template file
qcs_prj = "qcs"
repo_org_grp_success = os.path.join(cur_dir, "stash_org_grp_success.csv")
repo_org_grp_fail = os.path.join(cur_dir, "stash_org_grp_fail.csv")
repo_org_grp_empty = os.path.join(cur_dir, "stash_org_grp_empty.txt")
sonar_grp_info = os.path.join(cur_dir, "group_info_qa.csv")


class StashOrgGroup(object):
    """
    Write grouping info into specified template by analyzing stash and org
    """

    def __init__(self):
        self.stash = Stash()
        self.sonar = SonarTools()
        self.org_info = OrgInfo()
        self.utils = UtilityTools()
        self.diff_generator = DiffGenerator()
        self.repo_tpl_generator = RepoTplGenerator()

    def config_tmpl_to_grp(self, repo_tmpl_newer, stash_org_grp_success=None,
                           stash_org_grp_fail=None, stash_org_grp_empty=None):
        """
        Read repository template and append grouping info into new template. Single tasking.
        :param repo_tmpl_newer: All the qcs repos exists in this template.
        :param stash_org_grp_success: successful grouping info
        :param stash_org_grp_fail: failed grouping info.
        For example:
        Unable to obtain information about the employee who left the company or
        the employee who transferred the position or false mis or false email address.
        :param stash_org_grp_empty: empty repository info
        """
        # Analyze and configure all repos in qcs project into the corresponding template
        with open(repo_tmpl_newer, "r+") as f:
            for qcs_slug in f:
                qcs_slug = qcs_slug.strip()
                branch_name = self.stash.get_max_commits_branch(qcs_prj, qcs_slug)
                committer_list = self.stash.get_most_n_committer(qcs_prj, qcs_slug, branch_name,
                                                                 n=5, recent=10, flag=True)
                if committer_list:
                    mis_id = committer_list[0]
                    org_dep_name = self.org_info.get_org_dep_name(mis_id, 4)
                    if org_dep_name and org_dep_name in mapping_tmpl:
                        logger.info("{}: {},{}\n".format(qcs_slug, mis_id,
                                                         self.org_info.get_org_dep_name(mis_id, 4)))
                        self.utils.write_data_to_csv(stash_org_grp_success,
                                                     "{},{},{},{}".format(qcs_slug, mis_id, org_dep_name,
                                                                          mapping_tmpl[org_dep_name]).split(","))
                    else:
                        logger.info("{}: {} is problem repository.\n".format(qcs_slug, mis_id))
                        self.utils.write_data_to_csv(stash_org_grp_fail,
                                                     "{},{}".format(qcs_slug, mis_id).split(","))
                    # continue
                else:
                    logger.info("{} is empty repository.\n".format(qcs_slug))
                    self.utils.write_data_to_file(stash_org_grp_empty, qcs_slug)

    def config_tmpl_to_grp_v2(self, line_in_repo_tmpl_newer, stash_org_grp_success=None,
                              stash_org_grp_fail=None, stash_org_grp_empty=None):
        """
        Read repository template and append grouping info into new template. Multiple tasking.
        :param line_in_repo_tmpl_newer: Separate qcs repo info object exists in qcs repos list
        :param stash_org_grp_success: successful grouping info
        :param stash_org_grp_fail: failed grouping info.
        For example:
        Unable to obtain information about the employee who left the company or
        the employee who transferred the position or false mis or false email address.
        :param stash_org_grp_empty: empty repository info
        """
        # Analyze and configure all repos in qcs project in the corresponding template
        if line_in_repo_tmpl_newer:
            qcs_slug = line_in_repo_tmpl_newer.strip()
            branch_name = self.stash.get_max_commits_branch(qcs_prj, qcs_slug)
            committer_list = self.stash.get_most_n_committer(qcs_prj, qcs_slug, branch_name,
                                                             n=5, recent=10, flag=True)
            if committer_list:
                mis_id = committer_list[0]
                org_dep_name = self.org_info.get_org_dep_name(mis_id, 4)
                if org_dep_name and org_dep_name in mapping_tmpl:
                    logger.info("{}: {},{}\n".format(qcs_slug,
                                                     mis_id, self.org_info.get_org_dep_name(mis_id, 4)))
                    self.utils.write_data_to_csv(stash_org_grp_success,
                                                 "{},{},{},{}".format(qcs_slug, mis_id, org_dep_name,
                                                                      mapping_tmpl[org_dep_name]).split(","))
                else:
                    logger.info("{}: {} is problem repository.\n".format(qcs_slug, mis_id))
                    self.utils.write_data_to_csv(stash_org_grp_fail,
                                                 "{},{}".format(qcs_slug, mis_id).split(","))
            else:
                logger.info("{} is empty repository.\n".format(qcs_slug))
                self.utils.write_data_to_file(stash_org_grp_empty, qcs_slug)
        else:
            logger.error("Pls check data validity")

    def main_proc(self, repo_diff=False, collect_sonar_key=False, single_task=False,
                  init_repo_list=False, multiple_task_basis=False, multiple_task_pool=False):
        """
        Configure mapping between stash and committer and org
        :param repo_diff: generate repo and diff or not
        :param collect_sonar_key: collect sonar key or not
        :param single_task: config mapping with single task or not
        :param init_repo_list: init repo list or not
        :param multiple_task_basis: config mapping with multiple task basis or not
        :param multiple_task_pool: config mapping with multiple task pool or not
        """
        if repo_diff:
            # Init repo and diff template
            self.repo_tpl_generator.main_gen_proc()
            self.diff_generator.main_diff_proc()

        if collect_sonar_key:
            # Collect all measure filters from sonar and output them to stdout
            self.sonar.get_group_info(sonar_grp_info)
            self.utils.output_data_from_csv(sonar_grp_info)
        if single_task:
            # Single tasking
            sog.config_tmpl_to_grp(repo_template_newer, repo_org_grp_success,
                                   repo_org_grp_fail, repo_org_grp_empty)

        if init_repo_list:
            # Init repo list
            f_list = self.utils.read_file_to_list(repo_template_newer)

            if multiple_task_basis:
                # Multiple tasking with mp basics
                jobs = []
                for line in f_list:
                    p = multiprocessing.Process(target=sog.config_tmpl_to_grp_v2,
                                                args=(line, repo_org_grp_success,
                                                      repo_org_grp_fail, repo_org_grp_empty))
                    jobs.append(p)
                    p.start()

            if multiple_task_pool:
                # Multiple tasking with process pools
                pool_size = multiprocessing.cpu_count() * 3
                pool = multiprocessing.Pool(
                    processes=pool_size,
                )
                pool.map(partial(sog.config_tmpl_to_grp_v2, stash_org_grp_success=repo_org_grp_success,
                                 stash_org_grp_fail=repo_org_grp_fail, stash_org_grp_empty=repo_org_grp_empty), f_list)
                pool.close()
                pool.join()


if __name__ == "__main__":
    try:
        sog = StashOrgGroup()
        sog.main_proc(collect_sonar_key=True)
        # sog.main_proc(collect_sonar_key=True, init_repo_list=True, multiple_task_pool=True)
    except KeyboardInterrupt:
        pass
