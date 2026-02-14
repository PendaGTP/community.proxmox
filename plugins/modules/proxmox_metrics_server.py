#!/usr/bin/python

# Copyright (c) 2026, Clément Cruau (@PendaGTP) <38917281+PendaGTP@users.noreply.github.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


DOCUMENTATION = r"""
module: proxmox_metrics_server
short_description: Metrics server management for Proxmox VE cluster
version_added: "1.6.0"
author:
  - Clément Cruau (@PendaGTP)
description:
  - Create, update or delete external metrics servers in a Proxmox VE cluster.
  - External metric servers periodically receive statistics about hosts, virtual guests, and storage.
  - Supported plugin types are C(graphite), C(influxdb), and C(opentelemetry).
  - |
    Note: The PVE API only returns a subset of the metrics server configuration (C(id), C(type), C(server),
    C(disable), C(port)). The module cannot detect whether an update is actually needed for other options
    (e.g. C(graphite_path), C(mtu), C(timeout)). Therefore, when the metrics server already exists with
    O(state=present), the module always performs an update and reports C(changed=True).
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  id:
    description:
      - Unique ID of this metric server in PVE.
    type: str
    required: true
    aliases: [name]
  state:
    description:
      - Indicate desired state of the metrics server.
    type: str
    choices:
      - present
      - absent
    default: present
  disable:
    description:
      - Set this to V(true) to disable this metric server.
    type: bool
  port:
    description:
      - Server network port.
      - Allowed range C(1) - C(65535).
    type: int
    required: true
  server:
    description:
      - Server DNS name or IP address.
    type: str
    required: true
  type:
    description:
      - Plugin type.
    type: str
    required: true
    choices:
      - graphite
      - influxdb
      - opentelemetry
  # InfluxDB options
  influx_api_path_prefix:
    description:
      - API path prefix inserted between E(host:port/) and E(/api2/).
      - Can be useful if the InfluxDB service runs behind a reverse proxy.
    type: str
  influx_bucket:
    description:
      - The InfluxDB bucket/db. Only necessary when using the HTTP v2 API.
    type: str
  influx_db_proto:
    description:
      - Protocol for InfluxDB. If not set, PVE default is C(udp).
    type: str
    choices:
      - udp
      - http
      - https
  influx_max_body_size:
    description:
      - InfluxDB max-body-size in bytes. Requests are batched up to this size.
      - If not set, PVE default is C(25000000). Minimum is C(1).
    type: int
  influx_organization:
    description:
      - The InfluxDB organization. Only necessary when using the HTTP v2 API.
      - Has no meaning when using v2 compatibility API.
    type: str
  influx_token:
    description:
      - The InfluxDB access token. Only necessary when using the HTTP v2 API.
      - If the v2 compatibility API is used, use C(user:password) instead.
    type: str
    no_log: true
  influx_verify:
    description:
      - Set to V(false) to disable certificate verification for HTTPS endpoints.
      - If not set, PVE default is V(true).
    type: bool
  influxdb_mtu:
    description:
      - InfluxDB MTU (maximum transmission unit) for metrics transmission over UDP.
      - If not set, PVE default is C(1500). Allowed range C(512) - C(65536).
    type: int
  influx_timeout:
    description:
      - InfluxDB HTTP request timeout in seconds.
      - If not set, PVE default is C(5).
      - Allowed range C(1) - C(10).
    type: int
  # Graphite options
  graphite_path:
    description:
      - Root graphite path (e.g. C(proxmox.mycluster.mykey)).
    type: str
  graphite_timeout:
    description:
      - Graphite TCP socket timeout in seconds.
      - If not set, PVE default is C(1).
    type: int
  graphite_proto:
    description:
      - Protocol to send graphite data.
      - If not set, PVE default is C(udp).
    type: str
    choices:
      - udp
      - tcp
  graphite_mtu:
    description:
      - Graphite MTU (maximum transmission unit) for metrics transmission over UDP.
      - If not set, PVE default is C(1500). Allowed range C(512) - C(65536).
    type: int
  # OpenTelemetry options
  opentelemetry_proto:
    description:
      - Protocol for OLTP.
      - If not set, PVE default is C(https).
    type: str
    choices:
      - http
      - https
  opentelemetry_path:
    description:
      - OLTP endpoint path.
      - If not set, PVE default is C(/v1/metrics).
    type: str
  opentelemetry_timeout:
    description:
      - OLTP HTTP request timeout in seconds.
      - If not set, PVE default is C(5).
      - Allowed range C(1) - C(10).
    type: int
  opentelemetry_headers:
    description:
      - OpenTelemetry custom HTTP headers as JSON, base64 encoded.
      - Maximum length 1024 characters (base64 encoded).
    type: str
  opentelemetry_verify_ssl:
    description:
      - OpenTelemetry verify SSL certificates.
      - If not set, PVE default is V(true).
    type: bool
  opentelemetry_max_body_size:
    description:
      - OpenTelemetry maximum request body size in bytes.
      - If not set, PVE default is C(10000000).
      - Minimum C(1024).
    type: int
  opentelemetry_resource_attributes:
    description:
      - OpenTelemetry additional resource attributes as JSON, base64 encoded.
      - Maximum length 1024 characters.
    type: str
  opentelemetry_compression:
    description:
      - OpenTelemetry compression algorithm for requests.
      - If not set, PVE default is C(gzip).
    type: str
    choices:
      - none
      - gzip
extends_documentation_fragment:
  - community.proxmox.proxmox.actiongroup_proxmox
  - community.proxmox.proxmox.documentation
  - community.proxmox.attributes
"""

