# -*- coding: utf-8 -*-
# pylint: disable=C,R,W
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import simplejson as json

from flask import Response, request
from flask_appbuilder import expose
from sqlalchemy import and_, func
from werkzeug.routing import BaseConverter

from superset import app, appbuilder, db
from superset.models.tags import Tag, TaggedObject, TagTypes, ObjectTypes
from .base import BaseSupersetView


class ObjectTypeConverter(BaseConverter):

    """Validate that object_type is indeed an object type."""

    def to_python(self, object_type):
        return ObjectTypes[object_type]

    def to_url(self, object_type):
        return object_type.name


class TagView(BaseSupersetView):

    @expose('/tags/suggestions/', methods=['GET'])
    def suggestions(self):
        query = db.session.query(
            TaggedObject,
        ).group_by(TaggedObject.tag_id).order_by(func.count().desc()).all()
        tags = json.dumps([
            {'id': obj.tag.id, 'name': obj.tag.name} for obj in query])

        return Response(tags, status=200, content_type='application/json')

    @expose('/tags/<object_type:object_type>/<int:object_id>/', methods=['GET'])
    def get(self, object_type, object_id):
        """List all tags a given object has."""
        query = db.session.query(TaggedObject).filter(and_(
            TaggedObject.object_type == object_type,
            TaggedObject.object_id == object_id))
        tags = json.dumps([
            {'id': obj.tag.id, 'name': obj.tag.name} for obj in query])

        return Response(tags, status=200, content_type='application/json')

    @expose('/tags/<object_type:object_type>/<int:object_id>/', methods=['POST'])
    def post(self, object_type, object_id):
        """Add new tags to an object."""
        tagged_objects = []
        for name in request.get_json(force=True):
            if ':' in name:
                type_name = name.split(':', 1)[0]
                type_ = TagTypes[type_name]
            else:
                type_ = TagTypes.custom

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
        """Remove tags from an object."""
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
