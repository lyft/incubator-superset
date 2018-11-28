import os

from lyft.analytics_event_logger import AnalyticsEventLogger

from superset.utils.core import now_as_float


def log_query(database, query, schema=None, user=None, client=None):
    event = {
        'event_name': 'superset_query_logged',
        'database': database,
        'query': query,
        'submitted_at': now_as_float(),
        'environment': os.getenv('APPLICATION_ENV', 'development'),
    }
    if schema:
        event['schema'] = schema
    if user:
        event['user'] = user
    if client:
        event['client'] = client

    AnalyticsEventLogger(event)