EXAMPLES = r"""
- name: Create Graphite metrics server
  community.proxmox.proxmox_metrics_server:
    api_host: node1
    api_user: root@pam
    api_password: password
    id: my-graphite
    type: graphite
    server: graphite.example.com
    port: 2003
    graphite_path: proxmox.mycluster
    state: present

- name: Create InfluxDB metrics server with HTTP API
  community.proxmox.proxmox_metrics_server:
    api_host: node1
    api_user: root@pam
    api_password: password
    id: my-influxdb
    type: influxdb
    server: influxdb.example.com
    port: 8086
    influx_db_proto: https
    influx_organization: proxmox
    influx_bucket: proxmox
    influx_token: "{{ influx_token }}"
    state: present

- name: Create OpenTelemetry metrics server
  community.proxmox.proxmox_metrics_server:
    api_host: node1
    api_user: root@pam
    api_password: password
    id: my-otel
    type: opentelemetry
    server: otel.example.com
    port: 4318
    opentelemetry_proto: https
    opentelemetry_path: /v1/metrics
    state: present

- name: Delete metrics server
  community.proxmox.proxmox_metrics_server:
    api_host: node1
    api_user: root@pam
    api_password: password
    id: my-graphite
    state: absent
"""

RETURN = r"""
id:
  description: The metrics server ID which was created/updated/deleted.
  returned: on success
  type: str
  sample: my-graphite
msg:
  description: A short message on what the module did.
  returned: always
  type: str
  sample: "Metrics server my-graphite successfully created"
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.proxmox.plugins.module_utils.proxmox import (
    ProxmoxAnsible,
    ansible_to_proxmox_bool,
    proxmox_auth_argument_spec,
)

# OpenTelemetry API limits (PVE)
MIN_OPENTELEMETRY_MAX_BODY_SIZE = 1024
MAX_OPENTELEMETRY_STRING_LENGTH = 1024


def get_proxmox_args():
    return dict(
        state=dict(choices=["present", "absent"], default="present"),
        id=dict(required=True, aliases=["name"]),
        disable=dict(type="bool"),
        port=dict(type="int", required=True),
        server=dict(required=True),
        graphite_timeout=dict(type="int"),
        type=dict(required=True, choices=["graphite", "influxdb", "opentelemetry"]),
        # InfluxDB
        influx_api_path_prefix=dict(),
        influx_bucket=dict(),
        influx_db_proto=dict(choices=["udp", "http", "https"]),
        influx_max_body_size=dict(type="int"),
        influx_organization=dict(),
        influx_token=dict(no_log=True),
        influx_verify=dict(type="bool"),
        influx_timeout=dict(type="int"),
        influxdb_mtu=dict(type="int"),
        # Graphite
        graphite_path=dict(),
        graphite_proto=dict(choices=["udp", "tcp"]),
        graphite_mtu=dict(type="int"),
        # OpenTelemetry
        opentelemetry_proto=dict(choices=["http", "https"]),
        opentelemetry_path=dict(),
        opentelemetry_timeout=dict(type="int"),
        opentelemetry_headers=dict(),
        opentelemetry_verify_ssl=dict(type="bool"),
        opentelemetry_max_body_size=dict(type="int"),
        opentelemetry_resource_attributes=dict(),
        opentelemetry_compression=dict(choices=["none", "gzip"]),
    )


def get_ansible_module():
    module_args = proxmox_auth_argument_spec()
    module_args.update(get_proxmox_args())

    module = AnsibleModule(
        argument_spec=module_args,
        required_if=[
            ("state", "present", ["port", "server", "type"]),
        ],
        supports_check_mode=True,
    )
    return module


def validate_params(params):
    """Validate parameter constraints. Raises Exception with message on validation failure."""
    if params.get("state") != "present":
        return
    port = params.get("port")
    if port is not None and (port < 1 or port > 65535):
        raise Exception("port must be between 1 and 65535")
    for mtu_param in ("graphite_mtu", "influxdb_mtu"):
        mtu = params.get(mtu_param)
        if mtu is not None and (mtu < 512 or mtu > 65536):
            raise Exception(f"{mtu_param} must be between 512 and 65536")
    influx_timeout = params.get("influx_timeout")
    if influx_timeout is not None and (influx_timeout < 1 or influx_timeout > 10):
        raise Exception("influx_timeout must be between 1 and 10")
    opentelemetry_timeout = params.get("opentelemetry_timeout")
    if opentelemetry_timeout is not None and (opentelemetry_timeout < 1 or opentelemetry_timeout > 10):
        raise Exception("opentelemetry_timeout must be between 1 and 10")
    opentelemetry_max_body = params.get("opentelemetry_max_body_size")
    if opentelemetry_max_body is not None and opentelemetry_max_body < MIN_OPENTELEMETRY_MAX_BODY_SIZE:
        raise Exception(f"opentelemetry_max_body_size must be at least {MIN_OPENTELEMETRY_MAX_BODY_SIZE}")
    influx_max_body = params.get("influx_max_body_size")
    if influx_max_body is not None and influx_max_body < 1:
        raise Exception("influx_max_body_size must be at least 1")
    for key in ("opentelemetry_headers", "opentelemetry_resource_attributes"):
        val = params.get(key)
        if val is not None and len(val) > MAX_OPENTELEMETRY_STRING_LENGTH:
            raise Exception(f"{key} must be at most {MAX_OPENTELEMETRY_STRING_LENGTH} characters")


def build_metrics_server_params(params):
    """Build API payload from module params. Excludes auth and internal keys, maps renames, adds MTU by type."""
    SKIP_KEYS = frozenset(
        (
            "state",
            "api_host",
            "api_port",
            "api_user",
            "api_password",
            "api_token_id",
            "api_token_secret",
            "validate_certs",
            "api_timeout",
            "graphite_mtu",
            "influxdb_mtu",
        )
    )
    BOOL_KEYS = frozenset(("disable", "influx_verify", "opentelemetry_verify_ssl"))
    RENAME_KEYS = {"graphite_timeout": "timeout", "influx_timeout": "timeout"}

    out = {}
    for key, value in params.items():
        if value is None or key in SKIP_KEYS:
            continue
        if key in BOOL_KEYS:
            try:
                out[key] = ansible_to_proxmox_bool(value)
            except ValueError:
                pass
        elif key in RENAME_KEYS:
            out[RENAME_KEYS[key]] = value
        else:
            out[key] = value

    # MTU is only for graphite and influxdb (not opentelemetry)
    server_type = params.get("type")
    if server_type == "graphite" and params.get("graphite_mtu") is not None:
        out["mtu"] = params["graphite_mtu"]
    elif server_type == "influxdb" and params.get("influxdb_mtu") is not None:
        out["mtu"] = params["influxdb_mtu"]

    return out


class ProxmoxMetricsServerAnsible(ProxmoxAnsible):
    def __init__(self, module):
        super().__init__(module)
        self.params = module.params

    def run(self):
        state = self.params.get("state")
        server_id = self.params.get("id")

        if state == "present":
            self.metrics_server_present()
        else:
            self.metrics_server_absent(server_id)

    def _get_metrics_servers(self):
        try:
            return self.proxmox_api.cluster.config.metrics.get()
        except Exception as e:
            error_str = str(e).lower()
            if "does not exist" in error_str or "404" in error_str or "no such" in error_str:
                return []
            self.module.fail_json(msg=f"Failed to retrieve metrics servers: {e}")

    def _get_metrics_server(self, server_id):
        servers = self._get_metrics_servers()
        for s in servers:
            if s.get("id") == server_id:
                return s
        return None

    def metrics_server_present(self):
        server_id = self.params.get("id")
        desired = build_metrics_server_params(self.params)

        existing = self._get_metrics_server(server_id)

        if existing is None:
            if self.module.check_mode:
                self.module.exit_json(changed=True, id=server_id, msg=f"Metrics server {server_id} would be created")
            try:
                self.proxmox_api.cluster.config.metrics.post(**desired)
                self.module.exit_json(
                    changed=True, id=server_id, msg=f"Metrics server {server_id} successfully created"
                )
            except Exception as e:
                self.module.fail_json(
                    changed=False, id=server_id, msg=f"Failed to create metrics server {server_id}: {e}"
                )
        else:
            if self.module.check_mode:
                self.module.exit_json(changed=True, id=server_id, msg=f"Metrics server {server_id} would be updated")
            try:
                update_params = {k: v for k, v in desired.items() if k != "id"}
                self.proxmox_api.cluster.config.metrics(server_id).put(**update_params)
                self.module.exit_json(
                    changed=True, id=server_id, msg=f"Metrics server {server_id} successfully updated"
                )
            except Exception as e:
                self.module.fail_json(
                    changed=False, id=server_id, msg=f"Failed to update metrics server {server_id}: {e}"
                )

    def metrics_server_absent(self, server_id):
        existing = self._get_metrics_server(server_id)

        if existing is None:
            self.module.exit_json(changed=False, id=server_id, msg=f"Metrics server {server_id} does not exist")

        if self.module.check_mode:
            self.module.exit_json(changed=True, id=server_id, msg=f"Metrics server {server_id} would be deleted")

        try:
            self.proxmox_api.cluster.config.metrics(server_id).delete()
            self.module.exit_json(changed=True, id=server_id, msg=f"Metrics server {server_id} successfully deleted")
        except Exception as e:
            self.module.fail_json(changed=False, id=server_id, msg=f"Failed to delete metrics server {server_id}: {e}")


def main():
    module = get_ansible_module()
    try:
        validate_params(module.params)
    except Exception as e:
        module.fail_json(msg=str(e))
    proxmox = ProxmoxMetricsServerAnsible(module)

    try:
        proxmox.run()
    except Exception as e:
        module.fail_json(msg=f"An error occurred: {e}")


if __name__ == "__main__":
    main()
