# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# pylint: disable=C,R,W
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from flask import request, Response
from flask_appbuilder import expose
from flask_appbuilder.security.decorators import has_access_api
from jinja2.sandbox import SandboxedEnvironment
import simplejson as json
from sqlalchemy import and_, func
from werkzeug.routing import BaseConverter

from superset import app, appbuilder, db, utils
from superset.jinja_context import current_user_id, current_username
import superset.models.core
from superset.models.sql_lab import SavedQuery
from superset.models.tags import ObjectTypes, Tag, TaggedObject, TagTypes
from .base import BaseSupersetView, json_success


class ObjectTypeConverter(BaseConverter):

    """Validate that object_type is indeed an object type."""

    def to_python(self, object_type):
        return ObjectTypes[object_type]

    def to_url(self, object_type):
        return object_type.name


def process_template(content):
    env = SandboxedEnvironment()
    template = env.from_string(content)
    context = {
        'current_user_id': current_user_id,
        'current_username': current_username,
    }
    return template.render(context)


class TagView(BaseSupersetView):

    @has_access_api
    @expose('/tags/suggestions/', methods=['GET'])
    def suggestions(self):
        query = (
            db.session.query(TaggedObject)
            .with_entities(TaggedObject.tag_id, Tag.name)
            .group_by(TaggedObject.tag_id, Tag.name)
            .order_by(func.count().desc())
            .all()
        )
        tags = [{'id': id, 'name': name} for id, name in query]
        return json_success(json.dumps(tags))

    @has_access_api
    @expose('/tags/<object_type:object_type>/<int:object_id>/', methods=['GET'])
    def get(self, object_type, object_id):
        """List all tags a given object has."""
        query = db.session.query(TaggedObject).filter(and_(
            TaggedObject.object_type == object_type,
            TaggedObject.object_id == object_id))
        tags = [{'id': obj.tag.id, 'name': obj.tag.name} for obj in query]
        return json_success(json.dumps(tags))

    @has_access_api
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
                ),
            )

        db.session.add_all(tagged_objects)
        db.session.commit()

        return Response(status=201)  # 201 CREATED

    @has_access_api
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

    @has_access_api
    @expose('/tagged_objects/', methods=['GET', 'POST'])
    def tagged_objects(self):
        """
        query = db.session.query(
            TaggedObject,
            superset.models.core.Dashboard,
            superset.models.core.Slice,
            SavedQuery,
        ).join(Tag)
        """

        tags = [
            process_template(tag)
            for tag in request.args.get('tags', '').split(',') if tag
        ]
        if not tags:
            return json_success(json.dumps([]))

        # filter types
        types = [
            type_
            for type_ in request.args.get('types', '').split(',')
            if type_
        ]

        results = []

        # dashboards
        query = (
            db.session
            .query(TaggedObject, superset.models.core.Dashboard)
            .join(Tag)
            .filter(Tag.name.in_(tags)))
        if types:
            query = query.filter(TaggedObject.object_type.in_(types))
        dashboards = query.outerjoin(
            superset.models.core.Dashboard,
            and_(
                TaggedObject.object_id == superset.models.core.Dashboard.id,
                TaggedObject.object_type == ObjectTypes.dashboard,
            ),
        ).all()
        results.extend(
            {
                'id': obj.Dashboard.id,
                'type': obj.TaggedObject.object_type.name,
                'name': obj.Dashboard.dashboard_title,
                'url': obj.Dashboard.url,
                'changed_on': obj.Dashboard.changed_on,
                'created_by': obj.Dashboard.created_by_fk,
                'creator': obj.Dashboard.creator(),
            } for obj in dashboards if obj.Dashboard
        )

        # charts
        query = (
            db.session
            .query(TaggedObject, superset.models.core.Slice)
            .join(Tag)
            .filter(Tag.name.in_(tags)))
        if types:
            query = query.filter(TaggedObject.object_type.in_(types))
        charts = query.outerjoin(
            superset.models.core.Slice,
            and_(
                TaggedObject.object_id == superset.models.core.Slice.id,
                TaggedObject.object_type == ObjectTypes.chart,
            ),
        ).all()
        results.extend(
            {
                'id': obj.Slice.id,
                'type': obj.TaggedObject.object_type.name,
                'name': obj.Slice.slice_name,
                'url': obj.Slice.url,
                'changed_on': obj.Slice.changed_on,
                'created_by': obj.Slice.created_by_fk,
                'creator': obj.Slice.creator(),
            } for obj in charts if obj.Slice
        )

        # saved queries
        query = (
            db.session
            .query(TaggedObject, SavedQuery)
            .join(Tag)
            .filter(Tag.name.in_(tags)))
        if types:
            query = query.filter(TaggedObject.object_type.in_(types))
        saved_queries = query.outerjoin(
            SavedQuery,
            and_(
                TaggedObject.object_id == SavedQuery.id,
                TaggedObject.object_type == ObjectTypes.query,
            ),
        ).all()
        results.extend(
            {
                'id': obj.SavedQuery.id,
                'type': obj.TaggedObject.object_type.name,
                'name': obj.SavedQuery.label,
                'url': obj.SavedQuery.url,
                'changed_on': obj.SavedQuery.changed_on,
                'created_by': obj.SavedQuery.created_by_fk,
                'creator': obj.SavedQuery.creator(),
            } for obj in saved_queries if obj.SavedQuery
        )

        return json_success(json.dumps(results, default=utils.core.json_int_dttm_ser))


app.url_map.converters['object_type'] = ObjectTypeConverter
appbuilder.add_view_no_menu(TagView)
