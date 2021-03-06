from flask import Flask
from flask_cors import CORS

from controllers.diary import diary_app
from controllers.series import series_app
from controllers.user import user_app

def create_app(TEST_CONFIG = None):
    app = Flask(__name__)
    CORS(app, resources={r'*': {'origins': '*'}})
    app.register_blueprint(diary_app, url_prefix='/diary')
    app.register_blueprint(series_app, url_prefix='/series')
    app.register_blueprint(user_app, url_prefix='/user')
    return app
