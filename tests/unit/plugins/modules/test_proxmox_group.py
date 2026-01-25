# -*- coding: utf-8 -*-
#
# Copyright (c) 2026, Clément Cruau (@PendaGTP) <38917281+PendaGTP@users.noreply.github.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from unittest.mock import patch, Mock

import pytest

proxmoxer = pytest.importorskip("proxmoxer")

from ansible_collections.community.proxmox.plugins.modules import proxmox_group
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    ModuleTestCase,
    set_module_args,
)
import ansible_collections.community.proxmox.plugins.module_utils.proxmox as proxmox_utils

GROUP_ID = "group-test"
GROUP_COMMENT = "comment-test"


def exit_json(*args, **kwargs):
    """function to patch over exit_json; package return data into an exception"""
    if "changed" not in kwargs:
        kwargs["changed"] = False
    raise SystemExit(kwargs)


def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an exception"""
    kwargs["failed"] = True
    raise SystemExit(kwargs)


def get_module_args(groupid, comment=None, state="present"):
    return {
        "api_host": "host",
        "api_user": "user",
        "api_password": "password",
        "groupid": groupid,
        "comment": comment,
        "state": state
    }


class TestProxmoxGroupModule(ModuleTestCase):
    def setUp(self):
        super().setUp()
        proxmox_utils.HAS_PROXMOXER = True
        self.module = proxmox_group
        self.fail_json_patcher = patch("ansible.module_utils.basic.AnsibleModule.fail_json",
                                       new=Mock(side_effect=fail_json))
        self.exit_json_patcher = patch(
            "ansible.module_utils.basic.AnsibleModule.exit_json", new=exit_json)
        self.fail_json_mock = self.fail_json_patcher.start()
        self.exit_json_patcher.start()
        self.connect_mock = patch(
            "ansible_collections.community.proxmox.plugins.module_utils.proxmox.ProxmoxAnsible._connect"
        ).start()
        self.mock_get_group = patch.object(
            proxmox_group.ProxmoxGroupAnsible, "_get_group"
        ).start()

    def tearDown(self):
        self.connect_mock.stop()
        self.exit_json_patcher.stop()
        self.fail_json_patcher.stop()
        self.mock_get_group.stop()
        super().tearDown()

    def _run_module(self, args):
        with pytest.raises(SystemExit) as exc_info:
            with set_module_args(args):
                self.module.main()
        return exc_info.value.args[0]

    def _check_mode_args(self, **kwargs):
        return {**get_module_args(**kwargs), "_ansible_check_mode": True}

    def test_group_present(self):
        self.mock_get_group.return_value = None
        result = self._run_module(get_module_args(groupid=GROUP_ID))
        assert result["changed"] is True
        assert result["msg"] == f"Group {GROUP_ID} successfully created"
        assert result["groupid"] == GROUP_ID

        self.mock_get_group.return_value = {}
        result = self._run_module(get_module_args(groupid=GROUP_ID))
        assert result["changed"] is False
        assert result["msg"] == f"Group {GROUP_ID} already exists with desired comment"
        assert result["groupid"] == GROUP_ID

        self.mock_get_group.return_value = {}
        result = self._run_module(
            get_module_args(groupid=GROUP_ID, comment=GROUP_COMMENT)
        )
        assert result["changed"] is True
        assert result["msg"] == f"Group {GROUP_ID} successfully updated"
        assert result["groupid"] == GROUP_ID

        self.mock_get_group.return_value = {"comment": "test"}
        result = self._run_module(
            get_module_args(groupid=GROUP_ID, comment=GROUP_COMMENT)
        )
        assert result["changed"] is True
        assert result["msg"] == f"Group {GROUP_ID} successfully updated"
        assert result["groupid"] == GROUP_ID

    def test_group_absent(self):
        self.mock_get_group.return_value = {}
        result = self._run_module(
            get_module_args(groupid=GROUP_ID, state="absent")
        )
        assert result["changed"] is True
        assert result["msg"] == f"Group {GROUP_ID} successfully deleted"
        assert result["groupid"] == GROUP_ID

        self.mock_get_group.return_value = None
        result = self._run_module(
            get_module_args(groupid=GROUP_ID, state="absent")
        )
        assert result["changed"] is False
        assert result["msg"] == f"Group {GROUP_ID} does not exist"
        assert result["groupid"] == GROUP_ID

    def test_group_present_check_mode(self):
        self.mock_get_group.return_value = None
        result = self._run_module(
            self._check_mode_args(groupid=GROUP_ID)
        )
        assert result["changed"] is True
        assert result["msg"] == f"Group {GROUP_ID} would be created"
        assert result["groupid"] == GROUP_ID

        self.mock_get_group.return_value = {}
        result = self._run_module(
            self._check_mode_args(groupid=GROUP_ID)
        )
        assert result["changed"] is False
        assert result["msg"] == f"Group {GROUP_ID} already exists with desired comment"
        assert result["groupid"] == GROUP_ID

        self.mock_get_group.return_value = {}
        result = self._run_module(
            self._check_mode_args(groupid=GROUP_ID, comment=GROUP_COMMENT)
        )
        assert result["changed"] is True
        assert result["msg"] == f"Group {GROUP_ID} would be updated"
        assert result["groupid"] == GROUP_ID

        self.mock_get_group.return_value = {"comment": "test"}
        result = self._run_module(
            self._check_mode_args(groupid=GROUP_ID, comment=GROUP_COMMENT)
        )
        assert result["changed"] is True
        assert result["msg"] == f"Group {GROUP_ID} would be updated"
        assert result["groupid"] == GROUP_ID

    def test_group_absent_check_mode(self):
        self.mock_get_group.return_value = {}
        result = self._run_module(
            self._check_mode_args(groupid=GROUP_ID, state="absent")
        )
        assert result["changed"] is True
        assert result["msg"] == f"Group {GROUP_ID} would be deleted"
        assert result["groupid"] == GROUP_ID

        self.mock_get_group.return_value = None
        result = self._run_module(
            self._check_mode_args(groupid=GROUP_ID, state="absent")
        )
        assert result["changed"] is False
        assert result["msg"] == f"Group {GROUP_ID} does not exist"
        assert result["groupid"] == GROUP_ID
