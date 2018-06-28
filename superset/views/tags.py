# -*- coding: utf-8 -*-
# pylint: disable=C,R,W
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import simplejson as json

from flask import Response, request
from flask_appbuilder import expose
from flask_babel import gettext as __
from sqlalchemy import and_
from werkzeug.routing import BaseConverter

from superset import app, appbuilder, db
from superset.models.tags import Tag, TaggedObject, TagTypes, ObjectTypes
from .base import BaseSupersetView, json_error_response


class ObjectTypeConverter(BaseConverter):

    """Validate that object_type is indeed an object type."""

    def to_python(self, object_type):
        return ObjectTypes[object_type]

    def to_url(self, object_type):
        return object_type.name


class TagView(BaseSupersetView):

    @expose('/tags/<object_type:object_type>/<int:object_id>/', methods=['GET'])
    def get(self, object_type, object_id):
        """List all tags a given object has."""
        query = db.session.query(TaggedObject).filter(and_(
            TaggedObject.object_type == object_type,
            TaggedObject.object_id == object_id))
        tags = json.dumps([obj.tag.name for obj in query])

        return Response(tags, status=200, content_type='application/json')

    @expose('/tags/<object_type:object_type>/<int:object_id>/', methods=['POST'])
    def post(self, object_type, object_id):
        tagged_objects = []
        for value in request.get_json(force=True):
            if ':' in value:
                type_name, name = value.split(':', 1)
                type_ = TagTypes[type_name]
            else:
                type_, name = TagTypes.custom, value

            tag = db.session.query(Tag).filter_by(name=name, type=type_).first()
            if not tag:
                tag = Tag(name=name, type=type_)

            tagged_objects.append(
                TaggedObject(
                    object_id=object_id,
                    object_type=object_type,
                    tag=tag,
                )
            )

        db.session.add_all(tagged_objects)
        db.session.commit()

        return Response(status=201)  # 201 CREATED

    @expose('/tags/<object_type:object_type>/<int:object_id>/', methods=['DELETE'])
    def delete(self, object_type, object_id):
        tag_names = request.get_json(force=True)
        if not tag_names:
            return Response(status=403)

        db.session.query(TaggedObject).filter(and_(
            TaggedObject.object_type == object_type,
            TaggedObject.object_id == object_id),
            TaggedObject.tag.has(Tag.name.in_(tag_names)),
        ).delete(synchronize_session=False)
        db.session.commit()
        
        return Response(status=204)  # 204 NO CONTENT


app.url_map.converters['object_type'] = ObjectTypeConverter
appbuilder.add_view_no_menu(TagView)
