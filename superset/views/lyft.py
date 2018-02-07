from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import logging
from flask import Response, request
from flask_babel import gettext as __
from flask_appbuilder import expose
from flask_appbuilder.security.decorators import has_access_api

from superset import app, appbuilder, utils
import superset.models.core as models
from superset.views.core import Superset

config = app.config
stats_logger = config.get('STATS_LOGGER')
log_this = models.Log.log_this
DAR = models.DatasourceAccessRequest


ALL_DATASOURCE_ACCESS_ERR = __(
    'This endpoint requires the `all_datasource_access` permission')
DATASOURCE_MISSING_ERR = __('The datasource seems to have been deleted')
ACCESS_REQUEST_MISSING_ERR = __(
    'The access requests seem to have been deleted')
USER_MISSING_ERR = __('The user seems to have been deleted')
DATASOURCE_ACCESS_ERR = __("You don't have access to this datasource")
SECRET_KEY = os.getenv("CREDENTIALS_SUPERSET_SECRET_KEY") or None


def json_success(json_msg, status=200):
    return Response(json_msg, status=status, mimetype='application/json')


class Lyft(Superset):

    def datasource_access(self, datasource, user=None):
        if SECRET_KEY is None:
            logging.error('No secret loaded')
            return False

        tom_request_key = request.headers.get('TOM_ACCESS_KEY')
        return tom_request_key == SECRET_KEY

    @has_access_api
    @expose('/sql_json/', methods=['POST', 'GET'])
    @log_this
    def sql_json(self):
        return super(Lyft, self).sql_json()


appbuilder.add_view_no_menu(Lyft)
