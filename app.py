from flask import Flask, json

from paths import TEMPLATE_FOLDER, STATIC_FOLDER
from extensions import db, bootstrap
from routes import router


def create_app(config):
    app = Flask("beurskrach", template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)
    app.config.update(config)
    
    db.init_app(app)
    bootstrap.init_app(app)
    
    app.register_blueprint(router)
    
    return app
    

def default_config():
    with open('config.json') as fp:
        return json.load(fp)
        
