#!/usr/bin/env python

from flask_script import Manager

from superset import app
from scripts.upload_log import UploadLog


manager = Manager(app)

manager.add_command('upload-log', UploadLog())

if __name__ == '__main__':
    manager.run()
