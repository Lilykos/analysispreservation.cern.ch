# -*- coding: utf-8 -*-
#
# This file is part of CERN Analysis Preservation Framework.
# Copyright (C) 2018 CERN.
#
# CERN Analysis Preservation Framework is free software; you can redistribute
# it and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# CERN Analysis Preservation Framework is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CERN Analysis Preservation Framework; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.


"""CAP ORCID service views."""

import requests

from flask import Blueprint, current_app, jsonify, request
from invenio_files_rest.models import FileInstance, ObjectVersion

from cap.modules.access.utils import login_required

from . import blueprint


@blueprint.route('/orcid')
@login_required
def get_orcid():
    """Get ORCID identifier registered for given name."""
    name = request.args.get('name', None)
    res = {}

    if not name:
        return jsonify(res)

    names = name.split()
    url = "https://pub.orcid.org/v2.1/search/?" \
        "q=given-names:{}+AND+family-name:{}" \
        .format(names[0], names[-1])

    resp = requests.get(url=url, headers={
        'Content-Type': 'application/json'
    })
    data = resp.json().get('result', [])

    # return only if one result
    if len(data) == 1:
        res['orcid'] = data[0]['orcid-identifier']['path']

    return jsonify(res)


@blueprint.route('/orcid/<orcid>')
@login_required
def get_record_by_orcid(orcid):
    """Get ORCID identifier registered for given name."""
    url = "https://pub.orcid.org/v2.1/{}/record" \
        .format(orcid)

    resp = requests.get(url=url, headers={
        'Content-Type': 'application/json'
    })
    data = resp.json()

    return jsonify(data)