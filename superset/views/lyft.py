from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from flask import Response, request, g
from flask_appbuilder import expose

from superset import app, appbuilder, security_manager
import superset.models.core as models
from superset.views.core import Superset

config = app.config
stats_logger = config.get('STATS_LOGGER')
log_this = models.Log.log_this
DAR = models.DatasourceAccessRequest


def json_success(json_msg, status=200):
    return Response(json_msg, status=status, mimetype='application/json')


class Lyft(Superset):

    def impersonate(self, email):
        user = security_manager.find_user(email=email)
        if not user:
            raise Exception("Email not found")
        g.user = user

    @expose('/sql_json/', methods=['POST', 'GET'])
    @log_this
    def sql_json(self):
        impersonate = request.headers.get('IMPERSONATE')
        if impersonate:
            self.impersonate(impersonate)
        return self.sql_json_call(request)


appbuilder.add_view_no_menu(Lyft)
