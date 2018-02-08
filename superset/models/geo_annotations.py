"""a collection of GeoJSON annotation-related models"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from flask_appbuilder import Model
from sqlalchemy import (
    Column, DateTime, ForeignKey, Index, Integer, String, Text,
)
from sqlalchemy.orm import relationship

from superset.models.helpers import AuditMixinNullable


class GeoAnnotationLayer(Model, AuditMixinNullable):

    """A logical namespace for a set of GeoJSON annotations"""

    __tablename__ = 'geo_annotation_layer'
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    descr = Column(Text)

    def __repr__(self):
        return self.name


class GeoAnnotation(Model, AuditMixinNullable):

    """GeoJSON annotation"""

    __tablename__ = 'geo_annotation'
    id = Column(Integer, primary_key=True)
    start_dttm = Column(DateTime)
    end_dttm = Column(DateTime)
    layer_id = Column(Integer, ForeignKey('geo_annotation_layer.id'))
    short_descr = Column(String(500))
    long_descr = Column(Text)
    geojson = Column(Text)
    layer = relationship(
        GeoAnnotationLayer,
        backref='geo_annotation')

    __table_args__ = (
        Index('ti_geo_annotation', layer_id, start_dttm, end_dttm),
    )

    @property
    def data(self):
        return {
            'layer_id': self.layer_id,
            'start_dttm': self.start_dttm,
            'end_dttm': self.end_dttm,
            'short_descr': self.short_descr,
            'long_descr': self.long_descr,
            'geojson': self.geojson,
            'layer': self.layer.name if self.layer else None,
        }
