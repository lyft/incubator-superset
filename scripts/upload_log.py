import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import sys
import time

from datetime import datetime
from datetime import timedelta
from os import getenv

from flask_script import Command
from flask_script import Option
from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import and_
from subprocess import check_call
from superset import db
from superset import security_manager
from superset.connectors.sqla.models import SqlaTable
from superset.models.core import Slice
from superset.models.core import Dashboard
from superset.models.core import Log


class UploadLog(Command):
    option_list = (
        Option('--date', type=str, required=False, help='the date'),
    )

    def run(self, date=None):
        date_format = '%Y-%m-%d'
        if date is None:
            end_date = datetime.now().strftime(date_format)
            ds = (datetime.now() - timedelta(days=1)).strftime(date_format)
        else:
            ds = date
            end_date = (datetime.strptime(ds, date_format) + timedelta(days=1)).strftime(date_format)

        self._upload_logs(ds, end_date)
        self._upload_ab_user(ds)
        self._upload_dashboards(ds)
        self._upload_slices(ds)
        self._upload_tables(ds)

    def _upload_dashboards(self, ds):
        dashboards = db.session.query(Dashboard).all()
        df_rows = [
            {
                'created_on': np.int64(time.mktime(row.created_on.timetuple())),
                'changed_on': np.int64(time.mktime(row.changed_on.timetuple())),
                'id': np.int64(row.id),
                'dashboard_title': row.dashboard_title,
                'position_json': row.position_json,
                'css': row.css,
                'description': row.description,
                'slug': row.slug,
                'json_metadata': row.json_metadata,
            }
            for row in dashboards
        ]
        pa_schema = pa.schema([
            ('created_on', pa.int64()),
            ('changed_on', pa.int64()),
            ('id', pa.int64()),
            ('dashboard_title', pa.string()),
            ('position_json', pa.string()),
            ('css', pa.string()),
            ('description', pa.string()),
            ('slug', pa.string()),
            ('json_metadata', pa.string()),
        ])
        self.write_df_rows_to_s3(df_rows=df_rows, pa_schema=pa_schema, tbl_name='dashboards', ds=ds)


    def _upload_slices(self, ds):
        slices = db.session.query(Slice).all()
        df_rows = [
            {
                'created_on': np.int64(time.mktime(row.created_on.timetuple())),
                'changed_on': np.int64(time.mktime(row.changed_on.timetuple())),
                'id': np.int64(row.id),
                'slice_name': row.slice_name,
                'datasource_type': row.datasource_type,
                'datasource_name': row.datasource_name,
                'viz_type': row.viz_type,
                'params': row.params,
                'description': row.description,
                'cache_timeout': None if row.cache_timeout is None else np.int64(row.cache_timeout),
                'perm': row.perm,
                'datasource_id': np.int64(row.datasource_id),
            }
            for row in slices
        ]
        pa_schema = pa.schema([
            ('created_on', pa.int64()),
            ('changed_on', pa.int64()),
            ('id', pa.int64()),
            ('slice_name', pa.string()),
            ('datasource_type', pa.string()),
            ('datasource_name', pa.string()),
            ('viz_type', pa.string()),
            ('params', pa.string()),
            ('description', pa.string()),
            ('cache_timeout', pa.int64()),
            ('perm', pa.string()),
            ('datasource_id', pa.int64()),
        ])
        self.write_df_rows_to_s3(df_rows=df_rows, pa_schema=pa_schema, tbl_name='slices', ds=ds)


    def _upload_tables(self, ds):
        tables = db.session.query(SqlaTable).all()
        df_rows = [
            {
                'created_on': np.int64(time.mktime(row.created_on.timetuple())),
                'changed_on': np.int64(time.mktime(row.changed_on.timetuple())),
                'id': np.int64(row.id),
                'table_name': row.table_name,
                'main_dttm_col': row.main_dttm_col,
                'default_endpoint': row.default_endpoint,
                'database_id': np.int64(row.database_id),
                'offset': None if row.offset is None else np.int64(row.offset),
                'description': row.description,
                'is_featured': np.int64(row.is_featured),
                'cache_timeout': None if row.cache_timeout is None else np.int64(row.cache_timeout),
                'schema': row.schema,
                'sql': row.sql,
                'params': row.params,
                'perm': row.perm,
                'filter_select_enabled': np.int64(row.filter_select_enabled),
                'fetch_values_predicate': row.fetch_values_predicate,
                'is_sqllab_view': np.int64(row.is_sqllab_view),
                'template_params': row.template_params,
            }
            for row in tables
        ]
        pa_schema = pa.schema([
            ('created_on', pa.int64()),
            ('changed_on', pa.int64()),
            ('id', pa.int64()),
            ('table_name', pa.string()),
            ('main_dttm_col', pa.string()),
            ('default_endpoint', pa.string()),
            ('database_id', pa.int64()),
            ('offset', pa.int64()),
            ('description', pa.string()),
            ('is_featured', pa.int64()),
            ('cache_timeout', pa.int64()),
            ('schema', pa.string()),
            ('sql', pa.string()),
            ('params', pa.string()),
            ('perm', pa.string()),
            ('filter_select_enabled', pa.int64()),
            ('fetch_values_predicate', pa.string()),
            ('is_sqllab_view', pa.int64()),
            ('template_params', pa.string()),
        ])
        self.write_df_rows_to_s3(df_rows=df_rows, pa_schema=pa_schema, tbl_name='tables', ds=ds)


    def _upload_ab_user(self, ds):
        AbUser = security_manager.user_model
        ab_users = db.session.query(AbUser).all()
        df_rows = [
            {
                'id': np.int64(row.id),
                'first_name': row.first_name,
                'last_name': row.last_name,
                'username': row.username,
                'active': np.int64(row.active),
                'email': row.email,
                'last_login': np.int64(time.mktime(row.last_login.timetuple())),
                'login_count': row.login_count,
                'fail_login_count': row.fail_login_count,
                'created_on': np.int64(time.mktime(row.created_on.timetuple())),
                'changed_on': np.int64(time.mktime(row.changed_on.timetuple())),
            }
            for row in ab_users
        ]
        pa_schema = pa.schema([
            ('id', pa.int64()),
            ('first_name', pa.string()),
            ('last_name', pa.string()),
            ('username', pa.string()),
            ('active', pa.int64()),
            ('email', pa.string()),
            ('last_login', pa.int64()),
            ('login_count', pa.int64()),
            ('fail_login_count', pa.int64()),
            ('created_on', pa.int64()),
            ('changed_on', pa.int64()),
        ])
        self.write_df_rows_to_s3(df_rows=df_rows, pa_schema=pa_schema, tbl_name='ab_user', ds=ds)


    def _upload_logs(self, ds, end_date):
        logs = db.session.query(Log).filter(and_(
            Log.dttm >= ds,
            Log.dttm < end_date,
        ))
        df_rows = [
            {
                'id': np.int64(row.id),
                'action': row.action,
                'user_id': None if row.user_id is None else np.int64(row.user_id),
                'json': row.json,
                'dttm': np.int64(time.mktime(row.dttm.timetuple())),
                'dashboard_id': None if row.dashboard_id is None else np.int64(row.dashboard_id),
                'slice_id': None if row.slice_id is None else np.int64(row.slice_id),
                'duration_ms': None if row.duration_ms is None else np.int64(row.duration_ms),
                'referrer': row.referrer,
                'ds': ds,
            }
            for row in logs
        ]
        pa_schema = pa.schema([
            ('id', pa.int64()),
            ('action', pa.string()),
            ('user_id', pa.int64()),
            ('json', pa.string()),
            ('dttm', pa.int64()),
            ('dashboard_id', pa.int64()),
            ('slice_id', pa.int64()),
            ('duration_ms', pa.int64()),
            ('referrer', pa.string()),
            ('ds', pa.string()),
        ])
        self.write_df_rows_to_s3(df_rows=df_rows, pa_schema=pa_schema, tbl_name='logs', ds=ds)


    def write_df_rows_to_s3(self, df_rows, pa_schema, tbl_name, ds):
        if len(df_rows) == 0:
            return

        df = pd.DataFrame(df_rows)
        tbl_content = pa.Table.from_pandas(df=df, schema=pa_schema)
        parquet_file_name = f'{tbl_name}_{ds}.snappy.parquet'
        pq.write_table(tbl_content, parquet_file_name)
        cmd = [
            'aws',
            's3',
            'cp',
            parquet_file_name,
            f's3://lyftqubole-iad/qubole/production/superset/{tbl_name}/ds={ds}/{parquet_file_name}',
            '--acl',
            'bucket-owner-full-control',
        ]
        check_call(cmd)
