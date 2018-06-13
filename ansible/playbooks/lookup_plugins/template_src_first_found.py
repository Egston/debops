# Copyright (C) 2018 DebOps https://debops.org/
# Based on `lookup_plugins/task_src.py` for DebOps
#   (c) 2015 by Robert Chady <rchady@sitepen.com>
# and on `runner/lookup_plugins/file.py` for Ansible
#   (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
#
# This file is part of Debops.
# This file is NOT part of Ansible yet.
#
# Debops is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Debops.  If not, see <https://www.gnu.org/licenses/>.

import os

from debops import *
from debops.cmds import *

'''

This file implements the `template_src_first_found` lookup plugin for
Ansible.

In difference to the `template_src` plugin, this returns first file found.

In difference to the `template` plugin, this searches values based on the
`template-paths` variable (colon separated) as configured in DebOps.

NOTE: This means this filter relies on DebOps.

'''

__copyright__ = "Copyright (C) 2018 DebOps https://debops.org/, 2015 by Robert Chady <rchady@sitepen.com>"
__license__ = "GNU General Public License version 3 (GPL v3) or later"

conf_tpl_paths = 'template-paths'

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase

class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):

        # this can happen if the variable contains a string,
        # strictly not desired for lookup plugins, but users may
        # try it, so make it work.
        if not isinstance(terms, list):
            terms = [terms]

        project_root = find_debops_project(required=False)
        config = read_config(project_root)
        places = []

        if 'paths' in config and conf_tpl_paths in config['paths']:
            custom_places = (
                    config['paths'][conf_tpl_paths].split(':'))
            for custom_path in custom_places:
                if os.path.isabs(custom_path):
                    places.append(custom_path)
                else:
                    places.append(os.path.join(
                        project_root, custom_path))

        if 'role_path' in variables:
            relative_path = (
                    self._loader.path_dwim_relative(
                        variables['role_path'], 'templates',
                        ''))
            places.append(relative_path)

        for term in terms:
            for path in places:
                template = os.path.join(path, term)
                if template and os.path.exists(template):
                    return [template]

        raise AnsibleError(
                "could not locate file in lookup: %s"
                % term)
