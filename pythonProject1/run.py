import os
from flask import Flask, render_template, send_file, jsonify, make_response
from flask_migrate import Migrate
from flask_minify import Minify
from sys import exit
from config import config_dict
from app import create_app, db
import multiprocessing
import schedule
import threading
import time
from flask_mail import Mail, Message
import schedule
import threading
import time
from app.model import *
from datetime import datetime, timedelta
from sqlalchemy import desc, exists, func, case,or_, extract ,and_


# Flask Application
app = Flask(__name__)


def run_background_task():
    from app import background


# WARNING: Don't run with debug turned on in production!
DEBUG = (os.getenv('DEBUG', 'False') == 'True')

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

try:

    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)
Migrate(app, db)

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)

if DEBUG:
    app.logger.info('DEBUG       = ' + str(DEBUG))
    app.logger.info('DBMS        = ' + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info('ASSETS_ROOT = ' + app_config.ASSETS_ROOT)


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=2020)
