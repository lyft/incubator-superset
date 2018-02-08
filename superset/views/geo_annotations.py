from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_babel import gettext as __

from superset import appbuilder
from superset.models.geo_annotations import GeoAnnotation, GeoAnnotationLayer
from .base import DeleteMixin, SupersetModelView


class GeoAnnotationModelView(SupersetModelView, DeleteMixin):  # noqa
    datamodel = SQLAInterface(GeoAnnotation)
    list_columns = ['layer', 'short_descr', 'start_dttm', 'end_dttm']
    edit_columns = [
        'layer',
        'short_descr',
        'long_descr',
        'geojson',
        'start_dttm',
        'end_dttm',
    ]
    add_columns = edit_columns

    def pre_add(self, obj):
        if not obj.layer:
            raise Exception('GeoAnnotation layer is required.')
        if not obj.geojson:
            raise Exception('GeoAnnotation GeoJSON is required.')

        if not obj.start_dttm and not obj.end_dttm:
            return
        elif obj.end_dttm and not obj.start_dttm:
            obj.start_dttm = obj.end_dttm
        elif obj.start_dttm and not obj.end_dttm:
            obj.end_dttm = obj.start_dttm
        elif obj.end_dttm < obj.start_dttm:
            raise Exception('GeoAnnotation end time must be no earlier than start time.')

    def pre_update(self, obj):
        self.pre_add(obj)


class GeoAnnotationLayerModelView(SupersetModelView, DeleteMixin):
    datamodel = SQLAInterface(GeoAnnotationLayer)
    list_columns = ['id', 'name']
    edit_columns = ['name', 'descr']
    add_columns = edit_columns


appbuilder.add_view(
    GeoAnnotationLayerModelView,
    'GeoAnnotation Layers',
    label=__('GeoAnnotation Layers'),
    icon='fa-comment',
    category='Manage',
    category_label=__('Manage'),
    category_icon='')
appbuilder.add_view(
    GeoAnnotationModelView,
    'GeoAnnotations',
    label=__('GeoAnnotations'),
    icon='fa-comments',
    category='Manage',
    category_label=__('Manage'),
    category_icon='')
