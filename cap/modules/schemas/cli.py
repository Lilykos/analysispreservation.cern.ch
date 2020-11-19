# * coding: utf8 *
#
# This file is part of CERN Analysis Preservation Framework.
# Copyright (C) 2016 CERN.
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
# MA 021111307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.
"""CAP Schema cli."""

import json
import os

import click
from flask_cli import with_appcontext
from invenio_db import db
from invenio_jsonschemas.errors import JSONSchemaNotFound
from invenio_search import current_search_client
from sqlalchemy.exc import IntegrityError

from cap.cli import MutuallyExclusiveOption
from cap.modules.deposit.errors import DepositValidationError
from cap.modules.fixtures.cli import fixtures
from cap.modules.records.api import CAPRecord
from cap.modules.schemas.models import Schema
from cap.modules.schemas.resolvers import resolve_schema_by_url,\
    resolve_schema_by_name_and_version, schema_name_to_url


@fixtures.command()
@click.option('--schema-url', '-u',
              cls=MutuallyExclusiveOption,
              mutually_exclusive=["ana_type", "ana_version"],
              help='The url of the schema used for validation.')
@click.option('--ana-type', '-a',
              cls=MutuallyExclusiveOption,
              mutually_exclusive=["schema_url"],
              help='The analysis type of the schema used for validation.')
@click.option('--ana-version', '-v',
              help='The analysis version of the records.')
@click.option('--compare-with', '-c',
              help='The schema version, that the '
                   'records should be compared to.')
@click.option('--status', '-s',
              default='draft',
              type=click.Choice(['draft', 'published'], case_sensitive=False),
              help='The metadata type that will be used for validation.')
@click.option('--export', '-e',
              type=click.Path(),
              help='A file where, the validation errors can be saved.')
@with_appcontext
def validate(schema_url, ana_type, ana_version, compare_with, status, export):
    """
    Validate deposit or record metadata based on their schema. Provide the
    schema url OR ana-type and version, as well as the schema version that you
    want to compare the records you get, to. E.g.

    If you do not provide an ana-version, it will get the latest. If you do
    not provide a -c parameter, the records will compare the data to their
    own schema.

    cap fixtures validate -u https://analysispreservation.cern.ch/schemas/deposits/records/test-v2.0.0.json -c 1.0.0  # noqa
    cap fixtures validate -a test -c 1.0.0
    """
    try:
        if schema_url:
            schema = resolve_schema_by_url(schema_url)
        elif ana_type:
            schema = resolve_schema_by_name_and_version(ana_type, ana_version)
        else:
            raise click.UsageError(
                'You need to provide the ana-type or the schema-url.')
    except JSONSchemaNotFound:
        raise click.UsageError(
            'Schema not found.')
    except ValueError:
        raise click.UsageError(
            'Version has to be passed as string <major>.<minor>.<patch>.')

    # differentiate between drafts/published
    from cap.modules.deposit.api import CAPDeposit
    if status == 'draft':
        search_path = 'deposits-records'
        cap_record_class = CAPDeposit
    else:
        search_path = 'records'
        cap_record_class = CAPRecord

    # get all the records for this specific schema/type combination
    records = current_search_client.search(
        search_path,
        q=f'_deposit.status: {status} AND '
          f'$schema: "{schema_name_to_url(schema.name, schema.version)}"',
        size=5000
    )['hits']['hits']
    pids = [rec['_id'] for rec in records]

    click.secho(
        f'{len(records)} record(s) of {schema.name} found.\n', fg='green')

    total_errors = []
    for pid in pids:
        cap_record = cap_record_class.get_record(pid)

        # get the url of the schema version, used for validation
        if compare_with:
            cap_record['$schema'] = schema_name_to_url(
                schema.name, compare_with)
        try:
            cap_record.validate()
            click.secho(f'No errors found in record {pid}', fg='green')
        except DepositValidationError as exc:
            error_list = '\n'.join(str(err.res) for err in exc.errors)
            msg = f'Errors in {pid}:\n{error_list}'
            click.secho(msg, fg='red')

            if export:
                total_errors.append(msg)

    # export the errors in a file
    if export:
        with open(export, 'w') as out:
            out.writelines('\n\n'.join(err for err in total_errors))
        click.secho(f'Errors saved at {export}.', fg='red')


@fixtures.command()
@with_appcontext
@click.option('--dir',
              '-d',
              type=click.Path(exists=True),
              default='cap/modules/fixtures/schemas')
def schemas(dir):
    """Load default schemas."""
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith(".json"):
                fullpath = os.path.join(root, file)
                with open(fullpath, 'r') as f:
                    try:
                        json_content = json.load(f)
                        add_schema_from_fixture(data=json_content)
                    except ValueError:
                        click.secho(
                            "Not valid json in {} file".format(fullpath),
                            fg='red')
                        continue


def add_schema_from_fixture(data=None):
    """Add or update schema."""
    allow_all = data.pop("allow_all", False)
    name = data['name']

    try:
        with db.session.begin_nested():
            with db.session.begin_nested():
                try:
                    schema = Schema.get(name=data['name'],
                                        version=data['version'])
                    click.secho('{} already exist in the db.'.format(
                        str(name)))
                    return

                except JSONSchemaNotFound:
                    schema = Schema(**data)
                    db.session.add(schema)

            if allow_all:
                schema.add_read_access_for_all_users()

    except IntegrityError:
        click.secho('Error occured during adding {} to the db. \n'.format(
            str(name)),
                    fg='red')
        return

    db.session.commit()
    click.secho('{} has been added.'.format(str(name)), fg='green')
