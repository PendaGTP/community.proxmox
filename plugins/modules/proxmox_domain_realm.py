#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2026, Clément Cruau (@PendaGTP) <38917281+PendaGTP@users.noreply.github.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

import copy

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.proxmox.plugins.module_utils.proxmox import (
    ProxmoxAnsible,
    proxmox_auth_argument_spec,
)

__metaclass__ = type

DOCUMENTATION = r"""
module: proxmox_domain_realm
short_description: Management of authentication realms for Proxmox VE cluster
description:
  - Create, update or delete Proxmox VE authentication realms.
author:
  - Clément Cruau (@PendaGTP)
version_added: "1.6.0"
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  realm:
    description:
      - The realm name.
    type: str
    aliases: ["name"]
    required: true
  state:
    description:
      - Desired state of the realm.
    choices: ["present", "absent"]
    default: present
    type: str
  type:
    description:
      - The realm type.
      - Only required when O(state=present).
    type: str
    choices: ["ad", "ldap", "openid", "pam", "pve"]
  options:
    description:
      - Realm configuration options.
      - See U(https://pve.proxmox.com/wiki/Manual:_datacenter.cfg) and L(Authentication Realms,https://pve.proxmox.com/pve-docs/chapter-pveum.html).
      - The entire value is masked in logs.
    type: dict

seealso:
  - module: community.proxmox.proxmox_domain_info
    description: Retrieve information about Proxmox VE authentication realms.

extends_documentation_fragment:
  - community.proxmox.proxmox.actiongroup_proxmox
  - community.proxmox.proxmox.documentation
  - community.proxmox.attributes
"""

EXAMPLES = r"""
- name: Update the comment on the pam realm
  community.proxmox.proxmox_domain_realm:
    api_host: node1
    api_user: root@pam
    api_password: password
    realm: pam
    type: pam
    options:
      comment: Updated PAM authentication comment

- name: Create a new Proxmox VE openid realm
  community.proxmox.proxmox_domain_realm:
    api_host: node1
    api_user: root@pam
    api_password: password
    realm: openid
    type: openid
    options:
      comment: OpenID authentication
      client-id: 1234567890
      client-key: 1234567890
      issuer-url: https://example.com/issuer

- name: Delete a Proxmox VE openid realm
  community.proxmox.proxmox_domain_realm:
    api_host: node1
    api_user: root@pam
    api_password: password
    realm: openid
    state: absent
"""

RETURN = r"""
realm:
  description: The realm name.
  returned: success
  type: str
  sample: test
msg:
  description: A short message on what the module did.
  returned: always
  type: str
  sample: "Realm test successfully created"
"""


def get_proxmox_args():
    return dict(
        state=dict(default="present", choices=["present", "absent"]),
        realm=dict(aliases=["name"], required=True),
        type=dict(choices=["ad", "ldap", "openid", "pam", "pve"]),
        options=dict(type="dict", no_log=True),
    )


def get_ansible_module():
    module_args = proxmox_auth_argument_spec()
    module_args.update(get_proxmox_args())

    return AnsibleModule(
        argument_spec=module_args,
        required_if=[("state", "present", ("type",))],
        supports_check_mode=True,
    )


class ProxmoxDomainRealmAnsible(ProxmoxAnsible):
    def __init__(self, module):
        super(ProxmoxDomainRealmAnsible, self).__init__(module)
        self.params = module.params

    def run(self):
        state = self.params.get("state")

        domain_realm_params = {
            "realm": self.params.get("realm"),
            "type": self.params.get("type"),
            "options": self.params.get("options"),
        }

        if state == "present":
            self.domain_realm_present(domain_realm_params)
        elif state == "absent":
            self.domain_realm_absent(domain_realm_params["realm"])

    def _get_domain_realm(self, realm):
        try:
            return self.proxmox_api.access.domains.get(realm)
        except Exception as e:
            error_str = str(e).lower()
            if "does not exist" in error_str:
                return None
            self.module.fail_json(msg=f"Failed to retrieve realm {realm}: {e}")

    def domain_realm_present(self, domain_realm_params):
        realm = domain_realm_params["realm"]
        realm_type = domain_realm_params["type"]
        options = copy.deepcopy(domain_realm_params["options"] or {})
        options.pop("type", None)

        existing_domain_realm = self._get_domain_realm(realm)

        if existing_domain_realm is None:
            if self.module.check_mode:
                self.module.exit_json(changed=True, realm=realm, msg=f"Realm {realm} would be created")
            try:
                self.proxmox_api.access.domains.post(realm=realm, type=realm_type, **options)
                self.module.exit_json(changed=True, realm=realm, msg=f"Realm {realm} successfully created")
            except Exception as e:
                self.module.fail_json(changed=False, realm=realm, msg=f"Failed to create realm {realm}: {e}")
        else:
            current_options = {k: v for k, v in existing_domain_realm.items() if k not in ("digest", "type")}
            needs_update = any(options.get(k) != current_options.get(k) for k in options)

            if not needs_update:
                self.module.exit_json(
                    changed=False, realm=realm, msg=f"Realm {realm} already exists with desired options"
                )

            if self.module.check_mode:
                self.module.exit_json(changed=True, realm=realm, msg=f"Realm {realm} would be updated")

            try:
                self.proxmox_api.access.domains(realm).put(realm=realm, **options)
                self.module.exit_json(changed=True, realm=realm, msg=f"Realm {realm} successfully updated")
            except Exception as e:
                self.module.fail_json(changed=False, realm=realm, msg=f"Failed to update realm {realm}: {e}")

    def domain_realm_absent(self, realm):
        existing_domain_realm = self._get_domain_realm(realm)

        if existing_domain_realm is None:
            self.module.exit_json(changed=False, realm=realm, msg=f"Realm {realm} does not exist")

        if self.module.check_mode:
            self.module.exit_json(changed=True, realm=realm, msg=f"Realm {realm} would be deleted")

        try:
            self.proxmox_api.access.domains(realm).delete()
            self.module.exit_json(changed=True, realm=realm, msg=f"Realm {realm} successfully deleted")
        except Exception as e:
            self.module.fail_json(changed=False, realm=realm, msg=f"Failed to delete realm {realm}: {e}")


def main():
    module = get_ansible_module()
    proxmox = ProxmoxDomainRealmAnsible(module)

    try:
        proxmox.run()
    except Exception as e:
        module.fail_json(msg="An error occurred: {0}".format(e))


if __name__ == "__main__":
    main()
