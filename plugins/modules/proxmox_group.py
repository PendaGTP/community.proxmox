#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2025, Jeffrey van Pelt (@Thulium-Drake) <jeff@vanpelt.one>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-FileCopyrightText: (c) 2025, Jeffrey van Pelt (Thulium-Drake) <jeff@vanpelt.one>
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
module: proxmox_group
short_description: Group management for Proxmox VE cluster
description:
  - Create or delete a user group for Proxmox VE clusters.
author:
  - "Jeffrey van Pelt (@Thulium-Drake) <jeff@vanpelt.one>"
  - Clément Cruau (@PendaGTP)
version_added: "1.2.0"
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  groupid:
    description:
      - The group name.
    type: str
    aliases: ["name"]
    required: true
  state:
    description:
      - Indicate desired state of the group.
    choices: ["present", "absent"]
    default: present
    type: str
  comment:
    description:
      - Specify the description for the group.
      - If not specified, considered as an empty comment.
    type: str

extends_documentation_fragment:
  - community.proxmox.proxmox.actiongroup_proxmox
  - community.proxmox.proxmox.documentation
  - community.proxmox.attributes
"""

EXAMPLES = r"""
- name: Create new Proxmox VE user group
  community.proxmox.proxmox_group:
    api_host: node1
    api_user: root@pam
    api_password: password
    name: administrators
    comment: IT Admins

- name: Delete a Proxmox VE user group
  community.proxmox.proxmox_group:
    api_host: node1
    api_user: root@pam
    api_password: password
    name: administrators
    state: absent
"""

RETURN = r"""
groupid:
  description: The group name.
  returned: success
  type: str
  sample: test
msg:
  description: A short message on what the module did.
  returned: always
  type: str
  sample: "Group test successfully created"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.proxmox.plugins.module_utils.proxmox import (proxmox_auth_argument_spec, ProxmoxAnsible)


def get_proxmox_args():
    return dict(
        state=dict(default="present", choices=[
                   "present", "absent"], required=False),
        groupid=dict(type="str", aliases=["name"], required=True),
        comment=dict(type="str"),
    )


def get_ansible_module():
    module_args = proxmox_auth_argument_spec()
    module_args.update(get_proxmox_args())

    return AnsibleModule(
        argument_spec=module_args,
        required_together=[("api_token_id", "api_token_secret")],
        required_one_of=[("api_password", "api_token_id")],
        supports_check_mode=True
    )


class ProxmoxGroupAnsible(ProxmoxAnsible):

    def __init__(self, module):
        super(ProxmoxGroupAnsible, self).__init__(module)
        self.params = module.params

    def run(self):
        state = self.params.get("state")

        group_params = {
            "groupid": self.params.get("groupid"),
            "comment": self.params.get("comment"),
        }

        if state == "present":
            self.group_present(group_params)
        elif state == "absent":
            self.group_absent(group_params["groupid"])

    def _get_group(self, groupid):
        try:
            return self.proxmox_api.access.groups.get(groupid)
        except Exception as e:
            error_str = str(e).lower()
            if "does not exist" in error_str:
                return None
            self.module.fail_json(
                msg=f"Failed to retrieve group {groupid}: {e}"
            )

    def group_present(self, group_params):
        groupid = group_params["groupid"]
        desired_comment = group_params["comment"] or ""

        existing_group = self._get_group(groupid)

        if existing_group is None:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    groupid=groupid,
                    msg=f"Group {groupid} would be created"
                )

            try:
                self.proxmox_api.access.groups.post(
                    groupid=groupid, comment=desired_comment)
                self.module.exit_json(
                    changed=True,
                    groupid=groupid,
                    msg=f"Group {groupid} successfully created"
                )
            except Exception as e:
                self.module.fail_json(
                    changed=False,
                    groupid=groupid,
                    msg=f"Failed to create group {groupid}: {e}"
                )
        else:
            needs_update = desired_comment != existing_group.get('comment', '')

            if not needs_update:
                self.module.exit_json(
                    changed=False,
                    groupid=groupid,
                    msg=f"Group {groupid} already exists with desired comment"
                )

            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    groupid=groupid,
                    msg=f"Group {groupid} would be updated"
                )

            try:
                self.proxmox_api.access.groups(
                    groupid).put(comment=desired_comment)
                self.module.exit_json(
                    changed=True,
                    groupid=groupid,
                    msg=f"Group {groupid} successfully updated"
                )

            except Exception as e:
                self.module.warn(
                    f"Failed to update group {groupid}: {e}")
                self.module.fail_json(
                    changed=False,
                    groupid=groupid,
                    msg=f"Failed to update group {groupid}: {e}"
                )

    def group_absent(self, groupid):
        existing_group = self._get_group(groupid)

        if existing_group is None:
            self.module.exit_json(
                changed=False,
                groupid=groupid,
                msg=f"Group {groupid} does not exist"
            )

        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                groupid=groupid,
                msg=f"Group {groupid} would be deleted"
            )

        try:
            self.proxmox_api.access.groups(groupid).delete()
            self.module.exit_json(
                changed=True,
                groupid=groupid,
                msg=f"Group {groupid} successfully deleted"
            )
        except Exception as e:
            self.module.fail_json(
                changed=False,
                groupid=groupid,
                msg=f"Failed to delete group {groupid}: {e}"
            )


def main():
    module = get_ansible_module()
    proxmox = ProxmoxGroupAnsible(module)

    try:
        proxmox.run()
    except Exception as e:
        module.fail_json(msg="An error occurred: {0}".format(e))


if __name__ == "__main__":
    main()
