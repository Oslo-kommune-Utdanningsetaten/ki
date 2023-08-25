from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

db = SQLAlchemy()
socketio = SocketIO()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)
    socketio.init_app(app)
    socketio.run(app)

    with app.app_context():
        from app.main.routes import main
        from app.main.auth import auth
        from app.main.api import api
        app.register_blueprint(main)
        app.register_blueprint(auth)
        app.register_blueprint(api)

    return app
