# -*- coding: utf-8 -*-
#
# This file is part of CERN Analysis Preservation Framework.
# Copyright (C) 2020 CERN.
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
# or submit itself to any jurisdiction.

import responses
from flask import current_app
from cap.modules.auth.views import get_oidc_user_groups


@responses.activate
def test_get_groups_by_mail_with_oidc(app):
    endpoint_id = current_app.config.get("OIDC_IDENTITY_API")
    endpoint_tk = current_app.config.get('OIDC_TOKEN_API')
    test_mail = 'test@cern.ch'
    test_uuid = 'test-uuid'

    responses.add(responses.POST, endpoint_tk,
                  json={'access_token': 'test-token'},
                  status=200)
    responses.add(
        responses.GET,
        f'{endpoint_id}/by_email/{test_mail}',
        json={
            "data": [{
                "type": "Person",
                "upn": "test-test",
                "displayName": "Test Test",
                "externalEmail": "test@gmail.com",
                "id": test_uuid
            }]
        },
        status=200)
    responses.add(
        responses.GET,
        f'{endpoint_id}/{test_uuid}/groups',
        json={
            "data": [{
                "groupIdentifier": "test group 1",
                "displayName": "rcs-sis-test",
                "description": "RCS-SIS",
                "ownerId": "c66cc763-b14b-5633-bec5-59715bffgtda",
                "administratorsId": "08d779a7-252c-trft-763c-2d1597f3f71e"
            }, {
                "groupIdentifier": "test group 2",
                "displayName": "rcs-sis-test2",
                "description": "RCS-SIS",
                "ownerId": "r56cc763-rt5b-45ea-bec5-ui715bf882da",
                "administratorsId": "08dfr9a7-54rt-7b7d-763c-2d15gtf3f71e"
                }
            ]
        },
        status=200)

    results = get_oidc_user_groups(test_mail)
    assert len(results) == 2
    assert results[0] == "test group 1"
    assert results[1] == "test group 2"
