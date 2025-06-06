# pylint: disable=missing-class-docstring, missing-function-docstring, missing-module-docstring
# pylint: disable=wrong-import-order, line-too-long

import os
import unittest
import pandas as pd

from __testing__ import Testing
from UltimateJiraSprintReport import UltimateJiraSprintReport
from UltimateJiraSprintReport.plugins.zephyr_scale.zephyr_sprint_report_plugin import ZephyrSprintReportPlugin

class TestPlugin(unittest.TestCase):

    def setUp(self):
        self.username = os.getenv("ATLASSIAN_USERNAME")
        self.password = os.getenv("ATLASSIAN_APIKEY")
        self.host = os.getenv("ATLASSIAN_HOST")
        self.zephyr_scale_api_key = os.getenv("ZEPHYR_SCALE_APIKEY")
        self.report = UltimateJiraSprintReport(self.username, self.password, self.host)
        self.report.connect()

    def test_initialization(self):
        self.assertIsInstance(self.report, UltimateJiraSprintReport)

    def test_show_report(self):
        project = 'FDSEWMSR'
        board_id = 364
        sprint_id = 944

        self.report.load(project, board_id, sprint_id)

        zephyr_plugin = self.report.load_plugin("zephyr_scale", zephyr_api=self.zephyr_scale_api_key)
        self.assertIsInstance(zephyr_plugin, ZephyrSprintReportPlugin)

        zephyr_plugin.load()
        # self.assertIsInstance(zephyr_plugin.test_case_statistics_data_table, pd.DataFrame)

        output = zephyr_plugin.show_report()
        self.assertIsInstance(output, str)

        if Testing.INTERACTIVE_TESTING_ENABLED:
            Testing.write_to_temp_html_file_then_open(output)

    def test_test_cycles(self):
        project = 'FDSEWMSR'
        board_id = 364
        sprint_id = 945

        sprint_report_url = (
            f"{self.report.jira_service.host}"
            f"jira/software/c/projects/{project}"
            f"/boards/{board_id}"
            f"/reports/sprint-retrospective?sprint={sprint_id}"
        )

        self.report._set_sprint_details(sprint_report_url) # pylint: disable=protected-access

        zephyr_plugin = self.report.load_plugin("zephyr_scale", zephyr_api=self.zephyr_scale_api_key)
        self.assertIsInstance(zephyr_plugin, ZephyrSprintReportPlugin)

        test_cycle, test_cases = zephyr_plugin.process_test_cycle()
        self.assertIsInstance(test_cycle, pd.DataFrame)
        self.assertIsInstance(test_cases, pd.DataFrame)


if __name__ == '__main__':
    unittest.main()
