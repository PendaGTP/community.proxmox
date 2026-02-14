#
# Copyright (c) 2026, Clément Cruau (@PendaGTP) <38917281+PendaGTP@users.noreply.github.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


from unittest.mock import Mock, patch

import pytest

proxmoxer = pytest.importorskip("proxmoxer")

from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    ModuleTestCase,
    set_module_args,
)

import ansible_collections.community.proxmox.plugins.module_utils.proxmox as proxmox_utils
from ansible_collections.community.proxmox.plugins.modules import proxmox_metrics_server

METRICS_SERVER_NAME = "my-graphite"


def exit_json(*args, **kwargs):
    if "changed" not in kwargs:
        kwargs["changed"] = False
    raise SystemExit(kwargs)


def fail_json(*args, **kwargs):
    kwargs["failed"] = True
    raise SystemExit(kwargs)


def get_module_args(server_id=METRICS_SERVER_NAME, state="present", **kwargs):
    base = {
        "api_host": "host",
        "api_user": "user",
        "api_password": "password",
        "id": server_id,
        "state": state,
        "type": "graphite",
        "server": "graphite.example.com",
        "port": 2003,
    }
    base.update(kwargs)
    return base


class TestProxmoxMetricsServerModule(ModuleTestCase):
    def setUp(self):
        super().setUp()
        proxmox_utils.HAS_PROXMOXER = True
        self.module = proxmox_metrics_server
        self.fail_json_patcher = patch(
            "ansible.module_utils.basic.AnsibleModule.fail_json",
            new=Mock(side_effect=fail_json),
        )
        self.exit_json_patcher = patch(
            "ansible.module_utils.basic.AnsibleModule.exit_json",
            new=exit_json,
        )
        self.fail_json_patcher.start()
        self.exit_json_patcher.start()
        self.connect_mock = patch(
            "ansible_collections.community.proxmox.plugins.module_utils.proxmox.ProxmoxAnsible._connect"
        ).start()
        self.mock_get_server = patch.object(
            proxmox_metrics_server.ProxmoxMetricsServerAnsible,
            "_get_metrics_server",
        ).start()

    def tearDown(self):
        self.connect_mock.stop()
        self.mock_get_server.stop()
        self.exit_json_patcher.stop()
        self.fail_json_patcher.stop()
        super().tearDown()

    def _run_module(self, args):
        with set_module_args(args), pytest.raises(SystemExit) as exc_info:
            self.module.main()
        return exc_info.value.args[0]

    def _check_mode_args(self, **kwargs):
        return {**get_module_args(**kwargs), "_ansible_check_mode": True}

    def test_metrics_server_present_create(self):
        self.mock_get_server.return_value = None
        result = self._run_module(get_module_args())
        assert result["changed"] is True
        assert result["msg"] == f"Metrics server {METRICS_SERVER_NAME} successfully created"
        assert result["id"] == METRICS_SERVER_NAME

    def test_metrics_server_present_always_updates_when_exists(self):
        """When server exists we always run update (API returns limited keys, so we cannot detect no-op)."""
        self.mock_get_server.return_value = {
            "id": METRICS_SERVER_NAME,
            "type": "graphite",
            "server": "graphite.example.com",
            "port": 2003,
        }
        result = self._run_module(get_module_args())
        assert result["changed"] is True
        assert result["msg"] == f"Metrics server {METRICS_SERVER_NAME} successfully updated"
        assert result["id"] == METRICS_SERVER_NAME

    def test_metrics_server_present_update(self):
        self.mock_get_server.return_value = {
            "id": METRICS_SERVER_NAME,
            "type": "graphite",
            "server": "graphite.example.com",
            "port": 2003,
        }
        result = self._run_module(get_module_args(graphite_path="proxmox.mycluster"))
        assert result["changed"] is True
        assert result["msg"] == f"Metrics server {METRICS_SERVER_NAME} successfully updated"
        assert result["id"] == METRICS_SERVER_NAME

    def test_metrics_server_absent_delete(self):
        self.mock_get_server.return_value = {"id": METRICS_SERVER_NAME}
        result = self._run_module(get_module_args(state="absent"))
        assert result["changed"] is True
        assert result["msg"] == f"Metrics server {METRICS_SERVER_NAME} successfully deleted"
        assert result["id"] == METRICS_SERVER_NAME

    def test_metrics_server_absent_not_found(self):
        self.mock_get_server.return_value = None
        result = self._run_module(get_module_args(state="absent"))
        assert result["changed"] is False
        assert result["msg"] == f"Metrics server {METRICS_SERVER_NAME} does not exist"
        assert result["id"] == METRICS_SERVER_NAME

    def test_metrics_server_present_check_mode_create(self):
        self.mock_get_server.return_value = None
        result = self._run_module(self._check_mode_args())
        assert result["changed"] is True
        assert result["msg"] == f"Metrics server {METRICS_SERVER_NAME} would be created"
        assert result["id"] == METRICS_SERVER_NAME

    def test_metrics_server_present_check_mode_always_would_update_when_exists(self):
        """When server exists we always report would update in check mode (API returns limited keys)."""
        self.mock_get_server.return_value = {
            "id": METRICS_SERVER_NAME,
            "type": "graphite",
            "server": "graphite.example.com",
            "port": 2003,
        }
        result = self._run_module(self._check_mode_args())
        assert result["changed"] is True
        assert result["msg"] == f"Metrics server {METRICS_SERVER_NAME} would be updated"

    def test_metrics_server_present_check_mode_update(self):
        self.mock_get_server.return_value = {
            "id": METRICS_SERVER_NAME,
            "type": "graphite",
            "server": "graphite.example.com",
            "port": 2003,
        }
        result = self._run_module(self._check_mode_args(graphite_path="proxmox.mycluster"))
        assert result["changed"] is True
        assert result["msg"] == f"Metrics server {METRICS_SERVER_NAME} would be updated"

    def test_metrics_server_absent_check_mode_delete(self):
        self.mock_get_server.return_value = {"id": METRICS_SERVER_NAME}
        result = self._run_module(self._check_mode_args(state="absent"))
        assert result["changed"] is True
        assert result["msg"] == f"Metrics server {METRICS_SERVER_NAME} would be deleted"

    def test_metrics_server_absent_check_mode_not_found(self):
        self.mock_get_server.return_value = None
        result = self._run_module(self._check_mode_args(state="absent"))
        assert result["changed"] is False
        assert result["msg"] == f"Metrics server {METRICS_SERVER_NAME} does not exist"

    def test_metrics_server_validation_fails_invalid_port(self):
        """Invalid port triggers validate_params -> Exception -> fail_json."""
        with set_module_args(get_module_args(port=0)), pytest.raises(SystemExit) as exc_info:
            self.module.main()
        result = exc_info.value.args[0]
        assert result["failed"] is True
        assert "port must be between 1 and 65535" in result["msg"]

    def test_metrics_server_validation_fails_invalid_graphite_mtu(self):
        """Invalid graphite_mtu triggers validate_params -> Exception -> fail_json."""
        with set_module_args(get_module_args(graphite_mtu=100)), pytest.raises(SystemExit) as exc_info:
            self.module.main()
        result = exc_info.value.args[0]
        assert result["failed"] is True
        assert "graphite_mtu must be between 512 and 65536" in result["msg"]
