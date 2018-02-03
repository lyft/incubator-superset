from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import logging
import traceback

from flask import (
     g, request, Response,
)
from flask_appbuilder import expose
from flask_appbuilder.security.decorators import has_access_api
from flask_babel import gettext as __

from superset import (
    app, appbuilder, db, utils,
)

import superset.models.core as models
from superset.views.core import Superset
from superset.utils import QueryStatus
from .base import (
    json_error_response, generate_download_headers, CsvResponse,
)

config = app.config
stats_logger = config.get('STATS_LOGGER')
log_this = models.Log.log_this
can_access = utils.can_access
DAR = models.DatasourceAccessRequest


ALL_DATASOURCE_ACCESS_ERR = __(
    'This endpoint requires the `all_datasource_access` permission')
DATASOURCE_MISSING_ERR = __('The datasource seems to have been deleted')
ACCESS_REQUEST_MISSING_ERR = __(
    'The access requests seem to have been deleted')
USER_MISSING_ERR = __('The user seems to have been deleted')
DATASOURCE_ACCESS_ERR = __("You don't have access to this datasource")


def json_success(json_msg, status=200):
    return Response(json_msg, status=status, mimetype='application/json')


class Lyft(Superset):

    def generate_json(self, datasource_type, datasource_id, form_data,
                      csv=False, query=False, force=False):
        try:
            viz_obj = self.get_viz(
                datasource_type=datasource_type,
                datasource_id=datasource_id,
                form_data=form_data)
        except Exception as e:
            logging.exception(e)
            return json_error_response(
                utils.error_msg_from_exception(e),
                stacktrace=traceback.format_exc())

        if csv:
            return CsvResponse(
                viz_obj.get_csv(),
                status=200,
                headers=generate_download_headers('csv'),
                mimetype='application/csv')

        if query:
            return self.get_query_string_response(viz_obj)

        try:
            payload = viz_obj.get_payload(
                force=force)
        except Exception as e:
            logging.exception(e)
            return json_error_response(utils.error_msg_from_exception(e))

        status = 200
        if payload.get('status') == QueryStatus.FAILED:
            status = 400

        return json_success(viz_obj.json_dumps(payload), status=status)


appbuilder.add_view_no_menu(Lyft)
