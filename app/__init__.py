# app/__init__.py
from flask import Flask
import os
from config import AUDIO_OUTPUT_DIR

def create_app():
    app = Flask(__name__)
    os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True) # 确保输出目录存在
    
    with app.app_context():
        from . import routes
        app.register_blueprint(routes.bp)
        
    return app
