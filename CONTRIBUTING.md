<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

# Contributing

We're following the general Ansible contributor guidelines; see [Ansible community guide](https://docs.ansible.com/projects/ansible/latest/community/index.html).

## Open pull requests

Please read our ['Contributing to collections'](https://docs.ansible.com/projects/ansible/devel/dev_guide/developing_collections_contributing.html#contributing-to-a-collection-community-general).

- Try committing your changes with an informative but short commit message.
- Do not squash your commits and force-push to your branch if not needed. Reviews of your pull request are much easier with individual commits to comprehend the pull request history. All commits of your pull request branch will be squashed into one commit by GitHub upon merge.
- Make sure your PR includes a [changelog fragment](https://docs.ansible.com/projects/ansible/devel/community/collection_development_process.html#creating-a-changelog-fragment) (in [fragments folder](https://github.com/ansible-collections/community.proxmox/tree/main/changelogs/fragments)), see below in sub-section for examples.
  - You must not include a fragment for new modules. Also you shouldn't include one for docs-only changes. (If you're not sure, simply don't include one, we'll tell you whether one is needed or not :) )
  - Please always include a link to the pull request itself, and if the PR is about an issue, also a link to the issue. Also make sure the fragment ends with a period, and begins with a lower-case letter after `-`. (Again, if you don't do this, we'll add suggestions to fix it, so don't worry too much :) )
- Note that we format the code with `ruff format`. If your change does not match the formatters expectations, CI will fail and your PR will not get merged. See below for how to format code with antsibull-nox.

You can also read the Ansible community's [Quick-start development guide](https://docs.ansible.com/projects/ansible/devel/community/create_pr_quick_start.html).

### Changelog fragments examples

Minor change, bugfixes or anything else small that does break existing tasks:

```yml
---
minor_changes:
  - module name - short description of the change, PR title could be fine (https://github.com/ansible-collections/community.proxmox/issues/XXX, https://github.com/ansible-collections/community.proxmox/pull/XXX).
```

Breaking changes, anything that requires end-users to change something on their end as well:

```yml
---
breaking_changes:
  - module name - will start eating your dog without ``dont_eat_dog: true`` (https://github.com/ansible-collections/community.proxmox/issues/XXX, https://github.com/ansible-collections/community.proxmox/pull/XXX).
```

Removed features:

```yml
---
removed_features:
  - Description of removed feature, module etc (https://github.com/ansible-collections/community.proxmox/issues/XXX, https://github.com/ansible-collections/community.proxmox/pull/XXX).
```

**Reminder:** You must not include a fragment for new modules. Also you shouldn't include one for docs-only changes.

## Test pull requests

If you want to test a PR locally, refer to [the community testing guide](https://docs.ansible.com/projects/ansible/devel/community/collection_contributors/collection_test_pr_locally.html) for instructions on how do it quickly.

## Format code; and run sanity or unit tests locally (with antsibull-nox)

The easiest way to format the code, and to run sanity and unit tests locally is to use [antsibull-nox](https://docs.ansible.com/projects/antsibull-nox/).
(If you have [nox](https://nox.thea.codes/en/stable/) installed, it will automatically install antsibull-nox in a virtual environment for you.)

### Format code

The following commands show how to run ansible-test sanity tests:

```bash
# Run all configured formatters:
nox -Re formatters

# If you notice discrepancies between your local formatter and CI, you might
# need to re-generate the virtual environment:
nox -e formatters
```

### Unit tests

The following commands show how to run unit tests:

```bash
# Run all unit tests:
nox -Re ansible-test-units-devel

# Run all unit tests for one Python version (a lot faster):
nox -Re ansible-test-units-devel -- --python 3.13

# Run a specific unit test (for the nmcli module) for one Python version:
nox -Re ansible-test-units-devel -- --python 3.13 tests/unit/plugins/modules/net_tools/test_nmcli.py
```

If you replace `-Re` with `-e`, then the virtual environments will be re-created. The `-R` re-uses them (if they already exist).

## Run basic sanity, unit or integration tests locally (with ansible-test)

Instead of using antsibull-nox, you can also run sanity and unit tests with ansible-test directly.
This also allows you to run integration tests.

You have to check out the repository into a specific path structure to be able to run `ansible-test`. The path to the git checkout must end with `.../ansible_collections/community/proxmox`. Please see [the community testing guide](https://docs.ansible.com/projects/ansible/devel/community/collection_contributors/collection_test_pr_locally.html) for instructions on how to check out the repository into a correct path structure. The short version of these instructions is:

```bash
mkdir -p ~/dev/ansible_collections/community
git clone https://github.com/ansible-collections/community.proxmox.git ~/dev/ansible_collections/community/proxmox
cd ~/dev/ansible_collections/community/proxmox
```

Then you can run `ansible-test` (which is a part of [ansible-core](https://pypi.org/project/ansible-core/)) inside the checkout. The following example commands expect that you have installed Docker or Podman. Note that Podman has only been supported by more recent ansible-core releases. If you are using Docker, the following will work with Ansible 2.9+.

### Basic sanity tests

The following commands show how to run basic sanity tests:

```bash
# Run basic sanity tests for all files in the collection:
ansible-test sanity --docker -v

# Run basic sanity tests for the given files and directories:
ansible-test sanity --docker -v plugins/modules/proxmox_cluster.py tests/integration/targets/proxmox/
```

### Unit tests

Note that for running unit tests, you need to install required collections in the same folder structure that `community.proxmox` is checked out in.
Right now, you need to install [`community.internal_test_tools`](https://github.com/ansible-collections/community.internal_test_tools).
If you want to use the latest version from GitHub, you can run:

```bash
git clone https://github.com/ansible-collections/community.internal_test_tools.git ~/dev/ansible_collections/community/internal_test_tools
```

The following commands show how to run unit tests:

```bash
# Run all unit tests:
ansible-test units --docker -v

# Run all unit tests for one Python version (a lot faster):
ansible-test units --docker -v --python 3.8

# Run a specific unit test (for the nmcli module) for one Python version:
ansible-test units --docker -v --python 3.8 tests/unit/plugins/modules/test_proxmox_cluster.py
```

## Creating new modules

Creating new modules requires a bit more work than other Pull Requests.

1. Please do not add more than one module in one PR, especially if it is the first module you are contributing.
   That makes it easier for reviewers, and increases the chance that your PR will get merged.

2. When creating a new module, please make sure that you follow various guidelines:
   - Follow [development conventions](https://docs.ansible.com/projects/ansible/devel/dev_guide/developing_modules_best_practices.html);
   - Follow [documentation standards](https://docs.ansible.com/projects/ansible/devel/dev_guide/developing_modules_documenting.html) and
     the [Ansible style guide](https://docs.ansible.com/projects/ansible/devel/dev_guide/style_guide/index.html#style-guide);
   - Make sure your modules are [GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0-standalone.html) licensed
     (new module_utils can also be [BSD-2-clause](https://opensource.org/licenses/BSD-2-Clause) licensed);
   - Make sure that new modules have tests (unit tests, integration tests, or both); it is preferable to have some tests
     which run in CI.

   When you add a new module, we expect that you perform maintainer duty for at least some time after contributing it.
