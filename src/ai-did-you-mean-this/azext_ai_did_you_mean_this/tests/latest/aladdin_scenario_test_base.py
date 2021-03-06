# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import re
from typing import Union
import unittest.mock as mock

from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.patches import mock_in_unit_test

from azext_ai_did_you_mean_this._cmd_table import CommandTable
from azext_ai_did_you_mean_this._const import (
    RECOMMENDATION_HEADER_FMT_STR,
    UNABLE_TO_HELP_FMT_STR
)
from azext_ai_did_you_mean_this.custom import recommend_recovery_options
from azext_ai_did_you_mean_this.tests.latest.data.user_fault_type import UserFaultType
from azext_ai_did_you_mean_this.tests.latest.mock.const import (
    AZURE_CLI_CORE_VERSION_PATCH_TARGET,
    MOCK_CORE_CLI_VERSION, MOCK_UUID,
    TELEMETRY_AZURE_SUBSCRIPTION_ID_PATCH_TARGET,
    TELEMETRY_CORRELATION_ID_PATCH_TARGET,
    TELEMETRY_IS_ENABLED_PATCH_TARGET
)

FMT_STR_PATTERN_REGEX = r'\[[^\]]+\]|{[^}]+}'
SUGGEST_AZ_FIND_PATTERN_REGEX = re.sub(FMT_STR_PATTERN_REGEX, r'.*', UNABLE_TO_HELP_FMT_STR)
SHOW_RECOMMENDATIONS_PATTERN_REGEX = re.sub(FMT_STR_PATTERN_REGEX, r'.*', RECOMMENDATION_HEADER_FMT_STR)


def patch_ids(unit_test):
    def _mock_uuid(*args, **kwargs):  # pylint: disable=unused-argument
        return MOCK_UUID

    mock_in_unit_test(unit_test,
                      TELEMETRY_CORRELATION_ID_PATCH_TARGET,
                      _mock_uuid())
    mock_in_unit_test(unit_test,
                      TELEMETRY_AZURE_SUBSCRIPTION_ID_PATCH_TARGET,
                      _mock_uuid)


def patch_version(unit_test):
    mock_in_unit_test(unit_test,
                      AZURE_CLI_CORE_VERSION_PATCH_TARGET,
                      MOCK_CORE_CLI_VERSION)


def patch_telemetry(unit_test):
    mock_in_unit_test(unit_test,
                      TELEMETRY_IS_ENABLED_PATCH_TARGET,
                      lambda: True)


class AladdinScenarioTest(ScenarioTest):
    def __init__(self, method_name, **kwargs):
        super().__init__(method_name, **kwargs)

        default_telemetry_patches = {
            patch_ids,
            patch_version,
            patch_telemetry
        }

        self._exception = None
        self._exit_code = None
        self._parser_error_msg = ''
        self._recommendation_msg = ''
        self._recommender_positional_arguments = None

        self.telemetry_patches = kwargs.pop('telemetry_patches', default_telemetry_patches)
        self.recommendations = []

    def setUp(self):
        super().setUp()

        for patch in self.telemetry_patches:
            patch(self)

    def cmd(self, command, checks=None, expect_failure=False, expect_user_fault_failure=False):
        from azure.cli.core.azlogging import AzCliLogging

        func = recommend_recovery_options
        logger_name = AzCliLogging._COMMAND_METADATA_LOGGER  # pylint: disable=protected-access
        base = super()

        def _hook(*args, **kwargs):
            self._recommender_positional_arguments = args
            result = func(*args, **kwargs)
            self.recommendations = result
            return result

        def run_cmd():
            base.cmd(command, checks=checks, expect_failure=expect_failure)

        with mock.patch('azext_ai_did_you_mean_this.custom.recommend_recovery_options', wraps=_hook):
            with self.assertLogs(logger_name, level=logging.ERROR) as parser_logs:
                if expect_user_fault_failure:
                    with self.assertRaises(SystemExit) as cm:
                        run_cmd()

                    self._exception = cm.exception
                    self._exit_code = self._exception.code
                    self._parser_error_msg = '\n'.join(parser_logs.output)
                    self._recommendation_msg = '\n'.join(self.recommendations)

                    self.assert_cmd_was_user_fault_failure()
                else:
                    run_cmd()

        if expect_user_fault_failure:
            self.assert_cmd_table_not_empty()
            self.assert_user_fault_is_of_correct_type(expect_user_fault_failure)

    def assert_user_fault_is_of_correct_type(self, user_fault_type: Union[UserFaultType, bool]):
        # check the user fault type where applicable
        if isinstance(user_fault_type, UserFaultType) and user_fault_type != UserFaultType.NOT_APPLICABLE:
            keyword = user_fault_type.keyword
            self.assertRegex(self._parser_error_msg, keyword)

    def assert_cmd_was_user_fault_failure(self):
        is_user_fault_failure = (isinstance(self._exception, SystemExit) and
                                 self._exit_code == 2)

        self.assertTrue(is_user_fault_failure)

    def assert_cmd_table_not_empty(self):
        self.assertIsNotNone(CommandTable.CMD_TBL)

    def assert_recommendations_were_shown(self):
        self.assertRegex(self._recommendation_msg, SHOW_RECOMMENDATIONS_PATTERN_REGEX)

    def assert_az_find_was_suggested(self):
        self.assertRegex(self._recommendation_msg, SUGGEST_AZ_FIND_PATTERN_REGEX)

    def assert_nothing_is_shown(self):
        self.assertEqual(self._recommendation_msg, '')

    @property
    def cli_version(self):
        from azure.cli.core import __version__ as core_version
        return core_version

    @property
    def recommender_postional_arguments(self):
        return self._recommender_positional_arguments
